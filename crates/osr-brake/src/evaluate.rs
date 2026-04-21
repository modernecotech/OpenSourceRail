//! Top-level brake evaluator.
//!
//! [`brake_evaluate`] is the single public entry point. All decisions
//! are taken from immutable inputs; the function is pure.

use osr_atp::BrakeCommand;

use crate::inputs::{BrakeInputs, BrakeParams};
use crate::output::{BrakeOutput, EmergencySources};

/// Evaluate one brake tick.
///
/// Pure function. See the crate-level safety properties B1–B5 in
/// [`crate`] docs.
#[must_use]
pub fn brake_evaluate(inputs: &BrakeInputs, params: &BrakeParams) -> BrakeOutput {
    // 1. Resolve emergency sources.
    let sources = EmergencySources {
        atp: matches!(inputs.atp_command, BrakeCommand::Emergency),
        vigilance: inputs.vigilance_emergency,
        fire: inputs.fire_emergency,
        derailment: inputs.derailment_emergency,
        driver: inputs.driver_emergency,
    };

    // 2. In emergency, produce a full-brake output (B3).
    if sources.any() {
        return emergency_output(inputs, params, sources);
    }

    // 3. Nominal service path.
    let service_ppt: u16 = match inputs.atp_command {
        BrakeCommand::Release => 0,
        BrakeCommand::Service(p) => p.min(1000),
        BrakeCommand::Emergency => unreachable!("emergency handled above"),
    };

    // 4. Blend regen + friction for the service demand.
    let (regen_request_ppt, friction_command) =
        blend_service(service_ppt, inputs.regen_available_ppt, params);

    // 5. WSP modulation on friction only (B4).
    let (friction_effort_ppt, wsp_active) =
        wsp_modulate(friction_command, inputs, params);

    // 6. Park brake (B5).
    let parking_brake_engaged = inputs.park_requested
        && inputs.measured_speed_mmps.unsigned_abs()
            <= params.park_brake_max_speed_mmps.unsigned_abs();

    // 7. Traction cut whenever the brake is active in any form.
    let traction_cut = !matches!(inputs.atp_command, BrakeCommand::Release)
        || wsp_active
        || parking_brake_engaged;

    BrakeOutput {
        command: inputs.atp_command,
        friction_effort_ppt,
        regen_request_ppt,
        traction_cut,
        parking_brake_engaged,
        wsp_active,
        emergency_sources: sources,
        friction_command_before_wsp_ppt: friction_command,
    }
}

fn emergency_output(
    inputs: &BrakeInputs,
    params: &BrakeParams,
    sources: EmergencySources,
) -> BrakeOutput {
    let friction_command = params.min_friction_emergency_ppt.min(1000).max(1000);
    // WSP is allowed to modulate even in emergency — otherwise a
    // slide would lock the wheel and prolong the stopping distance.
    // But WSP must still be subtractive; the floor is
    // `min_friction_emergency_ppt` minus the maximum modulation.
    let (friction_effort_ppt, wsp_active) =
        wsp_modulate(friction_command, inputs, params);

    let parking_brake_engaged = inputs.park_requested
        && inputs.measured_speed_mmps.unsigned_abs()
            <= params.park_brake_max_speed_mmps.unsigned_abs();

    BrakeOutput {
        command: BrakeCommand::Emergency,
        friction_effort_ppt,
        // Regen is requested at full availability but the safety case
        // does not depend on it.
        regen_request_ppt: inputs.regen_available_ppt.min(1000),
        traction_cut: true,
        parking_brake_engaged,
        wsp_active,
        emergency_sources: sources,
        friction_command_before_wsp_ppt: friction_command,
    }
}

/// Split a service-brake demand across regen and friction.
///
/// Returns `(regen_request_ppt, friction_command_ppt)`. When
/// `regen_priority` is enabled, regen is satisfied first up to the
/// converter's availability; any shortfall comes from friction.
fn blend_service(demand_ppt: u16, regen_available_ppt: u16, params: &BrakeParams) -> (u16, u16) {
    let demand = demand_ppt.min(1000);
    let regen_avail = regen_available_ppt.min(1000);
    if !params.regen_priority {
        return (0, demand);
    }
    let regen = demand.min(regen_avail);
    let friction = demand.saturating_sub(regen);
    (regen, friction)
}

