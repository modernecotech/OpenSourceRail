//! Property tests CB1–CB3.

use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams, ComponentHealth};
use proptest::prelude::*;

fn arb_inputs() -> impl Strategy<Value = CbmInputs> {
    (
        prop::collection::vec(0u32..10_000, 1..=6),
        prop::collection::vec(0i16..2_000, 1..=4),
        prop::collection::vec(0u16..=1_000, 1..=6),
        prop::collection::vec(0u16..=1_000, 1..=6),
    )
        .prop_map(|(vib, tmp, pad, wheel)| CbmInputs {
            now_ns: 0,
            train_id: 42,
            bearing_vib_ppt: vib,
            motor_temp_dc: tmp,
            brake_pad_remaining_ppt: pad,
            wheel_tread_remaining_ppt: wheel,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn cb1_determinism(i in arb_inputs()) {
        let p = CbmParams::default_metro();
        prop_assert_eq!(cbm_evaluate(&i, &p), cbm_evaluate(&i, &p));
    }

    /// CB2: improving every reading can only improve worst_health.
    /// Concretely: pinning all readings to their most-healthy values
    /// must yield Nominal.
    #[test]
    fn cb2_perfect_readings_are_nominal(i in arb_inputs()) {
        let p = CbmParams::default_metro();
        let perfect = CbmInputs {
            now_ns: i.now_ns,
            train_id: i.train_id,
            bearing_vib_ppt: vec![0; i.bearing_vib_ppt.len()],
            motor_temp_dc: vec![0; i.motor_temp_dc.len()],
            brake_pad_remaining_ppt: vec![1000; i.brake_pad_remaining_ppt.len()],
            wheel_tread_remaining_ppt: vec![1000; i.wheel_tread_remaining_ppt.len()],
        };
        let out = cbm_evaluate(&perfect, &p);
        prop_assert_eq!(out.sample.worst_health, ComponentHealth::Nominal);
        prop_assert!(out.flags.is_empty());
    }

    #[test]
    fn cb3_service_iff_any_component_exceeds(i in arb_inputs()) {
        let p = CbmParams::default_metro();
        let out = cbm_evaluate(&i, &p);

        let any_service = i.bearing_vib_ppt.iter().any(|&v| v >= p.bearing_service_ppt)
            || i.motor_temp_dc.iter().any(|&t| t >= p.motor_service_dc)
            || i.brake_pad_remaining_ppt.iter().any(|&w| w <= p.brake_pad_service_ppt)
            || i.wheel_tread_remaining_ppt.iter().any(|&w| w <= p.wheel_service_ppt);

        let reported_service = out.sample.worst_health == ComponentHealth::Service;
        prop_assert_eq!(reported_service, any_service);
    }
}
