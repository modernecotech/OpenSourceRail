//! OpenSourceRail wayside power-switch (points) controller.
//!
//! This is the first wayside SIL-4 crate built against the real
//! `osr-consensus` log (RFC 0005 §4.6, Phase 2d crate 2). It runs on
//! a W-SBC next to a commodity BLDC point machine with dual
//! redundant position detectors, accepts [`SwitchCommand`] entries
//! from the committed log, drives the motor to the commanded
//! position, and emits [`SwitchObservation`] entries whenever the
//! detected position changes.
//!
//! # Hardware model (abstracted)
//!
//! ```text
//!              ┌──────────────────┐
//! commanded ──►│                  │
//! from        │  point controller│──► motor drive (fwd / rev / stop)
//! consensus   │                  │
//!             └───▲───▲──────────┘
//!                 │   │
//!     sensor A ───┘   └─── sensor B      (dual-redundant detectors)
//! ```
//!
//! Sensors are read on every tick. The controller fuses them
//! conservatively: any disagreement, any stuck sensor, any
//! out-of-range reading results in [`DetectedPosition::Unknown`] —
//! the fail-restrictive side of the safety argument.
//!
//! # API shape
//!
//! One pure function — [`switch_evaluate`] — takes the previous
//! [`SwitchState`], a [`SwitchInputs`] snapshot, and fixed
//! [`SwitchParams`]. It returns a [`SwitchOutput`] describing the
//! new state, the motor command to apply, and optionally a
//! `SwitchObservation` to publish on the consensus log.
//!
//! # Safety properties (targeted)
//!
//! - **W1 (determinism):** pure function of its inputs.
//! - **W2 (fail-restrictive detection):** if the two sensors
//!   disagree or either is missing/unknown, [`SwitchState::detected`]
//!   is [`DetectedPosition::Unknown`].
//! - **W3 (motor stops at target):** when `detected == commanded`,
//!   motor command is [`MotorCommand::Stop`].
//! - **W4 (motor times out):** a motor that has been driving for
//!   longer than [`SwitchParams::motor_timeout_ms`] is commanded
//!   [`MotorCommand::Stop`] and the controller enters a cooldown
//!   fault state (no new motor operations permitted until
//!   `motor_cooldown_ms` has elapsed).
//! - **W5 (motor never drives away):** if a commanded position
//!   exists and detected is *already* that position, the motor is
//!   never commanded in the opposite direction.
//! - **W6 (observation tracks detection):** the published
//!   `SwitchObservation` reflects the current fused detection at
//!   the time it is emitted.
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only path (ns, ms). No floats.
//! - All public types `Debug + Clone + PartialEq`.
//! - No allocation in the hot path.

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod inputs;
pub mod output;
pub mod types;

#[cfg(kani)]
pub mod kani_proofs;

pub use evaluate::switch_evaluate;
pub use inputs::{SwitchInputs, SwitchParams};
pub use output::{FaultReason, SwitchOutput, SwitchState};
pub use types::{CommandedPosition, DetectedPosition, MotorCommand, RawSensor};
