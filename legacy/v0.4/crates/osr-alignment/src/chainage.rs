//! Chainage — the civil-surveyor's mile-post system.
//!
//! Every point along an alignment is identified by its chainage
//! (running metre-count from the alignment origin). This module
//! converts a chainage into a 3-D stationed point with bearing +
//! elevation + grade, for stake-out on site.

use serde::{Deserialize, Serialize};

use crate::alignment::Alignment;

/// A single stationed point — everything a surveyor needs at one
/// chainage.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct StationedPoint {
    pub chainage_m: f64,
    pub x_m: f64,
    pub y_m: f64,
    pub z_m: f64,
    /// Horizontal tangent bearing, radians.
    pub bearing_rad: f64,
    /// Vertical grade (rise/run).
    pub grade: f64,
}

/// Compute the stationed point at the given chainage on `alignment`.
/// Returns `None` if the chainage is outside the alignment extent.
pub fn station_at(alignment: &Alignment, chainage_m: f64) -> Option<StationedPoint> {
    let start = alignment.start_chainage_m;
    if chainage_m < start {
        return None;
    }
    // Horizontal: find the containing element.
    let mut acc = start;
    let mut xy = None;
    let mut bearing = 0.0;
    for el in &alignment.horizontal {
        let end = acc + el.length_m();
        if chainage_m <= end + 1e-6 {
            let (p, br) = el.point_at(chainage_m - acc);
            xy = Some(p);
            bearing = br;
            break;
        }
        acc = end;
    }
    let (x, y) = xy?;

    // Vertical: find the containing element.
    let mut acc = start;
    let mut z = 0.0;
    let mut grade = 0.0;
    for el in &alignment.vertical {
        let end = acc + el.length_m();
        if chainage_m <= end + 1e-6 {
            z = el.z_at(chainage_m - acc);
            grade = grade_at(el, chainage_m - acc);
            break;
        }
        acc = end;
    }
    Some(StationedPoint {
        chainage_m,
        x_m: x,
        y_m: y,
        z_m: z,
        bearing_rad: bearing,
        grade,
    })
}

fn grade_at(element: &crate::alignment::VerticalElement, s: f64) -> f64 {
    use crate::alignment::VerticalElement::*;
    match element {
        Grade { grade, .. } => *grade,
        VerticalCurve {
            length_m,
            start_grade,
            end_grade,
            ..
        } => start_grade + (end_grade - start_grade) * s / length_m,
    }
}

/// Sample the alignment every `interval_m` metres, starting at the
/// alignment origin. Useful for generating a stake-out table.
pub fn sample_every(alignment: &Alignment, interval_m: f64) -> Vec<StationedPoint> {
    let total = alignment.total_length_m();
    let start = alignment.start_chainage_m;
    let mut out = Vec::new();
    let mut s = 0.0;
    while s <= total {
        if let Some(p) = station_at(alignment, start + s) {
            out.push(p);
        }
        s += interval_m;
    }
    // Always include the end.
    if let Some(p) = station_at(alignment, start + total) {
        if out
            .last()
            .is_none_or(|last| (last.chainage_m - p.chainage_m).abs() > 1e-3)
        {
            out.push(p);
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alignment::{HorizontalElement, VerticalElement};

    fn straight_alignment() -> Alignment {
        Alignment {
            line_slug: "t".into(),
            design_speed_kmh: 80.0,
            start_chainage_m: 0.0,
            horizontal: vec![HorizontalElement::Tangent {
                length_m: 1000.0,
                bearing_rad: 0.0,
                start_xy: (0.0, 0.0),
            }],
            vertical: vec![VerticalElement::Grade {
                length_m: 1000.0,
                grade: 0.02,
                start_z_m: 0.0,
            }],
        }
    }

    #[test]
    fn station_at_origin() {
        let p = station_at(&straight_alignment(), 0.0).unwrap();
        assert!((p.x_m - 0.0).abs() < 1e-9);
        assert!((p.z_m - 0.0).abs() < 1e-9);
        assert!((p.grade - 0.02).abs() < 1e-9);
    }

    #[test]
    fn station_mid_tangent_uphill() {
        let p = station_at(&straight_alignment(), 500.0).unwrap();
        assert!((p.x_m - 500.0).abs() < 1e-6);
        assert!((p.y_m - 0.0).abs() < 1e-6);
        assert!((p.z_m - 10.0).abs() < 1e-6); // 500 m × 0.02
    }

    #[test]
    fn station_past_end_is_none() {
        assert!(station_at(&straight_alignment(), 1500.0).is_none());
    }

    #[test]
    fn sampling_hits_endpoints() {
        let samples = sample_every(&straight_alignment(), 200.0);
        assert!(samples.first().unwrap().chainage_m.abs() < 1e-6);
        assert!((samples.last().unwrap().chainage_m - 1000.0).abs() < 1e-6);
        // Should be 6 samples (0, 200, 400, 600, 800, 1000).
        assert_eq!(samples.len(), 6);
    }
}
