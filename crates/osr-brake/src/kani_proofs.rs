//! Kani bounded-model-checker harnesses for B1–B5.
//!
//! `brake_evaluate` is a pure function over an integer-only input
//! struct, so every property discharges without a topology walk.
//! Running:
//!
//! ```bash
//! cargo kani -p osr-brake
//! ```

#![cfg(kani)]

use osr_atp::BrakeCommand;

use crate::evaluate::brake_evaluate;
use crate::inputs::{BrakeInputs, BrakeParams};

fn params() -> BrakeParams {
    BrakeParams {
        wsp_enabled: true,
        wsp_slide_threshold_mmps: 500,
        wsp_reduction_ppt: 400,
        park_brake_max_speed_mmps: 200,
        regen_priority: true,
        min_friction_emergency_ppt: 1_000,
    }
}

fn arb_command() -> BrakeCommand {
    let tag: u8 = kani::any();
    kani::assume(tag < 3);
    match tag {
        0 => BrakeCommand::Release,
        1 => {
            let ppt: u16 = kani::any();
            kani::assume(ppt <= 1_000);
            BrakeCommand::Service(ppt)
        }
        _ => BrakeCommand::Emergency,
    }
}

fn arb_inputs() -> BrakeInputs {
    let measured_speed_mmps: i32 = kani::any();
    kani::assume(measured_speed_mmps.abs() <= 30_000);
    let wheel_speed_mmps: i32 = kani::any();
    kani::assume(wheel_speed_mmps.abs() <= 30_000);
    let regen_available_ppt: u16 = kani::any();
    kani::assume(regen_available_ppt <= 1_000);
    BrakeInputs {
        atp_command: arb_command(),
        vigilance_emergency: kani::any(),
        fire_emergency: kani::any(),
        derailment_emergency: kani::any(),
        driver_emergency: kani::any(),
        obstacle_emergency: kani::any(),
        park_requested: kani::any(),
        measured_speed_mmps,
        wheel_speed_mmps,
        regen_available_ppt,
        now_ns: 0,
    }
}

// ---------------------------------------------------------------------------
// B1 (determinism): same inputs → same output.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_b1_determinism() {
    let i = arb_inputs();
    let p = params();
    let a = brake_evaluate(&i, &p);
    let b = brake_evaluate(&i, &p);
    assert!(a == b);
}

// ---------------------------------------------------------------------------
// B2 (emergency union): if any source is asserted, command is
// Emergency and every active source is recorded.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_b2_emergency_union() {
    let i = arb_inputs();
    let p = params();
    let out = brake_evaluate(&i, &p);

    let any_source = matches!(i.atp_command, BrakeCommand::Emergency)
        || i.vigilance_emergency
        || i.fire_emergency
        || i.derailment_emergency
        || i.driver_emergency;

    if any_source {
        assert!(matches!(out.command, BrakeCommand::Emergency));
    }
    assert!(
        out.emergency_sources.atp == matches!(i.atp_command, BrakeCommand::Emergency)
    );
    assert!(out.emergency_sources.vigilance == i.vigilance_emergency);
    assert!(out.emergency_sources.fire == i.fire_emergency);
    assert!(out.emergency_sources.derailment == i.derailment_emergency);
    assert!(out.emergency_sources.driver == i.driver_emergency);
}

// ---------------------------------------------------------------------------
// B3 (emergency completeness): when Emergency, friction floor is
// `min_friction_emergency_ppt - wsp_reduction_ppt` (WSP is allowed
// to subtract even in emergency) and traction is cut.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_b3_emergency_completeness() {
    let mut i = arb_inputs();
    // Force Emergency via driver plunger so the other fields stay
    // symbolic.
    i.driver_emergency = true;
    let p = params();
    let out = brake_evaluate(&i, &p);

    assert!(matches!(out.command, BrakeCommand::Emergency));
    let floor = p.min_friction_emergency_ppt.saturating_sub(p.wsp_reduction_ppt);
    assert!(out.friction_effort_ppt >= floor);
    assert!(out.traction_cut);
}

// ---------------------------------------------------------------------------
// B4 (WSP conservative): WSP never increases commanded friction.
// `friction_effort_ppt ≤ friction_command_before_wsp_ppt` on every
// invocation.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_b4_wsp_conservative() {
    let i = arb_inputs();
    let p = params();
    let out = brake_evaluate(&i, &p);
    assert!(out.friction_effort_ppt <= out.friction_command_before_wsp_ppt);
}

// ---------------------------------------------------------------------------
// B5 (park safe): parking_brake_engaged ⇔ park_requested AND
// |speed| ≤ park_brake_max_speed_mmps.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_b5_park_safe() {
    let i = arb_inputs();
    let p = params();
    let out = brake_evaluate(&i, &p);

    let below_threshold = i.measured_speed_mmps.unsigned_abs()
        <= p.park_brake_max_speed_mmps.unsigned_abs();
    let expected = i.park_requested && below_threshold;
    assert!(out.parking_brake_engaged == expected);
}
