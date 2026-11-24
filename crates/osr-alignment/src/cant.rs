//! Preliminary cant and deficiency calculations for horizontal alignment geometry.

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::{Alignment, HorizontalElement, TurnDirection};

const GRAVITY_M_S2: f64 = 9.80665;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct CantSegment {
    pub start_chainage_m: f64,
    pub end_chainage_m: f64,
    /// Cant magnitudes. The rail outside the turn is raised.
    pub start_cant_mm: f64,
    pub end_cant_mm: f64,
    pub direction: Option<TurnDirection>,
    /// Maximum shortfall from equilibrium cant at the alignment design speed.
    pub max_deficiency_mm: f64,
    /// Absolute rate of change within this segment at the alignment design speed.
    pub cant_rate_mm_per_s: f64,
}

#[derive(Debug, Error)]
pub enum CantError {
    #[error("invalid cant calculation input: {0}")]
    InvalidInput(&'static str),
    #[error("invalid cant geometry at horizontal element {index}: {reason}")]
    InvalidElement { index: usize, reason: &'static str },
}

/// Calculate capped equilibrium cant on arcs and linearly interpolate applied
/// cant between the endpoints of each spiral. Tangents carry zero cant.
///
/// Effective rail spacing is the horizontal distance between the points used to
/// measure the rail height difference. Equilibrium cant follows
/// `spacing * speed² / (gravity * radius)` with consistent units. The alignment
/// supplies a single design speed. Review running speeds, comfort, clearances,
/// and continuity at element boundaries before using a schedule in design.
pub fn cant_design(
    alignment: &Alignment,
    effective_rail_spacing_mm: f64,
    applied_cant_cap_mm: f64,
) -> Result<Vec<CantSegment>, CantError> {
    for (value, name) in [
        (alignment.design_speed_kmh, "design speed"),
        (applied_cant_cap_mm, "applied cant cap"),
    ] {
        if !value.is_finite() || value < 0.0 {
            return Err(CantError::InvalidInput(name));
        }
    }
    if !effective_rail_spacing_mm.is_finite() || effective_rail_spacing_mm <= 0.0 {
        return Err(CantError::InvalidInput("effective rail spacing"));
    }
    if !alignment.start_chainage_m.is_finite() {
        return Err(CantError::InvalidInput("start chainage"));
    }

    let speed_m_s = alignment.design_speed_kmh / 3.6;
    let mut chainage = alignment.start_chainage_m;
    let mut schedule = Vec::with_capacity(alignment.horizontal.len());
    for (index, element) in alignment.horizontal.iter().enumerate() {
        let invalid = |reason| CantError::InvalidElement { index, reason };
        let length = element.length_m();
        let end_chainage = chainage + length;
        if !end_chainage.is_finite() || end_chainage <= chainage {
            return Err(invalid("length must give a finite, increasing chainage"));
        }
        let (start_radius, end_radius, direction) = match *element {
            HorizontalElement::Tangent { .. } => (None, None, None),
            HorizontalElement::Arc {
                radius_m,
                direction,
                ..
            } => (Some(radius_m), Some(radius_m), Some(direction)),
            HorizontalElement::Spiral {
                start_radius_m,
                end_radius_m,
                direction,
                ..
            } => (start_radius_m, end_radius_m, Some(direction)),
        };
        let equilibrium = |radius: Option<f64>| {
            let Some(radius) = radius else {
                return Ok(0.0);
            };
            if !radius.is_finite() || radius <= 0.0 {
                return Err(invalid("radius must be finite and positive"));
            }
            let cant =
                effective_rail_spacing_mm * (speed_m_s / GRAVITY_M_S2) * (speed_m_s / radius);
            if !cant.is_finite() {
                return Err(invalid("equilibrium cant is outside the numerical range"));
            }
            Ok(cant)
        };
        let equilibrium_start = equilibrium(start_radius)?;
        let equilibrium_end = equilibrium(end_radius)?;
        let start_cant = equilibrium_start.min(applied_cant_cap_mm);
        let end_cant = equilibrium_end.min(applied_cant_cap_mm);
        let cant_rate = ((end_cant - start_cant) * speed_m_s / length).abs();
        if !cant_rate.is_finite() {
            return Err(invalid("cant rate is outside the numerical range"));
        }
        // Both equilibrium cant and applied cant vary linearly along a spiral.
        let max_deficiency = (equilibrium_start - start_cant).max(equilibrium_end - end_cant);
        schedule.push(CantSegment {
            start_chainage_m: chainage,
            end_chainage_m: end_chainage,
            start_cant_mm: start_cant,
            end_cant_mm: end_cant,
            direction,
            max_deficiency_mm: max_deficiency,
            cant_rate_mm_per_s: cant_rate,
        });
        chainage = end_chainage;
    }
    Ok(schedule)
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_abs_diff_eq;

    fn route() -> Alignment {
        Alignment {
            line_slug: "cant-fixture".into(),
            design_speed_kmh: 72.0,
            start_chainage_m: 100.0,
            horizontal: vec![
                HorizontalElement::Tangent {
                    length_m: 30.0,
                    bearing_rad: 0.0,
                    start_xy: (0.0, 0.0),
                },
                HorizontalElement::Spiral {
                    length_m: 40.0,
                    start_radius_m: None,
                    end_radius_m: Some(400.0),
                    direction: TurnDirection::Right,
                    start_xy: (30.0, 0.0),
                    start_bearing_rad: 0.0,
                },
                HorizontalElement::Arc {
                    length_m: 100.0,
                    radius_m: 400.0,
                    direction: TurnDirection::Right,
                    start_xy: (70.0, -0.7),
                    start_bearing_rad: -0.05,
                },
            ],
            vertical: vec![],
        }
    }

    #[test]
    fn capped_curve_and_spiral_preserve_chainage_direction_and_rate() {
        let schedule = cant_design(&route(), 1500.0, 100.0).unwrap();
        let [tangent, spiral, arc] = schedule.as_slice() else {
            panic!("expected three segments");
        };
        assert_eq!(tangent.start_chainage_m, 100.0);
        assert_eq!(tangent.end_chainage_m, 130.0);
        assert_eq!(tangent.end_cant_mm, 0.0);
        assert_eq!(tangent.max_deficiency_mm, 0.0);
        assert_eq!(tangent.direction, None);
        assert_eq!(spiral.start_chainage_m, tangent.end_chainage_m);
        assert_eq!(spiral.end_chainage_m, 170.0);
        assert_eq!(spiral.start_cant_mm, 0.0);
        assert_eq!(spiral.end_cant_mm, 100.0);
        assert_eq!(spiral.cant_rate_mm_per_s, 50.0);
        assert_eq!(spiral.direction, Some(TurnDirection::Right));
        assert_eq!(arc.start_chainage_m, spiral.end_chainage_m);
        assert_eq!(arc.end_chainage_m, 270.0);
        assert_eq!(arc.start_cant_mm, spiral.end_cant_mm);
        assert_eq!(arc.end_cant_mm, arc.start_cant_mm);
        assert_eq!(arc.cant_rate_mm_per_s, 0.0);
        // At 20 m/s on a 400 m radius, centrifugal acceleration is 1 m/s².
        assert_abs_diff_eq!(arc.max_deficiency_mm, 52.9574319467, epsilon = 1e-9);
        assert_eq!(spiral.max_deficiency_mm, arc.max_deficiency_mm);
    }

    #[test]
    fn explicit_spacing_changes_uncapped_equilibrium() {
        let narrow = cant_design(&route(), 1000.0, 200.0).unwrap();
        let wide = cant_design(&route(), 1500.0, 200.0).unwrap();
        assert_eq!(narrow[2].max_deficiency_mm, 0.0);
        assert_eq!(wide[2].max_deficiency_mm, 0.0);
        assert_abs_diff_eq!(wide[2].start_cant_mm, narrow[2].start_cant_mm * 1.5);
    }

    #[test]
    fn rejects_invalid_configuration_and_spiral_radius() {
        let mut route = route();
        assert!(matches!(
            cant_design(&route, 0.0, 100.0),
            Err(CantError::InvalidInput("effective rail spacing"))
        ));
        assert!(matches!(
            cant_design(&route, 1500.0, f64::NAN),
            Err(CantError::InvalidInput("applied cant cap"))
        ));
        if let HorizontalElement::Spiral { end_radius_m, .. } = &mut route.horizontal[1] {
            *end_radius_m = Some(0.0);
        }
        assert!(matches!(
            cant_design(&route, 1500.0, 100.0),
            Err(CantError::InvalidElement { index: 1, .. })
        ));
    }
}
