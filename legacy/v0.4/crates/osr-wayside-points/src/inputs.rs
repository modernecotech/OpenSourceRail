//! Inputs and calibration for the points controller.

use serde::{Deserialize, Serialize};

use crate::types::{CommandedPosition, RawSensor};

/// Per-tick controller inputs.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SwitchInputs {
    pub now_ns: u64,
    /// Raw reading from the A-channel end-of-travel sensor.
    pub sensor_a: RawSensor,
    /// Raw reading from the B-channel end-of-travel sensor.
    pub sensor_b: RawSensor,
    /// Most recent `SwitchCommand` from the consensus log (delivered
    /// by the node's Raft committed-entry applier). `None` when no
    /// command is pending.
    pub commanded: Option<CommandedPosition>,
    /// Motor thermal over-temperature flag from the drive
    /// electronics. `true` immediately stops the motor and engages
    /// the cooldown-fault latch.
    pub motor_over_temp: bool,
    /// Motor drive electronics reports an uncleared fault (over-current,
    /// under-voltage, encoder loss). Treated like `motor_over_temp`.
    pub motor_drive_fault: bool,
}

/// Fixed parameters of the point machine. Loaded at commissioning.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SwitchParams {
    /// Maximum continuous motor run time, in milliseconds. Exceeding
    /// this enters the cooldown-fault state. Typical 5 000 ms
    /// (5 s) — a healthy point machine throws in ≤ 2 s.
    pub motor_timeout_ms: u32,
    /// Rest period, in milliseconds, required after a cooldown-fault
    /// before the controller will attempt another motor operation.
    /// Typical 30 000 ms.
    pub motor_cooldown_ms: u32,
}

impl SwitchParams {
    /// Sensible defaults for a metro-grade power point machine.
    #[must_use]
    pub fn typical() -> Self {
        Self {
            motor_timeout_ms: 5_000,
            motor_cooldown_ms: 30_000,
        }
    }
}