/// Apply wheel-slide-protection modulation.
///
/// Slide is detected when the wheel is rotating slower than the
/// train's reference speed by more than the threshold. Only the
/// friction effort is modulated — regen is a torque request to the
/// converter, which has its own anti-slip in `osr-traction`. WSP is
/// strictly subtractive (B4).
fn wsp_modulate(
    friction_command_ppt: u16,
    inputs: &BrakeInputs,
    params: &BrakeParams,
) -> (u16, bool) {
    if !params.wsp_enabled {
        return (friction_command_ppt, false);
    }
    // Slide amount on the signed axis the train is moving.
    let ref_speed_abs = inputs.measured_speed_mmps.unsigned_abs();
    let wheel_speed_abs = inputs.wheel_speed_mmps.unsigned_abs();
    let slide_mmps = ref_speed_abs.saturating_sub(wheel_speed_abs) as i32;
    let slide_detected =
        slide_mmps >= params.wsp_slide_threshold_mmps.max(1);

    if !slide_detected {
        return (friction_command_ppt, false);
    }

    // Reduce the commanded friction by `wsp_reduction_ppt` ppt of
    // the maximum (not a fraction of the commanded effort). This
    // preserves monotonicity: higher commanded → higher actual.
    let reduction = u32::from(params.wsp_reduction_ppt.min(1000));
    let reduced = u32::from(friction_command_ppt).saturating_sub(reduction) as u16;
    (reduced, true)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::inputs::{BrakeInputs, BrakeParams};

    fn nominal_inputs() -> BrakeInputs {
        BrakeInputs {
            atp_command: BrakeCommand::Release,
            vigilance_emergency: false,
            fire_emergency: false,
            derailment_emergency: false,
            driver_emergency: false,
            park_requested: false,
            measured_speed_mmps: 10_000,
            wheel_speed_mmps: 10_000,
            regen_available_ppt: 800,
            now_ns: 1_000_000_000,
        }
    }

    #[test]
    fn release_emits_nothing() {
        let i = nominal_inputs();
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.is_release());
        assert_eq!(out.friction_effort_ppt, 0);
        assert_eq!(out.regen_request_ppt, 0);
        assert!(!out.traction_cut);
        assert!(!out.wsp_active);
        assert!(!out.parking_brake_engaged);
    }

    #[test]
    fn service_blends_regen_first() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Service(500);
        i.regen_available_ppt = 300;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.is_service());
        assert_eq!(out.regen_request_ppt, 300);
        assert_eq!(out.friction_effort_ppt, 200);
        assert!(out.traction_cut);
    }

    #[test]
    fn service_regen_unavailable_uses_friction() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Service(700);
        i.regen_available_ppt = 0;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert_eq!(out.regen_request_ppt, 0);
        assert_eq!(out.friction_effort_ppt, 700);
    }

    #[test]
    fn atp_emergency_trips() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Emergency;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.is_emergency());
        assert!(out.friction_effort_ppt >= p.min_friction_emergency_ppt.saturating_sub(p.wsp_reduction_ppt));
        assert!(out.traction_cut);
        assert!(out.emergency_sources.atp);
    }

    #[test]
    fn vigilance_alone_trips() {
        let mut i = nominal_inputs();
        i.vigilance_emergency = true;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.is_emergency());
        assert!(out.emergency_sources.vigilance);
        assert!(!out.emergency_sources.atp);
    }

    #[test]
    fn fire_alone_trips() {
        let mut i = nominal_inputs();
        i.fire_emergency = true;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.is_emergency());
        assert!(out.emergency_sources.fire);
    }

    #[test]
    fn multiple_sources_all_recorded() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Emergency;
        i.vigilance_emergency = true;
        i.derailment_emergency = true;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert_eq!(out.emergency_sources.count(), 3);
    }

    #[test]
    fn wsp_activates_on_slide_and_subtracts() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Service(800);
        i.measured_speed_mmps = 10_000;
        i.wheel_speed_mmps = 5_000; // 5 m/s deficit
        i.regen_available_ppt = 0;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.wsp_active);
        assert_eq!(out.friction_command_before_wsp_ppt, 800);
        assert!(out.friction_effort_ppt < 800, "WSP did not subtract: {out:?}");
        assert_eq!(out.friction_effort_ppt, 800 - p.wsp_reduction_ppt);
    }

    #[test]
    fn wsp_disabled_passes_through() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Service(500);
        i.measured_speed_mmps = 10_000;
        i.wheel_speed_mmps = 0;
        i.regen_available_ppt = 0;
        let mut p = BrakeParams::light_metro_default();
        p.wsp_enabled = false;
        let out = brake_evaluate(&i, &p);
        assert!(!out.wsp_active);
        assert_eq!(out.friction_effort_ppt, 500);
    }

    #[test]
    fn park_only_below_threshold() {
        let mut i = nominal_inputs();
        i.park_requested = true;
        // Above threshold: don't engage.
        i.measured_speed_mmps = 500;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(!out.parking_brake_engaged);

        // Below threshold: engage.
        i.measured_speed_mmps = 100;
        let out = brake_evaluate(&i, &p);
        assert!(out.parking_brake_engaged);
    }

    #[test]
    fn park_not_requested_never_engaged() {
        let mut i = nominal_inputs();
        i.park_requested = false;
        i.measured_speed_mmps = 0;
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(!out.parking_brake_engaged);
    }

    #[test]
    fn service_mode_cuts_traction() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Service(100);
        let p = BrakeParams::light_metro_default();
        let out = brake_evaluate(&i, &p);
        assert!(out.traction_cut);
    }

    #[test]
    fn determinism() {
        let mut i = nominal_inputs();
        i.atp_command = BrakeCommand::Service(400);
        i.regen_available_ppt = 300;
        let p = BrakeParams::light_metro_default();
        let a = brake_evaluate(&i, &p);
        let b = brake_evaluate(&i, &p);
        assert_eq!(a, b);
    }
}
