//! Property-based tests for `osr-brake`.
//!
//! Exercises the crate-level safety properties B1–B5 over random
//! inputs. Candidates for future Kani harnesses once the SIL-4
//! partition migrates to bounded formal verification.

use osr_atp::BrakeCommand;
use osr_brake::{brake_evaluate, BrakeInputs, BrakeParams};
use proptest::prelude::*;

fn arb_cmd() -> impl Strategy<Value = BrakeCommand> {
    prop_oneof![
        Just(BrakeCommand::Release),
        (0u16..=1000).prop_map(BrakeCommand::Service),
        Just(BrakeCommand::Emergency),
    ]
}

fn arb_inputs() -> impl Strategy<Value = BrakeInputs> {
    (
        arb_cmd(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        -30_000i32..30_000,
        -30_000i32..30_000,
        0u16..=1000,
    )
        .prop_map(
            |(cmd, vig, fire, derail, driver, park, meas, wheel, regen)| BrakeInputs {
                atp_command: cmd,
                vigilance_emergency: vig,
                fire_emergency: fire,
                derailment_emergency: derail,
                driver_emergency: driver,
                park_requested: park,
                measured_speed_mmps: meas,
                wheel_speed_mmps: wheel,
                regen_available_ppt: regen,
                now_ns: 1_000_000_000,
            },
        )
}

// ---------------------------------------------------------------------------
// B1: determinism. Identical inputs produce identical outputs.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn b1_determinism(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let a = brake_evaluate(&i, &p);
        let b = brake_evaluate(&i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// B2: emergency union. Any emergency source → Emergency output,
// with that source recorded.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn b2_emergency_union(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        let any_in = i.any_emergency();
        prop_assert_eq!(out.is_emergency(), any_in);
        prop_assert_eq!(out.emergency_sources.any(), any_in);

        // Each individual source flag is faithfully propagated.
        prop_assert_eq!(
            out.emergency_sources.atp,
            matches!(i.atp_command, BrakeCommand::Emergency)
        );
        prop_assert_eq!(out.emergency_sources.vigilance, i.vigilance_emergency);
        prop_assert_eq!(out.emergency_sources.fire, i.fire_emergency);
        prop_assert_eq!(out.emergency_sources.derailment, i.derailment_emergency);
        prop_assert_eq!(out.emergency_sources.driver, i.driver_emergency);
    }
}

// ---------------------------------------------------------------------------
// B3: emergency completeness. In any emergency, friction is at least
// the emergency floor minus at most the WSP reduction, and traction
// is cut.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn b3_emergency_completeness(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        if out.is_emergency() {
            let floor = p.min_friction_emergency_ppt.saturating_sub(p.wsp_reduction_ppt);
            prop_assert!(
                out.friction_effort_ppt >= floor,
                "emergency friction {} below floor {}",
                out.friction_effort_ppt, floor
            );
            prop_assert!(out.traction_cut);
            prop_assert_eq!(out.friction_command_before_wsp_ppt, p.min_friction_emergency_ppt);
        }
    }
}

// ---------------------------------------------------------------------------
// B4: WSP is conservative — friction_effort never exceeds the
// commanded-before-WSP value.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn b4_wsp_conservative(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        prop_assert!(
            out.friction_effort_ppt <= out.friction_command_before_wsp_ppt,
            "WSP increased friction: before={} after={}",
            out.friction_command_before_wsp_ppt, out.friction_effort_ppt
        );
    }
}

// ---------------------------------------------------------------------------
// B5: park-brake safety. Engaged iff requested AND below threshold.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn b5_park_brake_safe(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        let expected = i.park_requested
            && i.measured_speed_mmps.unsigned_abs()
                <= p.park_brake_max_speed_mmps.unsigned_abs();
        prop_assert_eq!(out.parking_brake_engaged, expected);
    }
}

// ---------------------------------------------------------------------------
// Service-blend regen-shortfall invariant: regen + friction equals
// the service demand (within ppt rounding) whenever no emergency and
// WSP does not fire.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn service_blend_sums_to_demand(
        service_ppt in 0u16..=1000,
        regen_avail in 0u16..=1000,
    ) {
        let i = BrakeInputs {
            atp_command: BrakeCommand::Service(service_ppt),
            vigilance_emergency: false,
            fire_emergency: false,
            derailment_emergency: false,
            driver_emergency: false,
            park_requested: false,
            measured_speed_mmps: 10_000,
            wheel_speed_mmps: 10_000,  // no slide
            regen_available_ppt: regen_avail,
            now_ns: 0,
        };
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        prop_assert!(!out.wsp_active);
        prop_assert_eq!(
            u32::from(out.regen_request_ppt) + u32::from(out.friction_effort_ppt),
            u32::from(service_ppt),
            "regen+friction does not sum to service: {:?}", out
        );
    }
}

// ---------------------------------------------------------------------------
// Traction cut is set whenever the command is not Release (or WSP
// active, or park engaged).
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn traction_cut_whenever_not_release(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        let is_release_no_park = matches!(out.command, BrakeCommand::Release)
            && !out.wsp_active
            && !out.parking_brake_engaged;
        if !is_release_no_park {
            prop_assert!(out.traction_cut);
        }
    }
}

// ---------------------------------------------------------------------------
// Regen is clamped to available.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn regen_clamped_to_available(i in arb_inputs()) {
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        prop_assert!(out.regen_request_ppt <= i.regen_available_ppt.min(1000));
    }
}
