//! Deterministic multi-node harness for testing.
//!
//! [`Cluster`] owns a set of [`RaftNode`]s and an in-memory message
//! bag. Test code advances time with [`Cluster::tick`], injects
//! proposals with [`Cluster::propose`], and inspects committed logs.
//!
//! Network behaviour is controlled by [`NetworkPolicy`]: default is
//! reliable instant delivery; tests can drop messages by from/to,
//! reorder, duplicate, or delay.

use std::collections::{BTreeMap, BTreeSet, VecDeque};

use crate::messages::Message;
use crate::node::{Config, RaftNode};
use crate::step::{step, Action, Event};
use crate::types::{Category, Entry, LogIndex, NodeId, Term};

/// Controls message delivery for failure-injection tests.
#[derive(Clone, Debug, Default)]
pub struct NetworkPolicy {
    /// Nodes that are "partitioned" — no messages in or out.
    pub partitioned: BTreeSet<NodeId>,
    /// Drop all messages sent FROM the given node (silent failure).
    pub drop_from: BTreeSet<NodeId>,
    /// Drop all messages sent TO the given node.
    pub drop_to: BTreeSet<NodeId>,
}

impl NetworkPolicy {
    #[must_use]
    pub fn allow(&self, msg: &Message) -> bool {
        if self.partitioned.contains(&msg.from()) || self.partitioned.contains(&msg.to()) {
            return false;
        }
        if self.drop_from.contains(&msg.from()) {
            return false;
        }
        if self.drop_to.contains(&msg.to()) {
            return false;
        }
        true
    }
}

pub struct Cluster {
    pub nodes: BTreeMap<NodeId, RaftNode>,
    pub inbox: BTreeMap<NodeId, VecDeque<Message>>,
    pub policy: NetworkPolicy,
    pub committed: BTreeMap<NodeId, Vec<(LogIndex, Entry)>>,
    pub became_leader: Vec<(u64, NodeId, Term)>, // (now_ns, who, term)
    pub now_ns: u64,
}

impl core::fmt::Debug for Cluster {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.debug_struct("Cluster")
            .field("nodes", &self.nodes.keys().collect::<Vec<_>>())
            .field("now_ns", &self.now_ns)
            .finish()
    }
}

impl Cluster {
    /// Build a cluster with `n` nodes, ids `NodeId(0)..NodeId(n)`.
    ///
    /// Each node gets an election timeout of
    /// `base_election_timeout_ns + 20ms * i`, ensuring deterministic
    /// leader selection in tests (lowest id elected first under no
    /// other pressure).
    #[must_use]
    pub fn new(n: u16, base_election_timeout_ns: u64) -> Self {
        let ids: BTreeSet<NodeId> = (0..n).map(NodeId::new).collect();
        let mut nodes = BTreeMap::new();
        let mut inbox = BTreeMap::new();
        let mut committed = BTreeMap::new();
        for id in &ids {
            let mut cfg = Config::with_defaults(*id, ids.clone());
            cfg.election_timeout_ns =
                base_election_timeout_ns + 20_000_000_u64 * u64::from(id.0);
            nodes.insert(*id, RaftNode::new(cfg, 0));
            inbox.insert(*id, VecDeque::new());
            committed.insert(*id, Vec::new());
        }
        Self {
            nodes,
            inbox,
            policy: NetworkPolicy::default(),
            committed,
            became_leader: Vec::new(),
            now_ns: 0,
        }
    }

    /// Advance clock by `dt_ns` and run `Tick` events on every node.
    /// Then deliver all pending messages round-robin until stable.
    pub fn tick(&mut self, dt_ns: u64) {
        self.now_ns = self.now_ns.saturating_add(dt_ns);
        for id in self.node_ids() {
            self.run_node(id, Event::Tick);
        }
        self.drain_network();
    }

    /// Inject a client proposal at `leader`. Panics if `leader` is
    /// not the leader — the test should first confirm election.
    pub fn propose(&mut self, at: NodeId, value: Vec<u8>, category: Category) {
        self.run_node(at, Event::Propose { value, category });
        self.drain_network();
    }

    /// Drain all pending messages from every inbox, running `Recv`
    /// events, until no more messages are in-flight.
    pub fn drain_network(&mut self) {
        // Safety rails: bound iterations to avoid runaway test loops.
        let max_iters = 1_000_usize;
        for _ in 0..max_iters {
            let to_deliver: Vec<(NodeId, Message)> = self
                .inbox
                .iter_mut()
                .flat_map(|(id, q)| q.drain(..).map(|m| (*id, m)).collect::<Vec<_>>())
                .collect();
            if to_deliver.is_empty() {
                return;
            }
            for (to, msg) in to_deliver {
                if !self.policy.allow(&msg) {
                    continue;
                }
                self.run_node(to, Event::Recv(msg));
            }
        }
        panic!("cluster message drain did not stabilise in {max_iters} iterations");
    }

    fn run_node(&mut self, id: NodeId, event: Event) {
        let Some(node) = self.nodes.get_mut(&id) else { return };
        let actions = step(node, event, self.now_ns);
        for action in actions {
            match action {
                Action::Send(msg) => {
                    if !self.policy.allow(&msg) {
                        continue;
                    }
                    if let Some(q) = self.inbox.get_mut(&msg.to()) {
                        q.push_back(msg);
                    }
                }
                Action::Committed { index, entry } => {
                    self.committed
                        .entry(id)
                        .or_default()
                        .push((index, entry));
                }
                Action::BecameLeader { term } => {
                    self.became_leader.push((self.now_ns, id, term));
                }
                Action::BecameFollower { .. } | Action::ProposeRejected { .. } => {}
            }
        }
    }

    /// Node ids in ascending order.
    pub fn node_ids(&self) -> Vec<NodeId> {
        self.nodes.keys().copied().collect()
    }

    /// Return the current leader, if any. If multiple nodes think
    /// they are leader in the same term (shouldn't happen under
    /// ElectionSafety) the lowest id is returned.
    #[must_use]
    pub fn leader(&self) -> Option<NodeId> {
        let candidates: Vec<_> = self
            .nodes
            .iter()
            .filter(|(_, n)| n.role == crate::node::Role::Leader)
            .map(|(id, n)| (*id, n.current_term))
            .collect();
        if candidates.is_empty() {
            return None;
        }
        // Highest term wins in case of stale leaders.
        let max_term = candidates.iter().map(|(_, t)| *t).max()?;
        candidates
            .into_iter()
            .filter(|(_, t)| *t == max_term)
            .map(|(id, _)| id)
            .min()
    }

    /// Run `tick(dt_ns)` repeatedly until a leader exists.
    /// Returns the elected leader, or `None` if `max_ticks` exhausted.
    pub fn run_until_leader(&mut self, dt_ns: u64, max_ticks: u32) -> Option<NodeId> {
        for _ in 0..max_ticks {
            self.tick(dt_ns);
            if let Some(l) = self.leader() {
                return Some(l);
            }
        }
        self.leader()
    }

    /// Repeatedly tick until every non-partitioned node has committed
    /// at least `min_index` entries, or give up.
    pub fn run_until_committed(&mut self, dt_ns: u64, min_index: LogIndex, max_ticks: u32) -> bool {
        for _ in 0..max_ticks {
            self.tick(dt_ns);
            let ok = self
                .nodes
                .iter()
                .filter(|(id, _)| !self.policy.partitioned.contains(id))
                .all(|(_, n)| n.commit_index >= min_index);
            if ok {
                return true;
            }
        }
        false
    }
}
