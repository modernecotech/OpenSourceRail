//! The single pure evaluator.

use crate::inputs::{BmsInputs, BmsParams, ContactorCommand};
use crate::output::{AlarmLevel, BmsOutput, BmsState, FaultMask};
use crate::types::{ContactorState, FaultReason};

/// Evaluate one BMS tick.
///
/// Pure function of `(prev, inputs, params)`. See crate docs for the
/// M1–M6 safety properties.
#[must_use]
pub fn bms_evaluate(prev: &BmsState, inputs: &BmsInputs<'_>, params: &BmsParams) -> BmsOutput {
    // --- 1. Integrate SoC via Coulomb counting -------------------------
    // dQ (mA·s) = pack_current_ma · dt_s = pack_current_ma · dt_ns / 1e9
    let dt_ns_i = i64::try_from(inputs.dt_ns).unwrap_or(i64::MAX);
    let d_charge_mas = i64::from(inputs.pack_current_ma).saturating_mul(dt_ns_i) / 1_000_000_000;

    // Absolute charge throughput drives a conservative equivalent-full-cycle
    // SoH estimator. Hot cell operation counts more heavily; persisting the
    // weighted accumulator prevents small per-tick losses from integer
    // rounding and makes restart recovery deterministic.
    let absolute_throughput_mas = u64::from(inputs.pack_current_ma.unsigned_abs())
        .saturating_mul(inputs.dt_ns)
        / 1_000_000_000;
    let hottest_cell_dc = inputs.cell_temps_dc.iter().copied().max().unwrap_or(0);
    let temperature_multiplier = if hottest_cell_dc >= params.hot_cycle_threshold_dc {
        u64::from(params.hot_cycle_multiplier.max(1))
    } else {
        1
    };
    let degradation_weighted_mas = prev
        .degradation_weighted_mas
        .saturating_add(absolute_throughput_mas.saturating_mul(temperature_multiplier));
    let equivalent_full_cycle_mas = u64::from(params.cell_capacity_mah)
        .saturating_mul(3_600)
        .saturating_mul(2)
        .max(1);
    let degradation_ppm = degradation_weighted_mas
        .saturating_mul(u64::from(params.cycle_fade_ppm_per_efc))
        / equivalent_full_cycle_mas;
    let estimated_soh_ppt = 1_000_u16
        .saturating_sub(u16::try_from((degradation_ppm / 1_000).min(1_000)).unwrap_or(1_000));
    let soh_ppt = prev.soh_ppt.min(estimated_soh_ppt);

    // Pack capacity in mA·s, assuming cells in series (series-parallel
    // strings present the same capacity as one cell on the pack side,
    // though real packs multiply by parallel count — here we use the
    // params as given and let the caller configure `cell_capacity_mah`
    // to the pack-side effective capacity).
    let pack_capacity_mas = i64::from(params.cell_capacity_mah).saturating_mul(3_600);

    let (soc_ppt, charge_accum_mas) = if pack_capacity_mas <= 0 {
        (prev.soc_ppt, prev.charge_accum_mas)
    } else {
        let quantum_mas = (pack_capacity_mas / 1_000).max(1);
        let accumulated = prev.charge_accum_mas.saturating_add(d_charge_mas);
        let delta_ppt = accumulated / quantum_mas;
        let unclamped = i64::from(prev.soc_ppt).saturating_add(delta_ppt);
        let clamped = unclamped.clamp(0, 1_000);
        let residual = if unclamped != clamped {
            0
        } else {
            accumulated % quantum_mas
        };
        (u16::try_from(clamped).unwrap_or(0), residual)
    };

    // --- 2. Detect faults and warnings ---------------------------------
    //
    // Scan into `current_faults` (what the sensors say THIS tick);
    // `faults` is then `prev.faults | current_faults` (the latched
    // mask). Clearing requires `current_faults == empty`.
    let mut current_faults = FaultMask::empty();
    let mut alarm = AlarmLevel::Nominal;

    if inputs.off_gas_detected {
        current_faults.insert(FaultReason::OffGasDetected);
    }
    if inputs.external_fire_trip {
        current_faults.insert(FaultReason::ExternalFireTrip);
    }

    if inputs.cell_voltages_mv.is_empty()
        || inputs.cell_voltages_mv.len() != inputs.cell_temps_dc.len()
    {
        current_faults.insert(FaultReason::SensorMismatch);
    } else {
        // Voltage scan.
        let mut v_max = u16::MIN;
        let mut v_min = u16::MAX;
        for &v in inputs.cell_voltages_mv {
            if v > v_max {
                v_max = v;
            }
            if v < v_min {
                v_min = v;
            }
        }
        if v_max >= params.v_trip_max_mv {
            current_faults.insert(FaultReason::OverVoltage);
        }
        if v_min <= params.v_trip_min_mv {
            current_faults.insert(FaultReason::UnderVoltage);
        }
        if v_max >= params.v_warn_max_mv && alarm == AlarmLevel::Nominal {
            alarm = AlarmLevel::Warning;
        }
        if v_min <= params.v_warn_min_mv && alarm == AlarmLevel::Nominal {
            alarm = AlarmLevel::Warning;
        }
        if v_max.saturating_sub(v_min) >= params.imbalance_trip_mv {
            current_faults.insert(FaultReason::Imbalance);
        }

        // Temperature scan.
        let mut t_max = i16::MIN;
        let mut t_min = i16::MAX;
        for &t in inputs.cell_temps_dc {
            if t > t_max {
                t_max = t;
            }
            if t < t_min {
                t_min = t;
            }
        }
        if t_max >= params.t_trip_max_dc {
            current_faults.insert(FaultReason::OverTemperature);
        }
        if t_min <= params.t_trip_min_dc {
            current_faults.insert(FaultReason::UnderTemperature);
        }
        if t_max >= params.t_warn_max_dc && alarm == AlarmLevel::Nominal {
            alarm = AlarmLevel::Warning;
        }
        if t_min <= params.t_warn_min_dc && alarm == AlarmLevel::Nominal {
            alarm = AlarmLevel::Warning;
        }

        // Current scan.
        let ic = inputs.pack_current_ma.unsigned_abs();
        if ic >= params.current_trip_ma {
            current_faults.insert(FaultReason::OverCurrent);
        }
    }

    // Latched mask: union of previously-latched and currently-active.
    let mut faults = FaultMask(prev.faults.0 | current_faults.0);

    if faults.any() {
        alarm = AlarmLevel::Trip;
    }

    // --- 3. Fault latch / cooldown -------------------------------------
    let mut fault_until_ns = prev.fault_until_ns;
    if current_faults.any() {
        let new_deadline = inputs
            .now_ns
            .saturating_add(u64::from(params.fault_cooldown_ms) * 1_000_000);
        fault_until_ns = Some(match fault_until_ns {
            Some(existing) => existing.max(new_deadline),
            None => new_deadline,
        });
    }

    // ClearFault: honoured only when cooldown has elapsed AND no
    // sensor-observed fault this tick.
    let cooldown_expired = match fault_until_ns {
        Some(until) => inputs.now_ns >= until,
        None => true,
    };
    let clear_requested = matches!(inputs.external_command, ContactorCommand::ClearFault);
    if clear_requested && cooldown_expired && !current_faults.any() {
        fault_until_ns = None;
        faults = FaultMask::empty();
        if alarm == AlarmLevel::Trip {
            alarm = AlarmLevel::Nominal;
        }
    }

    // --- 4. Contactor state --------------------------------------------
    let contactor = if faults.any() || fault_until_ns.is_some() {
        ContactorState::OpenFault
    } else {
        match inputs.external_command {
            ContactorCommand::RequestClose => ContactorState::Closed,
            ContactorCommand::RequestOpen => ContactorState::Open,
            ContactorCommand::ClearFault => {
                // Already cleared above; default to Open.
                ContactorState::Open
            }
        }
    };

    // --- 5. Derated current limits (M4, M6) ----------------------------
    let (charge_limit_ma, discharge_limit_ma) = if contactor != ContactorState::Closed {
        (0, 0)
    } else {
        derate_limits(inputs, params, alarm)
    };

    let state = BmsState {
        soc_ppt,
        soh_ppt,
        degradation_weighted_mas,
        contactor,
        faults,
        fault_until_ns,
        charge_accum_mas,
        alarm,
    };

    BmsOutput {
        state,
        contactor,
        charge_limit_ma,
        discharge_limit_ma,
        charge_inhibited: inputs.off_gas_detected || inputs.external_fire_trip || faults.any(),
        pack_isolation_requested: inputs.off_gas_detected || inputs.external_fire_trip,
        hazard_module_id: inputs.hazard_module_id,
        hazard_string_id: inputs.hazard_string_id,
    }
}

