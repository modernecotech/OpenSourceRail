//! Deterministic regression guard for the 5-node partition+heal
//! sequence that proptest originally discovered as the
//! `safety_invariants_5node` counterexample (seed `b6fb2d40…`,
//! 2026-04-22). Every op is a direct call on `Cluster` so this test
//! reproduces bit-identically regardless of proptest's internal
//! shrinking behaviour.
//!
//! The bug: `handle_append_entries` returned `match_index =
//! node.log_len()` on a successful AE, which overstates replication
//! for a follower whose pre-existing log (from a prior term) is
//! longer than what the current leader just verified. The fix sets
//! `match_index = prev_log_index + entries.len()` — see
//! `crates/osr-consensus/src/step.rs`. After the fix, this trace
//! converges on a consistent `[term1, term4]` log across every
//! node and `leader_completeness` holds at every step.
//!
//! Run with `cargo test -p osr-consensus --test replay_5node -- --nocapture`
//! to see the per-op state trace.

use osr_consensus::invariants::{check_all, leader_completeness};
use osr_consensus::{Category, Cluster};

/// Exact op sequence from the `b6fb2d40…` regression seed, mapped
/// from the proptest-Action enum to direct `Cluster` calls. The
/// Partition/Heal u8 is `k % n`, so on 5 nodes (`ids = [N0..N4]`):
///   214 % 5 = 4  → N4
///   181 % 5 = 1  → N1
///   4   % 5 = 4  → N4
///   31  % 5 = 1  → N1
fn drive() -> Cluster {
    let mut c = Cluster::new(5, 100_000_000);
    c.run_until_leader(30_000_000, 200);

    let mut step = 0;
    let mut do_step = |c: &mut Cluster, label: &str, f: &mut dyn FnMut(&mut Cluster)| {
        step += 1;
        f(c);
        let res = check_all(c);
        let lc = leader_completeness(c);
        let leader = c
            .leader()
            .map(|id| format!("{id}"))
            .unwrap_or_else(|| "none".into());
        eprintln!(
            "\n[step {step:2}] {label:30}  leader={leader}  check_all={}  lc={}",
            res.as_ref().err().map(String::as_str).unwrap_or("ok"),
            lc.as_ref().err().map(String::as_str).unwrap_or("ok"),
        );
        for (id, n) in &c.nodes {
            let terms: Vec<u64> = n.log.iter().map(|e| e.term.0).collect();
            eprintln!(
                "   {id}: role={:?} term={} voted_for={:?} commit={} log_terms={:?}",
                n.role, n.current_term.0, n.voted_for, n.commit_index.0, terms,
            );
        }
    };

    let ids = c.node_ids();
    let n4 = ids[4];
    let n1 = ids[1];

    do_step(&mut c, "partition N4", &mut |c| {
        c.policy.partitioned.insert(n4);
    });
    do_step(&mut c, "tick 10ms", &mut |c| c.tick(10_000_000));
    do_step(&mut c, "tick 50ms", &mut |c| c.tick(50_000_000));
    do_step(&mut c, "propose (1)", &mut |c| {
        if let Some(l) = c.leader() {
            c.propose(l, vec![0], Category::Advisory);
        }
    });
    do_step(&mut c, "propose (2)", &mut |c| {
        if let Some(l) = c.leader() {
            c.propose(l, vec![0], Category::Advisory);
        }
    });
    do_step(&mut c, "propose (3)", &mut |c| {
        if let Some(l) = c.leader() {
            c.propose(l, vec![0], Category::Advisory);
        }
    });
    do_step(&mut c, "tick 120ms", &mut |c| c.tick(120_000_000));
    do_step(&mut c, "partition N1", &mut |c| {
        c.policy.partitioned.insert(n1);
    });
    do_step(&mut c, "tick 100ms", &mut |c| c.tick(100_000_000));
    do_step(&mut c, "heal N4", &mut |c| {
        c.policy.partitioned.remove(&n4);
    });
    do_step(&mut c, "tick 140ms", &mut |c| c.tick(140_000_000));
    do_step(&mut c, "propose (4)", &mut |c| {
        if let Some(l) = c.leader() {
            c.propose(l, vec![0], Category::Advisory);
        }
    });
    do_step(&mut c, "tick 10ms", &mut |c| c.tick(10_000_000));
    do_step(&mut c, "heal N1", &mut |c| {
        c.policy.partitioned.remove(&n1);
    });
    do_step(&mut c, "tick 100ms", &mut |c| c.tick(100_000_000));
    do_step(&mut c, "tick 10ms", &mut |c| c.tick(10_000_000));

    c
}

#[test]
fn regression_5node_partition_heal_preserves_safety() {
    let c = drive();

    // The authoritative check: every TLA+ safety invariant must hold
    // on the final state.
    check_all(&c).expect("safety invariants must hold post-fix");
    leader_completeness(&c).expect("LeaderCompleteness must hold post-fix");

    // Additional structural check: on a cluster that has fully
    // healed and converged, every non-partitioned node's log must
    // match the leader's log up to its commit_index.
    let leader_id = c.leader().expect("a leader must exist after convergence");
    let leader = &c.nodes[&leader_id];
    for (id, node) in &c.nodes {
        if *id == leader_id {
            continue;
        }
        let ci = node.commit_index.0 as usize;
        for k in 0..ci {
            assert_eq!(
                Some(&node.log[k]),
                leader.log.get(k),
                "{id} commit_index={} diverges from leader {leader_id} at log index {}",
                node.commit_index.0,
                k + 1,
            );
        }
    }
}
