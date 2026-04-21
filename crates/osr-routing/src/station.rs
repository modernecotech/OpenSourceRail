//! Station placement — walk a line's cell sequence and drop stations at
//! the spacing given by the recipe (urban_core_m / urban_m / peri_urban_m),
//! snapping to nearby anchors when one is within a small search radius.
//!
//! The spacing band is chosen from local demand intensity: high demand
//! → urban_core spacing, medium → urban, low → peri_urban. This gives
//! the density-aware "closer stops downtown, wider at the edges" pattern
//! real metros exhibit without requiring a separate population input.

use serde::{Deserialize, Serialize};

use crate::raster::{Anchor, Grid};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Station {
    pub row: usize,
    pub col: usize,
    pub lat: f64,
    pub lon: f64,
    /// Optional — set when the station snapped to a named OSM anchor.
    pub anchor_id: Option<i64>,
    pub anchor_kind: Option<String>,
    pub anchor_name: Option<String>,
    /// Which line this station belongs to.
    pub line_name: String,
    /// Distance along the line, in metres.
    pub s_m: f64,
    /// Local demand at this cell, for archetype selection downstream.
    pub demand: f32,
}

/// Spacing thresholds come from the recipe defaults (Step 5) but are
/// overridable by the orchestrator. Distances in metres.
#[derive(Debug, Clone, Copy)]
pub struct SpacingConfig {
    pub urban_core_m: f64,
    pub urban_m: f64,
    pub peri_urban_m: f64,
    /// Demand thresholds — cells above `core_thr` get urban_core spacing,
    /// above `urban_thr` get urban, below get peri_urban.
    pub core_thr: f32,
    pub urban_thr: f32,
    /// Search radius in cells for anchor-snap.
    pub snap_radius_cells: usize,
}

impl Default for SpacingConfig {
    fn default() -> Self {
        Self {
            urban_core_m: 800.0,
            urban_m: 1200.0,
            peri_urban_m: 1800.0,
            core_thr: 0.6,
            urban_thr: 0.25,
            snap_radius_cells: 6,
        }
    }
}

#[must_use]
pub fn place_stations(
    grid: &Grid,
    anchors: &[Anchor],
    line_name: &str,
    cells: &[(usize, usize)],
    cfg: SpacingConfig,
) -> Vec<Station> {
    if cells.len() < 2 {
        return Vec::new();
    }

    let mut stations: Vec<Station> = Vec::new();

    // Always place a station at the very first cell (endpoint).
    stations.push(make_station(grid, anchors, line_name, cells[0], 0.0, cfg));

    let mut s_m = 0.0_f64;
    let mut since_last = 0.0_f64;

    for pair in cells.windows(2) {
        let (r0, c0) = pair[0];
        let (r1, c1) = pair[1];
        let dr = (r1 as f64 - r0 as f64).abs();
        let dc = (c1 as f64 - c0 as f64).abs();
        let step_cells = (dr * dr + dc * dc).sqrt();
        let step_m = step_cells * grid.reference.cell_m;
        s_m += step_m;
        since_last += step_m;

        let local_demand = grid.demand_at(r1, c1);
        let target = if local_demand >= cfg.core_thr {
            cfg.urban_core_m
        } else if local_demand >= cfg.urban_thr {
            cfg.urban_m
        } else {
            cfg.peri_urban_m
        };

        if since_last >= target {
            let st = make_station(grid, anchors, line_name, (r1, c1), s_m, cfg);
            stations.push(st);
            since_last = 0.0;
        }
    }

    // Always place one at the endpoint if we did not just place one.
    let last_cell = *cells.last().unwrap();
    let last_station_cell = stations
        .last()
        .map(|s| (s.row, s.col))
        .unwrap_or((usize::MAX, usize::MAX));
    if last_station_cell != last_cell {
        stations.push(make_station(grid, anchors, line_name, last_cell, s_m, cfg));
    }

    stations
}

fn make_station(
    grid: &Grid,
    anchors: &[Anchor],
    line_name: &str,
    cell: (usize, usize),
    s_m: f64,
    cfg: SpacingConfig,
) -> Station {
    let (row, col) = cell;
    let (mut final_row, mut final_col) = cell;
    let mut anchor_id = None;
    let mut anchor_kind = None;
    let mut anchor_name = None;

    // Look for an anchor within snap_radius_cells.
    let mut best_d2: isize = (cfg.snap_radius_cells * cfg.snap_radius_cells) as isize;
    for a in anchors {
        let dr = a.row as isize - row as isize;
        let dc = a.col as isize - col as isize;
        let d2 = dr * dr + dc * dc;
        if d2 <= best_d2 {
            best_d2 = d2;
            final_row = a.row;
            final_col = a.col;
            anchor_id = Some(a.id);
            anchor_kind = Some(a.kind.clone());
            anchor_name = a.name.clone();
        }
    }

    let (lat, lon) = grid.reference.rc_to_latlon(final_row, final_col);
    let demand = grid.demand_at(final_row.min(grid.reference.height - 1), final_col.min(grid.reference.width - 1));
    Station {
        row: final_row,
        col: final_col,
        lat,
        lon,
        anchor_id,
        anchor_kind,
        anchor_name,
        line_name: line_name.to_string(),
        s_m,
        demand,
    }
}