/// Derate pack-level charge / discharge limits based on the
/// worst-case margin of any cell to any voltage / temperature
/// threshold. Monotone: as the margin narrows, the limit decreases
/// linearly toward 0.
fn derate_limits(inputs: &BmsInputs<'_>, params: &BmsParams, alarm: AlarmLevel) -> (u32, u32) {
    if matches!(alarm, AlarmLevel::Trip) {
        return (0, 0);
    }

    // Start at nominal maxima.
    let mut charge = params.max_charge_ma;
    let mut discharge = params.max_discharge_ma;

    // Voltage-based derating — charge limited by how close the
    // highest cell is to `v_warn_max`; discharge limited by how close
    // the lowest cell is to `v_warn_min`.
    let mut v_max = u16::MIN;
    let mut v_min = u16::MAX;
    for &v in inputs.cell_voltages_mv {
        v_max = v_max.max(v);
        v_min = v_min.min(v);
    }
    let charge_headroom_mv = params.v_trip_max_mv.saturating_sub(v_max);
    let discharge_headroom_mv = v_min.saturating_sub(params.v_trip_min_mv);
    let v_charge_window = params
        .v_trip_max_mv
        .saturating_sub(params.v_warn_max_mv)
        .max(1);
    let v_discharge_window = params
        .v_warn_min_mv
        .saturating_sub(params.v_trip_min_mv)
        .max(1);

    charge = scale_down(charge, charge_headroom_mv, v_charge_window);
    discharge = scale_down(discharge, discharge_headroom_mv, v_discharge_window);

    // Temperature-based derating.
    let mut t_max = i16::MIN;
    let mut t_min = i16::MAX;
    for &t in inputs.cell_temps_dc {
        t_max = t_max.max(t);
        t_min = t_min.min(t);
    }
    let charge_t_headroom_dc = params.t_trip_max_dc.saturating_sub(t_max).max(0) as u16;
    let charge_t_window = params
        .t_trip_max_dc
        .saturating_sub(params.t_warn_max_dc)
        .max(1) as u16;
    charge = scale_down(charge, charge_t_headroom_dc, charge_t_window);

    // Under-temperature also derates charge (LFP especially hates
    // cold charging), and discharge to a lesser degree.
    let cold_headroom_dc = (t_min.saturating_sub(params.t_trip_min_dc)).max(0) as u16;
    let cold_window = params
        .t_warn_min_dc
        .saturating_sub(params.t_trip_min_dc)
        .max(1) as u16;
    charge = scale_down(charge, cold_headroom_dc, cold_window);
    discharge = scale_down(discharge, cold_headroom_dc, cold_window);

    (charge, discharge)
}

