//! Station placement — walk a line's cell sequence and drop stations at
//! the spacing given by the recipe (urban_core_m / urban_m / peri_urban_m /
//! outer_m),
//! snapping to nearby anchors when one is within a small search radius.
//!
//! The spacing band is chosen from local demand intensity: high demand
//! → urban_core spacing, medium → urban, low → peri_urban/outer. This gives
//! the density-aware "closer stops downtown, wider at the edges" pattern
//! real metros exhibit without requiring a separate population input.

use serde::{Deserialize, Serialize};

use crate::raster::{Anchor, Grid};
use crate::solver::{solve_path_in_bbox, DemandWeight};
use crate::topology::{maximum_axis_backtrack_m, Line, LineShape, MAX_RADIAL_BACKTRACK_M};

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
    pub outer_m: f64,
    /// Demand thresholds — cells above `core_thr` get urban_core spacing,
    /// above `urban_thr` get urban, above `outer_thr` get peri-urban, and
    /// the lowest-demand fringe gets outer spacing.
    pub core_thr: f32,
    pub urban_thr: f32,
    pub outer_thr: f32,
    /// Search radius in cells for anchor-snap.
    pub snap_radius_cells: usize,
}

impl Default for SpacingConfig {
    fn default() -> Self {
        // Operator-supplied spacing rule for OSR auto-planned networks:
        // **1.6 km between stations in central areas, 3 km in the wider
        // urban area, and up to 7 km on suburban approaches / the
        // lowest-demand outer fringe.** Stops in close proximity stretch
        // dwell-budget and add infrastructure cost without pulling new catchment.
        // Demand thresholds bin each cell:
        //   demand ≥ core_thr   → urban_core_m  (CBD / interchanges)
        //   demand ≥ urban_thr  → urban_m       (ordinary city fabric)
        //   demand <  urban_thr → peri/outer_m  (suburban approaches / fringe)
        Self {
            urban_core_m: 1600.0,
            urban_m: 3000.0,
            peri_urban_m: 7000.0,
            outer_m: 7000.0,
            core_thr: 0.9,
            urban_thr: 0.35,
            outer_thr: 0.35,
            snap_radius_cells: 6,
        }
    }
}

