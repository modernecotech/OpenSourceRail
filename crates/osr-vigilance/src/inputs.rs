//! Inputs and parameters for the vigilance evaluator.

use serde::{Deserialize, Serialize};

/// Per-tick vigilance inputs.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct VigilanceInputs {
    /// Current time (ns since an arbitrary reference). Used to
    /// compute elapsed time since last ack.
    pub now_ns: u64,
    /// Measured train speed, mm/s. Used only in magnitude for the
    /// enable-threshold check.
    pub speed_mmps: i32,
    /// `true` if the driver or ATO asserted acknowledgement on this
    /// tick. Latching is handled by the evaluator — callers pass
    /// `true` only on the tick the ack event arrived.
    pub ack_received_this_tick: bool,
}

/// Configuration of the vigilance controller. Constant per train;
/// loaded from the consist's commissioning record.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct VigilanceParams {
    /// Maximum allowed gap between acks, in milliseconds, before the
    /// Warning state engages. Typical 30 000 ms (30 s).
    pub ack_interval_ms: u32,
    /// Duration of the Warning state, in milliseconds, before
    /// escalating to Tripped. Typical 5 000 ms.
    pub warning_ms: u32,
    /// Speed below which vigilance is suppressed, in mm/s. Typical
    /// 1 000 mm/s (1 m/s). Setting to 0 disables suppression.
    pub enable_speed_mmps: u32,
}

impl VigilanceParams {
    /// Reasonable defaults for a light-metro trainset.
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            ack_interval_ms: 30_000,
            warning_ms: 5_000,
            enable_speed_mmps: 1_000,
        }
    }
}
