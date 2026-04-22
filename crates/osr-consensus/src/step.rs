//! Pure state-machine step function.
//!
//! `step(node, event, now_ns)` is the single interaction point. It
//! mutates the node, returns the list of outgoing actions, and has
//! no side effects besides that mutation.
//!
//! Each TLA+ action maps to a handler here:
//!
//! | TLA+                           | Rust handler                 |
//! |--------------------------------|------------------------------|
//! | `Timeout(s)`                   | `on_tick` (when deadline hit)|
//! | `BecomeLeader(s)`              | `maybe_become_leader`        |
//! | `RequestVote(s,t)`             | `emit_request_votes`         |
//! | `HandleRequestVote(s,m)`       | `handle_request_vote`        |
//! | `HandleRequestVoteResponse`    | `handle_request_vote_response`|
//! | `AppendEntries(s,t)`           | `emit_append_entries`        |
//! | `HandleAppendEntries(s,m)`     | `handle_append_entries`      |
//! | `HandleAppendEntriesResponse`  | `handle_append_entries_response`|
//! | `AdvanceCommitIndex(s)`        | `advance_commit_index`       |
//! | `ClientRequest(s,v,c)`         | `propose`                    |
//! | `QuorumConfirmationExpires(s)` | `on_tick` (when window lapsed)|

use crate::messages::{
    AppendEntriesRequest, AppendEntriesResponse, Message, RequestVoteRequest, RequestVoteResponse,
};
use crate::node::{RaftNode, Role};
use crate::types::{Category, Entry, LogIndex, NodeId, Term};

/// An input to the state machine.
#[derive(Clone, Debug)]
pub enum Event {
    /// Wall clock advanced; re-evaluate timers.
    Tick,
    /// An RPC message arrived.
    Recv(Message),
    /// The local application wants to append an entry.
    Propose { value: Vec<u8>, category: Category },
}

/// An output of the state machine.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Action {
    /// Send this message to its addressee.
    Send(Message),
    /// An entry has just been committed; caller should apply to its
    /// state machine.
    Committed { index: LogIndex, entry: Entry },
    /// The local node transitioned to Leader in `term`.
    BecameLeader { term: Term },
    /// The local node transitioned to Follower in `term`.
    BecameFollower { term: Term },
    /// A `Propose` was rejected.
    ProposeRejected { reason: RejectReason },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RejectReason {
    NotLeader,
    FailRestrictive,
}

/// Top-level step function.
///
/// Pure in the sense that all I/O (sending messages, applying
/// committed entries) is deferred to the caller via the returned
/// `Action` list.
pub fn step(node: &mut RaftNode, event: Event, now_ns: u64) -> Vec<Action> {
    let mut actions = Vec::new();
    match event {
        Event::Tick => on_tick(node, now_ns, &mut actions),
        Event::Recv(msg) => on_recv(node, msg, now_ns, &mut actions),
        Event::Propose { value, category } => {
            propose(node, value, category, &mut actions);
        }
    }
    actions
}

// ---------------------------------------------------------------------------
// Timer-driven actions
// ---------------------------------------------------------------------------

fn on_tick(node: &mut RaftNode, now_ns: u64, actions: &mut Vec<Action>) {
    // TLA+ `Timeout(s)`: election timeout on follower or candidate.
    if matches!(node.role, Role::Follower | Role::Candidate) && now_ns >= node.election_deadline_ns
    {
        start_election(node, now_ns, actions);
    }

    // TLA+ `QuorumConfirmationExpires(s)`: as leader, window elapses.
    if node.role == Role::Leader
        && node.last_quorum_confirmed_term == node.current_term
        && now_ns >= node.last_quorum_confirmed_ns.saturating_add(node.config.fail_restrictive_window_ns)
    {
        // Mark stale: set to a strictly-earlier term than current.
        node.last_quorum_confirmed_term = Term(node.current_term.0.saturating_sub(1));
    }

    // Leader heartbeat.
    if node.role == Role::Leader && now_ns >= node.next_heartbeat_ns {
        emit_append_entries_broadcast(node, actions);
        node.next_heartbeat_ns = now_ns.saturating_add(node.config.heartbeat_interval_ns);
    }
}

