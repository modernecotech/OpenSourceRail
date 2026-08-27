//! Civil-class assignment per polyline segment.
//!
//! Per [RFC 0011](../../../docs/rfcs/0011-civil-infrastructure-design-standard.md),
//! the catalogue has **three classes only — at-grade, elevated, and
//! bridge (for water crossings)**. No tunnels. Dense built-up cells
//! that a previous version of this inference classified as
//! `BoredTunnel` now route `Elevated`, matching the no-tunnel
//! invariant from RFC 0011 §1.
//!
//! Heuristic: the cost raster encodes "how built-up / constrained"
//! a cell is. So:
//!   - low cost (on arterial)     → at-grade
//!   - medium cost (side-street)  → at-grade (tight but feasible)
//!   - high cost (park, narrow gap between buildings) → elevated
//!   - water cells                → bridge
//!   - buildings / dense built-up → elevated (the no-tunnel rule —
//!     where the corridor can't be at-grade, it goes above, never
//!     below).

use serde::{Deserialize, Serialize};

use crate::raster::Grid;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum CivilClass {
    AtGrade,
    Elevated,
    Bridge,
}

/// Alternatives evaluated at a road/rail conflict before committing to a
/// long elevated railway approach.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, PartialOrd, Ord)]
#[serde(rename_all = "kebab-case")]
pub enum CrossingAlternative {
    RailwayElevated,
    RoadOverbridge,
    RoadUnderpass,
    RoadClosureOrRelocation,
    ShortModularRailBridge,
}

/// Additive planning penalties attached to an alignment or crossing option.
/// Values are monetary planning inputs supplied by the city project, not
/// embedded global unit rates.
#[derive(Debug, Clone, Copy, Default, Serialize, Deserialize, PartialEq)]
pub struct ConstructionCostPenalties {
    pub foundation_risk: f64,
    pub utility_relocation: f64,
    pub crane_access: f64,
    pub temporary_traffic: f64,
    pub flood_and_scour: f64,
    pub retaining_wall_feasibility: f64,
    pub station_transfer_structure: f64,
    pub nonstandard_components: f64,
}

impl ConstructionCostPenalties {
    #[must_use]
    pub fn total(self) -> f64 {
        self.foundation_risk
            + self.utility_relocation
            + self.crane_access
            + self.temporary_traffic
            + self.flood_and_scour
            + self.retaining_wall_feasibility
            + self.station_transfer_structure
            + self.nonstandard_components
    }

