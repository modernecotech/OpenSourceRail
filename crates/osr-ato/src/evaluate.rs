//! The pure evaluator.

use crate::envelope::station_approach_speed_mmps;
use crate::inputs::{AtoInputs, AtoParams};
use crate::output::{AtoOutput, AtoState};
use crate::types::AtoMode;

/// Evaluate one ATO tick.
///
/// Pure. See the crate-level AO1–AO8 property list.
#[must_use]
pub fn ato_evaluate(prev: &AtoState, inputs: &AtoInputs, params: &AtoParams) -> AtoOutput {
    // --- AO4: disengaged → all-zero command --------------------------
    if !inputs.ato_engaged {
        return AtoOutput {
            state: AtoState {
                integral_mnm: 0,
                last_mode: AtoMode::Off,
                last_tick_ns: inputs.now_ns,
            },
            torque_setpoint_mnm: 0,
            service_brake_ppt: 0,
            mode: AtoMode::Off,
            effective_target_mmps: 0,
        };
    }

    // --- AO5: stopped at platform → holding brake --------------------
    let speed_abs = inputs.current_speed_mmps.unsigned_abs() as i32;
    if inputs.at_station && speed_abs <= params.stop_tolerance_mmps {
        let mode = if inputs.dwell_remaining_ms > 0 {
            AtoMode::Dwelling
        } else {
            AtoMode::Stopped
        };
        return AtoOutput {
            state: AtoState {
                integral_mnm: 0,
                last_mode: mode,
                last_tick_ns: inputs.now_ns,
            },
            torque_setpoint_mnm: 0,
            service_brake_ppt: params.holding_brake_ppt.min(params.max_service_brake_ppt),
            mode,
            effective_target_mmps: 0,
        };
    }

    // --- Determine the effective target speed ------------------------
    //
    // The target is the minimum of:
    //   - cruise_target_mmps (schedule),
    //   - station_approach_speed_mmps(distance, decel) if a stop is in
    //     range (this is what drives the deceleration profile),
    //   - envelope_mmps - envelope_margin_mmps (ATP guard band).
    //
    // All three are floored at 0 and capped at i32::MAX internally.
    let mut target = inputs.cruise_target_mmps.max(0);

    let mut mode = AtoMode::Cruising;

    if let Some(d_mm) = inputs.distance_to_stop_mm {
        let approach = station_approach_speed_mmps(d_mm, params.station_approach_decel_mmps2);
        if approach < target {
            target = approach;
            mode = AtoMode::StationApproach;
        }
    }

    let envelope_cap = inputs
        .envelope_mmps
        .saturating_sub(params.envelope_margin_mmps)
        .max(0);
    if envelope_cap < target {
        target = envelope_cap;
    }

    // --- AO8 guard: if already above envelope, zero out any positive
    // target — we must be decelerating.
    if inputs.current_speed_mmps > inputs.envelope_mmps {
        target = 0;
    }

    // --- PI control loop --------------------------------------------
    let err_mmps = target.saturating_sub(inputs.current_speed_mmps);

    // Integrator update, in units of mN·m · s.
    // Contribution per tick: err (mm/s) × ki (mN·m / (mm/s · s)) × dt_s.
    let dt_s_milli = inputs.dt_ns / 1_000_000; // to ms; then /1000 for s below
    let mut integral = prev.integral_mnm;

    if err_mmps.unsigned_abs() > params.cruise_deadband_mmps as u32 {
        let delta = i64::from(err_mmps)
            .saturating_mul(i64::from(params.ki_mnm_per_mmps_s))
            .saturating_mul(dt_s_milli as i64)
            / 1_000;
        integral = integral.saturating_add(delta);
    }
    let clamp = i64::from(params.max_integral_mnm);
    if integral > clamp {
        integral = clamp;
    } else if integral < -clamp {
        integral = -clamp;
    }

    let p_term = i64::from(err_mmps).saturating_mul(i64::from(params.kp_mnm_per_mmps));
    let demand_mnm_i64 = p_term.saturating_add(integral);
    let demand_mnm = clamp_i64_to_i32(
        demand_mnm_i64,
        -i64::from(params.max_torque_mnm),
        i64::from(params.max_torque_mnm),
    );

    // --- Map PI output to (torque, brake) ----------------------------
    let (torque_setpoint_mnm, service_brake_ppt, demand_mode) =
        if demand_mnm > params.coast_band_mnm {
            (demand_mnm, 0u16, AtoMode::Accelerating)
        } else if demand_mnm >= -params.coast_band_mnm {
            // Deadband / coast: zero torque, zero brake.
            if err_mmps.unsigned_abs() <= params.cruise_deadband_mmps as u32 {
                (0, 0u16, AtoMode::Cruising)
            } else {
                (0, 0u16, AtoMode::Coasting)
            }
        } else {
            // Service brake: demand is a large-magnitude negative value.
            let brake_abs_i64 = (-i64::from(demand_mnm)).max(0);
            let ppt_i64 = brake_abs_i64.saturating_mul(i64::from(params.max_service_brake_ppt))
                / i64::from(params.full_brake_demand_mnm.max(1));
            let ppt = u16::try_from(ppt_i64.clamp(0, 1_000)).unwrap_or(0);
            let ppt = ppt.min(params.max_service_brake_ppt);
            (0, ppt, AtoMode::Braking)
        };

    // Station-approach mode dominates Accelerating / Cruising when
    // the station profile is binding.
    let final_mode = match (mode, demand_mode) {
        (AtoMode::StationApproach, AtoMode::Braking) => AtoMode::StationApproach,
        (_, m) => m,
    };

    AtoOutput {
        state: AtoState {
            integral_mnm: integral,
            last_mode: final_mode,
            last_tick_ns: inputs.now_ns,
        },
        torque_setpoint_mnm,
        service_brake_ppt,
        mode: final_mode,
        effective_target_mmps: target,
    }
}

