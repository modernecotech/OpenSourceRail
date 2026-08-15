//! Property-based tests for the BMS — M1 through M6.

use osr_bms::{
    bms_evaluate, BmsInputs, BmsParams, BmsState, ContactorCommand, ContactorState, FaultReason,
};
use proptest::prelude::*;

fn params() -> BmsParams {
    BmsParams::lfp_default(8, 100_000)
}

fn clean_cells() -> (Vec<u16>, Vec<i16>) {
    (vec![3_200_u16; 8], vec![250_i16; 8])
}

// ---------------------------------------------------------------------------
// M1: determinism.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn m1_determinism(
        current_ma in -2_000_000i32..2_000_000,
        now_ns in 0u64..60_000_000_000,
        dt_ns in 1_000_000u64..1_000_000_000,
    ) {
        let p = params();
        let (v, t) = clean_cells();
        let prev = BmsState::initial(500);
        let i = BmsInputs {
            now_ns, cell_voltages_mv: &v, cell_temps_dc: &t,
            pack_current_ma: current_ma, pack_voltage_mv: 675_000,
            off_gas_detected: false, external_fire_trip: false,
            hazard_module_id: None, hazard_string_id: None,
            external_command: ContactorCommand::RequestClose, dt_ns,
        };
        let a = bms_evaluate(&prev, &i, &p);
        let b = bms_evaluate(&prev, &i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// M2: hard faults open contactor this tick.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn m2_hard_fault_opens_contactor(
        trip_cell_idx in 0usize..8,
        over_voltage in any::<bool>(),
    ) {
        let p = params();
        let mut v = vec![3_200_u16; 8];
        let t = vec![250_i16; 8];
        if over_voltage {
            v[trip_cell_idx] = 4_000; // above v_trip_max 3_950
        } else {
            v[trip_cell_idx] = 1_800; // below v_trip_min 2_000
        }
        let prev = BmsState::initial(500);
        let i = BmsInputs {
            now_ns: 0, cell_voltages_mv: &v, cell_temps_dc: &t,
            pack_current_ma: 0, pack_voltage_mv: 675_000,
            off_gas_detected: false, external_fire_trip: false,
            hazard_module_id: None, hazard_string_id: None,
            external_command: ContactorCommand::RequestClose, dt_ns: 100_000_000,
        };
        let out = bms_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.contactor, ContactorState::OpenFault);
        if over_voltage {
            prop_assert!(out.state.faults.contains(FaultReason::OverVoltage));
        } else {
            prop_assert!(out.state.faults.contains(FaultReason::UnderVoltage));
        }
    }
}

// ---------------------------------------------------------------------------
// M3: fault latches through cooldown.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn m3_fault_latches_through_cooldown(
        dt_ns in 1_000_000u64..100_000_000,
    ) {
        // Trigger a fault at t=0.
        let p = params();
        let mut v = vec![3_200_u16; 8];
        v[0] = 4_000;
        let t = vec![250_i16; 8];
        let prev = BmsState::initial(500);
        let i = BmsInputs {
            now_ns: 0, cell_voltages_mv: &v, cell_temps_dc: &t,
            pack_current_ma: 0, pack_voltage_mv: 675_000,
            off_gas_detected: false, external_fire_trip: false,
            hazard_module_id: None, hazard_string_id: None,
            external_command: ContactorCommand::RequestClose, dt_ns,
        };
        let mut state = bms_evaluate(&prev, &i, &p).state;
        prop_assert_eq!(state.contactor, ContactorState::OpenFault);
        let fault_until = state.fault_until_ns.unwrap();

        // Resolve the voltage violation and clock forward in dt_ns
        // increments. Contactor must stay OpenFault while now < fault_until.
        let v_ok = vec![3_200_u16; 8];
        let mut now_ns = 0_u64;
        while now_ns < fault_until {
            now_ns = now_ns.saturating_add(dt_ns);
            let i = BmsInputs {
                now_ns, cell_voltages_mv: &v_ok, cell_temps_dc: &t,
                pack_current_ma: 0, pack_voltage_mv: 675_000,
                off_gas_detected: false, external_fire_trip: false,
                hazard_module_id: None, hazard_string_id: None,
                external_command: ContactorCommand::RequestClose, dt_ns,
            };
            let out = bms_evaluate(&state, &i, &p);
            if now_ns < fault_until {
                prop_assert_eq!(
                    out.contactor, ContactorState::OpenFault,
                    "contactor closed during cooldown at now_ns={}", now_ns
                );
            }
            state = out.state;
        }
    }
}

// ---------------------------------------------------------------------------
// M4: derating is conservative — cell close to warning threshold
// produces charge limit ≤ nominal.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn m4_derating_is_conservative(
        top_cell_voltage in 3_200u16..3_945,
    ) {
        let p = params();
        let mut v = vec![3_200_u16; 8];
        v[0] = top_cell_voltage;
        let t = vec![250_i16; 8];
        let prev = BmsState::initial(500);
        let i = BmsInputs {
            now_ns: 0, cell_voltages_mv: &v, cell_temps_dc: &t,
            pack_current_ma: 0, pack_voltage_mv: 675_000,
            off_gas_detected: false, external_fire_trip: false,
            hazard_module_id: None, hazard_string_id: None,
            external_command: ContactorCommand::RequestClose, dt_ns: 100_000_000,
        };
        let out = bms_evaluate(&prev, &i, &p);
        prop_assert!(out.charge_limit_ma <= p.max_charge_ma);
        prop_assert!(out.discharge_limit_ma <= p.max_discharge_ma);
    }
}

// ---------------------------------------------------------------------------
// M5: SoC always within [0, 1000].
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn m5_soc_bounded(
        current_ma in -2_000_000i32..2_000_000,
        dt_ns in 0u64..10_000_000_000_000,
        initial_soc in 0u16..=1000,
    ) {
        let p = params();
        let (v, t) = clean_cells();
        let prev = BmsState::initial(initial_soc);
        let i = BmsInputs {
            now_ns: 0, cell_voltages_mv: &v, cell_temps_dc: &t,
            pack_current_ma: current_ma, pack_voltage_mv: 675_000,
            off_gas_detected: false, external_fire_trip: false,
            hazard_module_id: None, hazard_string_id: None,
            external_command: ContactorCommand::RequestClose, dt_ns,
        };
        let out = bms_evaluate(&prev, &i, &p);
        prop_assert!(out.state.soc_ppt <= 1000);
    }
}

// ---------------------------------------------------------------------------
// M6: contactor open implies zero limits.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn m6_open_contactor_zero_limits(
        current_ma in -2_000_000i32..2_000_000,
        cmd_variant in 0u8..3,
    ) {
        let p = params();
        let (v, t) = clean_cells();
        let prev = BmsState::initial(500);
        let cmd = match cmd_variant {
            0 => ContactorCommand::RequestOpen,
            1 => ContactorCommand::RequestClose,
            _ => ContactorCommand::ClearFault,
        };
        let i = BmsInputs {
            now_ns: 0, cell_voltages_mv: &v, cell_temps_dc: &t,
            pack_current_ma: current_ma, pack_voltage_mv: 675_000,
            off_gas_detected: false, external_fire_trip: false,
            hazard_module_id: None, hazard_string_id: None,
            external_command: cmd, dt_ns: 100_000_000,
        };
        let out = bms_evaluate(&prev, &i, &p);
        if out.contactor != ContactorState::Closed {
            prop_assert_eq!(out.charge_limit_ma, 0);
            prop_assert_eq!(out.discharge_limit_ma, 0);
        }
    }
}
