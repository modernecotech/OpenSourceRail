//! Property tests for osr-event-recorder.

use osr_event_recorder::{EventCategory, EventRecord, EventRecorder};
use proptest::prelude::*;

fn arb_record() -> impl Strategy<Value = EventRecord> {
    (any::<u64>(), any::<u16>(), any::<i64>(), any::<i64>()).prop_map(|(ts, code, a, b)| {
        EventRecord::new(ts, EventCategory::Diagnostic, code).with_values(a, b)
    })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn er1_capacity_bounded(cap in 1usize..=256, records in prop::collection::vec(arb_record(), 0..1_000)) {
        let mut r = EventRecorder::new(cap);
        for rec in &records {
            r.record(*rec);
            prop_assert!(r.len() <= r.capacity());
        }
    }

    #[test]
    fn er2_fifo_order(cap in 2usize..=64, records in prop::collection::vec(arb_record(), 1..200)) {
        let mut r = EventRecorder::new(cap);
        for rec in &records {
            r.record(*rec);
        }
        // The iterator yields the most recent `min(n, cap)` records,
        // in the order they were written.
        let expected_tail = &records[records.len().saturating_sub(cap)..];
        let got: Vec<EventRecord> = r.iter().copied().collect();
        prop_assert_eq!(got.as_slice(), expected_tail);
    }

    #[test]
    fn er3_dropped_accounting(cap in 1usize..=64, n in 0usize..500) {
        let mut r = EventRecorder::new(cap);
        for i in 0..n {
            r.record(EventRecord::new(i as u64, EventCategory::Diagnostic, 0));
        }
        prop_assert_eq!(r.total_written(), n as u64);
        prop_assert_eq!(r.dropped(), (n as u64).saturating_sub(cap as u64));
        prop_assert_eq!(r.len(), n.min(cap));
    }

    #[test]
    fn er4_most_recent_retained(
        cap in 4usize..=64,
        records in prop::collection::vec(arb_record(), 1..200),
    ) {
        let mut r = EventRecorder::new(cap);
        for rec in &records {
            r.record(*rec);
        }
        // The last `min(records.len(), cap)` records should all appear.
        let k = records.len().min(cap);
        let last_k: Vec<_> = records.iter().rev().take(k).copied().collect();
        let mut iter_reversed: Vec<_> = r.iter().rev().copied().collect();
        iter_reversed.truncate(k);
        prop_assert_eq!(iter_reversed, last_k);
    }

    #[test]
    fn er5_snapshot_roundtrip(cap in 1usize..=64, records in prop::collection::vec(arb_record(), 0..200)) {
        let mut r = EventRecorder::new(cap);
        for rec in &records {
            r.record(*rec);
        }
        let snap = r.snapshot();
        let r2 = EventRecorder::restore(snap);
        prop_assert_eq!(r, r2);
    }

    #[test]
    fn clear_is_idempotent(cap in 1usize..=64, records in prop::collection::vec(arb_record(), 0..100)) {
        let mut r = EventRecorder::new(cap);
        for rec in &records {
            r.record(*rec);
        }
        r.clear();
        let a = r.clone();
        r.clear();
        prop_assert_eq!(r.clone(), a);
        prop_assert_eq!(r.len(), 0);
        prop_assert_eq!(r.total_written(), 0);
    }
}