fn start_election(node: &mut RaftNode, now_ns: u64, actions: &mut Vec<Action>) {
    // TLA+ `Timeout(s)`: new term, become candidate, self-vote.
    node.current_term = node.current_term.succ();
    node.role = Role::Candidate;
    node.voted_for = Some(node.config.me);
    node.votes_granted.clear();
    node.votes_granted.insert(node.config.me);
    node.reset_election_deadline(now_ns);

    // Degenerate cluster: if single-node, self-vote is already a quorum.
    if node.votes_granted.len() >= node.config.quorum_size() {
        become_leader(node, now_ns, actions);
        return;
    }

    emit_request_votes(node, actions);
}

fn emit_request_votes(node: &RaftNode, actions: &mut Vec<Action>) {
    let req_template = RequestVoteRequest {
        term: node.current_term,
        from: node.config.me,
        to: NodeId(0), // filled per-peer
        last_log_index: node.log_len(),
        last_log_term: node.last_log_term(),
    };
    for p in &node.config.peers {
        if *p == node.config.me {
            continue;
        }
        let mut req = req_template.clone();
        req.to = *p;
        actions.push(Action::Send(Message::RequestVoteRequest(req)));
    }
}

fn become_leader(node: &mut RaftNode, now_ns: u64, actions: &mut Vec<Action>) {
    // TLA+ `BecomeLeader(s)`.
    node.role = Role::Leader;
    let next = node.log_len().succ();
    for p in &node.config.peers {
        node.next_index.insert(*p, next);
        node.match_index.insert(*p, LogIndex::zero());
    }
    // Self-match is the leader's own log length. Used by the commit
    // logic (the leader counts itself in the quorum).
    node.match_index.insert(node.config.me, node.log_len());
    // Fresh quorum confirmation for our own term.
    node.last_quorum_confirmed_term = node.current_term;
    node.last_quorum_confirmed_ns = now_ns;
    node.next_heartbeat_ns = now_ns; // heartbeat immediately
    actions.push(Action::BecameLeader {
        term: node.current_term,
    });
    // Immediate AE broadcast so followers learn of the new leader.
    emit_append_entries_broadcast(node, actions);
}

// ---------------------------------------------------------------------------
// Proposals (client requests)
// ---------------------------------------------------------------------------

fn propose(
    node: &mut RaftNode,
    value: Vec<u8>,
    category: Category,
    actions: &mut Vec<Action>,
) {
    if node.role != Role::Leader {
        actions.push(Action::ProposeRejected {
            reason: RejectReason::NotLeader,
        });
        return;
    }
    // Fail-restrictive: Safety entries require fresh quorum confirmation.
    if category == Category::Safety && !node.quorum_confirmation_fresh() {
        actions.push(Action::ProposeRejected {
            reason: RejectReason::FailRestrictive,
        });
        return;
    }
    node.log.push(Entry::new(node.current_term, value, category));
    // Self-match bumps with our own append.
    node.match_index.insert(node.config.me, node.log_len());
    // The new entry ships on the next heartbeat tick; no immediate AE.
}

// ---------------------------------------------------------------------------
// Incoming messages
// ---------------------------------------------------------------------------

fn on_recv(node: &mut RaftNode, msg: Message, now_ns: u64, actions: &mut Vec<Action>) {
    // Any higher-term observation demotes this node. Uniform across
    // message types (TLA+ `UpdateTerm` applies in every handler).
    let incoming_term = msg.term();
    if incoming_term > node.current_term {
        let was_leader = node.role == Role::Leader;
        node.update_term(incoming_term, now_ns);
        if was_leader {
            actions.push(Action::BecameFollower {
                term: node.current_term,
            });
        }
    }

    match msg {
        Message::RequestVoteRequest(m) => handle_request_vote(node, m, actions),
        Message::RequestVoteResponse(m) => handle_request_vote_response(node, m, now_ns, actions),
        Message::AppendEntriesRequest(m) => handle_append_entries(node, m, now_ns, actions),
        Message::AppendEntriesResponse(m) => handle_append_entries_response(node, m, now_ns, actions),
    }
}

