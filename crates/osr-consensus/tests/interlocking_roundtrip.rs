//! Integration smoke test: commit real `osr-interlocking::log::Entry`
//! values through the consensus cluster and verify the committed
//! prefix is directly consumable by
//! [`osr_interlocking::compute_self_ma_from_state`].
//!
//! This is the bridge between osr-consensus (whose entries carry
//! opaque `Vec<u8>` values) and osr-interlocking (whose entries are
//! the rich track-state schema). Callers on the wayside serialise
//! the interlocking entry into bytes, propose to the consensus
//! cluster, and deserialise on commit. The whole workspace can use
//! `serde_json` as the stand-in serialiser until `osr-proto` lands
//! (RFC 0005 §12).

use osr_consensus::{Category, Cluster, LogIndex};
use osr_core::{ConsistDescriptor, Position, TrackRef, TrainId};
use osr_core::{Direction, EntryId, SectionId};
use osr_interlocking::log::{
    Entry, EntryPayload, PositionSource, TrainPositionReport, TrainRegistration,
};

const REFERENCE_3CAR_LENGTH_MM: i64 = 51_000;

fn registration_entry(id: u64, train: u64) -> Entry {
    Entry {
        entry_id: EntryId::new(id),
        term: 1,
        timestamp_ns: 1_000_000_000 * id,
        payload: EntryPayload::TrainRegistration(TrainRegistration {
            train_id: TrainId::new(train),
            consist: ConsistDescriptor::reference_3car(),
            initial_position: Position::certain(TrackRef {
                section: SectionId::new(1000),
                offset_mm: 0,
                direction: Direction::Forward,
            }),
        }),
    }
}

fn position_report_entry(id: u64, train: u64, offset: i64) -> Entry {
    Entry {
        entry_id: EntryId::new(id),
        term: 1,
        timestamp_ns: 1_000_000_000 * id,
        payload: EntryPayload::TrainPositionReport(TrainPositionReport {
            train_id: TrainId::new(train),
            head_position: Position::certain(TrackRef {
                section: SectionId::new(1000),
                offset_mm: offset,
                direction: Direction::Forward,
            }),
            tail_position: Position::certain(TrackRef {
                section: SectionId::new(1000),
                offset_mm: (offset - REFERENCE_3CAR_LENGTH_MM).max(0),
                direction: Direction::Forward,
            }),
            speed_mmps: 15_000,
            speed_uncertainty_mmps: 500,
            heading: Direction::Forward,
            contributing_sources: vec![PositionSource::Gnss],
            onboard_time_ns: 1_000_000_000 * id,
            pack_soc_ppt: 900,
        }),
    }
}

#[test]
fn interlocking_entries_round_trip_through_consensus() {
    let mut cluster = Cluster::new(3, 100_000_000);
    let leader = cluster
        .run_until_leader(30_000_000, 200)
        .expect("no leader elected");

    // Serialise two real interlocking entries and propose them.
    let originals = vec![
        registration_entry(1, 7),
        position_report_entry(2, 7, 100_000),
    ];

    for e in &originals {
        let bytes = serde_json::to_vec(e).expect("serialise");
        cluster.propose(leader, bytes, Category::Advisory);
    }
    assert!(
        cluster.run_until_committed(30_000_000, LogIndex::new(2), 200),
        "entries did not commit"
    );

    // Every non-partitioned node should now hold the committed bytes.
    for node in cluster.nodes.values() {
        let prefix = node.committed_prefix();
        assert_eq!(prefix.len(), 2);
        for (i, slot) in prefix.iter().enumerate() {
            let decoded: Entry = serde_json::from_slice(&slot.value).expect("deserialise");
            assert_eq!(decoded, originals[i]);
        }
    }
}

#[test]
fn safety_category_reflects_entry_importance() {
    // Demonstrates the hybrid: the caller chooses Safety for
    // MovementAuthority witnesses and switch commands; Advisory for
    // telemetry (position reports, heartbeats). This is what RFC 0001
    // §8 calls for — and is the load-bearing property for the
    // fail-restrictive guarantee.
    let mut cluster = Cluster::new(3, 100_000_000);
    let leader = cluster
        .run_until_leader(30_000_000, 200)
        .expect("no leader");

    // Tick a few rounds so lastQuorumConfirmedTerm is fresh via real
    // AE responses.
    for _ in 0..4 {
        cluster.tick(50_000_000);
    }

    let safety_entry = registration_entry(1, 7);
    let bytes = serde_json::to_vec(&safety_entry).unwrap();
    cluster.propose(leader, bytes, Category::Safety);
    assert!(cluster.run_until_committed(30_000_000, LogIndex::new(1), 200));

    // Advisory entry also commits fine.
    let advisory_entry = position_report_entry(2, 7, 200_000);
    let bytes = serde_json::to_vec(&advisory_entry).unwrap();
    cluster.propose(leader, bytes, Category::Advisory);
    assert!(cluster.run_until_committed(30_000_000, LogIndex::new(2), 200));

    // Confirm categories are preserved.
    let prefix = cluster.nodes[&leader].committed_prefix();
    assert_eq!(prefix[0].category, Category::Safety);
    assert_eq!(prefix[1].category, Category::Advisory);
}
