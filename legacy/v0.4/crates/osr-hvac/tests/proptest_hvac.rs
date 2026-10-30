//! Property tests for osr-hvac.

use osr_hvac::{hvac_evaluate, HvacInputs, HvacMode, HvacParams, HvacState};
use proptest::prelude::*;

fn params() -> HvacParams {
    HvacParams::light_metro_default()
}

fn arb_inputs() -> impl Strategy<Value = HvacInputs> {
    (
        0u64..60_000_000_000,
        10_000_000u64..2_000_000_000,
        -500i16..700,
        -300i16..500,
        100i16..350,
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(|(now, dt, cabin, amb, sp, rail, enable)| HvacInputs {
            now_ns: now,
            dt_ns: dt,
            cabin_temp_dc: cabin,
            ambient_temp_dc: amb,
            setpoint_dc: sp,
            direct_hv_enabled: rail,
            hvac_enable_request: enable,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn determinism(i in arb_inputs()) {
        let p = params();
        let a = hvac_evaluate(&HvacState::default(), &i, &p);
        let b = hvac_evaluate(&HvacState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn compressor_and_heater_mutually_exclusive(i in arb_inputs()) {
        let p = params();
        let out = hvac_evaluate(&HvacState::default(), &i, &p);
        prop_assert!(!(out.compressor_ppt > 0 && out.heater_ppt > 0));
    }

    #[test]
    fn disabled_is_all_zero(mut i in arb_inputs()) {
        let p = params();
        i.hvac_enable_request = false;
        let out = hvac_evaluate(&HvacState::default(), &i, &p);
        prop_assert_eq!(out.mode, HvacMode::Off);
        prop_assert_eq!(out.compressor_ppt, 0);
        prop_assert_eq!(out.heater_ppt, 0);
        prop_assert_eq!(out.fan_ppt, 0);
    }

    #[test]
    fn rail_down_forces_reduced(mut i in arb_inputs()) {
        let p = params();
        i.direct_hv_enabled = false;
        i.hvac_enable_request = true;
        let out = hvac_evaluate(&HvacState::default(), &i, &p);
        prop_assert_eq!(out.mode, HvacMode::Reduced);
        prop_assert_eq!(out.compressor_ppt, 0);
        prop_assert_eq!(out.heater_ppt, 0);
    }

    #[test]
    fn outputs_bounded(i in arb_inputs()) {
        let p = params();
        let out = hvac_evaluate(&HvacState::default(), &i, &p);
        prop_assert!(out.compressor_ppt <= p.max_compressor_ppt);
        prop_assert!(out.heater_ppt <= p.max_heater_ppt);
        prop_assert!(out.fan_ppt <= p.max_fan_ppt);
    }
}