fn handle_request_vote(node: &mut RaftNode, m: RequestVoteRequest, actions: &mut Vec<Action>) {
    // TLA+ `HandleRequestVote`.
    let log_ok = m.last_log_term > node.last_log_term()
        || (m.last_log_term == node.last_log_term() && m.last_log_index >= node.log_len());
    let term_ok = m.term == node.current_term;
    let already_voted_for_candidate = matches!(node.voted_for, Some(v) if v == m.from);
    let can_grant = term_ok
        && log_ok
        && (node.voted_for.is_none() || already_voted_for_candidate);

    if can_grant {
        node.voted_for = Some(m.from);
    }
    let resp = RequestVoteResponse {
        term: node.current_term,
        from: node.config.me,
        to: m.from,
        vote_granted: can_grant,
    };
    actions.push(Action::Send(Message::RequestVoteResponse(resp)));
}

fn handle_request_vote_response(
    node: &mut RaftNode,
    m: RequestVoteResponse,
    now_ns: u64,
    actions: &mut Vec<Action>,
) {
    // TLA+ `HandleRequestVoteResponse`.
    if node.role != Role::Candidate || m.term != node.current_term {
        return;
    }
    if !m.vote_granted {
        return;
    }
    node.votes_granted.insert(m.from);
    if node.votes_granted.len() >= node.config.quorum_size() {
        become_leader(node, now_ns, actions);
    }
}

fn handle_append_entries(
    node: &mut RaftNode,
    m: AppendEntriesRequest,
    now_ns: u64,
    actions: &mut Vec<Action>,
) {
    // TLA+ `HandleAppendEntries`.
    let term_ok = m.term >= node.current_term;

    // A valid AE resets the election timer and demotes a stale candidate.
    if term_ok {
        node.reset_election_deadline(now_ns);
        if node.role == Role::Candidate {
            node.role = Role::Follower;
        }
    }

    let prev_ok = m.prev_log_index == LogIndex::zero()
        || (m.prev_log_index <= node.log_len() && node.term_at(m.prev_log_index) == m.prev_log_term);

    // The response's `match_index` must be the highest log index the
    // follower has just verified *against the leader*, not the
    // follower's total log length. A follower carrying stale entries
    // from a prior term (e.g., a recently-deposed leader) would
    // otherwise falsely report replication at indices it only holds
    // locally, which lets the new leader advance commit_index past
    // true quorum. That was the root cause of the 5-node
    // LeaderCompleteness counterexample — see
    // `crates/osr-consensus/tests/replay_5node.rs`.
    //
    // The correct reported value is `prev_log_index + entries.len()`:
    // entries just written are by construction a verbatim copy of the
    // leader's log at those indices; anything past that point is
    // unverified and must not contribute to the leader's quorum count.
    let (success, match_index_reply) = if term_ok && prev_ok {
        // Raft §5.3: for each entry in m.entries, if it conflicts
        // with the follower's existing log (same index, different
        // term), truncate from that point and append the rest.
        // Otherwise leave the follower's log alone — heartbeats
        // and redundant AEs must not wipe committed entries.
        let start = m.prev_log_index.0 as usize;
        for (offset, new_entry) in m.entries.iter().enumerate() {
            let pos = start + offset;
            match node.log.get(pos) {
                Some(existing) if existing.term != new_entry.term => {
                    node.log.truncate(pos);
                    node.log.extend_from_slice(&m.entries[offset..]);
                    break;
                }
                None => {
                    node.log.extend_from_slice(&m.entries[offset..]);
                    break;
                }
                Some(_) => {
                    // Same term at this position — entry already
                    // present; keep it.
                }
            }
        }
        // The up-to-which-index this AE just validated against the
        // leader. Always ≤ node.log_len().
        let verified = LogIndex::new(
            m.prev_log_index
                .0
                .saturating_add(m.entries.len() as u64),
        );
        // Advance commit index — bounded by what we've verified, not
        // by the follower's total log length. A follower that still
        // holds un-truncated entries past `verified` must not let the
        // leader's leader_commit advance its own commit_index into
        // those un-verified entries.
        if m.leader_commit > node.commit_index {
            let advance_to = core::cmp::min(m.leader_commit, verified);
            if advance_to > node.commit_index {
                let begin = node.commit_index.0;
                let end = advance_to.0;
                for i in (begin + 1)..=end {
                    if let Some(e) = node.entry_at(LogIndex::new(i)) {
                        actions.push(Action::Committed {
                            index: LogIndex::new(i),
                            entry: e.clone(),
                        });
                    }
                }
                node.commit_index = advance_to;
            }
        }
        (true, verified)
    } else {
        (false, LogIndex::zero())
    };

    let resp = AppendEntriesResponse {
        term: node.current_term,
        from: node.config.me,
        to: m.from,
        success,
        match_index: match_index_reply,
    };
    actions.push(Action::Send(Message::AppendEntriesResponse(resp)));
}

