//! Property-based tests of the five TLA+ safety invariants.
//!
//! Drives a randomised 3-node or 5-node cluster through arbitrary
//! proposals, partitions, and heals, and after every random step
//! checks [`osr_consensus::invariants::check_all`]. Any failure
//! prints the offending trace.

use osr_consensus::invariants::{
    check_all, election_safety, fail_restrictive, leader_completeness, log_matching,
    state_machine_safety,
};
use osr_consensus::{Category, Cluster, LogIndex, NodeId};
use proptest::prelude::*;

#[derive(Clone, Debug)]
enum Action {
    Tick(u8),            // u8 * 10 ms, so up to 2550 ms
    Propose(u8, u8),     // value byte + category bit (0 = Advisory, 1 = Safety)
    Partition(u8),       // mod n picks a node
    Heal(u8),
}

fn arb_action() -> impl Strategy<Value = Action> {
    prop_oneof![
        (1u8..30u8).prop_map(Action::Tick),
        (any::<u8>(), any::<u8>()).prop_map(|(v, c)| Action::Propose(v, c)),
        any::<u8>().prop_map(Action::Partition),
        any::<u8>().prop_map(Action::Heal),
    ]
}

fn run_scenario(n: u16, ops: &[Action]) -> (Cluster, Vec<(usize, String)>) {
    let mut c = Cluster::new(n, 100_000_000);
    // Seed an initial leader before the randomised ops; without a
    // leader every Propose is a rejected no-op, which weakens the
    // test coverage.
    c.run_until_leader(30_000_000, 200);
    let mut failures = Vec::new();

    for (i, op) in ops.iter().enumerate() {
        match op {
            Action::Tick(ms) => {
                c.tick((*ms as u64) * 10_000_000);
            }
            Action::Propose(v, c_bit) => {
                if let Some(leader) = c.leader() {
                    let cat = if c_bit & 1 == 0 {
                        Category::Advisory
                    } else {
                        Category::Safety
                    };
                    c.propose(leader, vec![*v], cat);
                }
            }
            Action::Partition(k) => {
                let ids = c.node_ids();
                let id = ids[(*k as usize) % ids.len()];
                c.policy.partitioned.insert(id);
            }
            Action::Heal(k) => {
                let ids = c.node_ids();
                let id = ids[(*k as usize) % ids.len()];
                c.policy.partitioned.remove(&id);
            }
        }
        if let Err(e) = check_all(&c) {
            failures.push((i, e));
        }
    }
    (c, failures)
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, max_shrink_iters: 256, .. ProptestConfig::default() })]

    #[test]
    fn safety_invariants_3node(ops in prop::collection::vec(arb_action(), 1..60)) {
        let (_c, failures) = run_scenario(3, &ops);
        prop_assert!(failures.is_empty(), "invariant failures: {:?}", failures);
    }

    #[test]
    fn safety_invariants_5node(ops in prop::collection::vec(arb_action(), 1..80)) {
        let (_c, failures) = run_scenario(5, &ops);
        prop_assert!(failures.is_empty(), "invariant failures: {:?}", failures);
    }
}

// Focused property: with only Advisory proposals, committed entries at
// common indices across all nodes must be byte-identical (StateMachineSafety).
proptest! {
    #![proptest_config(ProptestConfig { cases: 64, .. ProptestConfig::default() })]

    #[test]
    fn advisory_only_preserves_state_machine_safety(
        mut ops in prop::collection::vec(arb_action(), 1..80),
    ) {
        // Zero out the Safety bit on every Propose.
        for op in &mut ops {
            if let Action::Propose(_, c) = op {
                *c &= 0xFE; // low bit → Advisory
            }
        }
        let (c, _) = run_scenario(3, &ops);
        prop_assert!(state_machine_safety(&c).is_ok(), "SMS failed in advisory-only run");
    }
}

// Focused property: a single proposal against an isolated leader
// never commits. Serves as a regression for quorum_loss_prevents.
proptest! {
    #![proptest_config(ProptestConfig { cases: 32, .. ProptestConfig::default() })]

    #[test]
    fn isolated_leader_never_commits(
        which_value in any::<u8>(),
    ) {
        let mut c = Cluster::new(3, 100_000_000);
        let leader = c.run_until_leader(30_000_000, 200).expect("no leader");
        // Partition followers.
        for id in c.node_ids() {
            if id != leader {
                c.policy.partitioned.insert(id);
            }
        }
        c.propose(leader, vec![which_value], Category::Advisory);
        for _ in 0..20 { c.tick(100_000_000); }
        prop_assert_eq!(c.nodes[&leader].commit_index, LogIndex::zero());
        prop_assert!(check_all(&c).is_ok());
    }
}

// Individual invariants as their own smoke tests at fixed cases, just
// in case a future regression breaks only one of them.
#[test]
fn individual_invariants_compile_and_smoke() {
    let mut c = Cluster::new(3, 100_000_000);
    c.run_until_leader(30_000_000, 200);
    assert!(election_safety(&c).is_ok());
    assert!(log_matching(&c).is_ok());
    assert!(state_machine_safety(&c).is_ok());
    assert!(leader_completeness(&c).is_ok());
    assert!(fail_restrictive(&c).is_ok());
    // Suppress unused-import warning.
    let _ = NodeId::new(0);
}
