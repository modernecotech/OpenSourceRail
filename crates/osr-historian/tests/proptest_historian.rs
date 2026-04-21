//! Property tests for osr-historian.

use osr_historian::{Historian, HistorianParams, Sample};
use proptest::prelude::*;

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn h1_raw_retains_recent(
        raw_cap in 1usize..=100,
        dec_cap in 1usize..=200,
        samples in prop::collection::vec(0u64..1_000_000, 0..200),
    ) {
        let params = HistorianParams {
            raw_capacity: raw_cap,
            decimated_capacity: dec_cap,
            decimate_every: 1_000_000, // never decimate
        };
        let mut h = Historian::new(params);
        for (i, ts) in samples.iter().enumerate() {
            h.ingest("x", Sample { timestamp_ns: *ts, value: i as f64 });
        }
        prop_assert!(h.raw_len("x") <= raw_cap);
        prop_assert_eq!(h.raw_len("x"), samples.len().min(raw_cap));
    }

    #[test]
    fn h2_decimation_ratio(
        every in 2u32..20,
        n in 0usize..200,
    ) {
        let params = HistorianParams {
            raw_capacity: 1000,
            decimated_capacity: 1000,
            decimate_every: every,
        };
        let mut h = Historian::new(params);
        for i in 0..n {
            h.ingest("x", Sample { timestamp_ns: i as u64, value: 0.0 });
        }
        // Should have ceil(n / every) samples in decimated tier.
        let expected = (n as u32).div_ceil(every) as usize;
        prop_assert_eq!(h.decimated_len("x"), expected);
    }

    #[test]
    fn h3_query_range(
        samples in prop::collection::vec(0u64..10_000, 0..100),
        t1 in 0u64..10_000,
        t2 in 0u64..10_000,
    ) {
        let (t1, t2) = if t1 <= t2 { (t1, t2) } else { (t2, t1) };
        let mut h = Historian::new(HistorianParams::default_metro());
        for ts in &samples {
            h.ingest("x", Sample { timestamp_ns: *ts, value: 0.0 });
        }
        for s in h.query("x", t1, t2) {
            prop_assert!(s.timestamp_ns >= t1 && s.timestamp_ns <= t2);
        }
    }

    #[test]
    fn h4_query_sorted(
        samples in prop::collection::vec(0u64..10_000, 0..100),
    ) {
        let mut h = Historian::new(HistorianParams::default_metro());
        for ts in &samples {
            h.ingest("x", Sample { timestamp_ns: *ts, value: 0.0 });
        }
        let q = h.query("x", 0, u64::MAX);
        for w in q.windows(2) {
            prop_assert!(w[0].timestamp_ns <= w[1].timestamp_ns);
        }
    }
}
