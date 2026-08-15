//! Property tests CBB1–CBB3.

use osr_cbm_backend::{ingest_sample, CbmBackendParams, CbmBackendState, Priority};
use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams};
use proptest::prelude::*;

fn arb_inputs(train_id: u32) -> impl Strategy<Value = CbmInputs> {
    (
        prop::collection::vec(0u32..10_000, 1..=4),
        prop::collection::vec(0i16..2_000, 1..=2),
        prop::collection::vec(0u16..=1_000, 1..=4),
        prop::collection::vec(0u16..=1_000, 1..=4),
    )
        .prop_map(move |(v, t, p, w)| CbmInputs {
            now_ns: 0,
            train_id,
            bearing_vib_ppt: v,
            motor_temp_dc: t,
            brake_pad_remaining_ppt: p,
            wheel_tread_remaining_ppt: w,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn cbb1_determinism(i in arb_inputs(42)) {
        let s = cbm_evaluate(&i, &CbmParams::default_metro()).sample;
        let p = CbmBackendParams::default_depot();
        let a = ingest_sample(&CbmBackendState::default(), &s, &p);
        let b = ingest_sample(&CbmBackendState::default(), &s, &p);
        prop_assert_eq!(a, b);
    }

    /// CBB2: any Service-level sample produces at least one urgent order.
    #[test]
    fn cbb2_service_produces_urgent_order(i in arb_inputs(42)) {
        let out_on = cbm_evaluate(&i, &CbmParams::default_metro());
        prop_assume!(out_on.sample.worst_health == osr_cbm_onboard::ComponentHealth::Service);
        let p = CbmBackendParams::default_depot();
        let out = ingest_sample(&CbmBackendState::default(), &out_on.sample, &p);
        prop_assert!(!out.orders.is_empty());
        prop_assert!(out.orders.iter().any(|o| o.priority == Priority::Urgent));
    }

    /// CBB3: a fully-nominal sample never produces an order.
    /// Generate inputs that are nominal *by construction* so we're
    /// not waiting for random sampling to give us a clean input.
    #[test]
    fn cbb3_nominal_produces_no_order(
        vib in prop::collection::vec(0u32..3_999, 1..=4),
        tmp in prop::collection::vec(0i16..1_399, 1..=2),
        pad in prop::collection::vec(301u16..=1_000, 1..=4),
        wheel in prop::collection::vec(301u16..=1_000, 1..=4),
    ) {
        let i = CbmInputs {
            now_ns: 0,
            train_id: 42,
            bearing_vib_ppt: vib,
            motor_temp_dc: tmp,
            brake_pad_remaining_ppt: pad,
            wheel_tread_remaining_ppt: wheel,
        };
        let out_on = cbm_evaluate(&i, &CbmParams::default_metro());
        prop_assert_eq!(out_on.sample.worst_health, osr_cbm_onboard::ComponentHealth::Nominal);
        let p = CbmBackendParams::default_depot();
        let out = ingest_sample(&CbmBackendState::default(), &out_on.sample, &p);
        prop_assert!(out.orders.is_empty());
    }
}
