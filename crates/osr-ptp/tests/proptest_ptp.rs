//! Property tests PT1–PT4.

use osr_ptp::{estimate, ptp_update, LockState, PtpParams, PtpSample, PtpState};
use proptest::prelude::*;

/// Build a sample with chosen slave-clock offset and symmetric
/// one-way delay. Master epoch starts at `t1`.
fn symmetric_sample(t1: i64, offset: i64, one_way_delay: i64) -> PtpSample {
    PtpSample {
        t1_master_tx_ns: t1,
        t2_slave_rx_ns: t1 + one_way_delay + offset,
        t3_slave_tx_ns: t1 + one_way_delay + offset + 1_000, // slave sits 1 µs before replying
        t4_master_rx_ns: t1 + 2 * one_way_delay + 1_000,
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn pt1_determinism(t1 in 0i64..1_000_000, off in -10_000i64..10_000, d in 0i64..10_000) {
        let s = symmetric_sample(t1, off, d);
        let p = PtpParams::default_trackside();
        prop_assert_eq!(ptp_update(&PtpState::default(), &s, &p),
                        ptp_update(&PtpState::default(), &s, &p));
    }

    /// PT2: on a symmetric path with offset=0, the estimator returns 0.
    #[test]
    fn pt2_zero_offset_on_symmetric_path(t1 in 0i64..1_000_000, d in 0i64..10_000) {
        let s = symmetric_sample(t1, 0, d);
        let (offset, _) = estimate(&s);
        prop_assert_eq!(offset, 0);
    }

    /// PT3: path delay is always non-negative.
    #[test]
    fn pt3_path_delay_nonneg(t1 in 0i64..1_000_000, off in -10_000i64..10_000, d in 0i64..10_000) {
        let s = symmetric_sample(t1, off, d);
        let (_, delay) = estimate(&s);
        prop_assert!(delay >= 0);
    }

    /// PT4: repeated in-range samples eventually drive to Locked.
    #[test]
    fn pt4_eventually_locks(t1 in 0i64..1_000_000, d in 0i64..1_000) {
        let p = PtpParams { lock_threshold_ns: 500, lock_streak: 3, unlock_streak: 2 };
        let s = symmetric_sample(t1, 0, d);
        let mut st = PtpState::default();
        for _ in 0..p.lock_streak + 1 {
            let out = ptp_update(&st, &s, &p);
            st = out.state;
        }
        prop_assert_eq!(st.lock, LockState::Locked);
    }
}
