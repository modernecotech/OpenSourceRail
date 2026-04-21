//! Vigilance state machine and evaluator output.
//!
//! The state is latched by the caller between ticks: each
//! [`crate::vigilance_evaluate`] call consumes the previous
//! [`VigilanceOutput`] and produces the next. A default is provided
//! for the first tick.

use serde::{Deserialize, Serialize};

/// Vigilance state. See crate docs for the state-machine diagram.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub enum VigilanceState {
    /// Train below enable speed; vigilance inactive.
    #[default]
    Suppressed,
    /// Driver ack within interval; all good.
    Nominal,
    /// Ack overdue; cab buzzer active, driver has `warning_ms` to ack.
    Warning,
    /// Ack not received in warning window; emergency brake requested.
    Tripped,
}

/// One tick's worth of evaluator output. Carry this value across
/// ticks; the evaluator uses the previous output as the starting
/// state.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct VigilanceOutput {
    pub state: VigilanceState,
    /// Caller-facing emergency-brake request. Equivalent to
    /// `state == Tripped`.
    pub emergency_requested: bool,
    /// ns-since-epoch at which the most recent ack was registered.
    /// Zero before the first ack.
    pub last_ack_ns: u64,
    /// Time since last ack (or since initialisation) in ms at
    /// evaluation time. Useful for DMI display.
    pub time_since_ack_ms: u64,
    /// Time remaining before entering Warning, in ms. `None` once
    /// Warning has been entered or when Suppressed.
    pub time_to_warning_ms: Option<u32>,
    /// Time remaining before entering Tripped, in ms. `None` once
    /// Tripped or when Suppressed.
    pub time_to_trip_ms: Option<u32>,
}
