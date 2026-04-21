//! OpenSourceRail VVVF traction supervisor.
//!
//! `osr-traction` is the SIL-4 coordination layer that sits between
//! the high-level torque demand (from [`osr_ato`] or the brake crate
//! during regen) and the low-level FOC firmware running on the
//! inverter's SiC drive chip. Per [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md)
//! this is **Phase 2b, crate 2**.
//!
//! The field-oriented control math itself — d-q transforms, PLL,
//! PWM generation — lives on the drive electronics and is out of
//! scope for this Rust crate. What [`traction_evaluate`] does is:
//!
//! 1. Accept a torque setpoint and current [`osr_bms`] limits
//!    (charge / discharge, contactor state).
//! 2. Clamp the torque to what the pack will physically allow.
//! 3. Detect wheel slip (driving wheel faster than reference body
//!    speed) and slide (driving wheel slower) — reduce or zero
//!    torque on detection. True WSP during service / emergency
//!    braking is owned by `osr-brake`; here we cover the *traction*
//!    side, i.e. loss of adhesion under motor torque.
//! 4. Gate the inverter: enable only when BMS contactor is closed,
//!    no thermal / drive faults, and an explicit enable request is
//!    present.
//! 5. Produce a pack-current estimate that [`osr_bms`] uses as
//!    pre-knowledge of the load.
//!
//! # API shape
//!
//! One pure function — [`traction_evaluate`] — taking the previous
//! [`TractionState`], a [`TractionInputs`] snapshot, and fixed
//! [`TractionParams`]. Returns a [`TractionOutput`] describing the
//! new state, the torque command to forward to the drive, the
//! inverter-enable signal, and the estimated pack current.
//!
//! # Safety properties (targeted, proptest-verified)
//!
//! - **TR1 (determinism):** pure function.
//! - **TR2 (pack-limit clamping):** `estimated_current_ma` never
//!   exceeds BMS limits in magnitude (discharge limit for +current,
//!   charge limit for −current).
//! - **TR3 (anti-slip never adds torque):**
//!   `|commanded_torque_mnm| ≤ |torque_setpoint_mnm|` always.
//! - **TR4 (inverter off without contactor):** if
//!   `bms_contactor_closed == false`, inverter is `Disabled` and
//!   `commanded_torque_mnm == 0`.
//! - **TR5 (fault disables inverter):** any inverter over-temp or
//!   drive-fault forces `Faulted` (latched) with zero torque.
//! - **TR6 (torque sign consistent with current):** positive torque
//!   implies `estimated_current_ma ≥ 0` (discharge); negative torque
//!   implies `≤ 0` (regen / charge).
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only path (mN·m, mA, mV, mm/s, ns, ppt).
//! - All public types `Debug + Clone + PartialEq`.
//! - No allocation.

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod inputs;
pub mod output;
pub mod types;

pub use evaluate::traction_evaluate;
pub use inputs::{TractionInputs, TractionParams};
pub use output::{TractionOutput, TractionState};
pub use types::{FaultReason, InverterState};
