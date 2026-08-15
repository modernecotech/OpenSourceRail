//! OpenSourceRail onboard Automatic Train Protection (ATP).
//!
//! ATP is the safety-critical enforcement layer on the train. It
//! receives a [`MovementAuthority`] computed by the wayside
//! `osr-interlocking` crate and, against the train's measured state,
//! decides one of three outcomes every tick:
//!
//! 1. [`BrakeCommand::Release`] — the train is within its safe envelope;
//!    no brake application is required.
//! 2. [`BrakeCommand::Service`] — the train is approaching the envelope;
//!    service brake is applied, proportional to the gap.
//! 3. [`BrakeCommand::Emergency`] — the envelope is breached (or the MA
//!    is no longer valid); emergency brake is commanded.
//!
//! The core API is a single pure function — [`atp_evaluate`] — taking
//! an immutable snapshot of inputs and returning an [`AtpOutcome`].
//! All I/O (reading odometry, commanding the brake bus) is delegated
//! to the caller. This keeps the safety-critical logic free of any
//! runtime coupling and amenable to exhaustive testing and future
//! Kani harnesses.
//!
//! This crate is **Phase 2a, crate 1** of RFC 0005 — the first
//! onboard SBC crate. It is the dual to `osr-interlocking`: the
//! interlocking decides *what is allowed*; ATP enforces *what actually
//! happens* on the train.
//!
//! # Safety properties (targeted)
//!
//! These properties anchor future Kani harnesses. None are
//! formally verified yet; all are exercised by proptests and unit
//! tests under `tests/`.
//!
//! - **A1 (determinism):** `atp_evaluate` is a pure function. Same
//!   inputs → byte-identical output.
//! - **A2 (expired MA trips):** if `now_ns >= ma.valid_until_ns` the
//!   outcome is [`BrakeCommand::Emergency`].
//! - **A3 (unknown position trips):** if `!ma.has_known_position` the
//!   outcome is [`BrakeCommand::Emergency`].
//! - **A4 (train mismatch trips):** if `ma.train_id != state.train_id`
//!   the outcome is [`BrakeCommand::Emergency`].
//! - **A5 (head past MA end trips):** if the head's forward distance
//!   to the MA end is ≤ 0 the outcome is [`BrakeCommand::Emergency`].
//! - **A6 (overspeed trips):** if measured speed + speed uncertainty
//!   exceeds the envelope by more than
//!   [`OVERSPEED_EMERGENCY_MARGIN_MMPS`] the outcome is
//!   [`BrakeCommand::Emergency`].
//! - **A7 (conservatism):** widening any uncertainty or shortening
//!   the MA never moves the outcome in the less-restrictive direction
//!   (Release → Service → Emergency is a total order on severity).
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7, this crate follows the SIL-4 conventions:
//!
//! - `#![forbid(unsafe_code)]` at crate root (workspace already forbids
//!   it; repeated here for clarity).
//! - Integer-only safety path: millimetres, millimetres-per-second,
//!   milliseconds, nanoseconds. The one float boundary is the
//!   conversion of [`BrakingCurve`] to [`DecelTable`] at construction
//!   time, which rounds deceleration *down* to the nearest integer
//!   mm/s² (safe-side rounding).
//! - All public types `Debug + Clone + PartialEq`.
//! - No allocation on the hot path (`atp_evaluate` allocates only for
//!   the forward-chain walk, which is bounded by
//!   [`osr_interlocking::MAX_MA_DISTANCE_MM`]).
//!
//! `no_std` support is deferred: this crate follows the workspace
//! convention set by `osr-interlocking` (std-dependent, `alloc` not
//! feature-gated). Migration across the SIL-4 partition is a
//! single-step future change, not a piecemeal per-crate effort.

#![forbid(unsafe_code)]

pub mod envelope;
pub mod evaluate;
pub mod state;

// Kani bounded-model-checker harnesses. Gated by `#[cfg(kani)]` so
// they compile only when `cargo kani` is driving the build and are
// invisible to plain `cargo test`.
#[cfg(kani)]
pub mod kani_proofs;

pub use envelope::{isqrt, max_safe_speed_mmps, DecelTable};
pub use evaluate::{
    atp_evaluate, AtpOutcome, BrakeCommand, TriggerReason, OVERSPEED_EMERGENCY_MARGIN_MMPS,
    SERVICE_BRAKE_MARGIN_MMPS,
};
pub use state::TrainState;
