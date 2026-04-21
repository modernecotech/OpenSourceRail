//! Property-based tests TR1–TR6.

use osr_traction::{
    traction_evaluate, InverterState, TractionInputs, TractionParams, TractionState,
};
use proptest::prelude::*;

fn params() -> TractionParams {
    TractionParams::light_metro_default()
}

fn arb_inputs() -> impl Strategy<Value = TractionInputs> {
    (
        0u64..60_000_000_000,
        -12_000_000i32..12_000_000,
        any::<bool>(),
        any::<bool>(),
        0u32..2_000_000,
        0u32..2_000_000,
        -30_000i32..30_000,
        -30_000i32..30_000,
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(
            |(now, torque, enable, cc, dis, chg, ref_s, wheel, ot, df)| TractionInputs {
                now_ns: now,
                torque_setpoint_mnm: torque,
                enable_requested: enable,
                bms_contactor_closed: cc,
                bms_discharge_limit_ma: dis,
                bms_charge_limit_ma: chg,
                pack_voltage_mv: 320_000,
                reference_speed_mmps: ref_s,
                wheel_speed_mmps: wheel,
                inverter_over_temp: ot,
                inverter_drive_fault: df,
            },
        )
}

// ---------------------------------------------------------------------------
// TR1: determinism.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn tr1_determinism(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let a = traction_evaluate(&prev, &i, &p);
        let b = traction_evaluate(&prev, &i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// TR2: pack-limit clamping. estimated_current_ma stays within
// [-charge_limit, +discharge_limit].
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn tr2_pack_limits(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &i, &p);
        let hi = i64::from(i.bms_discharge_limit_ma);
        let lo = -i64::from(i.bms_charge_limit_ma);
        let c = i64::from(out.estimated_current_ma);
        prop_assert!(c <= hi, "current {} exceeds discharge limit {}", c, hi);
        prop_assert!(c >= lo, "current {} below -charge limit {}", c, lo);
    }
}

// ---------------------------------------------------------------------------
// TR3: anti-slip never adds torque. |commanded| ≤ |setpoint|.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn tr3_anti_slip_never_adds_torque(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &i, &p);
        prop_assert!(
            out.commanded_torque_mnm.unsigned_abs()
                <= i.torque_setpoint_mnm.unsigned_abs(),
            "commanded {} > setpoint {}",
            out.commanded_torque_mnm, i.torque_setpoint_mnm,
        );
    }
}

// ---------------------------------------------------------------------------
// TR4: no contactor → inverter Disabled, torque 0, current 0.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn tr4_contactor_open_disables(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &i, &p);
        if !i.bms_contactor_closed {
            // Either Disabled (clean) or Faulted (if prev was Running
            // and it just opened — a ride-through fault is also
            // acceptable). Torque and current must be zero either way.
            prop_assert!(matches!(
                out.state.inverter,
                InverterState::Disabled | InverterState::Faulted
            ));
            prop_assert_eq!(out.commanded_torque_mnm, 0);
            prop_assert_eq!(out.estimated_current_ma, 0);
        }
    }
}

// ---------------------------------------------------------------------------
// TR5: any drive fault → Faulted state + zero torque.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn tr5_drive_fault_stops_inverter(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &i, &p);
        if i.inverter_over_temp || i.inverter_drive_fault {
            prop_assert_eq!(out.state.inverter, InverterState::Faulted);
            prop_assert_eq!(out.commanded_torque_mnm, 0);
            prop_assert!(!out.inverter_enable);
        }
    }
}

// ---------------------------------------------------------------------------
// TR6: torque and current sign agree. +torque → +/0 current; -torque → -/0.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn tr6_sign_consistent(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &i, &p);
        if out.commanded_torque_mnm > 0 {
            prop_assert!(out.estimated_current_ma >= 0);
        }
        if out.commanded_torque_mnm < 0 {
            prop_assert!(out.estimated_current_ma <= 0);
        }
    }
}

// ---------------------------------------------------------------------------
// Sanity: torque bounded by motor rating.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn torque_never_exceeds_rating(i in arb_inputs()) {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &i, &p);
        prop_assert!(out.commanded_torque_mnm.unsigned_abs() <= p.max_torque_mnm);
    }
}
