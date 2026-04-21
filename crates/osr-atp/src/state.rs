//! Real-time train state input to the ATP.
//!
//! `osr-odometry` (Phase 2a, crate 2) is the producer of this type.
//! For now it is constructed directly in tests and in the simulator
//! shim.

use osr_core::{TrackRef, TrainId};
use serde::{Deserialize, Serialize};

/// Snapshot of the train's measured state at evaluation time.
///
/// Every field is integer-only on the safety path. Uncertainties are
/// half-widths at a deployment-defined confidence interval (95% per
/// `osr-core::geometry::Position`).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TrainState {
    pub train_id: TrainId,
    /// Head position.
    pub head: TrackRef,
    /// Signed forward speed in millimetres per second.
    pub speed_mmps: i32,
    /// Speed half-width uncertainty in millimetres per second.
    /// Added to `speed_mmps` on the safe side of envelope comparisons.
    pub speed_uncertainty_mmps: u32,
    /// Head-position half-width uncertainty in millimetres.
    /// Subtracted from distance-to-end on the safe side.
    pub position_uncertainty_mm: u32,
}