/// If `headroom < window`, scale `limit` linearly down toward 0.
/// Otherwise leave unchanged. Never increases.
fn scale_down(limit: u32, headroom: u16, window: u16) -> u32 {
    if headroom >= window {
        return limit;
    }
    let scaled = u64::from(limit).saturating_mul(u64::from(headroom)) / u64::from(window.max(1));
    scaled as u32
}

#[cfg(test)]
mod tests {
    use super::*;

    fn params() -> BmsParams {
        BmsParams::lfp_default(96, 100_000) // 96s, 100 Ah cells
    }

    fn nominal_inputs<'a>(
        now_ns: u64,
        cell_voltages: &'a [u16],
        cell_temps: &'a [i16],
    ) -> BmsInputs<'a> {
        BmsInputs {
            now_ns,
            cell_voltages_mv: cell_voltages,
            cell_temps_dc: cell_temps,
            pack_current_ma: 0,
            pack_voltage_mv: 320_000,
            off_gas_detected: false,
            external_fire_trip: false,
            hazard_module_id: None,
            hazard_string_id: None,
            external_command: ContactorCommand::RequestClose,
            dt_ns: 100_000_000, // 100 ms
        }
    }

    #[test]
    fn nominal_operation_closes_contactor_and_gives_full_limits() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(800);
        let out = bms_evaluate(&prev, &nominal_inputs(1_000_000, &v, &t), &p);
        assert_eq!(out.contactor, ContactorState::Closed);
        assert!(out.charge_limit_ma > 0);
        assert!(out.discharge_limit_ma > 0);
        assert_eq!(out.state.alarm, AlarmLevel::Nominal);
    }

    #[test]
    fn over_voltage_trips_contactor() {
        let p = params();
        let mut v = vec![3_200_u16; 96];
        v[5] = 4_000; // above trip max 3_950
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(800);
        let out = bms_evaluate(&prev, &nominal_inputs(1_000_000, &v, &t), &p);
        assert_eq!(out.contactor, ContactorState::OpenFault);
        assert!(out.state.faults.contains(FaultReason::OverVoltage));
        assert_eq!(out.charge_limit_ma, 0);
        assert_eq!(out.discharge_limit_ma, 0);
    }

    #[test]
    fn cooldown_latches_through_resolve() {
        let p = params();
        // Seed a fault at t=0.
        let v_bad = vec![4_000_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(800);
        let mid = bms_evaluate(&prev, &nominal_inputs(0, &v_bad, &t), &p);
        assert_eq!(mid.contactor, ContactorState::OpenFault);
        // Resolve the fault at t=1s — but cooldown (10 s default) is active.
        let v_ok = vec![3_200_u16; 96];
        let mut i = nominal_inputs(1_000_000_000, &v_ok, &t);
        i.external_command = ContactorCommand::ClearFault;
        let out = bms_evaluate(&mid.state, &i, &p);
        assert_eq!(out.contactor, ContactorState::OpenFault);
        // After cooldown (>10 s) with ClearFault, it clears.
        let mut i = nominal_inputs(11_000_000_000, &v_ok, &t);
        i.external_command = ContactorCommand::ClearFault;
        let out = bms_evaluate(&mid.state, &i, &p);
        assert_eq!(out.contactor, ContactorState::Open);
        assert!(!out.state.faults.any());
    }

    #[test]
    fn sensor_mismatch_trips() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 95]; // off by one
        let prev = BmsState::initial(800);
        let out = bms_evaluate(&prev, &nominal_inputs(0, &v, &t), &p);
        assert!(out.state.faults.contains(FaultReason::SensorMismatch));
        assert_eq!(out.contactor, ContactorState::OpenFault);
    }

    #[test]
    fn soc_increases_under_charge_current() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(500);
        let mut i = nominal_inputs(0, &v, &t);
        i.pack_current_ma = 50_000; // 50 A charge
        i.dt_ns = 10_000_000_000; // 10 s
        let out = bms_evaluate(&prev, &i, &p);
        assert!(out.state.soc_ppt >= prev.soc_ppt);
    }

    #[test]
    fn soc_decreases_under_discharge_current() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(500);
        let mut i = nominal_inputs(0, &v, &t);
        i.pack_current_ma = -50_000;
        i.dt_ns = 10_000_000_000;
        let out = bms_evaluate(&prev, &i, &p);
        assert!(out.state.soc_ppt <= prev.soc_ppt);
    }

    #[test]
    fn soc_bounded_at_100() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(999);
        let mut i = nominal_inputs(0, &v, &t);
        i.pack_current_ma = 1_000_000;
        i.dt_ns = 1_000_000_000_000;
        let out = bms_evaluate(&prev, &i, &p);
        assert!(out.state.soc_ppt <= 1000);
    }

    #[test]
    fn soh_degrades_with_equivalent_full_cycle_throughput() {
        let p = BmsParams::lfp_default(8, 1_000);
        let v = vec![3_200_u16; 8];
        let t = vec![250_i16; 8];
        let prev = BmsState::initial(500);
        let mut i = nominal_inputs(72_000_000_000_000, &v, &t);
        i.pack_current_ma = 1_000;
        // 1 A for 20 h is 20 Ah throughput = 10 EFC for a 1 Ah cell.
        i.dt_ns = 72_000_000_000_000;
        let out = bms_evaluate(&prev, &i, &p);
        assert_eq!(out.state.soh_ppt, 998);
        assert!(out.state.degradation_weighted_mas > 0);
    }

    #[test]
    fn hot_cycles_accelerate_soh_degradation() {
        let p = BmsParams::lfp_default(8, 1_000);
        let v = vec![3_200_u16; 8];
        let nominal_t = vec![250_i16; 8];
        let hot_t = vec![500_i16; 8];
        let prev = BmsState::initial(500);
        let mut nominal = nominal_inputs(72_000_000_000_000, &v, &nominal_t);
        nominal.pack_current_ma = 1_000;
        nominal.dt_ns = 72_000_000_000_000;
        let mut hot = nominal_inputs(72_000_000_000_000, &v, &hot_t);
        hot.pack_current_ma = 1_000;
        hot.dt_ns = 72_000_000_000_000;

        let nominal_out = bms_evaluate(&prev, &nominal, &p);
        let hot_out = bms_evaluate(&prev, &hot, &p);
        assert!(hot_out.state.soh_ppt < nominal_out.state.soh_ppt);
        assert_eq!(
            hot_out.state.degradation_weighted_mas,
            nominal_out.state.degradation_weighted_mas * 2
        );
    }

    #[test]
    fn off_gas_trip_opens_pack_and_preserves_module_identity() {
        let p = BmsParams::lfp_default(8, 100_000);
        let v = vec![3_200_u16; 8];
        let t = vec![250_i16; 8];
        let mut i = nominal_inputs(0, &v, &t);
        i.off_gas_detected = true;
        i.hazard_module_id = Some(3);
        i.hazard_string_id = Some(1);
        let out = bms_evaluate(&BmsState::initial(800), &i, &p);
        assert_eq!(out.contactor, ContactorState::OpenFault);
        assert!(out.charge_inhibited);
        assert!(out.pack_isolation_requested);
        assert_eq!(out.hazard_module_id, Some(3));
        assert_eq!(out.hazard_string_id, Some(1));
    }

    #[test]
    fn imbalance_trips_fault() {
        let p = params();
        let mut v = vec![3_200_u16; 96];
        v[0] = 3_000;
        v[1] = 3_500; // spread 500 mV > imbalance_trip 150
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(800);
        let out = bms_evaluate(&prev, &nominal_inputs(0, &v, &t), &p);
        assert!(out.state.faults.contains(FaultReason::Imbalance));
    }

    #[test]
    fn over_temp_trips_fault() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let mut t = vec![250_i16; 96];
        t[10] = 700; // 70 °C > trip 65 °C
        let prev = BmsState::initial(800);
        let out = bms_evaluate(&prev, &nominal_inputs(0, &v, &t), &p);
        assert!(out.state.faults.contains(FaultReason::OverTemperature));
    }

    #[test]
    fn determinism() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(750);
        let i = nominal_inputs(1_234_567, &v, &t);
        let a = bms_evaluate(&prev, &i, &p);
        let b = bms_evaluate(&prev, &i, &p);
        assert_eq!(a, b);
    }

    #[test]
    fn open_contactor_gives_zero_limits() {
        let p = params();
        let v = vec![3_200_u16; 96];
        let t = vec![250_i16; 96];
        let prev = BmsState::initial(800);
        let mut i = nominal_inputs(0, &v, &t);
        i.external_command = ContactorCommand::RequestOpen;
        let out = bms_evaluate(&prev, &i, &p);
        assert_eq!(out.contactor, ContactorState::Open);
        assert_eq!(out.charge_limit_ma, 0);
        assert_eq!(out.discharge_limit_ma, 0);
    }
}
