//! Value types.

use serde::{Deserialize, Serialize};

/// Diagnostic mode reported by the evaluator. Purely informational;
/// control decisions are taken on the raw inputs every tick.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AtoMode {
    /// ATO disengaged. Driver in manual control.
    #[default]
    Off,
    /// Speed below target by more than the deadband — applying traction.
    Accelerating,
    /// Within deadband of target speed.
    Cruising,
    /// Slightly above target, letting the train drift down without
    /// active braking (energy-efficient).
    Coasting,
    /// Above target enough to warrant service brake.
    Braking,
    /// Within station-approach profile: target speed is the
    /// quadratic `sqrt(2·a·d)` profile.
    StationApproach,
    /// At platform, speed ≤ tolerance. Holding brake applied.
    Stopped,
    /// Stopped with a dwell timer active.
    Dwelling,
}
