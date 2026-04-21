//! Topology synthesis — pick line endpoints + waypoints from anchors.
//!
//! Given a topology archetype (see designs/recipes/city-to-design.toml
//! Step 4), plus the anchor set, produce one or more lines. A line is a
//! sequence of anchor indices that the solver will then wire together
//! in order, calling `solver::solve_path` for each adjacent pair.
//!
//! Archetypes are intentionally small; complexity comes from how the
//! solver snakes between the selected points, not from clever topology.

use std::collections::HashSet;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::raster::{Anchor, Grid};
use crate::solver::{solve_path, DemandWeight, SolverError};

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum TopologyArchetype {
    SingleRadial,
    RadialPlusRing,
    CrossPlusRing,
    HubAndSpokeDualRing,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum LineShape {
    Radial,
    Ring,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Line {
    pub name: String,
    pub shape: LineShape,
    /// Indices into the anchors slice, in line order.
    pub anchor_ids: Vec<usize>,
    /// Concatenated cell sequence from endpoint to endpoint.
    pub cells: Vec<(usize, usize)>,
}

#[derive(Debug, Error)]
pub enum TopologyError {
    #[error("need at least {min} anchors, got {got}")]
    TooFewAnchors { min: usize, got: usize },
    #[error("solver error: {0}")]
    Solver(#[from] SolverError),
}

/// Pick a topology archetype from population (matching the recipe rules).
#[must_use]
pub fn pick_archetype(population: u64) -> TopologyArchetype {
    match population {
        0..=300_000 => TopologyArchetype::SingleRadial,
        300_001..=1_000_000 => TopologyArchetype::RadialPlusRing,
        1_000_001..=3_000_000 => TopologyArchetype::CrossPlusRing,
        _ => TopologyArchetype::HubAndSpokeDualRing,
    }
}

/// Synthesize lines + route them on the grid.
pub fn synthesize_lines(
    grid: &Grid,
    anchors: &[Anchor],
    archetype: TopologyArchetype,
    demand_w: DemandWeight,
) -> Result<Vec<Line>, TopologyError> {
    if anchors.len() < 2 {
        return Err(TopologyError::TooFewAnchors { min: 2, got: anchors.len() });
    }

    // Order anchors by weight for consistent endpoint selection.
    let mut ordered: Vec<usize> = (0..anchors.len()).collect();
    ordered.sort_by(|&a, &b| {
        anchors[b]
            .weight
            .partial_cmp(&anchors[a].weight)
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    let centre = grid_centre(grid);

    match archetype {
        TopologyArchetype::SingleRadial => {
            let (endpoints, _used) = pick_radial_endpoints(grid, anchors, &ordered, 1)?;
            let (a, b) = endpoints[0];
            let cells = solve_path(grid, anchors[a].cell(), anchors[b].cell(), demand_w)?;
            Ok(vec![Line {
                name: "line-1".into(),
                shape: LineShape::Radial,
                anchor_ids: vec![a, b],
                cells,
            }])
        }
        TopologyArchetype::RadialPlusRing => {
            let (endpoints, used) = pick_radial_endpoints(grid, anchors, &ordered, 1)?;
            let (a, b) = endpoints[0];
            let radial_cells =
                via_centre(grid, anchors, a, b, centre, demand_w)?;

            let ring_anchors = pick_ring_anchors(grid, anchors, &ordered, &used, 4)?;
            let ring_cells = route_ring(grid, anchors, &ring_anchors, demand_w)?;

            Ok(vec![
                Line {
                    name: "line-1".into(),
                    shape: LineShape::Radial,
                    anchor_ids: vec![a, b],
                    cells: radial_cells,
                },
                Line {
                    name: "line-2".into(),
                    shape: LineShape::Ring,
                    anchor_ids: ring_anchors.clone(),
                    cells: ring_cells,
                },
            ])
        }
        TopologyArchetype::CrossPlusRing => {
            let (endpoints, used) = pick_radial_endpoints(grid, anchors, &ordered, 2)?;
            let mut lines = Vec::new();
            for (i, (a, b)) in endpoints.iter().enumerate() {
                let cells = via_centre(grid, anchors, *a, *b, centre, demand_w)?;
                lines.push(Line {
                    name: format!("line-{}", i + 1),
                    shape: LineShape::Radial,
                    anchor_ids: vec![*a, *b],
                    cells,
                });
            }
            let ring_anchors = pick_ring_anchors(grid, anchors, &ordered, &used, 6)?;
            let ring_cells = route_ring(grid, anchors, &ring_anchors, demand_w)?;
            lines.push(Line {
                name: "line-3".into(),
                shape: LineShape::Ring,
                anchor_ids: ring_anchors,
                cells: ring_cells,
            });
            Ok(lines)
        }
        TopologyArchetype::HubAndSpokeDualRing => {
            let (endpoints, used) = pick_radial_endpoints(grid, anchors, &ordered, 4)?;
            let mut lines = Vec::new();
            for (i, (a, b)) in endpoints.iter().enumerate() {
                let cells = via_centre(grid, anchors, *a, *b, centre, demand_w)?;
                lines.push(Line {
                    name: format!("line-{}", i + 1),
                    shape: LineShape::Radial,
                    anchor_ids: vec![*a, *b],
                    cells,
                });
            }

            // Inner ring: 6 anchors closer to centre.
            let inner = pick_ring_anchors_by_radius(grid, anchors, &ordered, &used, 6, RingBand::Inner)?;
            let mut used2 = used.clone();
            used2.extend(&inner);
            let inner_cells = route_ring(grid, anchors, &inner, demand_w)?;
            lines.push(Line {
                name: "line-5".into(),
                shape: LineShape::Ring,
                anchor_ids: inner,
                cells: inner_cells,
            });

            // Outer ring: 8 anchors farther out.
            let outer = pick_ring_anchors_by_radius(grid, anchors, &ordered, &used2, 8, RingBand::Outer)?;
            let outer_cells = route_ring(grid, anchors, &outer, demand_w)?;
            lines.push(Line {
                name: "line-6".into(),
                shape: LineShape::Ring,
                anchor_ids: outer,
                cells: outer_cells,
            });

            Ok(lines)
        }
    }
}

// ---- Helpers ---------------------------------------------------------

#[derive(Clone, Copy)]
enum RingBand {
    Inner,
    Outer,
}

fn grid_centre(grid: &Grid) -> (usize, usize) {
    (grid.reference.height / 2, grid.reference.width / 2)
}

fn dist_from(rc: (usize, usize), centre: (usize, usize)) -> f32 {
    let dr = rc.0 as f32 - centre.0 as f32;
    let dc = rc.1 as f32 - centre.1 as f32;
    (dr * dr + dc * dc).sqrt()
}

impl Anchor {
    #[must_use]
    pub fn cell(&self) -> (usize, usize) {
        (self.row, self.col)
    }
}

/// Pick `count` radial endpoint pairs. Each pair consists of two anchors
/// roughly opposite each other through the centre, both reasonably far
/// from the centre (endpoints should be peripheral, not core).
fn pick_radial_endpoints(
    grid: &Grid,
    anchors: &[Anchor],
    ordered: &[usize],
    count: usize,
) -> Result<(Vec<(usize, usize)>, HashSet<usize>), TopologyError> {
    let centre = grid_centre(grid);
    // Periphery set: anchors in the outer half of the bbox.
    let max_d = dist_from((0, 0), centre);
    let peripheral: Vec<usize> = ordered
        .iter()
        .copied()
        .filter(|&i| dist_from(anchors[i].cell(), centre) > 0.4 * max_d)
        .collect();

    if peripheral.len() < 2 * count {
        // Fall back: use everything, just pick farthest.
        return pick_radial_from_all(anchors, ordered, count);
    }

    let mut endpoints: Vec<(usize, usize)> = Vec::new();
    let mut used: HashSet<usize> = HashSet::new();

    for _ in 0..count {
        // Pick the highest-weight peripheral anchor not yet used.
        let Some(&a) = peripheral.iter().find(|&&i| !used.contains(&i)) else {
            break;
        };
        used.insert(a);
        // Pick the peripheral anchor with largest angular distance from a.
        let (arow, acol) = anchors[a].cell();
        let centre_r = centre.0 as f32;
        let centre_c = centre.1 as f32;
        let a_angle = (arow as f32 - centre_r).atan2(acol as f32 - centre_c);

        let mut best: Option<usize> = None;
        let mut best_score = f32::NEG_INFINITY;
        for &b in &peripheral {
            if used.contains(&b) {
                continue;
            }
            let (brow, bcol) = anchors[b].cell();
            let b_angle = (brow as f32 - centre_r).atan2(bcol as f32 - centre_c);
            // Angular separation, normalized to [0, π].
            let mut da = (b_angle - a_angle).abs();
            if da > std::f32::consts::PI {
                da = 2.0 * std::f32::consts::PI - da;
            }
            // Score: reward opposite angle + high weight.
            let score = da + 0.1 * anchors[b].weight;
            if score > best_score {
                best_score = score;
                best = Some(b);
            }
        }
        if let Some(b) = best {
            used.insert(b);
            endpoints.push((a, b));
        }
    }

    if endpoints.is_empty() {
        return Err(TopologyError::TooFewAnchors { min: 2 * count, got: 0 });
    }
    Ok((endpoints, used))
}

fn pick_radial_from_all(
    anchors: &[Anchor],
    ordered: &[usize],
    count: usize,
) -> Result<(Vec<(usize, usize)>, HashSet<usize>), TopologyError> {
    if anchors.len() < 2 * count {
        return Err(TopologyError::TooFewAnchors {
            min: 2 * count,
            got: anchors.len(),
        });
    }
    let mut endpoints = Vec::new();
    let mut used: HashSet<usize> = HashSet::new();
    for i in 0..count {
        let a = ordered[2 * i];
        let b = ordered[2 * i + 1];
        used.insert(a);
        used.insert(b);
        endpoints.push((a, b));
    }
    Ok((endpoints, used))
}

/// Route a-centre-b so radials actually pass through the downtown.
fn via_centre(
    grid: &Grid,
    anchors: &[Anchor],
    a: usize,
    b: usize,
    centre: (usize, usize),
    demand_w: DemandWeight,
) -> Result<Vec<(usize, usize)>, SolverError> {
    // Pick a buildable centre — if the geometric centre lands on a
    // building, walk outward until we find an open cell.
    let centre = nudge_to_buildable(grid, centre).unwrap_or(centre);
    let mut path = solve_path(grid, anchors[a].cell(), centre, demand_w)?;
    let tail = solve_path(grid, centre, anchors[b].cell(), demand_w)?;
    // Avoid duplicating the junction cell.
    if path.last() == tail.first() {
        path.extend(tail.into_iter().skip(1));
    } else {
        path.extend(tail);
    }
    Ok(path)
}

fn nudge_to_buildable(grid: &Grid, (r, c): (usize, usize)) -> Option<(usize, usize)> {
    let h = grid.reference.height;
    let w = grid.reference.width;
    for radius in 0..20 {
        for dr in -(radius as isize)..=(radius as isize) {
            for dc in -(radius as isize)..=(radius as isize) {
                let nr = r as isize + dr;
                let nc = c as isize + dc;
                if !grid.in_bounds(nr, nc) {
                    continue;
                }
                let nr = nr as usize;
                let nc = nc as usize;
                if nr < h && nc < w && grid.is_buildable(nr, nc) && grid.cost_at(nr, nc).is_finite() {
                    return Some((nr, nc));
                }
            }
        }
    }
    None
}

/// Pick `n` anchors forming a ring — evenly distributed in angle,
/// excluding anchors already used by radials.
fn pick_ring_anchors(
    grid: &Grid,
    anchors: &[Anchor],
    ordered: &[usize],
    used: &HashSet<usize>,
    n: usize,
) -> Result<Vec<usize>, TopologyError> {
    pick_ring_anchors_by_radius(grid, anchors, ordered, used, n, RingBand::Outer)
}

fn pick_ring_anchors_by_radius(
    grid: &Grid,
    anchors: &[Anchor],
    ordered: &[usize],
    used: &HashSet<usize>,
    n: usize,
    band: RingBand,
) -> Result<Vec<usize>, TopologyError> {
    let centre = grid_centre(grid);
    let centre_r = centre.0 as f32;
    let centre_c = centre.1 as f32;
    let max_d = dist_from((0, 0), centre);

    let (radius_lo, radius_hi) = match band {
        RingBand::Inner => (0.2 * max_d, 0.5 * max_d),
        RingBand::Outer => (0.4 * max_d, max_d),
    };

    // Bin candidate anchors by angle bucket (n buckets spanning the full circle).
    let mut buckets: Vec<Option<(usize, f32)>> = vec![None; n];
    for &i in ordered {
        if used.contains(&i) {
            continue;
        }
        let (ar, ac) = anchors[i].cell();
        let d = dist_from((ar, ac), centre);
        if d < radius_lo || d > radius_hi {
            continue;
        }
        let angle = (ar as f32 - centre_r).atan2(ac as f32 - centre_c);
        // angle in [-π, π]; shift to [0, 2π).
        let norm = (angle + std::f32::consts::PI) / (2.0 * std::f32::consts::PI);
        let bucket = ((norm * n as f32).floor() as usize).min(n - 1);
        let score = anchors[i].weight - 0.0001 * ((d - (radius_lo + radius_hi) / 2.0).abs());
        match buckets[bucket] {
            None => buckets[bucket] = Some((i, score)),
            Some((_, s)) if score > s => buckets[bucket] = Some((i, score)),
            _ => {}
        }
    }

    let mut ring: Vec<usize> = buckets.into_iter().flatten().map(|(i, _)| i).collect();
    // Order by angle so the ring visits sequential neighbours.
    ring.sort_by(|&a, &b| {
        let aa = angle_of(anchors, a, centre_r, centre_c);
        let ab = angle_of(anchors, b, centre_r, centre_c);
        aa.partial_cmp(&ab).unwrap_or(std::cmp::Ordering::Equal)
    });

    if ring.len() < 3 {
        return Err(TopologyError::TooFewAnchors {
            min: 3,
            got: ring.len(),
        });
    }
    Ok(ring)
}

fn angle_of(anchors: &[Anchor], i: usize, cr: f32, cc: f32) -> f32 {
    let (r, c) = anchors[i].cell();
    (r as f32 - cr).atan2(c as f32 - cc)
}

/// Stitch a ring by solving paths between sequential anchors and closing
/// the loop.
fn route_ring(
    grid: &Grid,
    anchors: &[Anchor],
    ring_ids: &[usize],
    demand_w: DemandWeight,
) -> Result<Vec<(usize, usize)>, SolverError> {
    let mut cells: Vec<(usize, usize)> = Vec::new();
    for pair in ring_ids.windows(2) {
        let seg = solve_path(grid, anchors[pair[0]].cell(), anchors[pair[1]].cell(), demand_w)?;
        append_segment(&mut cells, seg);
    }
    // Close the ring.
    let seg = solve_path(
        grid,
        anchors[*ring_ids.last().unwrap()].cell(),
        anchors[ring_ids[0]].cell(),
        demand_w,
    )?;
    append_segment(&mut cells, seg);
    Ok(cells)
}

fn append_segment(acc: &mut Vec<(usize, usize)>, seg: Vec<(usize, usize)>) {
    if acc.is_empty() {
        acc.extend(seg);
    } else if acc.last() == seg.first() {
        acc.extend(seg.into_iter().skip(1));
    } else {
        acc.extend(seg);
    }
}