fn handle_append_entries_response(
    node: &mut RaftNode,
    m: AppendEntriesResponse,
    now_ns: u64,
    actions: &mut Vec<Action>,
) {
    // TLA+ `HandleAppendEntriesResponse`.
    if node.role != Role::Leader || m.term != node.current_term {
        return;
    }
    if m.success {
        node.match_index.insert(m.from, m.match_index);
        node.next_index.insert(m.from, m.match_index.succ());
        // Count confirmers (self + any follower whose match_index > 0).
        let confirmers = 1 + node
            .match_index
            .iter()
            .filter(|(p, mi)| **p != node.config.me && mi.0 > 0)
            .count();
        if confirmers >= node.config.quorum_size() {
            node.last_quorum_confirmed_term = node.current_term;
            node.last_quorum_confirmed_ns = now_ns;
        }
        advance_commit_index(node, actions);
    } else {
        // Back off by one (Raft's simple conflict resolution).
        let cur = node
            .next_index
            .get(&m.from)
            .copied()
            .unwrap_or(LogIndex::new(1));
        let new = if cur.0 > 1 { cur.pred() } else { LogIndex::new(1) };
        node.next_index.insert(m.from, new);
    }
}

// ---------------------------------------------------------------------------
// AdvanceCommitIndex
// ---------------------------------------------------------------------------

fn advance_commit_index(node: &mut RaftNode, actions: &mut Vec<Action>) {
    // TLA+ `AdvanceCommitIndex(s)`:
    // Find the largest N > commitIndex such that log[N].term == currentTerm
    // AND |{t : matchIndex[t] >= N}| is a quorum.
    let quorum = node.config.quorum_size();
    let max_n = node.log_len();
    let mut best: Option<LogIndex> = None;
    let start = node.commit_index.0 + 1;
    for n in start..=max_n.0 {
        let idx = LogIndex::new(n);
        let term_at_n = node.term_at(idx);
        if term_at_n != node.current_term {
            continue;
        }
        // Count match_index >= n (self already bumped to log_len in propose).
        let replicated_count = node
            .match_index
            .values()
            .filter(|mi| **mi >= idx)
            .count();
        if replicated_count >= quorum {
            best = Some(idx);
        }
    }
    if let Some(new_commit) = best {
        if new_commit > node.commit_index {
            let start = node.commit_index.0 + 1;
            for i in start..=new_commit.0 {
                if let Some(e) = node.entry_at(LogIndex::new(i)) {
                    actions.push(Action::Committed {
                        index: LogIndex::new(i),
                        entry: e.clone(),
                    });
                }
            }
            node.commit_index = new_commit;
        }
    }
}

// ---------------------------------------------------------------------------
// Heartbeat / AppendEntries broadcast
// ---------------------------------------------------------------------------

fn emit_append_entries_broadcast(node: &RaftNode, actions: &mut Vec<Action>) {
    for p in &node.config.peers {
        if *p == node.config.me {
            continue;
        }
        let next = node
            .next_index
            .get(p)
            .copied()
            .unwrap_or(LogIndex::new(1));
        let prev_idx = if next.0 > 0 {
            LogIndex::new(next.0.saturating_sub(1))
        } else {
            LogIndex::zero()
        };
        let prev_term = node.term_at(prev_idx);
        // Send one entry at a time (matches TLA+; can be batched later).
        let entries: Vec<Entry> = match next.as_vec_offset() {
            Some(off) if off < node.log.len() => vec![node.log[off].clone()],
            _ => Vec::new(),
        };
        let req = AppendEntriesRequest {
            term: node.current_term,
            from: node.config.me,
            to: *p,
            prev_log_index: prev_idx,
            prev_log_term: prev_term,
            entries,
            leader_commit: node.commit_index,
        };
        actions.push(Action::Send(Message::AppendEntriesRequest(req)));
    }
}