fn spacing_for_demand(demand: f32, cfg: SpacingConfig) -> f64 {
    if demand >= cfg.core_thr {
        cfg.urban_core_m
    } else if demand >= cfg.urban_thr {
        cfg.urban_m
    } else if demand >= cfg.outer_thr {
        cfg.peri_urban_m
    } else {
        cfg.outer_m
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

    for (edge_index, pair) in cells.windows(2).enumerate() {
        let (r0, c0) = pair[0];
        let (r1, c1) = pair[1];
        let dr = (r1 as f64 - r0 as f64).abs();
        let dc = (c1 as f64 - c0 as f64).abs();
        let step_cells = (dr * dr + dc * dc).sqrt();
        let step_m = step_cells * grid.reference.cell_m;
        s_m += step_m;
        since_last += step_m;

        let local_demand = grid.demand_at(r1, c1);
        let target = spacing_for_demand(local_demand, cfg);

        let closes_loop = edge_index + 2 == cells.len() && (r1, c1) == cells[0];
        if since_last >= target && !closes_loop {
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
    // Threshold: the gap to the previous stop must be ≥ 75 % of the
    // local target spacing, else we just re-snap the last placed
    // station to the endpoint cell instead of adding a new one.
    let last_cell = *cells.last().unwrap();
    // A closed ring repeats its first route cell at the end. That is one
    // physical platform, not a second station with the same coordinate/ID.
    // Keeping only the chainage-zero record also gives downstream simulators
    // an unambiguous node for the loop closure.
    if last_cell == cells[0] {
        return stations;
    }
    let last_station_cell = stations
        .last()
        .map(|s| (s.row, s.col))
        .unwrap_or((usize::MAX, usize::MAX));
    if last_station_cell != last_cell {
        let last_demand = grid.demand_at(last_cell.0, last_cell.1);
        let target = spacing_for_demand(last_demand, cfg);
        if since_last >= 0.75 * target {
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
    let mut anchor_id = None;
    let mut anchor_kind = None;
    let mut anchor_name = None;

    // Look for an anchor within snap_radius_cells to **label** this
    // station. Score is `weight × (1 - d²/r²)` so high-weight POIs
    // (universities w=1.0, airports w=1.0, hospitals w=0.9) win over
    // a slightly closer low-weight `place=neighbourhood` (w=0.6).
    //
    // The station's geometric position is **always** kept on the
    // routed cell — earlier code overwrote `final_row` / `final_col`
    // with the anchor's coordinates, which moved the station marker
    // up to 500 m off the line corridor (snap_radius_cells × cell_m).
    // The render then drew the station floating in space next to the
    // routed polyline. Now we only attach the anchor's *metadata*
    // (id / kind / name) — the marker stays on the line.
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
            anchor_id = Some(a.id);
            anchor_kind = Some(a.kind.clone());
            anchor_name = a.name.clone();
        }
    }

    let (lat, lon) = grid.reference.rc_to_latlon(row, col);
    let demand = grid.demand_at(
        row.min(grid.reference.height - 1),
        col.min(grid.reference.width - 1),
    );
    Station {
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

        // Place the hub station **on the routed corridor** at the
        // line's closest cell to the hub (best_i). Earlier the
        // station was placed at `hub` itself or at an anchor near
        // the hub — both off the line — which rendered as a marker
        // floating up to 600 m from the actual rails. Anchor metadata
        // is still attached for labelling but no longer overrides
        // the geometric position.
        let (final_row, final_col) = line.cells[best_i];
        let mut anchor_id = None;
        let mut anchor_kind = None;
        let mut anchor_name = None;
        let snap_r2: isize = 64;
        let mut best_a2: isize = snap_r2 + 1;
        for a in anchors {
            let dr = a.row as isize - hub_r as isize;
            let dc = a.col as isize - hub_c as isize;
            let d2 = dr * dr + dc * dc;
            if d2 <= snap_r2 && d2 < best_a2 {
                best_a2 = d2;
                anchor_id = Some(a.id);
                anchor_kind = Some(a.kind.clone());
                anchor_name = a.name.clone();
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
                replace_station_near(
                    stations,
                    &rad.name,
                    grid,
                    anchors,
                    ReplacementSite {
                        cell,
                        chainage_m: s_m_rad,
                        preserve_route_endpoints: true,
                        radius_cells: 6,
                        chainage_window_m: 120.0,
                    },
                );

                let k = nearest[cidx];
                let ring_cell = ring.cells[k];
                let s_m_ring = cumulative_m(&ring.cells, k, grid.reference.cell_m);
                replace_station_near(
                    stations,
                    &ring.name,
                    grid,
                    anchors,
                    ReplacementSite {
                        cell: ring_cell,
                        chainage_m: s_m_ring,
                        preserve_route_endpoints: false,
                        radius_cells: 6,
                        chainage_window_m: 120.0,
                    },
                );
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

/// Restore exact route endpoints after forced interchange insertion.
///
/// Replacement within the ring/hub envelopes is intentionally aggressive,
/// but an operational line must retain a station at chainage zero and at its
/// declared end. A ring repeats its first cell at the end, so only chainage
/// zero is required for rings.
pub fn ensure_endpoint_stations(
    stations: &mut Vec<Station>,
    lines: &[Line],
    grid: &Grid,
    anchors: &[Anchor],
    cfg: SpacingConfig,
) {
    for line in lines {
        if line.cells.len() < 2 {
            continue;
        }
        let total_m = cumulative_m(&line.cells, line.cells.len() - 1, grid.reference.cell_m);
        if !stations
            .iter()
            .any(|station| station.line_name == line.name && station.s_m.abs() <= 1.0)
        {
            stations.push(make_station(
                grid,
                anchors,
                &line.name,
                line.cells[0],
                0.0,
                cfg,
            ));
        }
        if matches!(line.shape, LineShape::Radial)
            && !stations.iter().any(|station| {
                station.line_name == line.name && (total_m - station.s_m).abs() <= 1.0
            })
        {
            stations.push(make_station(
                grid,
                anchors,
                &line.name,
                *line.cells.last().unwrap(),
                total_m,
                cfg,
            ));
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

/// Force a paired ring platform for every radial terminal close to a ring.
///
/// A radial may already cross the same ring elsewhere. The general crossing
/// pass therefore cannot prove that the *terminal* has a transfer. This pass
/// evaluates both endpoints independently and places a ring platform at the
/// nearest ring cell whenever the terminal lies inside the transfer envelope.
pub fn force_ring_radial_terminal_interchanges(
    stations: &mut Vec<Station>,
    lines: &[Line],
    grid: &Grid,
    anchors: &[Anchor],
    transfer_threshold_cells: usize,
) {
    let threshold2 = (transfer_threshold_cells * transfer_threshold_cells) as i64;
    for radial in lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Radial) && !line.cells.is_empty())
    {
        let radial_length_m = radial
            .cells
            .windows(2)
            .map(|pair| {
                let dr = pair[1].0 as f64 - pair[0].0 as f64;
                let dc = pair[1].1 as f64 - pair[0].1 as f64;
                (dr * dr + dc * dc).sqrt() * grid.reference.cell_m
            })
            .sum::<f64>();
        for ring in lines
            .iter()
            .filter(|line| matches!(line.shape, LineShape::Ring) && !line.cells.is_empty())
        {
            for (endpoint, endpoint_chainage) in [
                (radial.cells[0], 0.0),
                (*radial.cells.last().unwrap(), radial_length_m),
            ] {
                let Some((distance2, ring_index)) = ring
                    .cells
                    .iter()
                    .enumerate()
                    .map(|(index, &cell)| {
                        let dr = endpoint.0 as i64 - cell.0 as i64;
                        let dc = endpoint.1 as i64 - cell.1 as i64;
                        (dr * dr + dc * dc, index)
                    })
                    .min_by_key(|item| item.0)
                else {
                    continue;
                };
                if distance2 > threshold2 {
                    continue;
                }
                replace_station_near(
                    stations,
                    &radial.name,
                    grid,
                    anchors,
                    ReplacementSite {
                        cell: endpoint,
                        chainage_m: endpoint_chainage,
                        preserve_route_endpoints: false,
                        radius_cells: 60,
                        chainage_window_m: 1200.0,
                    },
                );
                let ring_cell = ring.cells[ring_index];
                let ring_chainage = cumulative_m(&ring.cells, ring_index, grid.reference.cell_m);
                replace_station_near(
                    stations,
                    &ring.name,
                    grid,
                    anchors,
                    ReplacementSite {
                        cell: ring_cell,
                        chainage_m: ring_chainage,
                        preserve_route_endpoints: false,
                        radius_cells: 60,
                        chainage_window_m: 1200.0,
                    },
                );
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

/// Extend radial endpoints that stop just short of a ring onto the ring.
///
/// A 600 m or shorter separation is handled as one station complex by
/// `force_ring_radial_crossings`. For a 600–1200 m endpoint near-miss, route a
/// short physical connector through the same buildability/cost grid and make
/// the ring cell the new terminus. Longer gaps are left for topology review;
/// silently adding kilometres of scope is not an interchange correction.
pub fn connect_radial_termini_to_rings(
    lines: &mut [Line],
    grid: &Grid,
    transfer_threshold_cells: usize,
    extension_threshold_cells: usize,
    demand_w: DemandWeight,
) -> usize {
    let ring_cells: Vec<(usize, usize)> = lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Ring))
        .flat_map(|line| line.cells.iter().copied())
        .collect();
    if ring_cells.is_empty() {
        return 0;
    }
    let transfer2 = (transfer_threshold_cells * transfer_threshold_cells) as i64;
    let extension2 = (extension_threshold_cells * extension_threshold_cells) as i64;
    let mut extended = 0;
    for line in lines.iter_mut() {
        if !matches!(line.shape, LineShape::Radial) || line.cells.len() < 2 {
            continue;
        }
        for at_start in [true, false] {
            let endpoint = if at_start {
                line.cells[0]
            } else {
                *line.cells.last().unwrap()
            };
            let mut targets: Vec<(i64, (usize, usize))> = ring_cells
                .iter()
                .map(|&cell| {
                    let dr = endpoint.0 as i64 - cell.0 as i64;
                    let dc = endpoint.1 as i64 - cell.1 as i64;
                    (dr * dr + dc * dc, cell)
                })
                .filter(|(distance2, _)| *distance2 > transfer2 && *distance2 <= extension2)
                .collect();
            targets.sort_by_key(|item| item.0);
            if targets.is_empty() {
                continue;
            }
            for (_, target) in targets {
                let margin = transfer_threshold_cells;
                let bbox = (
                    (
                        endpoint.0.min(target.0).saturating_sub(margin),
                        endpoint.1.min(target.1).saturating_sub(margin),
                    ),
                    (
                        (endpoint.0.max(target.0) + margin).min(grid.reference.height - 1),
                        (endpoint.1.max(target.1) + margin).min(grid.reference.width - 1),
                    ),
                );
                let Ok(mut connector) =
                    solve_path_in_bbox(grid, endpoint, target, demand_w, None, Some(bbox))
                else {
                    continue;
                };
                let mut candidate = line.cells.clone();
                if at_start {
                    connector.reverse();
                    connector.pop(); // original endpoint is already candidate[0]
                    connector.extend(candidate);
                    candidate = connector;
                } else {
                    candidate.extend(connector.into_iter().skip(1));
                }
                if maximum_axis_backtrack_m(&candidate, grid.reference.cell_m)
                    >= MAX_RADIAL_BACKTRACK_M
                {
                    continue;
                }
                line.cells = candidate;
                extended += 1;
                break;
            }
        }
    }
    extended
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

struct ReplacementSite {
    cell: (usize, usize),
    chainage_m: f64,
    preserve_route_endpoints: bool,
    radius_cells: usize,
    chainage_window_m: f64,
}

/// Drop stations on `line_name` near the replacement site, then insert
/// a fresh station there (anchor-snapped within 8 cells).
fn replace_station_near(
    stations: &mut Vec<Station>,
    line_name: &str,
    grid: &Grid,
    anchors: &[Anchor],
    site: ReplacementSite,
) {
    let cell = site.cell;
    let (cr, cc) = (cell.0 as isize, cell.1 as isize);
    let line_end_chainage = stations
        .iter()
        .filter(|station| station.line_name == line_name)
        .map(|station| station.s_m)
        .fold(0.0_f64, f64::max);
    // A crossing close to a terminal uses that terminal as the transfer
    // platform. Never replace it with a nearby in-line point: doing so can
    // leave the operational route 20–120 m short of its declared endpoint.
    if site.preserve_route_endpoints
        && stations.iter().any(|station| {
            if station.line_name != line_name
                || (station.s_m > 1.0 && (line_end_chainage - station.s_m).abs() > 1.0)
            {
                return false;
            }
            let dr = station.row as isize - cr;
            let dc = station.col as isize - cc;
            dr * dr + dc * dc <= 36
        })
    {
        return;
    }
    let replacement_radius2 = (site.radius_cells * site.radius_cells) as isize;
    stations.retain(|s| {
        if s.line_name != line_name {
            return true;
        }
        let dr = s.row as isize - cr;
        let dc = s.col as isize - cc;
        dr * dr + dc * dc > replacement_radius2
            && (s.s_m - site.chainage_m).abs() >= site.chainage_window_m
    });

    // Anchor metadata only — keep the geometric position on the
    // routed corridor (`cell`). Earlier code overwrote (row, col)
    // with the anchor's coordinates, which moved the ring↔radial
    // crossing station off the line.
    let mut anchor_id = None;
    let mut anchor_kind = None;
    let mut anchor_name = None;
    let snap_r2: i64 = 64;
    let mut best_a2 = snap_r2 + 1;
    let (row, col) = cell;
    for a in anchors {
        let dr = a.row as i64 - cell.0 as i64;
        let dc = a.col as i64 - cell.1 as i64;
        let d2 = dr * dr + dc * dc;
        if d2 <= snap_r2 && d2 < best_a2 {
            best_a2 = d2;
            anchor_id = Some(a.id);
            anchor_kind = Some(a.kind.clone());
            anchor_name = a.name.clone();
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
        s_m: site.chainage_m,
        demand,
        junction_group: None,
    });
}

/// Cross-line interchange merging.
///
/// Within `merge_radius_m` (default 250 m) of each other, stations on
/// *different* lines are grouped into one interchange. Neighbouring
/// interchange groups on the same line are then amalgamated into one
/// multi-line complex. Each grouped
/// station has its (lat, lon) snapped to the group centroid and its
/// `junction_group` set to a stable id, so downstream emitters can
/// render them as a single interchange complex with one platform per
/// line. Ordinary stations on the same line are never merged.
///
/// This addresses the "multiple stations in close proximity in central
/// zones" failure mode — when 3 radial lines all pass through downtown
/// they previously dropped 3 stations within ~150 m of each other.
pub fn merge_interchanges(stations: &mut [Station], merge_radius_m: f64) {
    // This function may run once before and once after consolidation. Always
    // rebuild group IDs from the current station set so a removed transfer
    // platform cannot leave a stale singleton junction behind.
    for station in stations.iter_mut() {
        station.junction_group = None;
    }
    let n = stations.len();
    if n < 2 {
        return;
    }

    // Union-find by lat/lon proximity, only across distinct lines. The routing
    // invariants are evaluated on the 20 m raster, while station coordinates
    // are later converted back to geodesic lat/lon. Accept either measure so a
    // forced raster-envelope transfer cannot be stranded by projection drift.
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
            let geo_d2 = haversine_sq_m(
                stations[i].lat,
                stations[i].lon,
                stations[j].lat,
                stations[j].lon,
            );
            let dr = stations[i].row as f64 - stations[j].row as f64;
            let dc = stations[i].col as f64 - stations[j].col as f64;
            let grid_d2 = (dr * dr + dc * dc) * 20.0 * 20.0;
            if geo_d2 <= r2 || (grid_d2 > 0.0 && grid_d2 <= r2) {
                let ri = find(&mut parent, i);
                let rj = find(&mut parent, j);
                if ri != rj {
                    parent[ri] = rj;
                }
            }
        }
    }

    // If two independently formed interchanges sit on the same line inside
    // one 1.2 km station envelope, treat them as a single multi-change
    // complex. This is the explicit exception to ordinary in-line spacing;
    // ordinary cross-line grouping remains at the stricter 600 m envelope.
    let mut component_lines =
        std::collections::HashMap::<usize, std::collections::BTreeSet<&str>>::new();
    for (index, station) in stations.iter().enumerate() {
        let root = find(&mut parent, index);
        component_lines
            .entry(root)
            .or_default()
            .insert(station.line_name.as_str());
    }
    let multichange_r2 = (2.0 * merge_radius_m) * (2.0 * merge_radius_m);
    for i in 0..n {
        for j in (i + 1)..n {
            if stations[i].line_name != stations[j].line_name {
                continue;
            }
            let ri = find(&mut parent, i);
            let rj = find(&mut parent, j);
            if ri == rj
                || component_lines.get(&ri).map_or(0, |lines| lines.len()) < 2
                || component_lines.get(&rj).map_or(0, |lines| lines.len()) < 2
            {
                continue;
            }
            let geo_d2 = haversine_sq_m(
                stations[i].lat,
                stations[i].lon,
                stations[j].lat,
                stations[j].lon,
            );
            let dr = stations[i].row as f64 - stations[j].row as f64;
            let dc = stations[i].col as f64 - stations[j].col as f64;
            let grid_d2 = (dr * dr + dc * dc) * 20.0 * 20.0;
            if geo_d2 <= multichange_r2 || (grid_d2 > 0.0 && grid_d2 <= multichange_r2) {
                parent[ri] = rj;
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

    // Tag interchange members with a stable junction_group id, but
    // **leave each station's geometry on its own line**. Earlier code
    // averaged the cluster's lat/lon and overwrote each member's
    // coordinates with the centroid — which moved every interchange
    // platform off the routed corridor (the centroid sits between the
    // two lines, on neither). The junction_group id alone is enough
    // for the map renderer / emitter to know "these N stations are
    // one complex"; if a deployment wants to render the cluster as a
    // single visual point the renderer can compute the centroid
    // on-the-fly from the per-line platforms.
    for (i, g) in group_of.iter_mut().enumerate() {
        if counts[g] < 2 {
            continue;
        }
        stations[i].junction_group = Some(id_map[g]);
    }
}

/// Give every mandatory ring/radial raster-envelope approach a shared
/// interchange group on the nearest retained platforms.
///
/// This is a final repair for sparse-spacing networks: the forced platform may
/// be consolidated into a nearby same-line platform, but the retained platform
/// still represents that walkable transfer complex.
pub fn force_ring_radial_group_ids(
    stations: &mut [Station],
    lines: &[Line],
    cell_m: f64,
    transfer_envelope_m: f64,
) {
    if stations.len() < 2 {
        return;
    }
    let mut next_group = stations
        .iter()
        .filter_map(|station| station.junction_group)
        .max()
        .map_or(0, |group| group + 1);
    let transfer2 = transfer_envelope_m * transfer_envelope_m;
    let station_index = |line_name: &str, target: (usize, usize), stations: &[Station]| {
        stations
            .iter()
            .enumerate()
            .filter(|(_, station)| station.line_name == line_name)
            .map(|(index, station)| {
                let dr = station.row as f64 - target.0 as f64;
                let dc = station.col as f64 - target.1 as f64;
                (index, (dr * dr + dc * dc) * cell_m * cell_m)
            })
            .min_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
    };

    for radial in lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Radial) && !line.cells.is_empty())
    {
        for ring in lines
            .iter()
            .filter(|line| matches!(line.shape, LineShape::Ring) && !line.cells.is_empty())
        {
            let Some((radial_cell, ring_cell, closest2)) = radial
                .cells
                .iter()
                .flat_map(|&radial_cell| {
                    ring.cells.iter().map(move |&ring_cell| {
                        let dr = radial_cell.0 as f64 - ring_cell.0 as f64;
                        let dc = radial_cell.1 as f64 - ring_cell.1 as f64;
                        (
                            radial_cell,
                            ring_cell,
                            (dr * dr + dc * dc) * cell_m * cell_m,
                        )
                    })
                })
                .min_by(|a, b| a.2.partial_cmp(&b.2).unwrap_or(std::cmp::Ordering::Equal))
            else {
                continue;
            };
            if closest2 > transfer2 {
                continue;
            }
            let Some((radial_index, _)) = station_index(&radial.name, radial_cell, stations) else {
                continue;
            };
            let Some((ring_index, _)) = station_index(&ring.name, ring_cell, stations) else {
                continue;
            };
            let group = stations[radial_index]
                .junction_group
                .or(stations[ring_index].junction_group)
                .unwrap_or_else(|| {
                    let group = next_group;
                    next_group += 1;
                    group
                });
            if let Some(other) = stations[radial_index].junction_group {
                if other != group {
                    for station in stations.iter_mut() {
                        if station.junction_group == Some(other) {
                            station.junction_group = Some(group);
                        }
                    }
                }
            }
            if let Some(other) = stations[ring_index].junction_group {
                if other != group {
                    for station in stations.iter_mut() {
                        if station.junction_group == Some(other) {
                            station.junction_group = Some(group);
                        }
                    }
                }
            }
            stations[radial_index].junction_group = Some(group);
            stations[ring_index].junction_group = Some(group);

            for endpoint in [radial.cells[0], *radial.cells.last().unwrap()] {
                let Some((ring_endpoint_cell, endpoint_distance2)) = ring
                    .cells
                    .iter()
                    .map(|&ring_cell| {
                        let dr = endpoint.0 as f64 - ring_cell.0 as f64;
                        let dc = endpoint.1 as f64 - ring_cell.1 as f64;
                        (ring_cell, (dr * dr + dc * dc) * cell_m * cell_m)
                    })
                    .min_by(|a, b| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
                else {
                    continue;
                };
                if endpoint_distance2 > transfer2 {
                    continue;
                }
                let Some((radial_endpoint_index, _)) =
                    station_index(&radial.name, endpoint, stations)
                else {
                    continue;
                };
                let Some((ring_endpoint_index, _)) =
                    station_index(&ring.name, ring_endpoint_cell, stations)
                else {
                    continue;
                };
                let endpoint_group = stations[radial_endpoint_index]
                    .junction_group
                    .or(stations[ring_endpoint_index].junction_group)
                    .unwrap_or_else(|| {
                        let group = next_group;
                        next_group += 1;
                        group
                    });
                for index in [radial_endpoint_index, ring_endpoint_index] {
                    if let Some(other) = stations[index].junction_group {
                        if other != endpoint_group {
                            for station in stations.iter_mut() {
                                if station.junction_group == Some(other) {
                                    station.junction_group = Some(endpoint_group);
                                }
                            }
                        }
                    }
                    stations[index].junction_group = Some(endpoint_group);
                }
            }
        }
    }
}

/// Return deterministic, human-readable findings for layout conditions that
/// would make a generated network ambiguous or disconnected.
///
/// This is deliberately kept in the routing crate rather than delegated only
/// to repository scripts: `osr-design` must never emit a design which it
/// already knows has duplicate/too-close platforms or a missing walkable
/// transfer. Site validation can add stricter rules later, but these are hard
/// generator invariants.
#[must_use]
pub fn station_layout_issues(
    stations: &[Station],
    lines: &[Line],
    cell_m: f64,
    transfer_envelope_m: f64,
    _terminus_extension_envelope_m: f64,
    minimum_inline_chainage_m: f64,
) -> Vec<String> {
    let mut issues = Vec::new();
    let mut by_line = std::collections::BTreeMap::<&str, Vec<&Station>>::new();
    let mut interchange_lines =
        std::collections::BTreeMap::<u32, std::collections::BTreeSet<&str>>::new();
    for station in stations {
        by_line
            .entry(station.line_name.as_str())
            .or_default()
            .push(station);
        if let Some(group) = station.junction_group {
            interchange_lines
                .entry(group)
                .or_default()
                .insert(station.line_name.as_str());
        }
    }
    for (line_name, line_stations) in &mut by_line {
        line_stations.sort_by(|a, b| {
            a.s_m
                .partial_cmp(&b.s_m)
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        for pair in line_stations.windows(2) {
            let gap = pair[1].s_m - pair[0].s_m;
            if gap < minimum_inline_chainage_m - 1e-6 {
                issues.push(format!(
                    "{line_name}: stations at {:.1} m ({:?}) and {:.1} m ({:?}) are only {:.1} m apart",
                    pair[0].s_m,
                    pair[0].junction_group,
                    pair[1].s_m,
                    pair[1].junction_group,
                    gap
                ));
            }
        }
    }
    for line in lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Ring) && line.cells.len() >= 2)
    {
        let Some(line_stations) = by_line.get(line.name.as_str()) else {
            continue;
        };
        if line_stations.len() < 2 {
            continue;
        }
        let route_length_m = line
            .cells
            .windows(2)
            .map(|pair| {
                let dr = pair[1].0 as f64 - pair[0].0 as f64;
                let dc = pair[1].1 as f64 - pair[0].1 as f64;
                (dr * dr + dc * dc).sqrt() * cell_m
            })
            .sum::<f64>();
        let wrap_gap_m =
            route_length_m - line_stations.last().unwrap().s_m + line_stations.first().unwrap().s_m;
        if wrap_gap_m < minimum_inline_chainage_m - 1e-6 {
            issues.push(format!(
                "{}: stations around the ring origin are only {:.1} m apart",
                line.name, wrap_gap_m
            ));
        }
    }

    let transfer2 = transfer_envelope_m * transfer_envelope_m;
    for (index, first) in stations.iter().enumerate() {
        for second in &stations[index + 1..] {
            if first.line_name == second.line_name {
                continue;
            }
            if haversine_sq_m(first.lat, first.lon, second.lat, second.lon) <= transfer2
                && (first.junction_group.is_none() || first.junction_group != second.junction_group)
            {
                issues.push(format!(
                    "{} and {} have platforms within {:.0} m but no common interchange",
                    first.line_name, second.line_name, transfer_envelope_m
                ));
            }
        }
    }

    for (group, line_names) in interchange_lines {
        if line_names.len() < 2 {
            issues.push(format!(
                "junction group {group} contains platforms from fewer than two lines"
            ));
        }
    }

    let rings: Vec<&Line> = lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Ring))
        .collect();
    let radials: Vec<&Line> = lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Radial))
        .collect();
    for radial in radials {
        let radial_groups: std::collections::BTreeSet<u32> = by_line
            .get(radial.name.as_str())
            .into_iter()
            .flatten()
            .filter_map(|station| station.junction_group)
            .collect();
        for ring in &rings {
            let ring_groups: std::collections::BTreeSet<u32> = by_line
                .get(ring.name.as_str())
                .into_iter()
                .flatten()
                .filter_map(|station| station.junction_group)
                .collect();
            let shares_interchange = !radial_groups.is_disjoint(&ring_groups);
            let radial_length_m = radial
                .cells
                .windows(2)
                .map(|pair| {
                    let dr = pair[1].0 as f64 - pair[0].0 as f64;
                    let dc = pair[1].1 as f64 - pair[0].1 as f64;
                    (dr * dr + dc * dc).sqrt() * cell_m
                })
                .sum::<f64>();
            for (endpoint, endpoint_chainage) in [
                (radial.cells.first().unwrap(), 0.0),
                (radial.cells.last().unwrap(), radial_length_m),
            ] {
                let endpoint_distance = ring
                    .cells
                    .iter()
                    .map(|&(row, col)| {
                        let dr = endpoint.0 as f64 - row as f64;
                        let dc = endpoint.1 as f64 - col as f64;
                        (dr * dr + dc * dc).sqrt() * cell_m
                    })
                    .fold(f64::INFINITY, f64::min);
                let terminal_group = by_line
                    .get(radial.name.as_str())
                    .into_iter()
                    .flatten()
                    .find(|station| (station.s_m - endpoint_chainage).abs() <= 1.0)
                    .and_then(|station| station.junction_group);
                if endpoint_distance <= transfer_envelope_m + 1e-6
                    && !terminal_group
                        .map(|group| ring_groups.contains(&group))
                        .unwrap_or(false)
                {
                    issues.push(format!(
                        "{} terminal within {:.0} m of {} has no endpoint interchange",
                        radial.name, transfer_envelope_m, ring.name
                    ));
                }
            }
            let closest_cells = radial
                .cells
                .iter()
                .flat_map(|&(rr, rc)| {
                    ring.cells.iter().map(move |&(gr, gc)| {
                        let dr = rr as f64 - gr as f64;
                        let dc = rc as f64 - gc as f64;
                        (dr * dr + dc * dc).sqrt() * cell_m
                    })
                })
                .fold(f64::INFINITY, f64::min);
            if !shares_interchange && closest_cells <= transfer_envelope_m + 1e-6 {
                issues.push(format!(
                    "{} and {} approach within the mandatory transfer/extension envelope but have no interchange",
                    radial.name, ring.name
                ));
            }
        }
    }

    issues.sort();
    issues.dedup();
    issues
}

/// Remove redundant same-line stops created when several forced transfer
/// points fall inside one station-complex envelope.
///
/// Cross-line platforms remain separate records because each must retain its
/// own line chainage, but `merge_interchanges` gives them one stable complex
/// id. On a given line this pass keeps at most one platform within
/// `minimum_spacing_m`: radial endpoints win, then interchange platforms,
/// higher local demand, named anchors, and finally earlier chainage. The rules contain no iteration-
/// order or random tie-breaks, so identical inputs produce identical stops.
pub fn consolidate_inline_station_clusters(
    stations: &mut Vec<Station>,
    lines: &[Line],
    minimum_spacing_m: f64,
) {
    if stations.len() < 2 || minimum_spacing_m <= 0.0 {
        return;
    }
    let radial_lines: std::collections::BTreeSet<String> = lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Radial))
        .map(|line| line.name.clone())
        .collect();
    let line_ends: std::collections::BTreeMap<String, f64> =
        stations
            .iter()
            .fold(std::collections::BTreeMap::new(), |mut ends, station| {
                ends.entry(station.line_name.clone())
                    .and_modify(|end| *end = end.max(station.s_m))
                    .or_insert(station.s_m);
                ends
            });
    let mut by_line = std::collections::BTreeMap::<String, Vec<Station>>::new();
    for station in stations.drain(..) {
        by_line
            .entry(station.line_name.clone())
            .or_default()
            .push(station);
    }
    let mut group_remap = std::collections::BTreeMap::<u32, u32>::new();
    for line_stations in by_line.values_mut() {
        line_stations.sort_by(|a, b| {
            a.s_m
                .partial_cmp(&b.s_m)
                .unwrap_or(std::cmp::Ordering::Equal)
                .then_with(|| a.row.cmp(&b.row))
                .then_with(|| a.col.cmp(&b.col))
        });
        let line_name = line_stations
            .first()
            .map(|station| station.line_name.as_str())
            .unwrap_or_default();
        let line_end = *line_ends.get(line_name).unwrap_or(&0.0);
        let is_radial = radial_lines.contains(line_name);
        let mut kept: Vec<Station> = Vec::with_capacity(line_stations.len());
        for candidate in line_stations.drain(..) {
            let Some(previous) = kept.last() else {
                kept.push(candidate);
                continue;
            };
            if candidate.s_m - previous.s_m >= minimum_spacing_m {
                kept.push(candidate);
                continue;
            }
            let endpoint = |station: &Station| {
                is_radial && (station.s_m.abs() <= 1.0 || (line_end - station.s_m).abs() <= 1.0)
            };
            let score = |station: &Station| {
                (
                    endpoint(station),
                    station.junction_group.is_some(),
                    (station.demand * 1_000_000.0).round() as i64,
                    station.anchor_name.is_some(),
                    station.anchor_id.is_some(),
                )
            };
            let previous_group = previous.junction_group;
            let candidate_group = candidate.junction_group;
            if score(&candidate) > score(previous) {
                if let (Some(drop_group), Some(keep_group)) = (previous_group, candidate_group) {
                    if drop_group != keep_group {
                        group_remap.insert(drop_group, keep_group);
                    }
                }
                *kept.last_mut().unwrap() = candidate;
            } else if previous_group.is_none() && candidate_group.is_some() {
                kept.last_mut().unwrap().junction_group = candidate_group;
            } else if let (Some(keep_group), Some(drop_group)) = (previous_group, candidate_group) {
                if keep_group != drop_group {
                    group_remap.insert(drop_group, keep_group);
                }
            }
        }
        *line_stations = kept;
    }
    *stations = by_line.into_values().flatten().collect();
    if !group_remap.is_empty() {
        let resolve_group = |mut group: u32, group_remap: &std::collections::BTreeMap<u32, u32>| {
            let mut seen = std::collections::BTreeSet::new();
            while let Some(&next) = group_remap.get(&group) {
                if !seen.insert(group) || next == group {
                    break;
                }
                group = next;
            }
            group
        };
        for station in stations.iter_mut() {
            if let Some(group) = station.junction_group {
                station.junction_group = Some(resolve_group(group, &group_remap));
            }
        }
    }
}

/// Consolidate the first/last station pair around a closed line's arbitrary
/// chainage origin. The ordinary in-line pass cannot see this wrap interval.
pub fn consolidate_ring_wrap_station_clusters(
    stations: &mut Vec<Station>,
    lines: &[Line],
    cell_m: f64,
    minimum_spacing_m: f64,
) -> usize {
    if stations.len() < 2 || minimum_spacing_m <= 0.0 {
        return 0;
    }

    let mut removed = 0;
    for line in lines
        .iter()
        .filter(|line| matches!(line.shape, LineShape::Ring) && line.cells.len() >= 2)
    {
        let route_length_m = line
            .cells
            .windows(2)
            .map(|pair| {
                let dr = pair[1].0 as f64 - pair[0].0 as f64;
                let dc = pair[1].1 as f64 - pair[0].1 as f64;
                (dr * dr + dc * dc).sqrt() * cell_m
            })
            .sum::<f64>();

        loop {
            let mut indices: Vec<usize> = stations
                .iter()
                .enumerate()
                .filter(|(_, station)| station.line_name == line.name)
                .map(|(index, _)| index)
                .collect();
            indices.sort_by(|&a, &b| {
                stations[a]
                    .s_m
                    .partial_cmp(&stations[b].s_m)
                    .unwrap_or(std::cmp::Ordering::Equal)
            });
            let (Some(&first), Some(&last)) = (indices.first(), indices.last()) else {
                break;
            };
            if first == last {
                break;
            }
            let wrap_gap_m = route_length_m - stations[last].s_m + stations[first].s_m;
            if wrap_gap_m >= minimum_spacing_m {
                break;
            }
            let score = |station: &Station| {
                (
                    station.junction_group.is_some(),
                    (station.demand * 1_000_000.0).round() as i64,
                    station.anchor_name.is_some(),
                    station.anchor_id.is_some(),
                )
            };
            let remove = if score(&stations[first]) >= score(&stations[last]) {
                if stations[first].junction_group.is_none()
                    && stations[last].junction_group.is_some()
                {
                    stations[first].junction_group = stations[last].junction_group;
                }
                last
            } else {
                if stations[last].junction_group.is_none()
                    && stations[first].junction_group.is_some()
                {
                    stations[last].junction_group = stations[first].junction_group;
                }
                first
            };
            stations.remove(remove);
            removed += 1;
        }
    }
    removed
}

/// Fill any gaps made too large by forced interchange insertion and
/// same-line consolidation.
///
/// Ordinary placement already follows the demand-sensitive spacing bands,
/// but replacing a nearby stop with a forced hub/crossing can join two gaps.
/// This deterministic repair inserts evenly spaced platforms on the routed
/// cells using the demand band at each interval's midpoint. A 25% tolerance
/// keeps a just-over-target urban interval from being split into two dense
/// stops; the 7 km suburban/fringe cap is kept strict.
pub fn fill_large_station_gaps(
    stations: &mut Vec<Station>,
    lines: &[Line],
    grid: &Grid,
    anchors: &[Anchor],
    cfg: SpacingConfig,
) -> usize {
    if stations.len() < 2 {
        return 0;
    }
    let mut additions = Vec::new();
    for line in lines {
        if line.cells.len() < 2 {
            continue;
        }
        let mut cumulative = Vec::with_capacity(line.cells.len());
        cumulative.push(0.0);
        for pair in line.cells.windows(2) {
            let dr = pair[1].0 as f64 - pair[0].0 as f64;
            let dc = pair[1].1 as f64 - pair[0].1 as f64;
            let next = cumulative.last().copied().unwrap_or(0.0)
                + (dr * dr + dc * dc).sqrt() * grid.reference.cell_m;
            cumulative.push(next);
        }
        let route_length = cumulative.last().copied().unwrap_or(0.0);
        let mut chainages: Vec<f64> = stations
            .iter()
            .filter(|station| station.line_name == line.name)
            .map(|station| station.s_m)
            .collect();
        chainages.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
        let mut intervals: Vec<(f64, f64)> = chainages
            .windows(2)
            .map(|pair| (pair[0], pair[1]))
            .collect();
        if matches!(line.shape, LineShape::Ring) {
            if let (Some(first), Some(last)) = (chainages.first(), chainages.last()) {
                intervals.push((*last, route_length + *first));
            }
        }

        let mut occupied: std::collections::BTreeSet<(usize, usize)> = stations
            .iter()
            .filter(|station| station.line_name == line.name)
            .map(|station| (station.row, station.col))
            .collect();
        for (start, end) in intervals {
            let gap = end - start;
            let midpoint = if route_length > 0.0 {
                (start + gap * 0.5) % route_length
            } else {
                start
            };
            let midpoint_index = cumulative
                .iter()
                .enumerate()
                .min_by(|(_, first), (_, second)| {
                    (*first - midpoint)
                        .abs()
                        .partial_cmp(&(*second - midpoint).abs())
                        .unwrap_or(std::cmp::Ordering::Equal)
                })
                .map(|(index, _)| index)
                .unwrap_or(0);
            let midpoint_demand =
                grid.demand_at(line.cells[midpoint_index].0, line.cells[midpoint_index].1);
            let local_target = spacing_for_demand(midpoint_demand, cfg);
            let repair_threshold = if midpoint_demand < cfg.outer_thr {
                cfg.outer_m
            } else {
                (local_target * 1.25).max(2.0 * cfg.urban_core_m)
            };
            if gap <= repair_threshold {
                continue;
            }

            let desired_segments = (gap / local_target).ceil() as usize;
            let maximum_segments = (gap / cfg.urban_core_m).floor() as usize;
            let segment_count = desired_segments.min(maximum_segments).max(1);
            let insert_count = segment_count.saturating_sub(1);
            for number in 1..=insert_count {
                let target = start + gap * number as f64 / (insert_count + 1) as f64;
                let wrapped_target = if route_length > 0.0 {
                    target % route_length
                } else {
                    target
                };
                let cell_index = cumulative
                    .iter()
                    .enumerate()
                    .min_by(|(_, first), (_, second)| {
                        (*first - wrapped_target)
                            .abs()
                            .partial_cmp(&(*second - wrapped_target).abs())
                            .unwrap_or(std::cmp::Ordering::Equal)
                    })
                    .map(|(index, _)| index)
                    .unwrap_or(0);
                let cell = line.cells[cell_index];
                if occupied.insert(cell) {
                    additions.push(make_station(
                        grid,
                        anchors,
                        &line.name,
                        cell,
                        cumulative[cell_index],
                        cfg,
                    ));
                }
            }
        }
    }
    let added = additions.len();
    stations.extend(additions);
    added
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
    use crate::raster::GridRef;

    fn uniform_grid(h: usize, w: usize) -> Grid {
        Grid {
            reference: GridRef {
                height: h,
                width: w,
                cell_m: 20.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_west: 0.0,
                bbox_north: 0.01,
                bbox_east: 0.01,
                m_per_deg_lat: 111_132.0,
                m_per_deg_lon: 111_320.0,
            },
            cost: vec![10.0; h * w],
            demand: vec![0.0; h * w],
            buildability: vec![1; h * w],
        }
    }

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
        // Merged stations keep their original on-line lat/lon — the
        // junction_group id alone is the marker that they form one
        // interchange complex. Earlier behaviour (averaging the
        // group's coordinates onto a shared centroid) was reverted
        // because it pulled each platform off its own routed
        // corridor; the renderer can compute a centroid on-the-fly
        // from the per-line platforms when one visual icon is
        // wanted.
        assert!((s[0].lat - 0.001).abs() < 1e-9);
        assert!((s[1].lat - 0.001003).abs() < 1e-9);
        assert!((s[2].lat - 0.001).abs() < 1e-9);
    }

    #[test]
    fn merge_does_not_combine_same_line_stations() {
        let mut s = vec![st("L1", 0.001, 0.001), st("L1", 0.001005, 0.001005)];
        merge_interchanges(&mut s, 250.0);
        assert_eq!(s[0].junction_group, None);
        assert_eq!(s[1].junction_group, None);
    }

    #[test]
    fn inline_cluster_keeps_one_deterministic_platform() {
        let lines = vec![line(
            "L1",
            LineShape::Radial,
            vec![(0, 0), (0, 1), (0, 2), (0, 3)],
        )];
        let mut stations = vec![
            Station {
                s_m: 0.0,
                demand: 0.1,
                ..st("L1", 0.0, 0.0)
            },
            Station {
                s_m: 300.0,
                demand: 0.9,
                ..st("L1", 0.0, 0.003)
            },
            Station {
                s_m: 1200.0,
                demand: 0.2,
                ..st("L1", 0.0, 0.012)
            },
        ];
        consolidate_inline_station_clusters(&mut stations, &lines, 600.0);
        assert_eq!(stations.len(), 2);
        assert_eq!(stations[0].s_m, 0.0, "radial endpoint must win");
        assert_eq!(stations[1].s_m, 1200.0);
    }

    #[test]
    fn inline_cluster_prefers_higher_demand_away_from_endpoint() {
        let lines = vec![line(
            "L1",
            LineShape::Radial,
            vec![(0, 0), (0, 1), (0, 2), (0, 3)],
        )];
        let mut stations = vec![
            Station {
                s_m: 1000.0,
                demand: 0.2,
                ..st("L1", 0.0, 0.01)
            },
            Station {
                s_m: 1300.0,
                demand: 0.8,
                ..st("L1", 0.0, 0.013)
            },
            Station {
                s_m: 2500.0,
                demand: 0.1,
                ..st("L1", 0.0, 0.025)
            },
        ];
        consolidate_inline_station_clusters(&mut stations, &lines, 600.0);
        assert_eq!(stations.len(), 2);
        assert_eq!(stations[0].s_m, 1300.0);
    }

    #[test]
    fn inline_cluster_preserves_forced_interchange_platform() {
        let lines = vec![line(
            "L1",
            LineShape::Radial,
            vec![(0, 0), (0, 1), (0, 2), (0, 3)],
        )];
        let mut stations = vec![
            Station {
                s_m: 1000.0,
                demand: 0.9,
                ..st("L1", 0.0, 0.01)
            },
            Station {
                s_m: 1300.0,
                demand: 0.2,
                junction_group: Some(4),
                ..st("L1", 0.0, 0.013)
            },
            Station {
                s_m: 2500.0,
                ..st("L1", 0.0, 0.025)
            },
        ];
        consolidate_inline_station_clusters(&mut stations, &lines, 600.0);
        assert_eq!(stations.len(), 2);
        assert_eq!(stations[0].s_m, 1300.0);
        assert_eq!(stations[0].junction_group, Some(4));
    }

    #[test]
    fn inline_cluster_collapses_same_line_platforms_inside_interchange_group() {
        let lines = vec![
            line(
                "L1",
                LineShape::Radial,
                vec![(0, 0), (0, 1), (0, 2), (0, 3)],
            ),
            line(
                "L2",
                LineShape::Radial,
                vec![(1, 0), (1, 1), (1, 2), (1, 3)],
            ),
        ];
        let mut stations = vec![
            Station {
                s_m: 1000.0,
                demand: 0.2,
                junction_group: Some(7),
                ..st("L1", 0.0, 0.010)
            },
            Station {
                s_m: 1120.0,
                demand: 0.8,
                junction_group: Some(7),
                ..st("L1", 0.0, 0.011)
            },
            Station {
                s_m: 1100.0,
                demand: 0.7,
                junction_group: Some(7),
                ..st("L2", 0.001, 0.011)
            },
        ];
        consolidate_inline_station_clusters(&mut stations, &lines, 1200.0);
        let l1: Vec<_> = stations
            .iter()
            .filter(|station| station.line_name == "L1")
            .collect();
        assert_eq!(l1.len(), 1);
        assert_eq!(l1[0].s_m, 1120.0);
        assert_eq!(l1[0].junction_group, Some(7));
        assert_eq!(
            stations
                .iter()
                .filter(|station| station.line_name == "L2")
                .count(),
            1
        );
    }

    #[test]
    fn ring_wrap_cluster_is_consolidated() {
        let lines = vec![line(
            "R1",
            LineShape::Ring,
            vec![(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)],
        )];
        let mut stations = vec![
            Station {
                s_m: 100.0,
                demand: 0.8,
                ..st("R1", 0.0, 0.0)
            },
            Station {
                s_m: 3_000.0,
                ..st("R1", 0.0, 0.03)
            },
            Station {
                s_m: 7_500.0,
                demand: 0.1,
                ..st("R1", 0.0, 0.075)
            },
        ];

        let removed = consolidate_ring_wrap_station_clusters(&mut stations, &lines, 20.0, 1_200.0);

        assert_eq!(removed, 1);
        assert_eq!(stations.len(), 2);
        assert!(stations.iter().any(|station| station.s_m == 100.0));
        assert!(!stations.iter().any(|station| station.s_m == 7_500.0));
    }

    #[test]
    fn large_gap_repair_inserts_evenly_spaced_stations() {
        let grid = uniform_grid(10, 401);
        let anchors = vec![];
        let lines = vec![line(
            "L1",
            LineShape::Radial,
            (0..=400).map(|col| (5, col)).collect(),
        )];
        let mut stations = vec![
            Station {
                row: 5,
                col: 0,
                s_m: 0.0,
                ..st("L1", 0.0, 0.0)
            },
            Station {
                row: 5,
                col: 400,
                s_m: 8000.0,
                ..st("L1", 0.0, 0.0)
            },
        ];
        let added = fill_large_station_gaps(
            &mut stations,
            &lines,
            &grid,
            &anchors,
            SpacingConfig::default(),
        );
        assert_eq!(added, 1);
        let mut chainages: Vec<f64> = stations.iter().map(|station| station.s_m).collect();
        chainages.sort_by(|a, b| a.partial_cmp(b).unwrap());
        assert!(chainages.windows(2).all(|pair| pair[1] - pair[0] <= 5000.0));
    }

    #[test]
    fn suburban_gap_repair_does_not_split_a_just_over_target_interval() {
        let mut grid = uniform_grid(10, 156);
        grid.demand.fill(0.2);
        let anchors = vec![];
        let lines = vec![line(
            "L1",
            LineShape::Radial,
            (0..=155).map(|col| (5, col)).collect(),
        )];
        let mut stations = vec![
            Station {
                row: 5,
                col: 0,
                s_m: 0.0,
                ..st("L1", 0.0, 0.0)
            },
            Station {
                row: 5,
                col: 155,
                s_m: 3100.0,
                ..st("L1", 0.0, 0.0)
            },
        ];

        let added = fill_large_station_gaps(
            &mut stations,
            &lines,
            &grid,
            &anchors,
            SpacingConfig::default(),
        );

        assert_eq!(added, 0);
        assert_eq!(stations.len(), 2);
    }

    #[test]
    fn layout_gate_rejects_an_ungrouped_cross_line_near_miss() {
        let lines = vec![
            line("L1", LineShape::Radial, vec![(0, 0), (0, 50)]),
            line("L2", LineShape::Radial, vec![(1, 0), (1, 50)]),
        ];
        let stations = vec![st("L1", 0.0, 0.0), st("L2", 0.0, 0.001)];
        let issues = station_layout_issues(&stations, &lines, 20.0, 600.0, 1200.0, 600.0);
        assert!(issues
            .iter()
            .any(|issue| issue.contains("no common interchange")));
    }

    #[test]
    fn forced_crossing_preserves_nearby_route_endpoint() {
        let grid = uniform_grid(30, 30);
        let anchors = vec![];
        let mut stations = vec![
            st("L1", 0.0, 0.0),
            Station {
                s_m: 200.0,
                row: 10,
                col: 10,
                ..st("L1", 0.0, 0.0)
            },
        ];
        replace_station_near(
            &mut stations,
            "L1",
            &grid,
            &anchors,
            ReplacementSite {
                cell: (10, 9),
                chainage_m: 180.0,
                preserve_route_endpoints: true,
                radius_cells: 6,
                chainage_window_m: 120.0,
            },
        );
        assert_eq!(stations.len(), 2);
        assert!(stations.iter().any(|station| station.s_m == 200.0));
    }

    #[test]
    fn endpoint_repair_restores_radial_but_not_duplicate_ring_end() {
        let grid = uniform_grid(30, 30);
        let anchors = vec![];
        let lines = vec![
            line("L1", LineShape::Radial, vec![(2, 2), (2, 3), (2, 4)]),
            line("R1", LineShape::Ring, vec![(10, 10), (10, 11), (10, 10)]),
        ];
        let mut stations = vec![
            Station {
                row: 2,
                col: 3,
                s_m: 20.0,
                ..st("L1", 0.0, 0.0)
            },
            st("R1", 0.0, 0.0),
        ];
        ensure_endpoint_stations(
            &mut stations,
            &lines,
            &grid,
            &anchors,
            SpacingConfig::default(),
        );
        let radial: Vec<_> = stations
            .iter()
            .filter(|station| station.line_name == "L1")
            .collect();
        let ring: Vec<_> = stations
            .iter()
            .filter(|station| station.line_name == "R1")
            .collect();
        assert!(radial.iter().any(|station| station.s_m == 0.0));
        assert!(radial.iter().any(|station| station.s_m == 40.0));
        assert_eq!(ring.len(), 1);
    }

    #[test]
    fn closed_line_has_one_station_at_its_shared_start_end_cell() {
        let grid = uniform_grid(30, 30);
        let cells = vec![(10, 10), (10, 20), (20, 20), (20, 10), (10, 10)];
        let stations = place_stations(
            &grid,
            &[],
            "R1",
            &cells,
            SpacingConfig {
                urban_core_m: 100.0,
                urban_m: 100.0,
                peri_urban_m: 100.0,
                outer_m: 100.0,
                ..SpacingConfig::default()
            },
        );
        assert_eq!(
            stations
                .iter()
                .filter(|station| (station.row, station.col) == cells[0])
                .count(),
            1
        );
        assert_eq!(stations[0].s_m, 0.0);
    }

    fn line(name: &str, shape: LineShape, cells: Vec<(usize, usize)>) -> Line {
        Line {
            name: name.to_string(),
            shape,
            cells,
            anchor_ids: vec![],
        }
    }

    #[test]
    fn radial_terminus_near_ring_gets_routed_extension() {
        let grid = uniform_grid(30, 30);
        let mut lines = vec![
            line("L1", LineShape::Radial, vec![(10, 0), (10, 2), (10, 4)]),
            line("R1", LineShape::Ring, vec![(10, 10), (11, 10), (12, 10)]),
        ];
        let count = connect_radial_termini_to_rings(&mut lines, &grid, 3, 8, DemandWeight(0.0));
        assert_eq!(count, 1);
        assert_eq!(lines[0].cells.last(), Some(&(10, 10)));
    }

    #[test]
    fn distant_radial_terminus_is_left_for_topology_review() {
        let grid = uniform_grid(40, 40);
        let original = vec![(2, 2), (2, 3), (2, 4)];
        let mut lines = vec![
            line("L1", LineShape::Radial, original.clone()),
            line("R1", LineShape::Ring, vec![(30, 30), (31, 30), (32, 30)]),
        ];
        let count = connect_radial_termini_to_rings(&mut lines, &grid, 3, 8, DemandWeight(0.0));
        assert_eq!(count, 0);
        assert_eq!(lines[0].cells, original);
    }
}
