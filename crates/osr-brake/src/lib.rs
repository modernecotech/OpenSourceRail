//! OpenSourceRail electropneumatic brake controller.
//!
//! `osr-brake` is the safety-critical actuator layer that consumes
//! [`BrakeCommand`](osr_atp::BrakeCommand) from [`osr_atp`], takes the
//! union with emergency signals from all other SIL-4 monitors
//! ([`osr-vigilance`], [`osr-fire-safety`], [`osr-derailment`], and
//! the driver's emergency-brake plunger), and produces the actuator
//! setpoints for:
//!
//! - friction brake effort (service + emergency)
//! - regenerative brake request to the traction converter
//! - traction cut (motor power disable)
//! - parking brake engagement
//!
//! It also hosts **Wheel-Slide Protection (WSP)**: when the wheel-
//! speed sensor reports a wheel rotating slower than the train is
//! actually moving (detected by comparing against the odometer's
//! fused reference speed), WSP modulates friction *down* to let the
//! wheel spin up. WSP is strictly subtractive; it never increases
//! friction effort.
//!
//! This crate is **Phase 2a, crate 3** of RFC 0005. Together with
//! [`osr_atp`] and [`osr_odometry`] it closes the onboard safety
//! chain:
//!
//! ```text
//!   wayside MA → osr-atp (decides) → osr-brake (acts)
//!                      ▲
//!                      │
//!        osr-odometry (positions and speed)
//! ```
//!
//! # API shape
//!
//! The core API is a single pure function — [`brake_evaluate`] —
//! taking a snapshot of [`BrakeInputs`] and a fixed [`BrakeParams`]
//! configuration. It returns a [`BrakeOutput`] that the caller
//! applies to the pneumatic valve, the regen-torque bus, and the
//! traction-cut relay.
//!
//! # Safety properties (targeted)
//!
//! These anchor future Kani harnesses per RFC 0005 §7:
//!
//! - **B1 (determinism):** [`brake_evaluate`] is a pure function;
//!   identical inputs produce identical outputs.
//! - **B2 (emergency union):** if *any* emergency source is asserted
//!   — ATP, vigilance, fire, derailment, driver plunger — the
//!   output's `command` is `Emergency` and `emergency_sources`
//!   records every active source.
//! - **B3 (emergency completeness):** in an emergency, friction
//!   effort is ≥ [`BrakeParams::min_friction_emergency_ppt`] and
//!   traction is cut. Regen is requested at full availability but
//!   is not relied upon for the stop.
//! - **B4 (WSP conservative):** for every invocation,
//!   `friction_effort_ppt ≤ commanded_friction_before_wsp`; WSP
//!   never increases braking effort.
//! - **B5 (park safe):** `parking_brake_engaged = park_requested
//!   AND |speed| ≤ park_brake_max_speed_mmps`. The park brake is
//!   never released except by an explicit `park_requested = false`
//!   and is never engaged above the park threshold speed.
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//!
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only path (ppt = parts-per-thousand, mm/s, ns).
//! - No allocation in the evaluator.
//! - All public types `Debug + Clone + PartialEq`.

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod inputs;
pub mod output;

pub use evaluate::brake_evaluate;
pub use inputs::{BrakeInputs, BrakeParams};
pub use output::{BrakeOutput, EmergencySources};
