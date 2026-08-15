//! OpenSourceRail Automatic Train Operation (ATO).
//!
//! `osr-ato` closes the onboard control-loop triangle: [`osr_atp`]
//! computes the safe speed envelope; `osr-ato` decides how to drive
//! the train *within* that envelope toward schedule targets, producing
//! torque setpoints for [`osr_traction`] and service-brake levels for
//! [`osr_brake`].
//!
//! This is **Phase 2b, crate 3** of
//! [RFC 0005](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # SIL-2, not SIL-4
//!
//! `osr-ato` is SIL-2 because ATP bounds any safety-critical outcome:
//! if ATO commands too much torque, ATP's brake-apply still stops the
//! train short of any obstacle. ATO "failing" means bad ride quality,
//! missed schedule, or inefficient driving — never unsafe motion.
//!
//! Conceptually this crate is comfort + efficiency; the SIL-4 safety
//! partition (ATP + brake + fire-safety + derailment) is
//! what protects life.
//!
//! # What each tick decides
//!
//! Given:
//! - current train speed (from `osr-odometry`)
//! - ATP envelope speed (from `osr-atp`)
//! - cruise target speed (schedule-derived)
//! - distance to next station stop (if one is in range)
//! - `ato_engaged` flag (driver's AUTO/MANUAL switch)
//!
//! `ato_evaluate` produces:
//! - torque setpoint for `osr-traction` (signed mN·m)
//! - service-brake effort for `osr-brake` (0..=1000 ppt)
//! - a diagnostic `AtoMode` (Accelerating / Cruising / Coasting /
//!   Braking / StationApproach / Stopped / Dwelling / Off)
//!
//! # Control law
//!
//! A classical PI controller on `speed_error = target - current`, with
//! target itself being the minimum of:
//! - the schedule cruise target,
//! - the quadratic station-approach profile
//!   `v_approach(d) = sqrt(2 · a_target · d)`, and
//! - `envelope - envelope_margin` (stay clear of the ATP trip band).
//!
//! The PI output is interpreted as a signed torque / brake demand:
//! positive → traction; negative → service brake proportional to
//! magnitude.
//!
//! Station stop: when `at_station && |speed| ≤ stop_tolerance`, a
//! holding brake is applied and torque is zeroed. Dwell timing is
//! external (the vehicle controller or schedule module drives the
//! `dwell_remaining_ms` input).
//!
//! # Safety properties (proptest-verified)
//!
//! - **AO1 determinism:** pure function.
//! - **AO2 mutual exclusion:** never commands positive torque AND
//!   non-zero service brake on the same tick.
//! - **AO3 envelope respected:** the internal effective target is
//!   ≤ `envelope_mmps - envelope_margin_mmps` (capped at 0).
//! - **AO4 disengaged is safe:** when `ato_engaged == false`,
//!   torque = 0 and brake = 0 (the human driver has full authority).
//! - **AO5 at-platform holding brake:** when `at_station` and
//!   `|current_speed| ≤ stop_tolerance_mmps`, service brake is
//!   ≥ `holding_brake_ppt` and torque is 0.
//! - **AO6 torque bounded:** `|torque| ≤ max_torque_mnm`.
//! - **AO7 brake bounded:** `brake_ppt ∈ [0, max_service_brake_ppt]`.
//! - **AO8 overspeed → no positive torque:** if
//!   `current_speed > envelope`, torque ≤ 0.
//!
//! # Coding-standard compliance
//!
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only (mm/s, mN·m, ppt, ns).
//! - No allocation.

#![forbid(unsafe_code)]

pub mod envelope;
pub mod evaluate;
pub mod inputs;
pub mod output;
pub mod types;

pub use envelope::station_approach_speed_mmps;
pub use evaluate::ato_evaluate;
pub use inputs::{AtoInputs, AtoParams};
pub use output::{AtoOutput, AtoState};
pub use types::AtoMode;
