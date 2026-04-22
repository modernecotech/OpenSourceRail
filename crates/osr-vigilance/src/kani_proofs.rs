//! Kani bounded-model-checker harnesses for V1–V6.
//!
//! The vigilance evaluator is a pure transition function over two
//! integer inputs and a small parameter struct, so every property
//! can be discharged with a two-tick harness and no topology. The
//! same properties are asserted unbounded in
//! [`tests/proptest_vigilance.rs`](../../tests/proptest_vigilance.rs).
//!
//! # Running
//!
//! ```bash
//! cargo kani -p osr-vigilance
//! ```

#![cfg(kani)]

use crate::evaluate::vigilance_evaluate;
use crate::inputs::{VigilanceInputs, VigilanceParams};
use crate::output::{VigilanceOutput, VigilanceState};

// ---------------------------------------------------------------------------
// Scaffolding
// ---------------------------------------------------------------------------

/// Fixed parameters — the same as `VigilanceParams::light_metro_default()`.
/// Hard-coding them keeps the Kani state space tractable; the proptest
/// suite covers parameter variation unbounded.
fn params() -> VigilanceParams {
    VigilanceParams {
        ack_interval_ms: 30_000,
        warning_ms: 5_000,
        enable_speed_mmps: 1_000,
    }
}

fn arb_prev_state() -> VigilanceState {
    let s: u8 = kani::any();
    kani::assume(s < 4);
    match s {
        0 => VigilanceState::Suppressed,
        1 => VigilanceState::Nominal,
        2 => VigilanceState::Warning,
        _ => VigilanceState::Tripped,
    }
}

fn arb_prev() -> VigilanceOutput {
    let state = arb_prev_state();
    let last_ack_ns: u64 = kani::any();
    kani::assume(last_ack_ns <= 100_000_000_000); // 100 s; keeps arithmetic in range
    VigilanceOutput {
        state,
        emergency_requested: matches!(state, VigilanceState::Tripped),
        last_ack_ns,
        time_since_ack_ms: 0,
        time_to_warning_ms: None,
        time_to_trip_ms: None,
    }
}

fn arb_inputs() -> VigilanceInputs {
    let now_ns: u64 = kani::any();
    kani::assume(now_ns <= 200_000_000_000); // 200 s wall clock
    let speed_mmps: i32 = kani::any();
    kani::assume(speed_mmps.abs() <= 30_000); // ≤ 30 m/s
    VigilanceInputs {
        now_ns,
        speed_mmps,
        ack_received_this_tick: kani::any(),
    }
}

// ---------------------------------------------------------------------------
// V1 (determinism): same inputs → same output.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_v1_determinism() {
    let prev = arb_prev();
    let inputs = arb_inputs();
    let p = params();
    let a = vigilance_evaluate(&prev, &inputs, &p);
    let b = vigilance_evaluate(&prev, &inputs, &p);
    assert!(a == b);
}

// ---------------------------------------------------------------------------
// V2 (suppression): speed < enable_speed_mmps → Suppressed,
// emergency_requested == false.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_v2_suppressed_below_threshold() {
    let prev = arb_prev();
    let inputs = arb_inputs();
    // Force |speed| below the enable threshold.
    kani::assume(inputs.speed_mmps.unsigned_abs() < params().enable_speed_mmps);
    let p = params();
    let out = vigilance_evaluate(&prev, &inputs, &p);
    assert!(matches!(out.state, VigilanceState::Suppressed));
    assert!(!out.emergency_requested);
}

