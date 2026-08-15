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

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CivilSegment {
    pub class: CivilClass,
    /// Inclusive cell index range into the parent line's `cells`.
    pub from_idx: usize,
    pub to_idx: usize,
    pub length_m: f64,
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

    // Collapse runs.
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
            segments.push(CivilSegment {
                class: classes[run_start],
                from_idx: run_start,
                to_idx: i - 1,
                length_m,
            });
            run_start = i;
        }
    }
    segments
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
    }
}
