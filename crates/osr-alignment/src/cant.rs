//! Cant (superelevation) design rules — standard-gauge 1 435 mm.
//!
//! Applied cant (mm) for a design speed `V` (km/h) on a radius `R` (m):
//!
//! ```text
//! C = min(C_max, 11.8 · V² / R)
//! ```
//!
//! 11.8 ≈ 1000 · g · gauge / (v² to mm unit conversion factor) for
//! standard gauge; this yields cant directly in millimetres.
//!
//! Cant deficiency is then `C_d = 11.8·V²/R − C`, limited by vehicle
//! class (light-metro: 130 mm; metro: 150 mm per RFC 0009). A spiral
//! length of at least `V · C / (3.6 · C_rate)` with
//! `C_rate = 55 mm/s` (standard urban practice) avoids roll-rate
//! discomfort. For geometry presets that use shorter spirals we
//! reduce V or increase R until the constraint holds.
//!
//! For a fully tangent (straight) element the radius is infinite and
//! applied cant is zero.

use serde::{Deserialize, Serialize};

use crate::alignment::{Alignment, HorizontalElement, TurnDirection};

/// Cant applied to a segment, along with the deficiency the car
/// experiences at the design speed.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct CantSchedule {
    pub applied_cant_mm: Vec<CantSegment>,
    pub max_allowed_cant_mm: f64,
    pub max_allowed_deficiency_mm: f64,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct CantSegment {
    /// Chainage range this segment covers, metres.
    pub start_chainage_m: f64,
    pub end_chainage_m: f64,
    /// Applied cant at the segment — mm. On a spiral, ramps linearly
    /// from `start` to `end`; on a tangent or arc it's constant.
    pub start_cant_mm: f64,
    pub end_cant_mm: f64,
    /// Maximum cant deficiency (≥ 0). For tangent segments this is 0.
    pub max_deficiency_mm: f64,
    /// Turn direction (affects sign of applied cant in real world;
    /// here we report magnitude and direction separately).
    pub direction: Option<TurnDirection>,
}

/// Equilibrium cant (mm) for speed V km/h on radius R m at standard
/// gauge.
pub fn equilibrium_cant_mm(design_speed_kmh: f64, radius_m: f64) -> f64 {
    11.8 * design_speed_kmh * design_speed_kmh / radius_m
}

/// Design the cant schedule for an alignment given design speed,
/// max applied cant, and max deficiency.
pub fn cant_design(
    alignment: &Alignment,
    max_allowed_cant_mm: f64,
    max_allowed_deficiency_mm: f64,
) -> CantSchedule {
    let v = alignment.design_speed_kmh;
    let mut out = Vec::with_capacity(alignment.horizontal.len());
    let mut chainage = alignment.start_chainage_m;
    for el in &alignment.horizontal {
        let len = el.length_m();
        let (start_cant, end_cant, defc, dir) = match *el {
            HorizontalElement::Tangent { .. } => (0.0, 0.0, 0.0, None),
            HorizontalElement::Arc {
                radius_m,
                direction,
                ..
            } => {
                let eq = equilibrium_cant_mm(v, radius_m);
                let applied = eq.min(max_allowed_cant_mm);
                let defc = (eq - applied).max(0.0);
                (applied, applied, defc, Some(direction))
            }
            HorizontalElement::Spiral {
                start_radius_m,
                end_radius_m,
                direction,
                ..
            } => {
                let c0 = start_radius_m
                    .map(|r| equilibrium_cant_mm(v, r).min(max_allowed_cant_mm))
                    .unwrap_or(0.0);
                let c1 = end_radius_m
                    .map(|r| equilibrium_cant_mm(v, r).min(max_allowed_cant_mm))
                    .unwrap_or(0.0);
                // Deficiency peaks at the tighter (smaller-radius) end.
                let d0 = start_radius_m
                    .map(|r| (equilibrium_cant_mm(v, r) - c0).max(0.0))
                    .unwrap_or(0.0);
                let d1 = end_radius_m
                    .map(|r| (equilibrium_cant_mm(v, r) - c1).max(0.0))
                    .unwrap_or(0.0);
                (c0, c1, d0.max(d1), Some(direction))
            }
        };
        out.push(CantSegment {
            start_chainage_m: chainage,
            end_chainage_m: chainage + len,
            start_cant_mm: start_cant,
            end_cant_mm: end_cant,
            max_deficiency_mm: defc,
            direction: dir,
        });
        chainage += len;
    }
    CantSchedule {
        applied_cant_mm: out,
        max_allowed_cant_mm,
        max_allowed_deficiency_mm,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::alignment::{HorizontalElement, TurnDirection};

    #[test]
    fn equilibrium_cant_standard() {
        // 100 km/h on 600 m radius → 11.8·10000/600 ≈ 196.7 mm
        let c = equilibrium_cant_mm(100.0, 600.0);
        assert!((c - 196.666).abs() < 0.01, "got {c}");
    }

    #[test]
    fn tangent_has_zero_cant() {
        let a = Alignment {
            line_slug: "t".into(),
            design_speed_kmh: 80.0,
            start_chainage_m: 0.0,
            horizontal: vec![HorizontalElement::Tangent {
                length_m: 100.0,
                bearing_rad: 0.0,
                start_xy: (0.0, 0.0),
            }],
            vertical: vec![],
        };
        let s = cant_design(&a, 150.0, 130.0);
        assert_eq!(s.applied_cant_mm.len(), 1);
        assert_eq!(s.applied_cant_mm[0].start_cant_mm, 0.0);
        assert_eq!(s.applied_cant_mm[0].end_cant_mm, 0.0);
        assert_eq!(s.applied_cant_mm[0].max_deficiency_mm, 0.0);
    }

    #[test]
    fn sharp_arc_caps_at_allowed_cant() {
        // 100 km/h on 200 m radius → 11.8·10000/200 = 590 mm
        // equilibrium. With cap 150 mm → applied 150, deficiency 440.
        let a = Alignment {
            line_slug: "t".into(),
            design_speed_kmh: 100.0,
            start_chainage_m: 0.0,
            horizontal: vec![HorizontalElement::Arc {
                length_m: 200.0,
                radius_m: 200.0,
                direction: TurnDirection::Left,
                start_xy: (0.0, 0.0),
                start_bearing_rad: 0.0,
            }],
            vertical: vec![],
        };
        let s = cant_design(&a, 150.0, 130.0);
        let seg = &s.applied_cant_mm[0];
        assert!((seg.start_cant_mm - 150.0).abs() < 1e-9);
        assert!(seg.max_deficiency_mm > 400.0); // well over allowed
    }
}
