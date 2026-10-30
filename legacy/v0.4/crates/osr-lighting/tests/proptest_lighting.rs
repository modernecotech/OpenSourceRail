//! Property tests for osr-lighting.

use osr_lighting::{lighting_evaluate, Heading, LightingInputs, LightingMode, LightingParams};
use proptest::prelude::*;

fn params() -> LightingParams {
    LightingParams::light_metro_default()
}

fn arb_mode() -> impl Strategy<Value = LightingMode> {
    prop_oneof![
        Just(LightingMode::Normal),
        Just(LightingMode::Dimmed),
        Just(LightingMode::Emergency),
        Just(LightingMode::Off),
    ]
}

fn arb_inputs() -> impl Strategy<Value = LightingInputs> {
    (
        0u64..60_000_000_000,
        arb_mode(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        prop_oneof![Just(Heading::Forward), Just(Heading::Reverse)],
        prop_oneof![Just(None), (0u32..100_000).prop_map(Some)],
    )
        .prop_map(|(now, mode, v110, v24, eu, heading, lx)| LightingInputs {
            now_ns: now,
            mode_request: mode,
            v110_rail_enabled: v110,
            v24_rail_enabled: v24,
            emergency_unlock: eu,
            heading,
            ambient_lux: lx,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn determinism(i in arb_inputs()) {
        let p = params();
        let a = lighting_evaluate(&i, &p);
        let b = lighting_evaluate(&i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn emergency_overrides_mode_request(mut i in arb_inputs()) {
        let p = params();
        i.emergency_unlock = true;
        let out = lighting_evaluate(&i, &p);
        prop_assert_eq!(out.mode, LightingMode::Emergency);
        prop_assert_eq!(out.interior_ppt, 0);
    }

    #[test]
    fn v110_down_forces_emergency(mut i in arb_inputs()) {
        let p = params();
        i.v110_rail_enabled = false;
        let out = lighting_evaluate(&i, &p);
        prop_assert_eq!(out.mode, LightingMode::Emergency);
    }

    #[test]
    fn interior_bounded(i in arb_inputs()) {
        let p = params();
        let out = lighting_evaluate(&i, &p);
        prop_assert!(out.interior_ppt <= p.interior_normal_ppt);
    }

    #[test]
    fn off_mode_is_zero(mut i in arb_inputs()) {
        let p = params();
        // Force the "clean Off" path: no emergency, 110 V up.
        i.mode_request = LightingMode::Off;
        i.emergency_unlock = false;
        i.v110_rail_enabled = true;
        let out = lighting_evaluate(&i, &p);
        prop_assert_eq!(out.mode, LightingMode::Off);
        prop_assert_eq!(out.interior_ppt, 0);
        prop_assert_eq!(out.headlight_front_ppt, 0);
        prop_assert_eq!(out.taillight_rear_ppt, 0);
    }
}
