//! Civil-class assignment per polyline segment.
//!
//! Given a line's cell sequence, look at what each cell sits on (from the
//! underlying cost surface) and classify the segment as at-grade /
//! elevated / bored-tunnel / cut-and-cover.
//!
//! Heuristic: the cost raster already encodes "how built-up / constrained"
//! a cell is. So:
//!   - low cost (on arterial)     → at-grade
//!   - medium cost (side-street)  → at-grade (tight but feasible)
//!   - high cost (park, through a gap between buildings) → elevated
//!   - water cells                → bridge
//!   - cells that would have been buildings had we been allowed to pass
//!     through them (inferred by finite cost > tunnel_thr after cost
//!     surface smoothing) → tunnel. In practice the solver never routes
//!     through buildings, so tunnel selection instead fires when a
//!     segment runs through a dense cluster that forced the solver into
//!     a narrow gap.

use serde::{Deserialize, Serialize};

use crate::raster::Grid;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum CivilClass {
    AtGrade,
    Elevated,
    Bridge,
    CutAndCoverTunnel,
    BoredTunnel,
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
            let length_m = segment_length_m(grid, &cells[run_start..i]);
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
    //   building       = 600    → bored tunnel
    if cost < 40.0 {
        CivilClass::AtGrade
    } else if cost < 100.0 {
        CivilClass::Elevated
    } else if cost < 400.0 {
        CivilClass::Bridge
    } else {
        // Buildings — solver tunnelled through.
        CivilClass::BoredTunnel
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
