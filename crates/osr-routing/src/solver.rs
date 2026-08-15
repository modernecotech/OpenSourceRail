//! Dijkstra least-cost-path on an 8-connected grid with a demand reward.
//!
//! Effective edge cost from cell A to cell B:
//!
//!   edge(A, B) = distance_factor × cost[B] − demand_weight × demand[B]
//!
//! where `distance_factor` is √2 for diagonal moves, 1 for orthogonal.
//! The demand reward is clamped so we never drive edges below a positive
//! floor — otherwise Dijkstra cannot reason about them.

use std::cmp::Ordering;
use std::collections::BinaryHeap;

use thiserror::Error;

use crate::raster::Grid;

/// Controls how strongly the solver prefers dense/high-demand cells.
///
/// 0.0 = ignore demand entirely (pure cheapest-to-build).
/// Higher values pull the route through populated areas even if the
/// civil cost is slightly higher. A typical sweet spot is ~5.0 at
/// default cost weights.
#[derive(Debug, Clone, Copy)]
pub struct DemandWeight(pub f32);

impl Default for DemandWeight {
    fn default() -> Self {
        Self(5.0)
    }
}

#[derive(Debug, Error)]
pub enum SolverError {
    #[error("start cell ({row}, {col}) out of bounds")]
    StartOob { row: isize, col: isize },
    #[error("goal cell ({row}, {col}) out of bounds")]
    GoalOob { row: isize, col: isize },
    #[error("no path exists between the given cells")]
    Unreachable,
}

// Neighbours: 8-connectivity with diagonal distance factor √2.
const NEIGHBOURS: [(isize, isize, f32); 8] = [
    (-1, -1, std::f32::consts::SQRT_2),
    (-1, 0, 1.0),
    (-1, 1, std::f32::consts::SQRT_2),
    (0, -1, 1.0),
    (0, 1, 1.0),
    (1, -1, std::f32::consts::SQRT_2),
    (1, 0, 1.0),
    (1, 1, std::f32::consts::SQRT_2),
];

/// Minimum effective edge cost after demand reward. Keeps Dijkstra sound.
const MIN_EDGE_COST: f32 = 0.5;

#[derive(Copy, Clone, PartialEq)]
struct State {
    cost: f32,
    idx: usize,
}

// BinaryHeap is a max-heap; invert Ord so it behaves like a min-heap.
impl Eq for State {}
impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other
            .cost
            .partial_cmp(&self.cost)
            .unwrap_or(Ordering::Equal)
            .then_with(|| self.idx.cmp(&other.idx))
    }
}
impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Solve a least-cost path from `start` to `goal`, returning the cell
/// sequence inclusive of both endpoints.
pub fn solve_path(
    grid: &Grid,
    start: (usize, usize),
    goal: (usize, usize),
    demand_w: DemandWeight,
) -> Result<Vec<(usize, usize)>, SolverError> {
    solve_path_with_penalty(grid, start, goal, demand_w, None)
}

/// Same as [`solve_path`] but adds a per-cell `penalty` (length H*W,
/// row-major) to the base cost before the demand reward. Used by
/// topology synthesis to push later legs of a line away from cells the
/// line has already used (anti-self-loop) and to nudge sister lines
/// off identical track unless sharing is structurally cheap.
pub fn solve_path_with_penalty(
    grid: &Grid,
    start: (usize, usize),
    goal: (usize, usize),
    demand_w: DemandWeight,
    penalty: Option<&[f32]>,
) -> Result<Vec<(usize, usize)>, SolverError> {
    solve_path_in_bbox(grid, start, goal, demand_w, penalty, None)
}

