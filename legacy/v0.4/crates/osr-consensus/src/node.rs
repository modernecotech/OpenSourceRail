//! `RaftNode` — the per-server state.
//!
//! Field layout mirrors the TLA+ VARIABLES section directly. Where
//! the TLA+ uses a function `[Server -> X]`, the Rust holds only this
//! server's view (one `X` per field).

use std::collections::{BTreeMap, BTreeSet};

use crate::types::{Entry, LogIndex, NodeId, Term};

/// The Raft role of a node.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Role {
    Follower,
    Candidate,
    Leader,
}

use serde::{Deserialize, Serialize};

/// Static-membership Raft configuration. Fixed at construction.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Config {
    pub me: NodeId,
    /// All nodes in the consensus group, including `me`.
    pub peers: BTreeSet<NodeId>,
    /// Election timeout in nanoseconds. A follower or candidate that
    /// has not heard from a leader for this duration times out and
    /// starts a new election. To mitigate split votes the timeout is
    /// randomised by the caller across nodes; this field is the
    /// *effective* timeout for this node.
    pub election_timeout_ns: u64,
    /// Heartbeat (empty `AppendEntries`) interval in nanoseconds for
    /// leaders. Must be < `election_timeout_ns`.
    pub heartbeat_interval_ns: u64,
    /// Fail-restrictive window in nanoseconds: a leader must hear
    /// from a quorum within this window or it loses the right to
    /// commit new `Safety` entries in this term.
    pub fail_restrictive_window_ns: u64,
}

impl Config {
    /// Sensible defaults for a 3-node wayside region.
    #[must_use]
    pub fn with_defaults(me: NodeId, peers: BTreeSet<NodeId>) -> Self {
        Self {
            me,
            peers,
            election_timeout_ns: 150_000_000,        // 150 ms
            heartbeat_interval_ns: 50_000_000,       // 50 ms
            fail_restrictive_window_ns: 500_000_000, // 500 ms
        }
    }

    /// Quorum size — strict majority of members.
    #[must_use]
    pub fn quorum_size(&self) -> usize {
        self.peers.len() / 2 + 1
    }
}

/// Per-server Raft state.
///
/// Field groupings follow the TLA+ `serverVars`, `candidateVars`,
/// `leaderVars`, `logVars`, `failRestrictVars` partitions.
#[derive(Clone, Debug)]
pub struct RaftNode {
    pub config: Config,

    // --- serverVars (persistent) --------------------------------------
    pub current_term: Term,
    pub voted_for: Option<NodeId>,
    pub log: Vec<Entry>,

    // --- serverVars (volatile) ----------------------------------------
    pub role: Role,
    pub commit_index: LogIndex,

    // --- candidateVars -------------------------------------------------
    pub votes_granted: BTreeSet<NodeId>,

    // --- leaderVars ----------------------------------------------------
    /// For each peer, the next log index to send.
    pub next_index: BTreeMap<NodeId, LogIndex>,
    /// For each peer, the highest log index known replicated.
    pub match_index: BTreeMap<NodeId, LogIndex>,

    // --- failRestrictVars ----------------------------------------------
    /// The largest term in which this node, as leader, last received
    /// an `AppendEntriesResponse(success=true)` from a quorum.
    /// Mirrors TLA+ `lastQuorumConfirmedTerm`.
    pub last_quorum_confirmed_term: Term,
    /// Absolute time (ns) at which the quorum confirmation was
    /// last refreshed. Drives [`Event::Tick`] expiry logic.
    pub last_quorum_confirmed_ns: u64,

    // --- Timers --------------------------------------------------------
    /// Deadline (ns) by which this node must hear from a leader
    /// (follower/candidate) or the election times out.
    pub election_deadline_ns: u64,
    /// Next time (ns) a leader should emit heartbeats.
    pub next_heartbeat_ns: u64,
}

impl RaftNode {
    /// Construct a fresh node.
    #[must_use]
    pub fn new(config: Config, now_ns: u64) -> Self {
        let peers = config.peers.clone();
        let mut next_index = BTreeMap::new();
        let mut match_index = BTreeMap::new();
        for p in &peers {
            next_index.insert(*p, LogIndex::new(1));
            match_index.insert(*p, LogIndex::zero());
        }
        Self {
            config: config.clone(),
            current_term: Term::zero(),
            voted_for: None,
            log: Vec::new(),
            role: Role::Follower,
            commit_index: LogIndex::zero(),
            votes_granted: BTreeSet::new(),
            next_index,
            match_index,
            last_quorum_confirmed_term: Term::zero(),
            last_quorum_confirmed_ns: now_ns,
            election_deadline_ns: now_ns.saturating_add(config.election_timeout_ns),
            next_heartbeat_ns: u64::MAX,
        }
    }

    /// Log length in TLA+ sense (number of entries).
    #[must_use]
    pub fn log_len(&self) -> LogIndex {
        LogIndex::new(self.log.len() as u64)
    }

    /// Term of the last log entry (0 if empty).
    #[must_use]
    pub fn last_log_term(&self) -> Term {
        Entry::last_term(&self.log)
    }

    /// Get entry at TLA+ 1-indexed `index`, or `None` if out of range.
    #[must_use]
    pub fn entry_at(&self, index: LogIndex) -> Option<&Entry> {
        let off = index.as_vec_offset()?;
        self.log.get(off)
    }

    /// Term at 1-indexed `index`, or 0 for index 0 / out of range.
    #[must_use]
    pub fn term_at(&self, index: LogIndex) -> Term {
        self.entry_at(index).map(|e| e.term).unwrap_or(Term::zero())
    }

    /// TLA+ `UpdateTerm`: on observing a higher term, step down to
    /// follower and clear vote.
    pub fn update_term(&mut self, new_term: Term, now_ns: u64) {
        if new_term > self.current_term {
            self.current_term = new_term;
            self.voted_for = None;
            self.role = Role::Follower;
            self.reset_election_deadline(now_ns);
        }
    }

    pub fn reset_election_deadline(&mut self, now_ns: u64) {
        self.election_deadline_ns = now_ns.saturating_add(self.config.election_timeout_ns);
    }

    /// Committed prefix. This is what `osr-interlocking` consumes.
    #[must_use]
    pub fn committed_prefix(&self) -> &[Entry] {
        let ci = self.commit_index.0 as usize;
        &self.log[..ci.min(self.log.len())]
    }

    /// True iff the fail-restrictive confirmation is fresh enough to
    /// commit new `Safety` entries in the current term.
    #[must_use]
    pub fn quorum_confirmation_fresh(&self) -> bool {
        self.last_quorum_confirmed_term == self.current_term
    }
}
