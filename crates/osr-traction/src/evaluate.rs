//! The single pure evaluator.

use crate::inputs::{TractionInputs, TractionParams};
use crate::output::{TractionOutput, TractionState};
use crate::types::{FaultMask, FaultReason, InverterState};

/// Run one supervisor tick.
///
/// Pure function. See the crate-level safety properties TR1–TR6.
#[must_use]
pub fn traction_evaluate(
    prev: &TractionState,
    inputs: &TractionInputs,
    params: &TractionParams,
) -> TractionOutput {
    // --- 1. Sensor / command faults this tick ---------------------------
    let mut current_faults = FaultMask::empty();
    if inputs.inverter_over_temp {
        current_faults.insert(FaultReason::OverTemperature);
    }
    if inputs.inverter_drive_fault {
        current_faults.insert(FaultReason::DriveFault);
    }
    // Contactor open while previously running is a ride-through
    // fault; if we're already disabled it's just nominal.
    if !inputs.bms_contactor_closed && prev.inverter == InverterState::Running {
        current_faults.insert(FaultReason::ContactorOpen);
    }

    // Compute slip (signed: +slip → wheel faster than body; −slip → slide).
    let slip_mmps = inputs
        .wheel_speed_mmps
        .saturating_sub(inputs.reference_speed_mmps);
    let slip_abs = slip_mmps.unsigned_abs() as i32;
    if slip_abs >= params.severe_slip_mmps.max(1) {
        current_faults.insert(FaultReason::SeverelySlipping);
    }

    // --- 2. Latch / cooldown --------------------------------------------
    let mut faults = FaultMask(prev.faults.0 | current_faults.0);
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
    let cooldown_expired = match fault_until_ns {
        Some(until) => inputs.now_ns >= until,
        None => true,
    };
    // A fresh enable request after cooldown and with no current
    // faults clears the latch.
    if inputs.enable_requested
        && cooldown_expired
        && !current_faults.any()
    {
        fault_until_ns = None;
        faults = FaultMask::empty();
    }

    // --- 3. Decide inverter state --------------------------------------
    let inverter = if fault_until_ns.is_some() || faults.any() {
        InverterState::Faulted
    } else if !inputs.bms_contactor_closed {
        InverterState::Disabled
    } else if !inputs.enable_requested {
        InverterState::Disabled
    } else {
        InverterState::Running
    };

    // --- 4. Apply anti-slip to the setpoint ----------------------------
    // Anti-slip is engaged only when we're *motoring and slipping* —
    // wheel running ahead of body by more than slip_threshold while
    // the setpoint is positive (traction). For regen-braking slide
    // the brake crate's WSP is the authority; here we still nudge
    // regen torque down on large slide to reduce pack stress.
    let mut anti_slip_active = false;
    let mut shaped_setpoint = inputs.torque_setpoint_mnm;
    if slip_mmps > params.slip_threshold_mmps.max(1) && shaped_setpoint > 0 {
        anti_slip_active = true;
        shaped_setpoint = scale_ppt(shaped_setpoint, params.anti_slip_retention_ppt);
    } else if slip_mmps < -params.slip_threshold_mmps.max(1) && shaped_setpoint < 0 {
        anti_slip_active = true;
        shaped_setpoint = scale_ppt(shaped_setpoint, params.anti_slip_retention_ppt);
    }
    // Clamp to motor torque rating.
    shaped_setpoint = shaped_setpoint.clamp(
        -(params.max_torque_mnm as i32),
        params.max_torque_mnm as i32,
    );

    // --- 5. Convert to current demand, clamp to BMS limits --------------
    // current (mA) = torque (mN·m) × 1000 / torque_constant (µN·m/mA)
    //   because 1 mN·m = 1000 µN·m, and torque_constant is µN·m/mA.
    let torque_constant_unmpma = i64::from(params.torque_constant_unmpma.max(1));
    let demanded_current_ma_i64 = i64::from(shaped_setpoint)
        .saturating_mul(1_000)
        .checked_div(torque_constant_unmpma)
        .unwrap_or(0);
    // Clamp to pack-side limits (signed).
    let clamped_current = clamp_to_bms(
        demanded_current_ma_i64,
        inputs.bms_discharge_limit_ma,
        inputs.bms_charge_limit_ma,
    );

    // Back-compute actual torque from clamped current so we never
    // command a torque the pack can't deliver.
    let actual_torque_mnm_i64 =
        clamped_current.saturating_mul(torque_constant_unmpma) / 1_000;
    let mut actual_torque_mnm =
        i32::try_from(actual_torque_mnm_i64.clamp(i32::MIN as i64, i32::MAX as i64))
            .unwrap_or(0);

    // --- 6. If inverter isn't Running, force zero torque + current -----
    let (commanded_torque_mnm, estimated_current_ma) =
        if matches!(inverter, InverterState::Running) {
            (
                actual_torque_mnm,
                i32::try_from(clamped_current.clamp(i32::MIN as i64, i32::MAX as i64))
                    .unwrap_or(0),
            )
        } else {
            actual_torque_mnm = 0;
            (0, 0)
        };

    // --- 7. Build state + output ---------------------------------------
    let state = TractionState {
        inverter,
        commanded_torque_mnm,
        estimated_current_ma,
        anti_slip_active: anti_slip_active && matches!(inverter, InverterState::Running),
        faults,
        fault_until_ns,
    };

    TractionOutput {
        state,
        commanded_torque_mnm,
        inverter_enable: matches!(inverter, InverterState::Running),
        estimated_current_ma,
        anti_slip_active: state.anti_slip_active,
    }
}

