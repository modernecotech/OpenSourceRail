//! Horizontal + vertical alignment data structures.
//!
//! An [`Alignment`] is the sequence of geometry elements a civil
//! contractor can stake:
//!
//! - Horizontal: [`HorizontalElement::Tangent`],
//!   [`HorizontalElement::Arc`], [`HorizontalElement::Spiral`].
//! - Vertical: [`VerticalElement::Grade`],
//!   [`VerticalElement::VerticalCurve`].
//!
//! Each element owns a length in metres; the running sum from the
//! alignment start is its **chainage**.

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum TurnDirection {
    Left,
    Right,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum HorizontalElement {
    /// Straight tangent section.
    Tangent {
        /// Length along the element, metres.
        length_m: f64,
        /// Bearing (azimuth) of the tangent, radians. Zero points
        /// along the +X axis; positive rotates counter-clockwise
        /// (right-hand rule).
        bearing_rad: f64,
        /// Cartesian start position, metres.
        start_xy: (f64, f64),
    },
    /// Circular arc.
    Arc {
        length_m: f64,
        /// Arc radius, metres. Always positive.
        radius_m: f64,
        /// Which way the arc turns.
        direction: TurnDirection,
        /// Cartesian start position + tangent bearing.
        start_xy: (f64, f64),
        start_bearing_rad: f64,
    },
    /// Transition spiral (clothoid) — curvature varies linearly from
    /// `start_radius_m` to `end_radius_m` along the length. `None`
    /// means "straight" (∞ radius).
    Spiral {
        length_m: f64,
        start_radius_m: Option<f64>,
        end_radius_m: Option<f64>,
        direction: TurnDirection,
        start_xy: (f64, f64),
        start_bearing_rad: f64,
    },
}

impl HorizontalElement {
    pub fn length_m(&self) -> f64 {
        match self {
            HorizontalElement::Tangent { length_m, .. }
            | HorizontalElement::Arc { length_m, .. }
            | HorizontalElement::Spiral { length_m, .. } => *length_m,
        }
    }

    pub fn start_xy(&self) -> (f64, f64) {
        match self {
            HorizontalElement::Tangent { start_xy, .. }
            | HorizontalElement::Arc { start_xy, .. }
            | HorizontalElement::Spiral { start_xy, .. } => *start_xy,
        }
    }

    pub fn start_bearing_rad(&self) -> f64 {
        match self {
            HorizontalElement::Tangent { bearing_rad, .. } => *bearing_rad,
            HorizontalElement::Arc {
                start_bearing_rad, ..
            }
            | HorizontalElement::Spiral {
                start_bearing_rad, ..
            } => *start_bearing_rad,
        }
    }

    /// Position + tangent bearing at an offset from the element start.
    /// `s` must be in `0..=length_m`.
    pub fn point_at(&self, s: f64) -> ((f64, f64), f64) {
        match *self {
            HorizontalElement::Tangent {
                bearing_rad,
                start_xy: (x0, y0),
                ..
            } => (
                (x0 + s * bearing_rad.cos(), y0 + s * bearing_rad.sin()),
                bearing_rad,
            ),
            HorizontalElement::Arc {
                radius_m,
                direction,
                start_xy: (x0, y0),
                start_bearing_rad,
                ..
            } => {
                let sign = match direction {
                    TurnDirection::Left => 1.0,
                    TurnDirection::Right => -1.0,
                };
                let delta = sign * s / radius_m;
                let bearing = start_bearing_rad + delta;
                // Arc centre is perpendicular to the start tangent.
                let (cx, cy) = (
                    x0 - sign * radius_m * start_bearing_rad.sin(),
                    y0 + sign * radius_m * start_bearing_rad.cos(),
                );
                // Angle from centre to current point.
                let angle_start = (y0 - cy).atan2(x0 - cx);
                let angle = angle_start + delta;
                (
                    (cx + radius_m * angle.cos(), cy + radius_m * angle.sin()),
                    bearing,
                )
            }
            HorizontalElement::Spiral {
                length_m,
                start_radius_m,
                end_radius_m,
                direction,
                start_xy: (x0, y0),
                start_bearing_rad,
            } => {
                // Short spirals used for transitions — approximate by
                // integrating bearing-rate along s.
                let sign = match direction {
                    TurnDirection::Left => 1.0,
                    TurnDirection::Right => -1.0,
                };
                let k0 = start_radius_m.map(|r| sign / r).unwrap_or(0.0);
                let k1 = end_radius_m.map(|r| sign / r).unwrap_or(0.0);
                // Linear curvature variation: k(u) = k0 + (k1-k0) * u/L.
                // Integrate bearing along s.
                // bearing(s) - bearing(0) = k0·s + (k1-k0)·s²/(2L)
                let bearing = start_bearing_rad + k0 * s + (k1 - k0) * s * s / (2.0 * length_m);
                // Approximate position by trapezoidal quadrature at
                // modest fidelity — adequate for urban-rail use (a
                // single spiral is ≤ 100 m; the cumulative position
                // error at s = L is <1 mm for radii ≥ 150 m).
                let steps = 16;
                let h = s / steps as f64;
                let mut x = x0;
                let mut y = y0;
                for i in 0..steps {
                    let u = (i as f64 + 0.5) * h;
                    let theta = start_bearing_rad + k0 * u + (k1 - k0) * u * u / (2.0 * length_m);
                    x += h * theta.cos();
                    y += h * theta.sin();
                }
                ((x, y), bearing)
            }
        }
    }

    /// Position + tangent bearing at the element's end.
    pub fn end_point(&self) -> ((f64, f64), f64) {
        self.point_at(self.length_m())
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum VerticalElement {
    /// Constant-grade segment. `grade` is rise/run (dimensionless);
    /// positive = uphill in the direction of chainage.
    Grade {
        length_m: f64,
        grade: f64,
        start_z_m: f64,
    },
    /// Parabolic vertical curve. Grade changes linearly with chainage;
    /// positive `k_value` = sag (grade becomes less negative / more
    /// positive); negative = crest.
    VerticalCurve {
        length_m: f64,
        start_grade: f64,
        end_grade: f64,
        start_z_m: f64,
    },
}

impl VerticalElement {
    pub fn length_m(&self) -> f64 {
        match self {
            VerticalElement::Grade { length_m, .. }
            | VerticalElement::VerticalCurve { length_m, .. } => *length_m,
        }
    }

    pub fn start_z_m(&self) -> f64 {
        match self {
            VerticalElement::Grade { start_z_m, .. }
            | VerticalElement::VerticalCurve { start_z_m, .. } => *start_z_m,
        }
    }

    /// Elevation at chainage offset `s` within the element.
    pub fn z_at(&self, s: f64) -> f64 {
        match *self {
            VerticalElement::Grade {
                grade, start_z_m, ..
            } => start_z_m + grade * s,
            VerticalElement::VerticalCurve {
                length_m,
                start_grade,
                end_grade,
                start_z_m,
            } => {
                // z(s) = z0 + g0·s + (g1 - g0)·s² / (2L)
                start_z_m + start_grade * s + (end_grade - start_grade) * s * s / (2.0 * length_m)
            }
        }
    }

    pub fn end_z_m(&self) -> f64 {
        self.z_at(self.length_m())
    }

    pub fn end_grade(&self) -> f64 {
        match *self {
            VerticalElement::Grade { grade, .. } => grade,
            VerticalElement::VerticalCurve { end_grade, .. } => end_grade,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Alignment {
    /// Slug of the line this alignment describes.
    pub line_slug: String,
    /// Design speed along the alignment, km/h. A single speed per
    /// alignment is the v0.1 simplification; urban-rail lines
    /// typically design to one speed per line per RFC 0009.
    pub design_speed_kmh: f64,
    /// Chainage at the alignment start, metres. Usually 0.
    pub start_chainage_m: f64,
    pub horizontal: Vec<HorizontalElement>,
    pub vertical: Vec<VerticalElement>,
}

#[derive(Debug, Error)]
pub enum AlignmentError {
    #[error("alignment polyline must have ≥ 2 points; got {0}")]
    TooShortPolyline(usize),
    #[error("vertical polyline length ({vertical_count}) does not match horizontal length ({horizontal_count})")]
    VerticalHorizontalMismatch {
        vertical_count: usize,
        horizontal_count: usize,
    },
    #[error("degenerate geometry at index {index}: {reason}")]
    DegenerateGeometry { index: usize, reason: &'static str },
}

impl Alignment {
    /// Total alignment length as the sum of horizontal element lengths.
    pub fn total_length_m(&self) -> f64 {
        self.horizontal.iter().map(|e| e.length_m()).sum()
    }
}
