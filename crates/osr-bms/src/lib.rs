//! OpenSourceRail onboard Battery Management System (BMS).
//!
//! `osr-bms` is the SIL-4 controller for the traction pack. Per
//! [RFC 0002](../../../docs/rfcs/0002-energy-sizing.md) the reference
//! chemistry is sodium-ion (LFP as a space-constrained alternative).
//! This crate is **Phase 2b, crate 1** of
//! [RFC 0005 §11](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # What the BMS decides each tick
//!
//! - **Pack State of Charge (SoC)** via Coulomb counting of pack
//!   current. Returned in parts-per-thousand (0…1000). SoH is a stub
//!   in v1; degradation modelling is future work.
//! - **Contactor state** — `Closed` under nominal operation; forced
//!   to `OpenFault` (latched, cooldown-gated) on any hard fault.
//! - **Charge / discharge current limits** — derated from the pack
//!   maximum by the worst-cell margin to the voltage and temperature
//!   windows. Consumers ([`osr-traction`], the charge controller at
//!   station pads) must clamp their requests to these.
//! - **Faults** (over-voltage, under-voltage, over-temperature,
//!   under-temperature, imbalance) — latched and exposed via a
//!   [`FaultMask`]; clear only via cooldown expiry.
//!
//! # API shape
//!
//! A single pure function [`bms_evaluate`]. Caller holds the
//! [`BmsState`] across ticks. All I/O (reading cell ADCs, commanding
//! the contactor coil, driving balancing shunts) is delegated.
//!
//! # Safety properties (targeted)
//!
//! Proptest-verified today; candidate Kani harnesses per RFC 0005 §7.
//!
//! - **M1 (determinism):** [`bms_evaluate`] is a pure function.
//! - **M2 (hard fault opens contactor):** any fault in the
//!   `trip` set forces `ContactorState::OpenFault` this tick.
//! - **M3 (fault latches through cooldown):** once `OpenFault`, the
//!   contactor stays open for at least `fault_cooldown_ms`.
//! - **M4 (derating is conservative):** if a cell's margin to any
//!   limit is narrow, the corresponding charge / discharge limit is
//!   ≤ the nominal pack limit (never exceeds it).
//! - **M5 (SoC bounds):** `soc_ppt ∈ [0, 1000]` every tick.
//! - **M6 (contactor open implies zero-current limits):** when
//!   `contactor != Closed`, both charge and discharge limits are 0.
//!
//! # Coding-standard compliance
//!
//! Per RFC 0005 §7 (SIL-4):
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only path (mV, dC ≡ tenths of °C, mA, ns, ppt).
//! - No allocation in the hot path (cell slices are caller-owned).
//! - All public types `Debug + Clone + PartialEq` (FaultMask uses `Eq`).

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod inputs;
pub mod output;
pub mod types;

pub use evaluate::bms_evaluate;
pub use inputs::{BmsInputs, BmsParams, ContactorCommand};
pub use output::{AlarmLevel, BmsOutput, BmsState, FaultMask};
pub use types::{Chemistry, ContactorState, FaultReason};