/// Multiply `v` by `ppt / 1000`, saturating. Preserves sign.
fn scale_ppt(v: i32, ppt: u16) -> i32 {
    let ppt = u32::from(ppt.min(1000));
    let abs = i64::from(v.unsigned_abs()).saturating_mul(i64::from(ppt)) / 1_000;
    let out = if v < 0 {
        -(abs as i64)
    } else {
        abs as i64
    };
    i32::try_from(out.clamp(i32::MIN as i64, i32::MAX as i64)).unwrap_or(0)
}

/// Clamp a signed current demand to `[-charge_limit_ma, discharge_limit_ma]`.
fn clamp_to_bms(demand_ma: i64, discharge_limit_ma: u32, charge_limit_ma: u32) -> i64 {
    let hi = i64::from(discharge_limit_ma);
    let lo = -i64::from(charge_limit_ma);
    demand_ma.clamp(lo, hi)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn params() -> TractionParams {
        TractionParams::light_metro_default()
    }

    fn nominal_inputs(now_ns: u64, torque: i32) -> TractionInputs {
        TractionInputs {
            now_ns,
            torque_setpoint_mnm: torque,
            enable_requested: true,
            bms_contactor_closed: true,
            bms_discharge_limit_ma: 1_000_000,
            bms_charge_limit_ma: 800_000,
            pack_voltage_mv: 320_000,
            reference_speed_mmps: 15_000,
            wheel_speed_mmps: 15_000,
            inverter_over_temp: false,
            inverter_drive_fault: false,
        }
    }

    #[test]
    fn nominal_motoring_passes_torque_through() {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &nominal_inputs(0, 3_000_000), &p);
        assert_eq!(out.state.inverter, InverterState::Running);
        assert!(out.commanded_torque_mnm > 0);
        assert!(out.estimated_current_ma > 0);
        assert!(out.inverter_enable);
        assert!(!out.anti_slip_active);
    }

    #[test]
    fn contactor_open_disables_inverter_and_zeros_torque() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, 3_000_000);
        i.bms_contactor_closed = false;
        let out = traction_evaluate(&prev, &i, &p);
        assert_eq!(out.state.inverter, InverterState::Disabled);
        assert_eq!(out.commanded_torque_mnm, 0);
        assert_eq!(out.estimated_current_ma, 0);
        assert!(!out.inverter_enable);
    }

    #[test]
    fn over_temp_faults_inverter() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, 3_000_000);
        i.inverter_over_temp = true;
        let out = traction_evaluate(&prev, &i, &p);
        assert_eq!(out.state.inverter, InverterState::Faulted);
        assert!(out.state.faults.contains(FaultReason::OverTemperature));
        assert_eq!(out.commanded_torque_mnm, 0);
        assert!(!out.inverter_enable);
    }

    #[test]
    fn slip_reduces_torque() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, 3_000_000);
        i.wheel_speed_mmps = 16_000; // 1 m/s ahead of body → slipping
        let out = traction_evaluate(&prev, &i, &p);
        assert!(out.anti_slip_active);
        // Torque should be reduced to ~40 % of nominal (minus any
        // pack-current clamping).
        let nominal_out = traction_evaluate(&prev, &nominal_inputs(0, 3_000_000), &p);
        assert!(out.commanded_torque_mnm < nominal_out.commanded_torque_mnm);
    }

    #[test]
    fn pack_limit_clamps_current() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, 12_000_000); // max torque
        i.bms_discharge_limit_ma = 100_000; // 100 A tight limit
        let out = traction_evaluate(&prev, &i, &p);
        assert!(out.estimated_current_ma <= 100_000);
        assert!(out.estimated_current_ma >= 0);
        // Torque should be reduced proportionally.
        assert!(out.commanded_torque_mnm < 12_000_000);
    }

    #[test]
    fn regen_produces_negative_current() {
        let p = params();
        let prev = TractionState::default();
        let out = traction_evaluate(&prev, &nominal_inputs(0, -2_000_000), &p);
        assert!(out.commanded_torque_mnm < 0);
        assert!(out.estimated_current_ma < 0);
    }

    #[test]
    fn regen_clamped_by_charge_limit() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, -12_000_000);
        i.bms_charge_limit_ma = 50_000; // 50 A tight charge
        let out = traction_evaluate(&prev, &i, &p);
        assert!(out.estimated_current_ma >= -50_000);
        assert!(out.estimated_current_ma <= 0);
    }

    #[test]
    fn disable_request_stops_inverter() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, 3_000_000);
        i.enable_requested = false;
        let out = traction_evaluate(&prev, &i, &p);
        assert_eq!(out.state.inverter, InverterState::Disabled);
        assert_eq!(out.commanded_torque_mnm, 0);
    }

    #[test]
    fn fault_latches_through_cooldown() {
        let p = params();
        // Trigger a fault.
        let mut i = nominal_inputs(0, 3_000_000);
        i.inverter_over_temp = true;
        let mid = traction_evaluate(&TractionState::default(), &i, &p);
        assert_eq!(mid.state.inverter, InverterState::Faulted);

        // Resolve the over-temp at t=1s but still in cooldown (5s default).
        let mut i = nominal_inputs(1_000_000_000, 3_000_000);
        i.inverter_over_temp = false;
        let out = traction_evaluate(&mid.state, &i, &p);
        assert_eq!(out.state.inverter, InverterState::Faulted);

        // After cooldown with fresh enable → clears.
        let i = nominal_inputs(6_000_000_000, 3_000_000);
        let out = traction_evaluate(&mid.state, &i, &p);
        assert_eq!(out.state.inverter, InverterState::Running);
        assert!(!out.state.faults.any());
    }

    #[test]
    fn severely_slipping_asserts_fault() {
        let p = params();
        let prev = TractionState::default();
        let mut i = nominal_inputs(0, 3_000_000);
        // Wheel 3 m/s faster than body → > 2 m/s severe threshold.
        i.wheel_speed_mmps = 18_000;
        let out = traction_evaluate(&prev, &i, &p);
        assert!(out.state.faults.contains(FaultReason::SeverelySlipping));
    }

    #[test]
    fn determinism() {
        let p = params();
        let prev = TractionState::default();
        let i = nominal_inputs(1_234_567, 4_500_000);
        let a = traction_evaluate(&prev, &i, &p);
        let b = traction_evaluate(&prev, &i, &p);
        assert_eq!(a, b);
    }
}
