//! Property-based tests for AO1–AO8.

use osr_ato::{ato_evaluate, AtoInputs, AtoMode, AtoParams, AtoState};
use proptest::prelude::*;

fn params() -> AtoParams {
    AtoParams::light_metro_default()
}

fn arb_inputs() -> impl Strategy<Value = AtoInputs> {
    (
        0u64..60_000_000_000,
        10_000_000u64..1_000_000_000,
        0i32..40_000,
        0i32..40_000,
        0i32..40_000,
        prop_oneof![Just(None), (0i64..3_000_000).prop_map(Some),],
        any::<bool>(),
        0u32..60_000,
        any::<bool>(),
    )
        .prop_map(
            |(now, dt, cur, env, cruise, dist, at_s, dwell, eng)| AtoInputs {
                now_ns: now,
                dt_ns: dt,
                current_speed_mmps: cur,
                envelope_mmps: env,
                cruise_target_mmps: cruise,
                distance_to_stop_mm: dist,
                at_station: at_s,
                dwell_remaining_ms: dwell,
                ato_engaged: eng,
            },
        )
}

// ---------------------------------------------------------------------------
// AO1: determinism.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ao1_determinism(i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        let a = ato_evaluate(&prev, &i, &p);
        let b = ato_evaluate(&prev, &i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// AO2: mutual exclusion. Never command +torque and +brake on the
// same tick.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn ao2_torque_and_brake_mutually_exclusive(i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        let out = ato_evaluate(&prev, &i, &p);
        prop_assert!(
            !(out.torque_setpoint_mnm > 0 && out.service_brake_ppt > 0),
            "both non-zero: {out:?}"
        );
    }
}

// ---------------------------------------------------------------------------
// AO3: effective target never exceeds envelope - margin
// (with 0 floor).
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ao3_effective_target_below_envelope(i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        let out = ato_evaluate(&prev, &i, &p);
        let cap = i.envelope_mmps.saturating_sub(p.envelope_margin_mmps).max(0);
        // Skip the stopped / dwelling / off modes where target has
        // no meaningful relationship to the envelope.
        if !matches!(out.mode, AtoMode::Stopped | AtoMode::Dwelling | AtoMode::Off) {
            prop_assert!(
                out.effective_target_mmps <= cap,
                "target {} > envelope cap {} (mode {:?})",
                out.effective_target_mmps, cap, out.mode
            );
        }
    }
}

// ---------------------------------------------------------------------------
// AO4: disengaged → zero everything.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ao4_disengaged_zero_output(mut i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        i.ato_engaged = false;
        let out = ato_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.torque_setpoint_mnm, 0);
        prop_assert_eq!(out.service_brake_ppt, 0);
        prop_assert_eq!(out.mode, AtoMode::Off);
    }
}

// ---------------------------------------------------------------------------
// AO5: at station with near-zero speed → holding brake held,
// torque zero.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn ao5_stopped_holding_brake(
        mut i in arb_inputs(),
        speed in -100i32..=100,
    ) {
        let p = params();
        let prev = AtoState::default();
        i.at_station = true;
        i.ato_engaged = true;
        i.current_speed_mmps = speed;
        let out = ato_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.torque_setpoint_mnm, 0);
        prop_assert!(out.service_brake_ppt >= p.holding_brake_ppt);
    }
}

// ---------------------------------------------------------------------------
// AO6: torque bounded by max_torque_mnm.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ao6_torque_bounded(i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        let out = ato_evaluate(&prev, &i, &p);
        prop_assert!(out.torque_setpoint_mnm <= p.max_torque_mnm);
        prop_assert!(out.torque_setpoint_mnm >= -p.max_torque_mnm);
    }
}

// ---------------------------------------------------------------------------
// AO7: brake bounded.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ao7_brake_bounded(i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        let out = ato_evaluate(&prev, &i, &p);
        prop_assert!(out.service_brake_ppt <= p.max_service_brake_ppt);
    }
}

// ---------------------------------------------------------------------------
// AO8: overspeed → no positive torque.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ao8_overspeed_no_positive_torque(i in arb_inputs()) {
        let p = params();
        let prev = AtoState::default();
        let out = ato_evaluate(&prev, &i, &p);
        if i.current_speed_mmps > i.envelope_mmps {
            prop_assert!(
                out.torque_setpoint_mnm <= 0,
                "positive torque at overspeed: {out:?} inputs {i:?}"
            );
        }
    }
}