    #[must_use]
    pub fn is_valid(self) -> bool {
        [
            self.foundation_risk,
            self.utility_relocation,
            self.crane_access,
            self.temporary_traffic,
            self.flood_and_scour,
            self.retaining_wall_feasibility,
            self.station_transfer_structure,
            self.nonstandard_components,
        ]
        .into_iter()
        .all(|value| value.is_finite() && value >= 0.0)
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub struct CrossingAlternativeEstimate {
    pub alternative: CrossingAlternative,
    pub direct_cost: f64,
    #[serde(default)]
    pub penalties: ConstructionCostPenalties,
    #[serde(default = "default_true")]
    pub feasible: bool,
}

const fn default_true() -> bool {
    true
}

impl CrossingAlternativeEstimate {
    #[must_use]
    pub fn whole_construction_cost(self) -> f64 {
        self.direct_cost + self.penalties.total()
    }

    #[must_use]
    pub fn is_valid(self) -> bool {
        self.direct_cost.is_finite() && self.direct_cost >= 0.0 && self.penalties.is_valid()
    }
}

/// Choose the least whole-construction-cost feasible option. Stable enum
/// ordering breaks exact ties, making regeneration deterministic.
#[must_use]
pub fn select_crossing_alternative(
    alternatives: &[CrossingAlternativeEstimate],
) -> Option<CrossingAlternativeEstimate> {
    alternatives
        .iter()
        .copied()
        .filter(|estimate| estimate.feasible && estimate.is_valid())
        .min_by(|left, right| {
            left.whole_construction_cost()
                .total_cmp(&right.whole_construction_cost())
                .then_with(|| left.alternative.cmp(&right.alternative))
        })
}

/// Planning product selected after a route cell has been classified Elevated.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum ElevatedViaductProduct {
    /// Normal transportable 25 m decked pi-beam, one beam per track.
    DeckedPi25,
    /// 20 m decked pi-beam produced on the same long-line mould.
    DeckedPi20,
    /// Legacy/special acoustic full-span U-trough retained for compatibility.
    FullSpanU25,
    /// Legacy/special acoustic 20 m U-trough retained for compatibility.
    ClosureU20,
    /// Unreleased 25--30 m full-span product requiring project transport,
    /// lifting and structural verification. It is never labelled OSR-U25.
    ProjectSpecificU30,
    /// Match-cast 2.5--3.0 m segmental U/box for access or curvature.
    SegmentalUs,
    /// Separately engineered crossing, turnout, or span over 30 m.
    SpecialSpan,
    /// The system geometry may be possible, but the economical elevated
    /// response is to relax or move the alignment before selecting structure.
    RealignOrSpecial,
}

pub const ELEVATED_PREFERRED_RADIUS_M: f64 = 300.0;
pub const MAX_FULL_SPAN_U_M: f64 = 30.0;

/// Large constructability multiplier for elevated curves below 300 m.
///
/// The general rolling-stock minimum remains available at grade. This factor
/// makes a 90 m elevated curve about 11 times the tangent/broad-curve seed so
/// route synthesis can strongly prefer realignment when it has alternatives.
#[must_use]
pub fn elevated_curve_cost_multiplier(radius_m: f64) -> f64 {
    if radius_m.is_nan() || radius_m <= 0.0 {
        return f64::INFINITY;
    }
    if radius_m >= ELEVATED_PREFERRED_RADIUS_M {
        1.0
    } else {
        (ELEVATED_PREFERRED_RADIUS_M / radius_m).powi(2)
    }
}

/// Select the planning structural family for known elevated geometry.
#[must_use]
pub fn elevated_product_for_geometry(
    radius_m: f64,
    crossing_span_m: f64,
    full_span_transport_access: bool,
) -> ElevatedViaductProduct {
    if radius_m.is_nan()
        || radius_m <= 0.0
        || !crossing_span_m.is_finite()
        || crossing_span_m <= 0.0
    {
        return ElevatedViaductProduct::RealignOrSpecial;
    }
    if crossing_span_m > MAX_FULL_SPAN_U_M {
        return ElevatedViaductProduct::SpecialSpan;
    }
    if radius_m < 120.0 {
        return ElevatedViaductProduct::RealignOrSpecial;
    }
    if !full_span_transport_access || radius_m < ELEVATED_PREFERRED_RADIUS_M {
        return ElevatedViaductProduct::SegmentalUs;
    }
    if crossing_span_m <= 20.0 {
        ElevatedViaductProduct::DeckedPi20
    } else if crossing_span_m <= 25.0 {
        ElevatedViaductProduct::DeckedPi25
    } else {
        ElevatedViaductProduct::ProjectSpecificU30
    }
}

impl ElevatedViaductProduct {
    /// Stable catalogue code written into generated design artifacts.
    #[must_use]
    pub const fn catalogue_code(self) -> &'static str {
        match self {
            Self::DeckedPi25 => "OSR-Pi25",
            Self::DeckedPi20 => "OSR-Pi20",
            Self::FullSpanU25 => "OSR-U25-SPECIAL",
            Self::ClosureU20 => "OSR-U20-SPECIAL",
            Self::ProjectSpecificU30 => "OSR-U30-PROJECT",
            Self::SegmentalUs => "OSR-US",
            Self::SpecialSpan => "OSR-SP",
            Self::RealignOrSpecial => "REALIGN-OR-SPECIAL",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CivilSegment {
    pub class: CivilClass,
    /// Inclusive cell index range into the parent line's `cells`.
    pub from_idx: usize,
    pub to_idx: usize,
    pub length_m: f64,
    /// Minimum planning radius inferred from a 100 m smoothed route window.
    /// `None` means tangent/no measurable curvature.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub minimum_curve_radius_m: Option<f64>,
    /// Structural family selected for elevated/bridge work.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub viaduct_product: Option<ElevatedViaductProduct>,
    /// Constructability factor applied to elevated planning cost.
    #[serde(default = "unit_multiplier")]
    pub elevated_cost_multiplier: f64,
}

const fn unit_multiplier() -> f64 {
    1.0
}

/// Classify each cell, then collapse runs into segments.
#[must_use]
pub fn classify_segments(grid: &Grid, cells: &[(usize, usize)]) -> Vec<CivilSegment> {
    if cells.is_empty() {
        return Vec::new();
    }

    // Per-cell class.
    let classes: Vec<CivilClass> = cells
        .iter()
        .map(|&(r, c)| classify_cell(grid, r, c))
        .collect();

    civil_segments_from_classes(grid, cells, &classes)
}

/// Route-wide factor used by production candidate scoring.
///
/// At-grade and bridge length retain factor 1. Elevated length is weighted by
/// its inferred curve multiplier, so alternatives serving equal demand lose
/// rank when they require tight, expensive segmental/realignment geometry.
#[must_use]
pub fn route_elevated_constructability_multiplier(grid: &Grid, cells: &[(usize, usize)]) -> f64 {
    let segments = classify_segments(grid, cells);
    let total_m: f64 = segments.iter().map(|segment| segment.length_m).sum();
    if total_m <= 0.0 {
        return 1.0;
    }
    let equivalent_m: f64 = segments
        .iter()
        .map(|segment| match segment.class {
            CivilClass::Elevated => segment.length_m * segment.elevated_cost_multiplier,
            CivilClass::AtGrade | CivilClass::Bridge => segment.length_m,
        })
        .sum();
    equivalent_m / total_m
}

/// Collapse a per-cell civil classification and attach elevated geometry.
///
/// This is also used after the production emitter promotes interchange
/// windows to elevated, ensuring those generated segments receive the same
/// product and curvature logic as initially classified route cells.
#[must_use]
pub fn civil_segments_from_classes(
    grid: &Grid,
    cells: &[(usize, usize)],
    classes: &[CivilClass],
) -> Vec<CivilSegment> {
    if cells.is_empty() {
        return Vec::new();
    }
    assert_eq!(
        cells.len(),
        classes.len(),
        "civil classes must match route cells"
    );

    let mut segments: Vec<CivilSegment> = Vec::new();
    let mut run_start = 0;
    for i in 1..=classes.len() {
        if i == classes.len() || classes[i] != classes[run_start] {
            // Carry the edge into the next run on the preceding span so
            // every route edge is counted exactly once. The former
            // `run_start..i` slice dropped one edge at every class
            // transition and gave single-cell spans zero length.
            let length_end = if i < cells.len() { i + 1 } else { i };
            let length_m = segment_length_m(grid, &cells[run_start..length_end]);
            let class = classes[run_start];
            let minimum_curve_radius_m = if class == CivilClass::Elevated {
                minimum_route_radius_m(cells, run_start, i.saturating_sub(1), grid.reference.cell_m)
            } else {
                None
            };
            let (viaduct_product, elevated_cost_multiplier) = match class {
                CivilClass::AtGrade => (None, 1.0),
                CivilClass::Bridge => (Some(ElevatedViaductProduct::SpecialSpan), 1.0),
                CivilClass::Elevated => {
                    let radius_m = minimum_curve_radius_m.unwrap_or(f64::INFINITY);
                    (
                        Some(elevated_product_for_geometry(radius_m, 25.0, true)),
                        elevated_curve_cost_multiplier(radius_m),
                    )
                }
            };
            segments.push(CivilSegment {
                class,
                from_idx: run_start,
                to_idx: i - 1,
                length_m,
                minimum_curve_radius_m,
                viaduct_product,
                elevated_cost_multiplier,
            });
            run_start = i;
        }
    }
    segments
}

/// Infer minimum radius using route points about 100 m apart.
///
/// The window filters 20 m raster stair-steps while retaining the geometry
/// signal needed to distinguish a broad U25 corridor from OSR-US/realignment.
fn minimum_route_radius_m(
    cells: &[(usize, usize)],
    from_idx: usize,
    to_idx: usize,
    cell_m: f64,
) -> Option<f64> {
    if cells.len() < 3 || from_idx >= cells.len() || from_idx > to_idx || cell_m <= 0.0 {
        return None;
    }
    let window = (100.0 / cell_m).round().max(1.0) as usize;
    let mut minimum = f64::INFINITY;
    for centre in from_idx..=to_idx.min(cells.len() - 1) {
        let left = centre.saturating_sub(window);
        let right = (centre + window).min(cells.len() - 1);
        if left == centre || centre == right {
            continue;
        }
        let point = |index: usize| {
            let (row, col) = cells[index];
            (col as f64 * cell_m, row as f64 * cell_m)
        };
        let a = point(left);
        let b = point(centre);
        let c = point(right);
        let ab = (b.0 - a.0).hypot(b.1 - a.1);
        let bc = (c.0 - b.0).hypot(c.1 - b.1);
        let ac = (c.0 - a.0).hypot(c.1 - a.1);
        let twice_area = ((b.0 - a.0) * (c.1 - a.1) - (b.1 - a.1) * (c.0 - a.0)).abs();
        if twice_area <= 1e-6 {
            continue;
        }
        let radius = ab * bc * ac / (2.0 * twice_area);
        if radius.is_finite() {
            minimum = minimum.min(radius);
        }
    }
    minimum.is_finite().then_some(minimum)
}

fn classify_cell(grid: &Grid, r: usize, c: usize) -> CivilClass {
    let cost = grid.cost_at(r, c);
    // Thresholds must stay in sync with COST_* constants in
    // osr_geo/rasterize.py:
    //   existing rail  = 3      → at-grade
    //   arterial       = 8      → at-grade
    //   open           = 20     → at-grade
    //   side street    = 25     → at-grade
    //   park           = 45     → elevated
    //   water          = 300    → bridge
    //   building       = 600    → **elevated** (no-tunnel rule,
    //                              RFC 0011 §8)
    if cost < 40.0 {
        CivilClass::AtGrade
    } else if cost < 100.0 {
        CivilClass::Elevated
    } else if cost < 400.0 {
        CivilClass::Bridge
    } else {
        // Dense built-up / building footprint. Previously this was
        // `BoredTunnel`; under RFC 0011's no-tunnel invariant the
        // corridor goes over, not under.
        CivilClass::Elevated
    }
}

fn segment_length_m(grid: &Grid, cells: &[(usize, usize)]) -> f64 {
    if cells.len() < 2 {
        return 0.0;
    }
    let mut total = 0.0;
    for pair in cells.windows(2) {
        let dr = pair[1].0 as f64 - pair[0].0 as f64;
        let dc = pair[1].1 as f64 - pair[0].1 as f64;
        total += (dr * dr + dc * dc).sqrt() * grid.reference.cell_m;
    }
    total
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::raster::GridRef;

    fn grid(cost: Vec<f32>) -> Grid {
        Grid {
            reference: GridRef {
                height: 1,
                width: cost.len(),
                cell_m: 20.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_west: 0.0,
                bbox_north: 1.0,
                bbox_east: 1.0,
                m_per_deg_lat: 111_132.0,
                m_per_deg_lon: 111_320.0,
            },
            demand: vec![0.0; cost.len()],
            buildability: vec![1; cost.len()],
            cost,
        }
    }

    fn square_grid(size: usize, cost: f32) -> Grid {
        Grid {
            reference: GridRef {
                height: size,
                width: size,
                cell_m: 20.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_west: 0.0,
                bbox_north: 1.0,
                bbox_east: 1.0,
                m_per_deg_lat: 111_132.0,
                m_per_deg_lon: 111_320.0,
            },
            demand: vec![0.0; size * size],
            buildability: vec![1; size * size],
            cost: vec![cost; size * size],
        }
    }

    #[test]
    fn civil_transition_edges_are_counted_exactly_once() {
        let grid = grid(vec![8.0, 45.0, 45.0, 8.0]);
        let cells = vec![(0, 0), (0, 1), (0, 2), (0, 3)];
        let segments = classify_segments(&grid, &cells);
        assert_eq!(segments.len(), 3);
        let total: f64 = segments.iter().map(|segment| segment.length_m).sum();
        assert_eq!(total, 60.0);
        assert_eq!(segments[0].length_m, 20.0);
        assert_eq!(segments[1].length_m, 40.0);
        assert_eq!(segments[2].length_m, 0.0);
        assert_eq!(
            segments[1].viaduct_product,
            Some(ElevatedViaductProduct::DeckedPi25)
        );
    }

    #[test]
    fn elevated_geometry_selects_constructible_product_family() {
        assert_eq!(
            elevated_product_for_geometry(400.0, 25.0, true),
            ElevatedViaductProduct::DeckedPi25
        );
        assert_eq!(
            elevated_product_for_geometry(400.0, 20.0, true),
            ElevatedViaductProduct::DeckedPi20
        );
        assert_eq!(
            elevated_product_for_geometry(200.0, 25.0, true),
            ElevatedViaductProduct::SegmentalUs
        );
        assert_eq!(
            elevated_product_for_geometry(90.0, 20.0, true),
            ElevatedViaductProduct::RealignOrSpecial
        );
        assert_eq!(
            elevated_product_for_geometry(500.0, 40.0, true),
            ElevatedViaductProduct::SpecialSpan
        );
        assert_eq!(
            elevated_product_for_geometry(500.0, 28.0, true),
            ElevatedViaductProduct::ProjectSpecificU30
        );
        assert_eq!(
            elevated_product_for_geometry(f64::INFINITY, 25.0, true),
            ElevatedViaductProduct::DeckedPi25
        );
        assert!(elevated_curve_cost_multiplier(90.0) > 10.0);
        assert_eq!(elevated_curve_cost_multiplier(300.0), 1.0);
        assert_eq!(elevated_curve_cost_multiplier(f64::INFINITY), 1.0);
    }

    #[test]
    fn classified_elevated_corner_gets_product_and_cost_penalty() {
        let grid = square_grid(11, 45.0);
        let mut cells: Vec<(usize, usize)> = (0..=5).map(|col| (5, col)).collect();
        cells.extend((6..=10).map(|row| (row, 5)));
        let segments = classify_segments(&grid, &cells);
        assert_eq!(segments.len(), 1);
        let segment = &segments[0];
        assert!(segment.minimum_curve_radius_m.unwrap() < 120.0);
        assert_eq!(
            segment.viaduct_product,
            Some(ElevatedViaductProduct::RealignOrSpecial)
        );
        assert!(segment.elevated_cost_multiplier > 10.0);
        assert!(route_elevated_constructability_multiplier(&grid, &cells) > 10.0);
    }

    #[test]
    fn crossing_comparison_includes_all_construction_penalties() {
        let railway = CrossingAlternativeEstimate {
            alternative: CrossingAlternative::RailwayElevated,
            direct_cost: 8_000_000.0,
            penalties: ConstructionCostPenalties {
                foundation_risk: 2_000_000.0,
                crane_access: 1_000_000.0,
                nonstandard_components: 500_000.0,
                ..ConstructionCostPenalties::default()
            },
            feasible: true,
        };
        let road = CrossingAlternativeEstimate {
            alternative: CrossingAlternative::RoadOverbridge,
            direct_cost: 6_500_000.0,
            penalties: ConstructionCostPenalties {
                temporary_traffic: 1_000_000.0,
                utility_relocation: 250_000.0,
                ..ConstructionCostPenalties::default()
            },
            feasible: true,
        };
        assert_eq!(
            select_crossing_alternative(&[railway, road])
                .unwrap()
                .alternative,
            CrossingAlternative::RoadOverbridge
        );
    }

    #[test]
    fn crossing_comparison_rejects_infeasible_or_invalid_inputs() {
        let invalid = CrossingAlternativeEstimate {
            alternative: CrossingAlternative::RoadUnderpass,
            direct_cost: -1.0,
            penalties: ConstructionCostPenalties::default(),
            feasible: true,
        };
        let infeasible = CrossingAlternativeEstimate {
            alternative: CrossingAlternative::RoadClosureOrRelocation,
            direct_cost: 1.0,
            penalties: ConstructionCostPenalties::default(),
            feasible: false,
        };
        assert!(select_crossing_alternative(&[invalid, infeasible]).is_none());
    }
}
