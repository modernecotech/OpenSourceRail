//! OpenSourceRail SIL-4 Interlocking.
//!
//! This crate implements the rail state machine described in
//! [RFC 0001 §7](../../docs/rfcs/0001-track-state-consensus.md), per the
//! implementation plan in
//! [RFC 0004](../../docs/rfcs/0004-osr-interlocking-plan.md).
//!
//! **Current milestone: M1 — types, log, and `derive_state`.**
//!
//! The MA computer itself lands in M2. Until then this crate exposes:
//! - The full `Entry` schema (mirror of `track_state.proto`).
//! - A `DerivedState` aggregating the committed log prefix.
//! - A pure `derive_state` function with proptest-verified determinism.
//!
//! The safety-critical style conventions from RFC 0004 apply:
//! - No `unsafe` (workspace-level `unsafe_code = "forbid"` in `Cargo.toml`).
//! - Integer units in the safety path (mm, mm/s, ns, Wh); floats only at
//!   sensor-input boundaries.
//! - All public types implement `Debug + Clone + PartialEq` for test
//!   ergonomics and determinism proofs.

pub mod log;
pub mod ma;
pub mod state;
pub mod topology;

pub use log::{
    Confidence, Entry, EntryPayload, FormatVersion, Heartbeat, MaintenanceOverride,
    PositionSource, RestrictionReason, RouteGrant, RouteRelease, RouteRequest,
    SpeedRestriction, SwitchCommand, SwitchObservation, SwitchPosition,
    TrainDeparture, TrainPositionReport, TrainRegistration,
};
pub use ma::{
    compute_self_ma, compute_self_ma_from_state, section_available_to, MovementAuthority,
    MAX_MA_DISTANCE_MM, MA_VALIDITY_WINDOW_NS,
};
pub use state::{DerivedState, SwitchState, TrainAwareness, derive_state};
pub use topology::{footprint_from, forward_chain, far_end_of};