// ---------------------------------------------------------------------------
// V3 (warning precedes trip): from a Nominal prev, one tick cannot
// jump directly to Tripped if `now_ns - last_ack_ns` is a sane
// small increment. We express this as: starting from a prev with
// `state == Nominal` and `last_ack_ns` within the Nominal window
// (elapsed ≤ ack_interval_ms), a next tick with `now_ns` ≤
// `last_ack_ns + ack_interval_ms + warning_ms` (i.e. inside or just
// entering the Warning band) produces Nominal or Warning — never
// Tripped.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_v3_warning_precedes_trip() {
    let p = params();
    let last_ack_ns: u64 = kani::any();
    kani::assume(last_ack_ns <= 100_000_000_000);
    let prev = VigilanceOutput {
        state: VigilanceState::Nominal,
        emergency_requested: false,
        last_ack_ns,
        time_since_ack_ms: 0,
        time_to_warning_ms: None,
        time_to_trip_ms: None,
    };

    // Choose now_ns strictly inside [last_ack_ns, last_ack_ns + ack + warning],
    // so the computed elapsed time does not reach the Tripped band.
    let elapsed_ms: u32 = kani::any();
    kani::assume(elapsed_ms < p.ack_interval_ms + p.warning_ms);
    let now_ns = last_ack_ns.saturating_add(u64::from(elapsed_ms) * 1_000_000);

    let speed_mmps: i32 = kani::any();
    kani::assume(speed_mmps.unsigned_abs() >= p.enable_speed_mmps);
    kani::assume(speed_mmps.abs() <= 30_000);

    let inputs = VigilanceInputs {
        now_ns,
        speed_mmps,
        ack_received_this_tick: false,
    };
    let out = vigilance_evaluate(&prev, &inputs, &p);
    assert!(!matches!(out.state, VigilanceState::Tripped));
}

// ---------------------------------------------------------------------------
// V4 (tripped ⇔ emergency_requested).
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_v4_tripped_iff_emergency() {
    let prev = arb_prev();
    let inputs = arb_inputs();
    let out = vigilance_evaluate(&prev, &inputs, &params());
    let is_tripped = matches!(out.state, VigilanceState::Tripped);
    assert!(out.emergency_requested == is_tripped);
}

// ---------------------------------------------------------------------------
// V5 (in-window ack clears Warning → Nominal).
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_v5_warning_ack_returns_to_nominal() {
    let p = params();

    let last_ack_ns: u64 = kani::any();
    kani::assume(last_ack_ns <= 100_000_000_000);
    let prev = VigilanceOutput {
        state: VigilanceState::Warning,
        emergency_requested: false,
        last_ack_ns,
        time_since_ack_ms: 0,
        time_to_warning_ms: None,
        time_to_trip_ms: None,
    };

    // now_ns somewhere inside the warning window.
    let warning_offset_ms: u32 = kani::any();
    kani::assume(warning_offset_ms <= p.ack_interval_ms + p.warning_ms);
    kani::assume(warning_offset_ms >= p.ack_interval_ms);
    let now_ns = last_ack_ns.saturating_add(u64::from(warning_offset_ms) * 1_000_000);

    let speed_mmps: i32 = kani::any();
    kani::assume(speed_mmps.unsigned_abs() >= p.enable_speed_mmps);
    kani::assume(speed_mmps.abs() <= 30_000);

    let inputs = VigilanceInputs {
        now_ns,
        speed_mmps,
        ack_received_this_tick: true,
    };
    let out = vigilance_evaluate(&prev, &inputs, &p);
    assert!(matches!(out.state, VigilanceState::Nominal));
}

// ---------------------------------------------------------------------------
// V6 (trip latches): from a Tripped prev, any tick above the enable
// speed leaves the output Tripped, regardless of ack or elapsed time.
// ---------------------------------------------------------------------------

#[kani::proof]
fn kani_v6_trip_latches_above_enable_speed() {
    let p = params();
    let last_ack_ns: u64 = kani::any();
    kani::assume(last_ack_ns <= 100_000_000_000);
    let prev = VigilanceOutput {
        state: VigilanceState::Tripped,
        emergency_requested: true,
        last_ack_ns,
        time_since_ack_ms: 0,
        time_to_warning_ms: None,
        time_to_trip_ms: None,
    };

    let inputs = {
        let mut i = arb_inputs();
        // Keep the train above the enable speed so we don't fall into
        // the V2 branch (which intentionally clears Tripped once the
        // train is effectively at rest — a separate cab reset path).
        kani::assume(i.speed_mmps.unsigned_abs() >= p.enable_speed_mmps);
        i.now_ns = kani::any();
        kani::assume(i.now_ns <= 200_000_000_000);
        i
    };

    let out = vigilance_evaluate(&prev, &inputs, &p);
    assert!(matches!(out.state, VigilanceState::Tripped));
    assert!(out.emergency_requested);
}
