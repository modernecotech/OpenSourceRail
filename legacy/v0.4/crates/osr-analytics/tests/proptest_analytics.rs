//! Property tests for osr-analytics.

use osr_analytics::{basic_stats, headway_adherence, mdbf_km};
use osr_historian::Sample;
use proptest::prelude::*;

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn a1_determinism(values in prop::collection::vec(-1000.0f64..1000.0, 0..50)) {
        let samples: Vec<Sample> = values.iter().enumerate().map(|(i, v)| Sample { timestamp_ns: i as u64, value: *v }).collect();
        let a = basic_stats(&samples);
        let b = basic_stats(&samples);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn a2_mean_in_range(values in prop::collection::vec(-1000.0f64..1000.0, 1..50)) {
        let samples: Vec<Sample> = values.iter().enumerate().map(|(i, v)| Sample { timestamp_ns: i as u64, value: *v }).collect();
        let b = basic_stats(&samples);
        let mean = b.mean.unwrap();
        let min = b.min.unwrap();
        let max = b.max.unwrap();
        prop_assert!(mean >= min && mean <= max);
    }

    #[test]
    fn a4_headway_adherence_bounded(
        base_ns in 0u64..10_000_000_000_000,
        deltas_s in prop::collection::vec(1u32..300, 0..10),
        target in 30u32..120,
        tol in 5u32..60,
    ) {
        let mut arrivals = vec![base_ns];
        for d in &deltas_s {
            let next = arrivals.last().unwrap() + u64::from(*d) * 1_000_000_000;
            arrivals.push(next);
        }
        let h = headway_adherence(&arrivals, target, tol);
        prop_assert!(h.adherence >= 0.0 && h.adherence <= 1.0);
    }

    #[test]
    fn mdbf_monotone_in_distance(km in 1.0f64..100_000.0, fails in 1u32..1000) {
        let a = mdbf_km(km, fails).unwrap();
        let b = mdbf_km(km * 2.0, fails).unwrap();
        prop_assert!(b > a);
    }
}

#[test]
fn a3_empty_means_none() {
    let b = basic_stats(&[]);
    assert_eq!(b.count, 0);
    assert_eq!(b.mean, None);
    assert_eq!(b.stddev, None);
}
