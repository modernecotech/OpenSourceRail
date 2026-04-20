//! Geometric primitives: direction, track reference, position.

use crate::ids::SectionId;
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Direction {
    Forward,
    Reverse,
}

impl Direction {
    pub fn reverse(self) -> Self {
        match self {
            Direction::Forward => Direction::Reverse,
            Direction::Reverse => Direction::Forward,
        }
    }
}

/// Pointer into the static track topology: a section + linear offset in mm.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct TrackRef {
    pub section: SectionId,
    pub offset_mm: i64,
    pub direction: Direction,
}

/// Fused position estimate with sensor-derived uncertainty (half-width, 95% CI).
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Position {
    pub track_ref: TrackRef,
    pub uncertainty_mm: u32,
}

impl Position {
    pub fn certain(track_ref: TrackRef) -> Self {
        Self { track_ref, uncertainty_mm: 0 }
    }
}
