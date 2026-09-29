use osr_consensus::durable::{RestoreError, StableStore, StoreError, WriteFault};
use osr_consensus::fault_harness::{FaultAction, FaultHarness};
use osr_consensus::{Category, Cluster, NodeId};

fn tick() -> FaultAction {
    FaultAction::Tick {
        duration_ns: 100_000_000,
    }
}

#[test]
fn atomic_store_preserves_last_good_state_on_disk_faults() {
    let mut cluster = Cluster::new(3, 100_000_000);
    let leader = cluster.run_until_leader(30_000_000, 200).expect("leader");
    let mut store = StableStore::from_node(&cluster.nodes[&leader]);
    let original = store.bytes().expect("snapshot").to_vec();
    cluster.propose(leader, b"later".to_vec(), Category::Advisory);
    assert_eq!(
        store.save(&cluster.nodes[&leader], WriteFault::DiskFull),
        Err(StoreError::DiskFull)
    );
    assert_eq!(store.bytes(), Some(original.as_slice()));
    assert_eq!(
        store.save(&cluster.nodes[&leader], WriteFault::PartialWrite(13)),
        Err(StoreError::PartialWrite)
    );
    assert_eq!(store.bytes(), Some(original.as_slice()));
}

#[test]
fn corrupted_or_wrong_node_state_never_restarts() {
    let cluster = Cluster::new(3, 100_000_000);
    let node = NodeId::new(0);
    let mut store = StableStore::from_node(&cluster.nodes[&node]);
    let wrong_config = cluster.nodes[&NodeId::new(1)].config.clone();
    assert!(matches!(
        store.restore(wrong_config, 0),
        Err(RestoreError::WrongNode { .. })
    ));
    assert!(store.corrupt_byte(20));
    assert!(matches!(
        store.restore(cluster.nodes[&node].config.clone(), 0),
        Err(RestoreError::ChecksumMismatch)
    ));
}

#[test]
fn restart_partition_clock_storage_and_telemetry_trace_is_deterministic() {
    let node0 = NodeId::new(0);
    let node1 = NodeId::new(1);
    let node2 = NodeId::new(2);
    let actions = vec![
        tick(),
        tick(),
        FaultAction::Propose {
            value: b"baseline".to_vec(),
            category: Category::Advisory,
        },
        FaultAction::Checkpoint { node: node2 },
        FaultAction::Delay {
            node: node2,
            ticks: 3,
        },
        FaultAction::DropFrom {
            node: node1,
            enabled: true,
        },
        tick(),
        FaultAction::Heal { node: node1 },
        tick(),
        tick(),
        FaultAction::DiskFull { node: node0 },
        FaultAction::PartialWrite {
            node: node1,
            bytes: 7,
        },
        FaultAction::Checkpoint { node: node2 },
        FaultAction::Crash { node: node2 },
        tick(),
        FaultAction::Restart { node: node2 },
        FaultAction::Telemetry { available: false },
        FaultAction::Propose {
            value: b"must-not-enter".to_vec(),
            category: Category::Safety,
        },
        FaultAction::Telemetry { available: true },
        FaultAction::ClockOffset {
            offset_ns: 8_000_000_000,
        },
        FaultAction::Propose {
            value: b"also-rejected".to_vec(),
            category: Category::Safety,
        },
        FaultAction::ClockOffset { offset_ns: 0 },
        FaultAction::TimeSource { available: false },
        FaultAction::Propose {
            value: b"time-rejected".to_vec(),
            category: Category::Safety,
        },
        FaultAction::TimeSource { available: true },
        tick(),
        tick(),
    ];

    let mut first = FaultHarness::new(3, 100_000_000);
    let mut second = FaultHarness::new(3, 100_000_000);
    let first_report = first.run(0x5eed, &actions);
    let second_report = second.run(0x5eed, &actions);
    assert_eq!(first_report, second_report);
    assert!(first_report.passed, "{:?}", first_report.invariant_failures);
    assert!(
        first_report
            .trace
            .iter()
            .filter(|row| row.outcome == "rejected-fail-restrictive")
            .count()
            >= 3
    );
    assert!(first_report.alarms.contains("node-0-disk-full"));
    assert!(first_report.alarms.contains("node-1-partial-write"));
}

#[test]
fn corrupt_restart_fails_closed_and_leaves_node_offline() {
    let node = NodeId::new(2);
    let actions = [
        FaultAction::CorruptStableByte { node, offset: 20 },
        FaultAction::Crash { node },
        FaultAction::Restart { node },
        tick(),
    ];
    let mut harness = FaultHarness::new(3, 100_000_000);
    let report = harness.run(7, &actions);
    assert!(report.passed);
    assert!(!harness.cluster.nodes.contains_key(&node));
    assert!(report
        .alarms
        .iter()
        .any(|alarm| alarm.contains("restore-rejected-ChecksumMismatch")));
}
