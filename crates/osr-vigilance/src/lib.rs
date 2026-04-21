//! OpenSourceRail driver alerter / dead-man controller ("vigilance").
//!
//! The vigilance system is the classic rail "dead-man's switch":
//! while the train is moving above a low-speed threshold, the driver
//! must periodically acknowledge that they are alert and in control.
//! Failure to acknowledge within a configured window triggers an
//! emergency brake application via the [O4 brake-apply
//! topic](../../../docs/rfcs/0005-sbc-software-architecture.md#6-interface-contracts).
//!
//! This crate is **Phase 2a, crate 4** of RFC 0005 — the smallest of
//! the SIL-4 onboard monitors. Its output is a single bool
//! (`emergency_requested`) that [`osr_brake::BrakeInputs::vigilance_emergency`]
//! consumes.
//!
//! # State machine
//!
//! ```text
//!     Suppressed  ─── speed ≥ enable threshold ───→  Nominal
//!            ▲                                        │
//!            │                                        │ elapsed > ack_interval
//!            └─── speed < enable threshold ───┐       ▼
//!                                             │    Warning
//!                                             │       │
//!                             ack in time ────┘       │ elapsed > ack_interval + warning
//!                                                     ▼
//!                                                  Tripped
//!                                                     │
//!                                     (no exit — brake applied; reset via
//!                                      separate cab procedure out of scope)
//! ```
//!
//! - **Suppressed.** Train is below the low-speed enable threshold
//!   (typically 1 m/s — "effectively at rest"). Vigilance is
//!   disabled to avoid nuisance alarms while dwelling at a platform.
//! - **Nominal.** Train is above the threshold; last ack was within
//!   `ack_interval_ms`.
//! - **Warning.** Above threshold; no ack for more than
//!   `ack_interval_ms`. A cab buzzer sounds and the driver has
//!   `warning_ms` to ack before the next state.
//! - **Tripped.** Above threshold; no ack within
//!   `ack_interval_ms + warning_ms`. Emergency brake is requested.
//!   The trip latches — a subsequent ack does *not* return the
//!   state to Nominal; resetting after a vigilance trip is a
//!   separate cab procedure (powered reset with the train at rest),
//!   out of scope for this crate.
//!
//! ATO engagement replaces the driver as the ack source: if the ATO
//! is driving (GoA 2–4), it asserts
//! [`VigilanceInputs::ack_received_this_tick`] on the configured
//! cadence automatically.
//!
//! # Safety properties (targeted)
//!
//! Candidates for future Kani harnesses per RFC 0005 §7.
//!
//! - **V1 (determinism):** [`vigilance_evaluate`] is a pure
//!   function of `(prev, inputs, params)`.
//! - **V2 (suppression under threshold):** if
//!   `speed_mmps.unsigned_abs() < params.enable_speed_mmps` the
//!   output is always `Suppressed` with
//!   `emergency_requested == false`, regardless of elapsed time.
//! - **V3 (warning precedes trip):** `Tripped` is reachable only
//!   from `Warning`. There is no direct `Nominal → Tripped` edge;
//!   any timeline that reaches `Tripped` passes through `Warning`.
//! - **V4 (trip is emergency):** `state == Tripped ⇔
//!   emergency_requested == true`.
//! - **V5 (in-window ack clears):** while in `Warning`, a tick
//!   with `ack_received_this_tick == true` returns state to
//!   `Nominal`. Ack has no effect on `Tripped`.
//! - **V6 (trip latches):** once `Tripped`, no input can make the
//!   next state `Nominal` or `Warning` — only `Tripped` persists
//!   (or `Suppressed` if the train drops below the enable speed).
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only path (ms, ns, mm/s).
//! - No allocation.

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod inputs;
pub mod output;

pub use evaluate::vigilance_evaluate;
pub use inputs::{VigilanceInputs, VigilanceParams};
pub use output::{VigilanceOutput, VigilanceState};