fn clamp_i64_to_i32(v: i64, lo: i64, hi: i64) -> i32 {
    let c = v.clamp(lo, hi);
    i32::try_from(c.clamp(i32::MIN as i64, i32::MAX as i64)).unwrap_or(0)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn params() -> AtoParams {
        AtoParams::light_metro_default()
    }

    fn nominal(
        current_mmps: i32,
        envelope_mmps: i32,
        cruise_mmps: i32,
        dist: Option<i64>,
    ) -> AtoInputs {
        AtoInputs {
            now_ns: 1_000_000_000,
            dt_ns: 100_000_000, // 100 ms tick
            current_speed_mmps: current_mmps,
            envelope_mmps,
            cruise_target_mmps: cruise_mmps,
            distance_to_stop_mm: dist,
            at_station: false,
            dwell_remaining_ms: 0,
            ato_engaged: true,
        }
    }

    #[test]
    fn disengaged_outputs_zero() {
        let p = params();
        let mut i = nominal(10_000, 22_000, 15_000, None);
        i.ato_engaged = false;
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert_eq!(out.torque_setpoint_mnm, 0);
        assert_eq!(out.service_brake_ppt, 0);
        assert_eq!(out.mode, AtoMode::Off);
    }

    #[test]
    fn below_target_accelerates() {
        let p = params();
        let i = nominal(5_000, 22_000, 15_000, None);
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert_eq!(out.mode, AtoMode::Accelerating);
        assert!(out.torque_setpoint_mnm > 0);
        assert_eq!(out.service_brake_ppt, 0);
    }

    #[test]
    fn at_target_cruises_no_output() {
        let p = params();
        let i = nominal(15_000, 22_000, 15_000, None);
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert_eq!(out.mode, AtoMode::Cruising);
        assert_eq!(out.torque_setpoint_mnm, 0);
        assert_eq!(out.service_brake_ppt, 0);
    }

    #[test]
    fn above_target_brakes() {
        let p = params();
        let i = nominal(20_000, 22_000, 10_000, None);
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert!(matches!(out.mode, AtoMode::Braking | AtoMode::Coasting));
        assert_eq!(out.torque_setpoint_mnm, 0);
    }

    #[test]
    fn envelope_caps_target() {
        let p = params();
        let i = nominal(10_000, 12_000, 25_000, None);
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        // Envelope 12_000 minus margin 500 = 11_500 < cruise 25_000
        assert!(out.effective_target_mmps <= 11_500);
    }

    #[test]
    fn overspeed_commands_no_positive_torque() {
        let p = params();
        let i = nominal(25_000, 20_000, 22_000, None); // above envelope
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert!(out.torque_setpoint_mnm <= 0);
    }

    #[test]
    fn at_station_applies_holding_brake() {
        let p = params();
        let mut i = nominal(0, 0, 0, None);
        i.at_station = true;
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert_eq!(out.mode, AtoMode::Stopped);
        assert_eq!(out.torque_setpoint_mnm, 0);
        assert!(out.service_brake_ppt >= p.holding_brake_ppt);
    }

    #[test]
    fn dwelling_reported_when_timer_active() {
        let p = params();
        let mut i = nominal(0, 0, 0, None);
        i.at_station = true;
        i.dwell_remaining_ms = 20_000;
        let out = ato_evaluate(&AtoState::default(), &i, &p);
        assert_eq!(out.mode, AtoMode::Dwelling);
    }

    #[test]
    fn station_approach_reduces_target_with_distance() {
        let p = params();
        let far = ato_evaluate(
            &AtoState::default(),
            &nominal(15_000, 22_000, 15_000, Some(500_000)),
            &p,
        );
        let close = ato_evaluate(
            &AtoState::default(),
            &nominal(15_000, 22_000, 15_000, Some(50_000)),
            &p,
        );
        assert!(close.effective_target_mmps < far.effective_target_mmps);
    }

    #[test]
    fn torque_and_brake_mutually_exclusive() {
        let p = params();
        // Sweep a range of current speeds against a mid target.
        for cur in (0..40_000).step_by(1_000) {
            let i = nominal(cur, 25_000, 20_000, None);
            let out = ato_evaluate(&AtoState::default(), &i, &p);
            assert!(
                !(out.torque_setpoint_mnm > 0 && out.service_brake_ppt > 0),
                "both non-zero at speed {cur}: torque {} brake {}",
                out.torque_setpoint_mnm,
                out.service_brake_ppt
            );
        }
    }

    #[test]
    fn determinism() {
        let p = params();
        let prev = AtoState::default();
        let i = nominal(12_500, 22_000, 15_000, Some(300_000));
        let a = ato_evaluate(&prev, &i, &p);
        let b = ato_evaluate(&prev, &i, &p);
        assert_eq!(a, b);
    }
}
