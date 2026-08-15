//! `OdomState` — the odometer's output state.
//!
//! Held by the caller across ticks; [`crate::odom_step`] consumes it
//! by reference and returns a new one.

use osr_atp::TrainState;
use osr_core::{TrackRef, TrainId};
use serde::{Deserialize, Serialize};

use crate::sensors::{BaliseId, PositionSource};

/// Fused sensor state. One value per tick; caller retains across
/// ticks.
///
/// `position_uncertainty_mm` and `speed_uncertainty_mmps` are
/// half-widths at the same confidence interval used throughout
/// `osr-core::geometry::Position` (95 %).
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct OdomState {
    pub train_id: TrainId,
    /// Fused head position.
    pub head: TrackRef,
    /// Signed speed (mm/s) in the head's heading direction.
    pub speed_mmps: i32,
    /// Position half-width uncertainty (mm).
    pub position_uncertainty_mm: u32,
    /// Speed half-width uncertainty (mm/s).
    pub speed_uncertainty_mmps: u32,
    /// Which source drove the most recent update.
    pub contributing_source: PositionSource,
    /// Most recent balise consumed, if any. Useful for diagnostics
    /// and for the event recorder to correlate balise passes.
    pub last_balise_id: Option<BaliseId>,
    /// Timestamp of the tick that produced this state (ns, monotonic).
    pub last_timestamp_ns: u64,
}

impl OdomState {
    /// Construct an initial state at a known position. Typical use:
    /// train registration at a platform where the head position is
    /// surveyed to ≤ `min_uncertainty_mm` mm.
    #[must_use]
    pub fn new_at(train_id: TrainId, head: TrackRef, uncertainty_mm: u32, now_ns: u64) -> Self {
        Self {
            train_id,
            head,
            speed_mmps: 0,
            position_uncertainty_mm: uncertainty_mm,
            speed_uncertainty_mmps: 0,
            contributing_source: PositionSource::WheelTachometer,
            last_balise_id: None,
            last_timestamp_ns: now_ns,
        }
    }

    /// Produce an ATP-shaped [`TrainState`] view of this odometer
    /// state. The identity mapping over the overlapping fields; no
    /// allocation or copying of nested buffers.
    #[must_use]
    pub fn to_train_state(&self) -> TrainState {
        TrainState {
            train_id: self.train_id,
            head: self.head,
            speed_mmps: self.speed_mmps,
            speed_uncertainty_mmps: self.speed_uncertainty_mmps,
            position_uncertainty_mm: self.position_uncertainty_mm,
        }
    }

    /// Produce an ATP-shaped state only while position uncertainty is
    /// still below the caller's "known position" threshold. The odometry
    /// calibration's `max_uncertainty_mm` is the usual threshold; once a
    /// state saturates there, the caller should withhold/expire MA rather
    /// than treating a very wide estimate as a known position.
    #[must_use]
    pub fn to_train_state_if_known(&self, max_known_uncertainty_mm: u32) -> Option<TrainState> {
        if self.position_uncertainty_mm >= max_known_uncertainty_mm {
            return None;
        }
        Some(self.to_train_state())
    }
}
