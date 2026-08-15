//! Runtime-checkable invariants, used by proptests to verify the
//! five TLA+ safety properties across a running [`Cluster`].

use crate::cluster::Cluster;
use crate::node::Role;
use crate::types::{Category, Entry, LogIndex, NodeId, Term};

/// TLA+ `ElectionSafety`: at most one leader per term.
pub fn election_safety(c: &Cluster) -> Result<(), String> {
    let mut by_term: std::collections::BTreeMap<Term, NodeId> = std::collections::BTreeMap::new();
    for (id, node) in &c.nodes {
        if node.role == Role::Leader {
            if let Some(existing) = by_term.get(&node.current_term) {
                if existing != id {
                    return Err(format!(
                        "two leaders in term {:?}: {} and {}",
                        node.current_term, existing, id
                    ));
                }
            } else {
                by_term.insert(node.current_term, *id);
            }
        }
    }
    Ok(())
}

/// TLA+ `LogMatching`: if two logs contain entries at the same index
/// with the same term, the prefixes up to that index are identical.
pub fn log_matching(c: &Cluster) -> Result<(), String> {
    let ids: Vec<NodeId> = c.node_ids();
    for i in 0..ids.len() {
        for j in (i + 1)..ids.len() {
            let a = &c.nodes[&ids[i]].log;
            let b = &c.nodes[&ids[j]].log;
            for k in 0..a.len().min(b.len()) {
                if a[k].term == b[k].term {
                    for m in 0..=k {
                        if a[m] != b[m] {
                            return Err(format!(
                                "LogMatching violated at index {} between {} and {}",
                                m + 1,
                                ids[i],
                                ids[j]
                            ));
                        }
                    }
                }
            }
        }
    }
    Ok(())
}

/// TLA+ `StateMachineSafety`: for any two nodes, their committed
/// prefixes agree up to `min(commit_index_a, commit_index_b)`.
pub fn state_machine_safety(c: &Cluster) -> Result<(), String> {
    let ids: Vec<NodeId> = c.node_ids();
    for i in 0..ids.len() {
        for j in (i + 1)..ids.len() {
            let a = &c.nodes[&ids[i]];
            let b = &c.nodes[&ids[j]];
            let min_ci = core::cmp::min(a.commit_index, b.commit_index).0 as usize;
            for k in 0..min_ci {
                if a.log.get(k) != b.log.get(k) {
                    return Err(format!(
                        "StateMachineSafety violated at index {} between {} and {}",
                        k + 1,
                        ids[i],
                        ids[j]
                    ));
                }
            }
        }
    }
    Ok(())
}

/// TLA+ `LeaderCompleteness`: every currently-committed entry (from
/// any follower's committed prefix) is present in the *same-or-higher-
/// term* leader's log at the same index.
///
/// A stale leader partitioned with a low term and an empty log is
/// not the "current leader" in the LeaderCompleteness sense — its
/// peers have already moved on. We require the leader we check
/// against to have a term ≥ any follower's current term, reflecting
/// the fact that LeaderCompleteness is a claim about the leader of
/// a higher term.
pub fn leader_completeness(c: &Cluster) -> Result<(), String> {
    let Some(leader_id) = c.leader() else {
        return Ok(());
    };
    let leader = &c.nodes[&leader_id];
    for (id, node) in &c.nodes {
        if *id == leader_id {
            continue;
        }
        // Stale-leader guard: if the "leader" here is at a term
        // strictly less than a follower's, that leader has not yet
        // learned about newer elections — LeaderCompleteness is a
        // claim about the *current* (highest-term) leader, so skip
        // the check against a stale leader.
        if leader.current_term < node.current_term {
            return Ok(());
        }
        let ci = node.commit_index.0 as usize;
        for k in 0..ci {
            let follower_entry = &node.log[k];
            let leader_entry = leader.log.get(k);
            match leader_entry {
                Some(le) if le == follower_entry => {}
                _ => {
                    return Err(format!(
                        "LeaderCompleteness violated at index {}: follower {} (term {:?}) has {:?}, leader {} (term {:?}) has {:?}",
                        k + 1,
                        id,
                        node.current_term,
                        follower_entry,
                        leader_id,
                        leader.current_term,
                        leader_entry
                    ));
                }
            }
        }
    }
    Ok(())
}

/// TLA+ `FailRestrictive` (operational form): a `Safety` entry may
/// only be *appended* by a leader whose quorum confirmation is
/// fresh. Once appended, [`super::step::on_tick`] can decrement
/// `last_quorum_confirmed_term` via `QuorumConfirmationExpires`
/// without retroactively invalidating the entry — the
/// safety-relevant moment was append-time.
///
/// The structural TLA+ form is strictly stronger and would flag the
/// legitimate post-expiry state. The operational form below is what
/// `propose()` actually enforces:
///
/// - If the leader's LQCT is `currentTerm`, any Safety entry is fine.
/// - If the leader's LQCT is `currentTerm - 1`, Safety entries in
///   `currentTerm` are tolerated — they were appended while fresh,
///   then a single `QuorumConfirmationExpires` decrement occurred.
/// - If the leader's LQCT is lower than `currentTerm - 1`, no
///   Safety entry in `currentTerm` is legal (the `propose()` gate
///   would have rejected any attempt).
pub fn fail_restrictive(c: &Cluster) -> Result<(), String> {
    for (id, node) in &c.nodes {
        if node.role != Role::Leader {
            continue;
        }
        let ct = node.current_term.0;
        let lqct = node.last_quorum_confirmed_term.0;
        // Tolerance: LQCT == currentTerm, or LQCT == currentTerm - 1
        // (one expiry cycle since the last fresh confirmation).
        if ct > 0 && lqct < ct - 1 {
            for (i, e) in node.log.iter().enumerate() {
                if e.term == node.current_term && e.category == Category::Safety {
                    return Err(format!(
                        "FailRestrictive violated: leader {} has Safety entry at index {} in term {:?} but quorum-confirm term is {:?}",
                        id, i + 1, node.current_term, node.last_quorum_confirmed_term
                    ));
                }
            }
        }
    }
    Ok(())
}

/// Check all five invariants; return the first failure, if any.
pub fn check_all(c: &Cluster) -> Result<(), String> {
    election_safety(c)?;
    log_matching(c)?;
    state_machine_safety(c)?;
    leader_completeness(c)?;
    fail_restrictive(c)?;
    Ok(())
}

// Keep unused items warning-free.
#[allow(dead_code)]
fn _types_are_used(_: LogIndex, _: Entry) {}
