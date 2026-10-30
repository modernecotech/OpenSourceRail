//! Property tests LC1–LC4.

use osr_level_crossing::{
    lc_evaluate, BarrierSensors, LcInputs, LcParams, LcState, LcStatePersistent,
};
use proptest::prelude::*;

fn arb_barriers() -> impl Strategy<Value = BarrierSensors> {
    (any::<bool>(), any::<bool>(), any::<bool>()).prop_map(|(u, d, f)| BarrierSensors {
        fully_up: u,
        fully_down: d,
        motor_fault: f,
    })
}

fn arb_inputs() -> impl Strategy<Value = LcInputs> {
    (
        0u64..300_000_000_000,
        any::<bool>(),
        any::<bool>(),
        arb_barriers(),
        arb_barriers(),
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(|(now, tapp, tclr, ba, bb, mel, mr)| LcInputs {
            now_ns: now,
            train_approaching: tapp,
            train_cleared: tclr,
            barrier_a: ba,
            barrier_b: bb,
            manual_emergency_lower: mel,
            manual_reset: mr,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn lc1_determinism(i in arb_inputs()) {
        let p = LcParams::default_metro();
        let a = lc_evaluate(&LcStatePersistent::default(), &i, &p);
        let b = lc_evaluate(&LcStatePersistent::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn lc2_safe_iff_closed_and_barriers_down(i in arb_inputs()) {
        let p = LcParams::default_metro();
        let out = lc_evaluate(&LcStatePersistent::default(), &i, &p);
        let both_down = i.barrier_a.fully_down && i.barrier_b.fully_down;
        let is_closed = out.state.state == LcState::Closed;
        prop_assert_eq!(out.crossing_safe_for_train, is_closed && both_down);
    }

    #[test]
    fn lc4_faulted_is_unsafe(i in arb_inputs()) {
        let p = LcParams::default_metro();
        let out = lc_evaluate(&LcStatePersistent::default(), &i, &p);
        if out.state.state == LcState::Faulted {
            prop_assert!(!out.crossing_safe_for_train);
        }
    }
}
