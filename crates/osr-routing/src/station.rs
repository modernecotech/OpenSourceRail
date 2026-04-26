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
use crate::topology::{Line, LineShape};

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
    /// When this station is one platform of a multi-line interchange,
    /// every Station in the group carries the same id. None for
    /// stand-alone stops. Set by `merge_interchanges`.
    #[serde(default)]
    pub junction_group: Option<u32>,
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
        // Operator-supplied spacing rule for OSR auto-planned networks:
        // **1.2 km average between stations in inner areas, 2–5 km in
        // outer areas.** Stops in close proximity stretch dwell-budget
        // and add infrastructure cost without pulling new catchment.
        // Demand thresholds (`core_thr` / `urban_thr`) bin each cell:
        //   demand ≥ core_thr   → urban_core_m  (CBD / interchanges)
        //   demand ≥ urban_thr  → urban_m       (transitional ring)
        //   demand <  urban_thr → peri_urban_m  (outer suburb / rural)
        Self {
            urban_core_m: 1200.0,
            urban_m: 2000.0,
            peri_urban_m: 4000.0,
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

    // Place a station at the endpoint — but only if it isn't going to
    // sit right on top of the previous one. The previous spacing pass
    // can drop a station ~80 % of the way along the final segment;
    // forcing another one at the very end then produces a 200–300 m
    // pair (one of the "stops in close proximity" failure modes).
    // Threshold: the gap to the previous stop must be ≥ 60 % of the
    // local target spacing, else we just re-snap the last placed
    // station to the endpoint cell instead of adding a new one.
    let last_cell = *cells.last().unwrap();
    let last_station_cell = stations
        .last()
        .map(|s| (s.row, s.col))
        .unwrap_or((usize::MAX, usize::MAX));
    if last_station_cell != last_cell {
        let last_demand = grid.demand_at(last_cell.0, last_cell.1);
        let target = if last_demand >= cfg.core_thr {
            cfg.urban_core_m
        } else if last_demand >= cfg.urban_thr {
            cfg.urban_m
        } else {
            cfg.peri_urban_m
        };
        if since_last >= 0.6 * target {
            stations.push(make_station(grid, anchors, line_name, last_cell, s_m, cfg));
        } else if let Some(last) = stations.last_mut() {
            // Re-snap the existing tail station to the actual endpoint
            // so the line still terminates on its anchor cell.
            let snapped = make_station(grid, anchors, line_name, last_cell, s_m, cfg);
            *last = snapped;
        }
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

    // Look for an anchor within snap_radius_cells. Score is
    //     weight × (1 - d²/r²)
    // so high-weight POIs (universities w=1.0, airports w=1.0,
    // hospitals w=0.9) win over a slightly closer low-weight
    // `place=neighbourhood` (w=0.6). Without this weighting, the
    // 2026-04-26 anchor expansion (adding place=*, aeroway=*)
    // displaced top-priority POIs from station snaps because their
    // POI centroid was a few cells further from the routed path
    // than a generic neighbourhood label.
    let r2 = (cfg.snap_radius_cells * cfg.snap_radius_cells) as f32;
    let mut best_score: f32 = 0.0;
    for a in anchors {
        let dr = a.row as isize - row as isize;
        let dc = a.col as isize - col as isize;
        let d2 = (dr * dr + dc * dc) as f32;
        if d2 > r2 {
            continue;
        }
        let score = a.weight * (1.0 - d2 / r2);
        if score > best_score {
            best_score = score;
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
        junction_group: None,
    }
}

/// Force a single CBD interchange.
///
/// For every *radial* line whose cell sequence enters the hub
/// (within `hub_radius_cells` of `hub`), this drops any in-line stations
/// that fall inside the hub circle and inserts one fresh station at the
/// hub cell exactly. After `merge_interchanges`, those per-line hub
/// stations collapse into a single multi-platform interchange — fixing
/// the "lines do not meet downtown" failure mode where 3 radials each
/// dropped their nearest-to-centre stop on a different block (~250-400 m
/// apart) and never merged.
///
/// Ring lines are skipped: rings are *meant* to bypass the centre.
pub fn force_hub_stations(
    stations: &mut Vec<Station>,
    lines: &[Line],
    hub: (usize, usize),
    grid: &Grid,
    anchors: &[Anchor],
    hub_radius_cells: usize,
) {
    let cell_m = grid.reference.cell_m;
    let hr = hub_radius_cells as f64;
    let hr2 = hr * hr;
    let (hub_r, hub_c) = hub;

    for line in lines {
        if !matches!(line.shape, LineShape::Radial) {
            continue;
        }
        // Closest cell on this line to the hub.
        let mut best_i = 0_usize;
        let mut best_d2 = f64::INFINITY;
        for (i, &(r, c)) in line.cells.iter().enumerate() {
            let dr = r as f64 - hub_r as f64;
            let dc = c as f64 - hub_c as f64;
            let d2 = dr * dr + dc * dc;
            if d2 < best_d2 {
                best_d2 = d2;
                best_i = i;
            }
        }
        if best_d2 > hr2 {
            continue;
        }

        // Cumulative distance to best_i along the routed cells.
        let mut s_m_hub = 0.0_f64;
        for pair in line.cells[..=best_i].windows(2) {
            let dr = pair[1].0 as f64 - pair[0].0 as f64;
            let dc = pair[1].1 as f64 - pair[0].1 as f64;
            s_m_hub += (dr * dr + dc * dc).sqrt() * cell_m;
        }

        // Drop pre-existing stations on this line that lie inside the hub
        // circle — they would otherwise sit ~200 m from the forced hub
        // station and produce the close-pair artefact.
        stations.retain(|s| {
            if s.line_name != line.name {
                return true;
            }
            let dr = s.row as f64 - hub_r as f64;
            let dc = s.col as f64 - hub_c as f64;
            dr * dr + dc * dc > hr2
        });

        // Snap to the nearest anchor within ~8 cells (160 m) so the hub
        // station picks up a real downtown name when one is available.
        let mut anchor_id = None;
        let mut anchor_kind = None;
        let mut anchor_name = None;
        let snap_r2: isize = 64;
        let mut best_a2: isize = snap_r2 + 1;
        let (mut final_row, mut final_col) = hub;
        for a in anchors {
            let dr = a.row as isize - hub_r as isize;
            let dc = a.col as isize - hub_c as isize;
            let d2 = dr * dr + dc * dc;
            if d2 <= snap_r2 && d2 < best_a2 {
                best_a2 = d2;
                anchor_id = Some(a.id);
                anchor_kind = Some(a.kind.clone());
                anchor_name = a.name.clone();
                final_row = a.row;
                final_col = a.col;
            }
        }
        let (lat, lon) = grid.reference.rc_to_latlon(final_row, final_col);
        let demand = grid.demand_at(final_row, final_col);
        stations.push(Station {
            row: final_row,
            col: final_col,
            lat,
            lon,
            anchor_id,
            anchor_kind,
            anchor_name,
            line_name: line.name.clone(),
            s_m: s_m_hub,
            demand,
            junction_group: None,
        });
    }

    // Keep stations grouped by line and ordered along each line so the
    // emitters (which iterate in order) produce a clean polyline.
    stations.sort_by(|a, b| {
        a.line_name.cmp(&b.line_name).then(
            a.s_m
                .partial_cmp(&b.s_m)
                .unwrap_or(std::cmp::Ordering::Equal),
        )
    });
}

/// Force interchange stations at every ring↔radial crossing.
///
/// Without this, ring stations are placed only by `place_stations` at
/// in-line spacing intervals — which means a radial that crosses the
/// ring usually does so *between* two ring stations, leaving no
/// transfer point. The map then shows a ring "with no connections" even
/// though it geometrically intersects every radial.
///
/// For each (radial, ring) pair we walk the radial, tracking the
/// distance to the nearest ring cell. Each dip below
/// `crossing_threshold_cells` is a crossing — we take the cell-pair at
/// the dip's minimum and force a station on each line there. After
/// `merge_interchanges`, those station-pairs collapse into one
/// interchange complex.
pub fn force_ring_radial_crossings(
    stations: &mut Vec<Station>,
    lines: &[Line],
    grid: &Grid,
    anchors: &[Anchor],
    crossing_threshold_cells: usize,
) {
    let thr2 = (crossing_threshold_cells * crossing_threshold_cells) as i64;
    let n = lines.len();
    for i in 0..n {
        for j in 0..n {
            if i == j {
                continue;
            }
            let (rad, ring) = match (&lines[i].shape, &lines[j].shape) {
                (LineShape::Radial, LineShape::Ring) => (&lines[i], &lines[j]),
                _ => continue,
            };
            if rad.cells.is_empty() || ring.cells.is_empty() {
                continue;
            }
            // Per-radial-cell, distance² to the nearest ring cell + which cell.
            let mut min_d2: Vec<i64> = Vec::with_capacity(rad.cells.len());
            let mut nearest: Vec<usize> = Vec::with_capacity(rad.cells.len());
            for &(rr, rc) in &rad.cells {
                let mut best = i64::MAX;
                let mut best_k = 0_usize;
                for (k, &(gr, gc)) in ring.cells.iter().enumerate() {
                    let dr = rr as i64 - gr as i64;
                    let dc = rc as i64 - gc as i64;
                    let d2 = dr * dr + dc * dc;
                    if d2 < best {
                        best = d2;
                        best_k = k;
                    }
                }
                min_d2.push(best);
                nearest.push(best_k);
            }
            // Local minima of min_d2 that dip below the threshold.
            let mut crossings: Vec<usize> = Vec::new();
            let mut p = 0_usize;
            while p < min_d2.len() {
                if min_d2[p] <= thr2 {
                    let mut best_p = p;
                    let mut best_d = min_d2[p];
                    while p < min_d2.len() && min_d2[p] <= thr2 {
                        if min_d2[p] < best_d {
                            best_d = min_d2[p];
                            best_p = p;
                        }
                        p += 1;
                    }
                    crossings.push(best_p);
                } else {
                    p += 1;
                }
            }
            for &cidx in &crossings {
                let cell = rad.cells[cidx];
                let s_m_rad = cumulative_m(&rad.cells, cidx, grid.reference.cell_m);
                replace_station_near(stations, &rad.name, cell, s_m_rad, grid, anchors);

                let k = nearest[cidx];
                let ring_cell = ring.cells[k];
                let s_m_ring = cumulative_m(&ring.cells, k, grid.reference.cell_m);
                replace_station_near(stations, &ring.name, ring_cell, s_m_ring, grid, anchors);
            }
        }
    }
    stations.sort_by(|a, b| {
        a.line_name.cmp(&b.line_name).then(
            a.s_m
                .partial_cmp(&b.s_m)
                .unwrap_or(std::cmp::Ordering::Equal),
        )
    });
}

fn cumulative_m(cells: &[(usize, usize)], up_to: usize, cell_m: f64) -> f64 {
    let mut s = 0.0_f64;
    for pair in cells[..=up_to].windows(2) {
        let dr = pair[1].0 as f64 - pair[0].0 as f64;
        let dc = pair[1].1 as f64 - pair[0].1 as f64;
        s += (dr * dr + dc * dc).sqrt() * cell_m;
    }
    s
}

/// Drop stations on `line_name` within ~6 cells of `cell`, then insert
/// a fresh station at `cell` (anchor-snapped within 8 cells).
fn replace_station_near(
    stations: &mut Vec<Station>,
    line_name: &str,
    cell: (usize, usize),
    s_m: f64,
    grid: &Grid,
    anchors: &[Anchor],
) {
    let (cr, cc) = (cell.0 as isize, cell.1 as isize);
    stations.retain(|s| {
        if s.line_name != line_name {
            return true;
        }
        let dr = s.row as isize - cr;
        let dc = s.col as isize - cc;
        dr * dr + dc * dc > 36 // 6 cells = 120 m
    });

    let mut anchor_id = None;
    let mut anchor_kind = None;
    let mut anchor_name = None;
    let snap_r2: i64 = 64;
    let mut best_a2 = snap_r2 + 1;
    let (mut row, mut col) = cell;
    for a in anchors {
        let dr = a.row as i64 - cell.0 as i64;
        let dc = a.col as i64 - cell.1 as i64;
        let d2 = dr * dr + dc * dc;
        if d2 <= snap_r2 && d2 < best_a2 {
            best_a2 = d2;
            anchor_id = Some(a.id);
            anchor_kind = Some(a.kind.clone());
            anchor_name = a.name.clone();
            row = a.row;
            col = a.col;
        }
    }
    let (lat, lon) = grid.reference.rc_to_latlon(row, col);
    let demand = grid.demand_at(row, col);
    stations.push(Station {
        row,
        col,
        lat,
        lon,
        anchor_id,
        anchor_kind,
        anchor_name,
        line_name: line_name.to_string(),
        s_m,
        demand,
        junction_group: None,
    });
}

/// Cross-line interchange merging.
///
/// Within `merge_radius_m` (default 250 m) of each other, stations on
/// *different* lines are grouped into one interchange. Each grouped
/// station has its (lat, lon) snapped to the group centroid and its
/// `junction_group` set to a stable id, so downstream emitters can
/// render them as a single interchange complex with one platform per
/// line. Stations on the same line are never merged (in-line spacing
/// is enforced separately by `place_stations`).
///
/// This addresses the "multiple stations in close proximity in central
/// zones" failure mode — when 3 radial lines all pass through downtown
/// they previously dropped 3 stations within ~150 m of each other.
pub fn merge_interchanges(stations: &mut [Station], merge_radius_m: f64) {
    let n = stations.len();
    if n < 2 {
        return;
    }

    // Union-find by lat/lon proximity, only across distinct lines.
    let mut parent: Vec<usize> = (0..n).collect();
    fn find(parent: &mut [usize], x: usize) -> usize {
        if parent[x] == x {
            x
        } else {
            let r = find(parent, parent[x]);
            parent[x] = r;
            r
        }
    }
    let r2 = merge_radius_m * merge_radius_m;
    for i in 0..n {
        for j in (i + 1)..n {
            if stations[i].line_name == stations[j].line_name {
                continue;
            }
            let d2 = haversine_sq_m(
                stations[i].lat,
                stations[i].lon,
                stations[j].lat,
                stations[j].lon,
            );
            if d2 <= r2 {
                let ri = find(&mut parent, i);
                let rj = find(&mut parent, j);
                if ri != rj {
                    parent[ri] = rj;
                }
            }
        }
    }

    // Materialize groups. Singletons get no group id.
    let mut group_of: Vec<usize> = (0..n).map(|i| find(&mut parent, i)).collect();
    let mut counts = std::collections::HashMap::<usize, usize>::new();
    for &g in &group_of {
        *counts.entry(g).or_default() += 1;
    }
    let mut id_map = std::collections::HashMap::<usize, u32>::new();
    let mut next_id: u32 = 0;
    for &g in &group_of {
        if counts[&g] >= 2 && !id_map.contains_key(&g) {
            id_map.insert(g, next_id);
            next_id += 1;
        }
    }

    // Centroid per group.
    let mut sums: std::collections::HashMap<usize, (f64, f64, usize)> =
        std::collections::HashMap::new();
    for (i, &g) in group_of.iter().enumerate() {
        if counts[&g] < 2 {
            continue;
        }
        let e = sums.entry(g).or_insert((0.0, 0.0, 0));
        e.0 += stations[i].lat;
        e.1 += stations[i].lon;
        e.2 += 1;
    }

    for (i, g) in group_of.iter_mut().enumerate() {
        if counts[g] < 2 {
            continue;
        }
        let (slat, slon, k) = sums[g];
        stations[i].lat = slat / k as f64;
        stations[i].lon = slon / k as f64;
        stations[i].junction_group = Some(id_map[g]);
    }
}

fn haversine_sq_m(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    let to_rad = std::f64::consts::PI / 180.0;
    let dlat = (lat2 - lat1) * to_rad;
    let dlon = (lon2 - lon1) * to_rad;
    let mid_lat = ((lat1 + lat2) * 0.5) * to_rad;
    let r = 6_371_000.0_f64;
    let dy = r * dlat;
    let dx = r * mid_lat.cos() * dlon;
    dy * dy + dx * dx
}

#[cfg(test)]
mod tests {
    use super::*;

    fn st(line: &str, lat: f64, lon: f64) -> Station {
        Station {
            row: 0,
            col: 0,
            lat,
            lon,
            anchor_id: None,
            anchor_kind: None,
            anchor_name: None,
            line_name: line.to_string(),
            s_m: 0.0,
            demand: 0.0,
            junction_group: None,
        }
    }

    #[test]
    fn merge_groups_close_cross_line_stations() {
        // Three lines crossing within ~50 m of (0.001, 0.001).
        let mut s = vec![
            st("L1", 0.001, 0.001),
            st("L2", 0.001003, 0.0010005),
            st("L3", 0.001, 0.001002),
            // Far-away station on L1 — should not be merged.
            st("L1", 0.05, 0.05),
        ];
        merge_interchanges(&mut s, 250.0);
        let g0 = s[0].junction_group;
        let g1 = s[1].junction_group;
        let g2 = s[2].junction_group;
        assert!(g0.is_some());
        assert_eq!(g0, g1);
        assert_eq!(g0, g2);
        assert_eq!(s[3].junction_group, None);
        // Merged stations share centroid lat/lon.
        assert!((s[0].lat - s[1].lat).abs() < 1e-9);
        assert!((s[0].lon - s[1].lon).abs() < 1e-9);
    }

    #[test]
    fn merge_does_not_combine_same_line_stations() {
        let mut s = vec![
            st("L1", 0.001, 0.001),
            st("L1", 0.001005, 0.001005),
        ];
        merge_interchanges(&mut s, 250.0);
        assert_eq!(s[0].junction_group, None);
        assert_eq!(s[1].junction_group, None);
    }
}