/// Like [`solve_path_with_penalty`] but additionally restricts the
/// search to cells inside `bbox = ((row_min, col_min), (row_max,
/// col_max))`. Used by the greedy synthesizer to clip exploration to a
/// margin around the chord between start and goal so each Dijkstra does
/// O(chord²) work instead of O(grid). The bbox is *inclusive* on both
/// corners and must contain start and goal — otherwise the result is
/// `Unreachable`.
pub fn solve_path_in_bbox(
    grid: &Grid,
    start: (usize, usize),
    goal: (usize, usize),
    demand_w: DemandWeight,
    penalty: Option<&[f32]>,
    bbox: Option<((usize, usize), (usize, usize))>,
) -> Result<Vec<(usize, usize)>, SolverError> {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let n = h * w;
    if let Some(p) = penalty {
        debug_assert_eq!(p.len(), n, "penalty mask must match grid cell count");
    }

    let sidx = start.0 * w + start.1;
    let gidx = goal.0 * w + goal.1;
    if sidx >= n {
        return Err(SolverError::StartOob {
            row: start.0 as isize,
            col: start.1 as isize,
        });
    }
    if gidx >= n {
        return Err(SolverError::GoalOob {
            row: goal.0 as isize,
            col: goal.1 as isize,
        });
    }

    let mut dist = vec![f32::INFINITY; n];
    let mut prev: Vec<i32> = vec![-1; n];
    dist[sidx] = 0.0;

    let mut heap: BinaryHeap<State> = BinaryHeap::new();
    heap.push(State {
        cost: 0.0,
        idx: sidx,
    });

    while let Some(State { cost, idx }) = heap.pop() {
        if idx == gidx {
            break;
        }
        // Stale heap entry — skip.
        if cost > dist[idx] {
            continue;
        }
        let row = idx / w;
        let col = idx % w;

        for (dr, dc, dist_factor) in NEIGHBOURS {
            let nr = row as isize + dr;
            let nc = col as isize + dc;
            if !grid.in_bounds(nr, nc) {
                continue;
            }
            let nrow = nr as usize;
            let ncol = nc as usize;
            if let Some(((rmin, cmin), (rmax, cmax))) = bbox {
                if nrow < rmin || nrow > rmax || ncol < cmin || ncol > cmax {
                    continue;
                }
            }
            if !grid.is_buildable(nrow, ncol) {
                continue;
            }
            let base = grid.cost_at(nrow, ncol);
            if !base.is_finite() {
                continue;
            }
            let nidx_pre = nrow * w + ncol;
            let extra = penalty.map(|p| p[nidx_pre]).unwrap_or(0.0);
            let reward = demand_w.0 * grid.demand_at(nrow, ncol);
            let effective = (base + extra - reward).max(MIN_EDGE_COST);
            let edge = dist_factor * effective;
            let nidx = nidx_pre;
            let ncost = cost + edge;
            if ncost < dist[nidx] {
                dist[nidx] = ncost;
                prev[nidx] = idx as i32;
                heap.push(State {
                    cost: ncost,
                    idx: nidx,
                });
            }
        }
    }

    if !dist[gidx].is_finite() {
        return Err(SolverError::Unreachable);
    }

    // Reconstruct path in reverse.
    let mut path: Vec<(usize, usize)> = Vec::new();
    let mut cur = gidx as i32;
    while cur >= 0 {
        let cur_usize = cur as usize;
        path.push((cur_usize / w, cur_usize % w));
        cur = prev[cur_usize];
    }
    path.reverse();
    Ok(path)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::raster::GridRef;

    fn uniform_grid(h: usize, w: usize, cost: f32) -> Grid {
        Grid {
            reference: GridRef {
                height: h,
                width: w,
                cell_m: 10.0,
                lat0: 0.0,
                bbox_south: 0.0,
                bbox_west: 0.0,
                bbox_north: 0.001,
                bbox_east: 0.001,
                m_per_deg_lat: 111_132.0,
                m_per_deg_lon: 111_320.0,
            },
            cost: vec![cost; h * w],
            demand: vec![0.0; h * w],
            buildability: vec![1; h * w],
        }
    }

    #[test]
    fn straight_line_on_uniform_grid() {
        let g = uniform_grid(5, 10, 10.0);
        let path = solve_path(&g, (2, 0), (2, 9), DemandWeight(0.0)).unwrap();
        assert_eq!(path.first(), Some(&(2, 0)));
        assert_eq!(path.last(), Some(&(2, 9)));
        assert_eq!(path.len(), 10); // straight horizontal line
    }

    #[test]
    fn routes_around_obstacle() {
        let mut g = uniform_grid(5, 7, 10.0);
        // Wall at column 3, except one gap at row 0.
        for r in 1..5 {
            let idx = r * g.reference.width + 3;
            g.cost[idx] = f32::INFINITY;
            g.buildability[idx] = 0;
        }
        let path = solve_path(&g, (2, 0), (2, 6), DemandWeight(0.0)).unwrap();
        // Must have detoured through row 0.
        assert!(path.iter().any(|&(r, _)| r == 0));
    }

    #[test]
    fn reports_unreachable() {
        let mut g = uniform_grid(5, 7, 10.0);
        for r in 0..5 {
            let idx = r * g.reference.width + 3;
            g.cost[idx] = f32::INFINITY;
            g.buildability[idx] = 0;
        }
        let err = solve_path(&g, (2, 0), (2, 6), DemandWeight(0.0)).unwrap_err();
        matches!(err, SolverError::Unreachable);
    }
}
