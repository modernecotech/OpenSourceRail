//! Core value types for the points controller.
//!
//! Intentionally self-contained — this crate does not depend on
//! `osr-interlocking` to stay decoupled from the log schema. Callers
//! map [`DetectedPosition`] and [`CommandedPosition`] to the
//! `SwitchPosition` enum in `osr_interlocking::log` at the consensus
//! boundary.

use serde::{Deserialize, Serialize};

/// Position the interlocking has commanded.
///
/// A switch is only ever commanded to one of two definite positions;
/// "Unknown" is never a commanded state.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum CommandedPosition {
    Normal,
    Reverse,
}

/// Position the controller has fused from its sensors.
///
/// `Unknown` is used whenever the two sensors disagree, either is
/// reporting an out-of-range value, or either is absent.
#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum DetectedPosition {
    Normal,
    Reverse,
    #[default]
    Unknown,
}

impl DetectedPosition {
    #[must_use]
    pub fn matches(self, commanded: CommandedPosition) -> bool {
        matches!(
            (self, commanded),
            (DetectedPosition::Normal, CommandedPosition::Normal)
                | (DetectedPosition::Reverse, CommandedPosition::Reverse)
        )
    }
}

/// One sensor's raw reading. `None` means the sensor is dead /
/// disconnected — treated as Unknown by the fusion step.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum RawSensor {
    ReadNormal,
    ReadReverse,
    /// Sensor reports an ambiguous/transitional value (e.g. neither
    /// end-of-travel switch closed).
    InTransit,
    /// Sensor link dead or stuck. Fail-restrictive: Unknown.
    Dead,
}

/// What the controller wants the motor to do.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize, Default)]
pub enum MotorCommand {
    /// Motor off.
    #[default]
    Stop,
    /// Drive toward the Normal end-of-travel stop.
    DriveToNormal,
    /// Drive toward the Reverse end-of-travel stop.
    DriveToReverse,
}
