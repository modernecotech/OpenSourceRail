//! Output and internal state of the points controller.

use serde::{Deserialize, Serialize};

use crate::types::{CommandedPosition, DetectedPosition, MotorCommand};

/// Reason for a cooldown-fault. Diagnostic only.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum FaultReason {
    /// Motor ran longer than `motor_timeout_ms` without reaching target.
    MotorTimeout,
    /// Drive electronics reported over-temperature.
    OverTemperature,
    /// Drive electronics reported an uncleared fault.
    DriveFault,
}

/// Persistent state of the controller. Caller carries across ticks.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize, Default)]
pub struct SwitchState {
    /// Fused detected position (W2-conservative).
    pub detected: DetectedPosition,
    /// The most recent command accepted. Persists across ticks until
    /// overwritten.
    pub commanded: Option<CommandedPosition>,
    /// Motor state this tick — echoed from the returned
    /// [`SwitchOutput::motor`] for convenience / diagnostics.
    pub motor: MotorCommand,
    /// If the motor is running, the timestamp it started. Used to
    /// enforce `motor_timeout_ms`.
    pub motor_started_ns: Option<u64>,
    /// If set, the controller is in cooldown after a fault; no motor
    /// operations permitted until this ns-since-epoch is reached.
    pub fault_until_ns: Option<u64>,
    /// If the controller is in fault, the reason.
    pub fault_reason: Option<FaultReason>,
    /// The last detected-position value we emitted via a published
    /// observation. Used to decide whether this tick needs a new
    /// `SwitchObservation` entry.
    pub last_emitted_detected: DetectedPosition,
}

impl Default for DetectedPosition {
    fn default() -> Self {
        DetectedPosition::Unknown
    }
}

/// Full per-tick output.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SwitchOutput {
    pub state: SwitchState,
    /// Motor command to apply this tick.
    pub motor: MotorCommand,
    /// `Some(pos)` when the controller wants a fresh
    /// `SwitchObservation` entry published on the consensus log
    /// (i.e., the fused detection changed since last emission).
    pub publish_observation: Option<DetectedPosition>,
}
