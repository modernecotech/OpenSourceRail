//! Basic Raft functionality: election, single-entry commit, quorum
//! loss semantics. All tests operate on the deterministic
//! [`Cluster`] harness; no wall-clock dependence.

use osr_consensus::invariants::check_all;
use osr_consensus::{Category, Cluster, LogIndex, NodeId};

#[test]
fn three_node_cluster_elects_a_leader() {
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200);
    assert!(leader.is_some(), "no leader elected");
    check_all(&c).unwrap();
}

#[test]
fn single_advisory_entry_commits() {
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
    c.propose(leader, b"hello".to_vec(), Category::Advisory);
    let ok = c.run_until_committed(30_000_000, LogIndex::new(1), 200);
    assert!(ok, "no quorum commit within budget");
    check_all(&c).unwrap();
    for (_id, committed) in &c.committed {
        assert!(committed.iter().any(|(i, e)| i.0 == 1 && e.value == b"hello"));
    }
}

#[test]
fn safety_entry_commits_when_quorum_fresh() {
    // New leader starts with a fresh quorum confirmation (by construction
    // in become_leader), so the first Safety proposal should go through.
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
    // Force a heartbeat round so lastQuorumConfirmed is updated via real
    // AE responses too.
    c.tick(50_000_000);
    c.tick(50_000_000);
    c.propose(leader, b"safe".to_vec(), Category::Safety);
    let ok = c.run_until_committed(30_000_000, LogIndex::new(1), 200);
    assert!(ok, "Safety commit failed");
    check_all(&c).unwrap();
}

#[test]
fn quorum_loss_prevents_new_commits() {
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
    // Partition both followers.
    for id in c.node_ids() {
        if id != leader {
            c.policy.partitioned.insert(id);
        }
    }
    // Propose an Advisory entry. It should append locally but NOT commit.
    c.propose(leader, b"orphan".to_vec(), Category::Advisory);
    c.tick(100_000_000);
    c.tick(100_000_000);
    let ln = c.nodes.get(&leader).unwrap();
    assert_eq!(ln.log.len(), 1);
    assert_eq!(ln.commit_index, LogIndex::zero(), "should not commit without quorum");
    check_all(&c).unwrap();
}

#[test]
fn safety_entry_rejected_when_quorum_confirmation_stale() {
    // Elect a leader, then partition it so its quorum confirmation
    // expires. Propose a Safety entry — should be rejected by
    // fail-restrictive gate.
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
    // Partition everyone except the leader to kill quorum confirmation.
    for id in c.node_ids() {
        if id != leader {
            c.policy.partitioned.insert(id);
        }
    }
    // Advance well past the fail-restrictive window (500 ms default).
    for _ in 0..40 {
        c.tick(50_000_000);
    }
    let ln = c.nodes.get(&leader).unwrap();
    assert_ne!(
        ln.last_quorum_confirmed_term, ln.current_term,
        "quorum confirmation should have expired"
    );
    // Propose a Safety entry — the propose path rejects it.
    c.propose(leader, b"late".to_vec(), Category::Safety);
    let ln = c.nodes.get(&leader).unwrap();
    assert_eq!(ln.log.len(), 0, "Safety entry should have been rejected");
    check_all(&c).unwrap();
}

#[test]
fn healing_partition_converges_committed_prefix() {
    // Elect leader, commit 2 entries, partition a node, commit 2 more,
    // heal partition, verify the partitioned node catches up.
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
    c.propose(leader, b"a".to_vec(), Category::Advisory);
    c.propose(leader, b"b".to_vec(), Category::Advisory);
    assert!(c.run_until_committed(30_000_000, LogIndex::new(2), 200));

    // Pick a non-leader and partition it.
    let victim = c.node_ids().into_iter().find(|id| *id != leader).unwrap();
    c.policy.partitioned.insert(victim);

    c.propose(leader, b"c".to_vec(), Category::Advisory);
    c.propose(leader, b"d".to_vec(), Category::Advisory);
    // Quorum still holds with leader + one healthy follower.
    assert!(c.run_until_committed(30_000_000, LogIndex::new(4), 200));

    // Heal.
    c.policy.partitioned.remove(&victim);
    for _ in 0..20 {
        c.tick(50_000_000);
    }
    let victim_node = &c.nodes[&victim];
    assert_eq!(
        victim_node.commit_index,
        LogIndex::new(4),
        "victim did not catch up after healing"
    );
    check_all(&c).unwrap();
}

#[test]
fn leader_death_triggers_new_election() {
    let mut c = Cluster::new(5, 100_000_000);
    let leader1 = c.run_until_leader(30_000_000, 200).expect("no leader");
    let leader1_term = c.nodes[&leader1].current_term;
    c.propose(leader1, b"before".to_vec(), Category::Advisory);
    assert!(c.run_until_committed(30_000_000, LogIndex::new(1), 200));

    // Kill the leader.
    c.policy.partitioned.insert(leader1);

    // Wait for a *different* node to become leader at a higher term.
    // `cluster.leader()` alone would still report the partitioned leader
    // (it hasn't learned that its peers moved on).
    let mut new_leader = None;
    for _ in 0..400 {
        c.tick(30_000_000);
        if let Some(l) = c.leader() {
            if l != leader1 && c.nodes[&l].current_term > leader1_term {
                new_leader = Some(l);
                break;
            }
        }
    }
    let new_leader = new_leader.expect("no new leader after partition");
    assert_ne!(new_leader, leader1);
    // LeaderCompleteness: the new leader has the previously-committed entry.
    let n = &c.nodes[&new_leader];
    assert!(n.log.iter().any(|e| e.value == b"before"));
    check_all(&c).unwrap();
}

#[test]
fn committed_prefix_accessor_matches_commit_index() {
    let mut c = Cluster::new(3, 100_000_000);
    let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
    c.propose(leader, b"one".to_vec(), Category::Advisory);
    c.propose(leader, b"two".to_vec(), Category::Advisory);
    c.run_until_committed(30_000_000, LogIndex::new(2), 200);
    let prefix = c.nodes[&leader].committed_prefix();
    assert_eq!(prefix.len(), 2);
    assert_eq!(prefix[0].value, b"one");
    assert_eq!(prefix[1].value, b"two");
}

// Suppress unused-warning on types that are only referenced through
// other modules' docs in this file.
#[allow(dead_code)]
fn _types_used(_: NodeId) {}
