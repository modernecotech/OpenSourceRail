//! Topology synthesis — pick line endpoints + waypoints from anchors.
//!
//! Given a topology archetype (see lib/recipes/city-to-design.toml
//! Step 4), plus the anchor set, produce one or more lines. A line is a
//! sequence of anchor indices that the solver will then wire together
//! in order, calling `solver::solve_path` for each adjacent pair.
//!
//! Archetypes are intentionally small; complexity comes from how the
//! solver snakes between the selected points, not from clever topology.

#![allow(clippy::too_many_arguments, clippy::type_complexity)]
// The planner carries a deliberately explicit scoring context and grid/chord
// tuple vocabulary, so these two lint classes are scoped to this module.

use std::collections::HashSet;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::raster::{Anchor, Grid};
use crate::solver::{solve_path_in_bbox, solve_path_with_penalty, DemandWeight, SolverError};

/// Soft penalty (cost units) added to cells already on the line being
/// built. ~50 is large compared to typical arterial cost (~8) so the
/// solver actively avoids re-entering its own corridor unless terrain
/// leaves no alternative — this is what stops "lines that go back on
/// themselves" through the same downtown.
const SELF_PENALTY: f32 = 60.0;
/// Soft penalty for cells already used by a *different* line in the same
/// city. Smaller than `SELF_PENALTY` because shared trunks (two lines on
/// one viaduct) are an acceptable real-world pattern; we just don't
/// want every line to collapse onto the same spine by default.
const CROSS_LINE_PENALTY: f32 = 12.0;
/// Radius (in cells, 20 m each) over which the penalty bleeds. 8 cells
/// ≈ 160 m — enough to push a parallel detour out of the same block.
const PENALTY_RADIUS_CELLS: usize = 8;

/// Radius around the demand-weighted hub within which radial self/cross
/// penalties are *not* applied. Without this carve-out every radial gets
/// pushed onto its own central corridor, producing the "lines do not
/// converge in the centre" failure mode (passengers cannot interchange
/// downtown without walking 600 m). With it, multiple radials may share
/// the central trunk and a forced hub station collapses them into a
/// single interchange.
///
/// 30 cells ≈ 600 m at the standard 20 m grid — a real-world central
/// shared trunk is typically 400-800 m before lines fan out.
pub const HUB_RADIUS_CELLS: usize = 30;

/// Demand threshold below which trailing cells at line endpoints are
/// trimmed away. The planner originally ran lines all the way out to
/// the chosen anchor regardless of whether anyone lives between the
/// last station and the terminus, producing the "1.8–2.8 km gap with
/// no stops at the line's end" failure mode. After routing we walk
/// inward from each end while demand stays below this threshold and
/// drop those cells; station placement then runs against the trimmed
/// cell sequence so the line literally ends at a station.
const TAIL_TRIM_DEMAND_THR: f32 = 0.06;
/// Maximum fraction of the original cell sequence that can be trimmed
/// at each end. Prevents runaway trimming on a leg that is genuinely
/// low-demand throughout (in which case the whole line should be
/// reconsidered, not silently shortened to nothing).
const TAIL_TRIM_MAX_FRAC: f32 = 0.35;

/// Half-width of the "corridor" around the chord between a leg's two
/// endpoints, expressed as a fraction of the chord length. Inside the
/// corridor there is no penalty; outside, every extra cell of
/// perpendicular distance adds `CORRIDOR_PENALTY_PER_CELL` to the
/// solver's per-cell cost.
///
/// Without this, the demand reward will pull a route 2 km off-axis to
/// touch a single high-demand cluster, producing the "line goes back
/// on itself" shape (tortuosity ~1.9× for Samawah's first radial).
/// Capped at `CORRIDOR_HALF_WIDTH_CAP_CELLS` so very long legs still
/// have to follow a sensible corridor.
const CORRIDOR_HALF_WIDTH_FRAC: f32 = 0.20;
const CORRIDOR_HALF_WIDTH_CAP_CELLS: f32 = 60.0; // ≈ 1.2 km
const CORRIDOR_PENALTY_PER_CELL: f32 = 10.0;

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
        return Err(TopologyError::TooFewAnchors {
            min: 2,
            got: anchors.len(),
        });
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
    let h = grid.reference.height;
    let w = grid.reference.width;
    // Cross-line mask accumulates a penalty for every cell already used
    // by an emitted line, so each subsequent line is pushed onto its own
    // corridor unless terrain forces sharing.
    let mut cross_mask: Vec<f32> = vec![0.0; h * w];

    match archetype {
        TopologyArchetype::SingleRadial => {
            let (endpoints, _used) = pick_radial_endpoints(grid, anchors, &ordered, 1)?;
            let (a, b) = endpoints[0];
            let mut mask = vec![0.0_f32; h * w];
            stamp_corridor(&mut mask, anchors[a].cell(), anchors[b].cell(), h, w);
            let cells = solve_path_with_penalty(
                grid,
                anchors[a].cell(),
                anchors[b].cell(),
                demand_w,
                Some(&mask),
            )?;
            let cells = trim_low_demand_tails(grid, &cells, false);
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
            let radial_cells = via_centre(grid, anchors, a, b, centre, demand_w, &cross_mask)?;
            let radial_cells = trim_low_demand_tails(grid, &radial_cells, false);
            stamp_penalty_excluding_hub(
                &mut cross_mask,
                &radial_cells,
                h,
                w,
                CROSS_LINE_PENALTY,
                centre,
                HUB_RADIUS_CELLS,
            );

            let ring_anchors = pick_ring_anchors(grid, anchors, &ordered, &used, 4)?;
            let ring_cells = route_ring(grid, anchors, &ring_anchors, demand_w, &cross_mask)?;
            stamp_penalty(&mut cross_mask, &ring_cells, h, w, CROSS_LINE_PENALTY);

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
                    anchor_ids: ring_anchors,
                    cells: ring_cells,
                },
            ])
        }
        TopologyArchetype::CrossPlusRing => {
            let (endpoints, used) = pick_radial_endpoints(grid, anchors, &ordered, 2)?;
            let mut lines = Vec::new();
            for (i, (a, b)) in endpoints.iter().enumerate() {
                let cells = via_centre(grid, anchors, *a, *b, centre, demand_w, &cross_mask)?;
                let cells = trim_low_demand_tails(grid, &cells, false);
                stamp_penalty_excluding_hub(
                    &mut cross_mask,
                    &cells,
                    h,
                    w,
                    CROSS_LINE_PENALTY,
                    centre,
                    HUB_RADIUS_CELLS,
                );
                lines.push(Line {
                    name: format!("line-{}", i + 1),
                    shape: LineShape::Radial,
                    anchor_ids: vec![*a, *b],
                    cells,
                });
            }
            let ring_anchors = pick_ring_anchors(grid, anchors, &ordered, &used, 6)?;
            let ring_cells = route_ring(grid, anchors, &ring_anchors, demand_w, &cross_mask)?;
            stamp_penalty(&mut cross_mask, &ring_cells, h, w, CROSS_LINE_PENALTY);
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
                let cells = via_centre(grid, anchors, *a, *b, centre, demand_w, &cross_mask)?;
                let cells = trim_low_demand_tails(grid, &cells, false);
                stamp_penalty_excluding_hub(
                    &mut cross_mask,
                    &cells,
                    h,
                    w,
                    CROSS_LINE_PENALTY,
                    centre,
                    HUB_RADIUS_CELLS,
                );
                lines.push(Line {
                    name: format!("line-{}", i + 1),
                    shape: LineShape::Radial,
                    anchor_ids: vec![*a, *b],
                    cells,
                });
            }

            // Inner ring: 6 anchors closer to centre.
            let inner =
                pick_ring_anchors_by_radius(grid, anchors, &ordered, &used, 6, RingBand::Inner)?;
            let mut used2 = used.clone();
            used2.extend(&inner);
            let inner_cells = route_ring(grid, anchors, &inner, demand_w, &cross_mask)?;
            stamp_penalty(&mut cross_mask, &inner_cells, h, w, CROSS_LINE_PENALTY);
            lines.push(Line {
                name: "line-5".into(),
                shape: LineShape::Ring,
                anchor_ids: inner,
                cells: inner_cells,
            });

            // Outer ring: 8 anchors farther out.
            let outer =
                pick_ring_anchors_by_radius(grid, anchors, &ordered, &used2, 8, RingBand::Outer)?;
            let outer_cells = route_ring(grid, anchors, &outer, demand_w, &cross_mask)?;
            stamp_penalty(&mut cross_mask, &outer_cells, h, w, CROSS_LINE_PENALTY);
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

/// Coverage-objective budget for `greedy_synthesize_lines`.
///
/// The greedy planner does not pre-commit to ring/radial archetypes — it
/// just keeps committing the best-coverage line until one of these limits
/// is hit. `coverage_radius_m` defines the disc around each line cell
/// considered "covered" (a proxy for station catchment); cells with
/// demand >= 0.30 inside any such disc count toward the network's
/// coverage objective.
#[derive(Debug, Clone, Copy)]
pub struct GreedyBudget {
    pub max_lines: usize,
    pub max_total_route_m: f64,
    /// Stop adding lines once the next-best candidate covers fewer than
    /// this many *new* high-demand cells per kilometre of route.
    pub min_coverage_per_km: f32,
    /// Catchment radius — cells within this distance of any line cell
    /// are "covered" and don't add to the next candidate's reward.
    pub coverage_radius_m: f32,
    pub min_line_length_m: f64,
    pub max_line_length_m: f64,
    /// Minimum anchor weight to be considered as a line endpoint.
    pub min_anchor_weight: f32,
    /// Run a real Dijkstra solve only for the top-K chord-prescored pairs
    /// per iteration. Higher K → better solution, slower wall-clock.
    pub top_k: usize,
    /// Anchors are coalesced into bins this many cells wide before pair
    /// generation — without this, big cities with thousands of anchors
    /// produce a quadratic prescore that runs for many minutes. Picks
    /// the highest-weight anchor per bin.
    pub coalesce_bin_cells: usize,
    /// When running Dijkstra, restrict exploration to a bbox covering
    /// the chord plus this fractional margin (e.g. 0.30 = 30% of the
    /// chord length on each side). Optimal least-cost paths almost
    /// always lie within ~10–20% of the chord; clipping the search at
    /// 30% gives a 5–10× speed-up over full-grid Dijkstra with
    /// effectively no quality cost.
    pub bbox_margin_frac: f32,
}

/// Population-tier budget defaults. Keep these on the conservative side —
/// the greedy stop condition (`min_coverage_per_km`) ends iteration when
/// the marginal line stops being worthwhile, so over-budget caps just
/// give the planner room to do its job; under-budget caps cut it off.
#[must_use]
pub fn budget_for_population(pop: u64) -> GreedyBudget {
    match pop {
        0..=300_000 => GreedyBudget {
            max_lines: 3,
            max_total_route_m: 36_000.0,
            min_coverage_per_km: 200.0,
            coverage_radius_m: 600.0,
            // Smaller regional cities can have compact but valid 2–4 km
            // demand spines (Soroti and Lichinga are concrete catalogue
            // examples). A 5 km floor discarded every endpoint pair before
            // routing; retain the coverage-per-km gate as the quality filter.
            min_line_length_m: 2_000.0,
            max_line_length_m: 16_000.0,
            min_anchor_weight: 0.15,
            top_k: 16,
            coalesce_bin_cells: 30, // 600 m
            bbox_margin_frac: 0.35,
        },
        300_001..=1_000_000 => GreedyBudget {
            max_lines: 3,
            // Bumped 60 → 100 km 2026-04-26 alongside the
            // served-catchment bbox widening: a ~20 × 20 km bbox
            // for a Cuenca-class light-metro city has a ~28 km
            // diagonal — three radials at ~25 km each + ring
            // exceed the old 60 km cap.
            max_total_route_m: 100_000.0,
            // Drop min_coverage_per_km 200 → 80 cells/km 2026-04-26.
            // The new sparser spacing (1.2 / 2 / 4 km) means the 2nd
            // and 3rd radials cover incremental rather than primary
            // demand — line-1 takes the highest-density chord and
            // raises the bar; subsequent lines must still cover real
            // population centres but at the *new-coverage* margin,
            // not the absolute density of line-1. 80 cells/km =
            // ~1.6 ha new walkshed per km, equivalent to one fresh
            // residential block per station — the user's brief.
            min_coverage_per_km: 80.0,
            coverage_radius_m: 600.0,
            // Drop min_line_length 8 km → 5 km 2026-04-26 — the
            // canonical 8 × 8 km bbox for a 374 k-pop city
            // in the small-city band can't fit an 8 km line that **also**
            // crosses the centre and reaches a peripheral anchor.
            // 5 km matches the small-city band's floor and lets the
            // 3rd radial pick a shorter outer chord instead of
            // failing the whole synthesis.
            min_line_length_m: 5_000.0,
            // Bumped 22 → 30 km 2026-04-26 to fit a corner-to-corner
            // chord in the served-catchment bbox (≈ 28 km diagonal).
            max_line_length_m: 30_000.0,
            min_anchor_weight: 0.15,
            top_k: 14,
            // Tighter coalescing (60 → 40 cells, 1.2 km → 800 m).
            // The population-aware demand layer surfaces residential
            // anchor clusters that the looser bin merged into a
            // single rep, hiding ~half of the real demand peaks.
            coalesce_bin_cells: 40,
            bbox_margin_frac: 0.30,
        },
        1_000_001..=3_000_000 => GreedyBudget {
            max_lines: 6,
            // Bumped 220 → 320 km 2026-04-26 alongside the
            // served-catchment bbox widening (~30 × 30 km): five
            // radials at ~38 km each + a ~110 km ring at
            // 0.55 × urban_radius. Tehran 280 km / 7 lines, Madrid
            // 290 km / 13 lines, Lyon Métropole real network ~
            // 195 km of metro+tram alone.
            max_total_route_m: 320_000.0,
            min_coverage_per_km: 150.0,
            coverage_radius_m: 600.0,
            min_line_length_m: 12_000.0,
            // Bumped 28 → 60 km 2026-04-26 to fit corner-to-corner
            // chords in the ~30 × 30 km served-catchment bbox: the
            // diagonal is ~42 km but Dijkstra paths through dense
            // arterials around water / restricted zones (Lyon:
            // Rhône + Saône + Parc de la Tête d'Or, Tunis: Lake of
            // Tunis, Coimbatore: airport perimeter) can add 30–40%
            // over straight-chord length. The greedy stop condition
            // (`min_coverage_per_km`) prevents long lines from being
            // chosen unless they actually cover demand, so a wider
            // line-length window doesn't produce wasteful routing.
            max_line_length_m: 60_000.0,
            min_anchor_weight: 0.20,
            top_k: 14,
            coalesce_bin_cells: 80, // 1.6 km
            bbox_margin_frac: 0.30,
        },
        _ => GreedyBudget {
            max_lines: 9,
            // 600 km — fits 8 cross-city via-hub radials at ~50 km
            // each (~400 km) plus a ~140 km circumferential ring at
            // 0.55 × urban_radius. Real comparators: London ~400 km
            // / 11 lines (no Crossrail), Beijing ~700 km / 22 lines,
            // Madrid 290 km / 13 lines, Tokyo metro+through-running
            // ~1000 km. Bumped 500 → 600 km 2026-04-26 alongside
            // the bbox-sizing policy widening.
            max_total_route_m: 600_000.0,
            min_coverage_per_km: 100.0,
            coverage_radius_m: 600.0,
            min_line_length_m: 16_000.0,
            // 60 km — sized so a centre-to-edge-of-bbox chord fits
            // for a 50 × 50 km mega-city served-catchment bbox
            // (~70 km diagonal); with ~15 % via-hub routing overhead
            // a 50 km chord lands at ~58 km routed. Bumped 48 → 60 km
            // 2026-04-26 — earlier 48 km left ~50 km Greater-Nairobi
            // satellites (Athi River, Kiambu) just out of radial reach
            // when the bbox extended to the metro periphery. Real
            // comparators: Cairo Line 3 = 44 km, Tehran Line 1 ≈ 38 km,
            // Beijing Line 6 = 53 km, Mumbai Aqua = 33 km.
            max_line_length_m: 60_000.0,
            min_anchor_weight: 0.20,
            top_k: 14,
            coalesce_bin_cells: 100, // 2 km
            bbox_margin_frac: 0.30,
        },
    }
}

/// Threshold above which a cell counts toward the coverage objective.
/// Has to be high enough to exclude farmland but low enough to capture
/// suburban residential. 0.30 was calibrated against Baghdad (where
/// 0.20 includes Mahmudiyah farmland and 0.40 misses Sadr City fringes).
const COVERAGE_DEMAND_THR: f32 = 0.30;
pub(crate) const MAX_RADIAL_BACKTRACK_M: f64 = 700.0;

/// Greedy coverage-first line synthesizer.
///
/// Replaces `synthesize_lines`'s archetype-driven flow (radial endpoints
/// → ring → enforce). Instead, at each step we:
///
/// 1. Enumerate all anchor pairs (a, b) with chord length in
///    `[min_line_length_m, max_line_length_m]` and weight ≥ threshold.
/// 2. Pre-score by chord-buffer coverage — count uncovered high-demand
///    cells within `coverage_radius_m` of the straight chord.
/// 3. Run real Dijkstra (with cross-line penalty mask) on the top-K and
///    score by *new coverage per kilometre* of routed length.
/// 4. Commit the best, stamp its corridor, mark its catchment covered,
///    and repeat until budget or marginal-coverage threshold is hit.
///
/// The coverage objective is the *fraction of high-demand cells within
/// `coverage_radius_m` of any line cell*. This is the same KPI we measure
/// post-hoc in `osr_scenario.diagnose`, so the optimizer is hill-climbing
/// the metric the user actually reads.
pub fn greedy_synthesize_lines(
    grid: &Grid,
    anchors: &[Anchor],
    demand_w: DemandWeight,
    budget: &GreedyBudget,
) -> Result<Vec<Line>, TopologyError> {
    if anchors.len() < 2 {
        return Err(TopologyError::TooFewAnchors {
            min: 2,
            got: anchors.len(),
        });
    }
    let h = grid.reference.height;
    let w = grid.reference.width;
    let cell_m = grid.reference.cell_m as f32;
    let radius_cells = ((budget.coverage_radius_m / cell_m).round() as usize).max(1);

    let raw_usable: Vec<usize> = (0..anchors.len())
        .filter(|&i| anchors[i].weight >= budget.min_anchor_weight)
        .collect();
    if raw_usable.len() < 2 {
        return Err(TopologyError::TooFewAnchors {
            min: 2,
            got: raw_usable.len(),
        });
    }
    let usable = coalesce_anchors(anchors, &raw_usable, budget.coalesce_bin_cells);
    eprintln!(
        "  greedy: {} anchors (weight ≥ {:.2}) coalesced into {} bin reps @ {} cells",
        raw_usable.len(),
        budget.min_anchor_weight,
        usable.len(),
        budget.coalesce_bin_cells,
    );
    if usable.len() < 2 {
        return Err(TopologyError::TooFewAnchors {
            min: 2,
            got: usable.len(),
        });
    }

    let hub_raw = grid_centre(grid);
    let hub = nudge_to_buildable(grid, hub_raw).unwrap_or(hub_raw);
    let urban_r = urban_radius(grid, hub);

    let mut covered = vec![false; h * w];
    let mut cross_mask = vec![0.0_f32; h * w];
    let mut lines: Vec<Line> = Vec::new();
    let mut committed_chords: Vec<((usize, usize), (usize, usize))> = Vec::new();
    let mut used_anchor_ids: HashSet<usize> = HashSet::new();
    let mut committed_terminus_angles: Vec<f32> = Vec::new();
    let mut total_route_m = 0.0_f64;

    // Reserve one slot for a circumferential ring on cities with
    // ≥ 4 lines. Cross-radial trips (suburb → suburb without going
    // downtown) and cross-radial transfers benefit from a ring at
    // ~0.55 × urban_radius, the same band every real metro of this
    // size deploys (London Circle, Beijing 2/10, Moscow Koltsevaya,
    // Madrid 6, Tokyo Yamanote). Without this slot, greedy radials
    // alone leave tangential demand stranded — the user-flagged
    // "no way to centre from suburbs without a transfer" problem.
    let reserve_ring = budget.max_lines >= 4;
    // Estimated ring length at 0.55 × urban_radius, including a
    // 1.4× road-snap detour factor (a real Dijkstra ring on the OSM
    // graph runs ~30-50 % longer than the great-circle chord set —
    // measured against Baghdad which produced a 108 km ring on a
    // ~24 km urban radius, vs the ideal 83 km chord ring). Keeping
    // this honest is what stops the radial loop from consuming the
    // whole route-km cap and starving the ring.
    let ring_length_estimate_m = if reserve_ring {
        // Length-budget estimate uses 0.70 × urban_r — the midpoint
        // of the (0.55, 0.85) outer-band the ring anchors land in.
        let ring_radius_cells = 0.70 * urban_r;
        let chord_circumference_cells = 2.0 * std::f32::consts::PI * ring_radius_cells;
        let detour_factor = 1.4_f32;
        f64::from(chord_circumference_cells * detour_factor * cell_m)
    } else {
        0.0
    };
    let radial_max_lines = if reserve_ring {
        budget.max_lines.saturating_sub(1)
    } else {
        budget.max_lines
    };
    let radial_budget_m = (budget.max_total_route_m - ring_length_estimate_m).max(0.0);

    while lines.len() < radial_max_lines && total_route_m < radial_budget_m {
        // Phase 2 kicks in once half the line budget is used: any
        // remaining line must reach a peripheral anchor (d > 0.9 ×
        // urban_r). Without this the greedy planner keeps picking
        // dense central rim-gap chords forever and never reaches the
        // satellite suburbs that motivated metro planning in the first
        // place (Abu Ghraib, Taji for Baghdad).
        //
        // Small (≤ 3-line) networks skip the peripheral requirement
        // — their bbox is too tight to populate the 0.9 × urban_r
        // outer ring with enough anchor reps to satisfy the filter,
        // and the cross_mask penalty already diversifies line picks
        // when there are only 3 candidates to choose between.
        let phase2_peripheral =
            budget.max_lines >= 4 && !lines.is_empty() && lines.len() >= budget.max_lines / 2;
        // Min angular separation between radial endpoints. Only applied
        // for networks of ≥ 5 radials — below that the parallelism
        // penalty already suffices and a strict angular filter starves
        // candidate generation in small anchor pools (Samawah dropped
        // to 2 lines under a 30° rule). For larger networks, threshold
        // is sized so 2·N endpoints fit around 360° with slack:
        // 360°/(2·N) · 0.5 ≈ a quarter sector.
        let min_angular_separation_rad = if radial_max_lines >= 5 {
            (360.0 / (2.0 * radial_max_lines as f32) * 0.5).to_radians()
        } else {
            0.0
        };
        let ctx = GreedyContext {
            hub,
            urban_r,
            committed_chords: &committed_chords,
            committed_termini: &used_anchor_ids,
            committed_terminus_angles: &committed_terminus_angles,
            min_angular_separation_rad,
            // 75 cells = 1500 m at 20 m grid: two arterials within this
            // perpendicular distance, running roughly parallel, are the
            // "ladder" failure mode the prescore needs to suppress.
            parallel_proximity_cells: 75.0,
            // 0.85 means a perfectly parallel + overlapping candidate
            // loses 85 % of its score — enough to lose to a clean
            // alternative without zeroing it out (so a parallel chord
            // is still a fallback if nothing else exists).
            parallelism_strength: 0.85,
            // chords passing this close to the hub get routed two-leg
            // via the hub rather than along the raw chord — this is
            // what stops radials from "avoiding the city centre" and
            // the post-routing hub-station snap from creating a dogleg.
            //
            // For ≤ 3-line networks (small cities like Samawah) every
            // radial **must** converge on the centre or the network
            // can't function as a hub-and-spoke — without this, the
            // 3rd radial picks an outer-to-outer pair that bypasses
            // the CBD entirely (the "superfluous green line" failure
            // mode flagged by operator review 2026-04-26). Make the
            // hub-attract radius cover the whole bounding-box on
            // ≤ 3-line networks; for megacities the inherited 1200 m
            // (2 × HUB_RADIUS) is enough because the ring + 4+
            // radials already create dense centre coverage.
            // For ≤ 3-line networks (small cities like Samawah)
            // every radial **must** converge on the centre or the
            // network is a set of disjoint orphans. The default
            // 60-cell (1.2 km) proximity is too tight — chords with
            // both endpoints in the same half-plane (e.g. SE Outer
            // ↔ N Outer) pass 1.5–2.5 km from the hub and route
            // direct, bypassing the CBD. Bumped to 150 cells (3 km)
            // for small-line networks: covers any chord crossing
            // the urban core, while still leaving genuinely
            // peripheral chords routed direct on megacity radials
            // (which already converge via the ring + 4+ siblings).
            hub_proximity_cells: if budget.max_lines <= 3 {
                150.0
            } else {
                2.0 * HUB_RADIUS_CELLS as f32
            },
            // Endpoint-periphery cap: deepest-suburb chord gets a 2×
            // raw-score multiplier. Modest because phase2 already
            // hard-filters peripheral chords; this just ranks among
            // them.
            peripheral_factor_cap: 2.0,
            require_peripheral_endpoint: phase2_peripheral,
        };
        let cand = match find_best_candidate(
            grid,
            anchors,
            &usable,
            demand_w,
            &cross_mask,
            &covered,
            budget,
            radius_cells,
            &ctx,
        )? {
            Some(c) => c,
            None => break,
        };
        if cand.coverage_per_km < budget.min_coverage_per_km {
            eprintln!(
                "  greedy: stopping — best next line covers {:.1}/km < min {:.1}/km",
                cand.coverage_per_km, budget.min_coverage_per_km
            );
            break;
        }
        eprintln!(
            "  greedy line-{}: anchors {}->{}  {:.0} m, +{} cells covered ({:.1}/km, elevated constructability x{:.2})",
            lines.len() + 1,
            cand.a,
            cand.b,
            cand.length_m,
            cand.new_coverage,
            cand.coverage_per_km,
            cand.constructability_multiplier,
        );

        update_covered(&mut covered, grid, &cand.cells, h, w, radius_cells);
        // Wider greedy stamp (≈ 500 m) than the archetype planner
        // (160 m). With absolute new-coverage as the score, the
        // greedy will naturally pick adjacent parallel corridors
        // unless they're suppressed — a 500 m exclusion buffer is
        // about one block-width off the previous line, enough to
        // force the next line onto a different arterial. Inside the
        // hub it's still excluded so radials can converge there.
        let greedy_stamp_radius_cells: usize = 25;
        let mut stamped = cand.cells.clone();
        // Drop cells inside the hub from the cross-line stamp so multiple
        // lines can converge on a shared central trunk.
        let hub_r2 = (HUB_RADIUS_CELLS * HUB_RADIUS_CELLS) as isize;
        stamped.retain(|&(r, c)| {
            let dr = r as isize - hub.0 as isize;
            let dc = c as isize - hub.1 as isize;
            dr * dr + dc * dc > hub_r2
        });
        stamp_penalty_radius(
            &mut cross_mask,
            &stamped,
            h,
            w,
            CROSS_LINE_PENALTY * 2.5,
            greedy_stamp_radius_cells,
        );
        total_route_m += cand.length_m;

        committed_chords.push((anchors[cand.a].cell(), anchors[cand.b].cell()));
        used_anchor_ids.insert(cand.a);
        used_anchor_ids.insert(cand.b);
        // Record the bearings of both endpoints from the hub. Endpoints
        // inside a small central radius (where bearing is meaningless)
        // are skipped — the via-hub branch routes the line through
        // centre regardless.
        let ang_thr = (0.20 * urban_r).max(20.0);
        for &aid in &[cand.a, cand.b] {
            let (ar, ac) = anchors[aid].cell();
            let dr = ar as f32 - hub.0 as f32;
            let dc = ac as f32 - hub.1 as f32;
            if (dr * dr + dc * dc).sqrt() >= ang_thr {
                committed_terminus_angles.push(dr.atan2(dc));
            }
        }
        let proposed_trim = trim_low_demand_tails(grid, &cand.cells, false);
        let trimmed = if maximum_axis_backtrack_m(&proposed_trim, f64::from(cell_m))
            >= MAX_RADIAL_BACKTRACK_M
        {
            cand.cells
        } else {
            proposed_trim
        };
        lines.push(Line {
            name: format!("line-{}", lines.len() + 1),
            shape: LineShape::Radial,
            anchor_ids: vec![cand.a, cand.b],
            cells: trimmed,
        });
    }

    if lines.is_empty() {
        return Err(TopologyError::TooFewAnchors { min: 2, got: 0 });
    }

    // Try to append a circumferential ring as the last line.
    if reserve_ring {
        match try_synthesize_ring(
            grid,
            anchors,
            &usable,
            &used_anchor_ids,
            demand_w,
            &cross_mask,
            budget,
            lines.len() + 1,
        ) {
            Ok(Some(ring_line)) => {
                let ring_len_m = cell_path_length_m(&ring_line.cells, f64::from(cell_m));
                // Allow up to a 10 % overshoot of the cap for the ring —
                // the estimate above is a chord-circle approximation and
                // the real route bends around no-build cells.
                let cap_with_slack = budget.max_total_route_m * 1.10;
                if total_route_m + ring_len_m <= cap_with_slack {
                    eprintln!(
                        "  greedy: appended ring (line-{}) — {} cells, {:.0} m",
                        lines.len() + 1,
                        ring_line.cells.len(),
                        ring_len_m,
                    );
                    lines.push(ring_line);
                } else {
                    eprintln!(
                        "  greedy: ring would exceed total budget \
                         ({:.0} m + {:.0} m > {:.0} m × 1.10), skipping",
                        total_route_m, ring_len_m, budget.max_total_route_m,
                    );
                }
            }
            Ok(None) => {
                eprintln!("  greedy: no ring synthesized (insufficient peripheral anchors)");
            }
            Err(e) => {
                eprintln!("  greedy: ring synthesis failed: {e}");
            }
        }
    }

    Ok(lines)
}

/// Build a circumferential ring from the unused-anchor pool, route it
/// with bbox-clipped Dijkstra (so a Baghdad-sized grid doesn't cost
/// minutes per segment), and return it as a `Line`. Returns `Ok(None)`
/// if the ring band can't be filled with at least 3 anchors — that is
/// the legitimate small-city case where no useful ring exists.
fn try_synthesize_ring(
    grid: &Grid,
    anchors: &[Anchor],
    usable: &[usize],
    used: &HashSet<usize>,
    demand_w: DemandWeight,
    cross_mask: &[f32],
    budget: &GreedyBudget,
    line_idx: usize,
) -> Result<Option<Line>, TopologyError> {
    // 8 anchors gives the ring an average chord of
    // 2 × R × sin(π/8) ≈ 0.77 × R per segment. Eight transfer points
    // around the city is also what real circle lines run with
    // (London Circle = 27 stops/7 lines, Madrid 6 = 28 stops, Beijing
    // 2 = 18 stops). Falling back to 6 below if the band is sparse.
    let preferred_n = 8_usize;
    let fallback_n = 6_usize;

    let mut ordered_usable: Vec<usize> = usable.to_vec();
    ordered_usable.sort_by(|&a, &b| {
        anchors[b]
            .weight
            .partial_cmp(&anchors[a].weight)
            .unwrap_or(std::cmp::Ordering::Equal)
    });

    let ring_ids = match pick_ring_anchors_by_radius(
        grid,
        anchors,
        &ordered_usable,
        used,
        preferred_n,
        RingBand::Outer,
    ) {
        Ok(v) => v,
        Err(_) => {
            // Outer band sparse — try Inner as a fallback so anchor-
            // poor cities (Samawah is below the threshold but a
            // future ~600k city could hit this) still get a ring.
            match pick_ring_anchors_by_radius(
                grid,
                anchors,
                &ordered_usable,
                used,
                fallback_n,
                RingBand::Inner,
            ) {
                Ok(v) => v,
                Err(_) => return Ok(None),
            }
        }
    };

    let cells = match route_ring_in_bbox(
        grid,
        anchors,
        &ring_ids,
        demand_w,
        cross_mask,
        budget.bbox_margin_frac,
    ) {
        Ok(c) => c,
        Err(_) => return Ok(None),
    };

    Ok(Some(Line {
        name: format!("line-{}", line_idx),
        shape: LineShape::Ring,
        anchor_ids: ring_ids,
        cells,
    }))
}

struct Candidate {
    a: usize,
    b: usize,
    cells: Vec<(usize, usize)>,
    length_m: f64,
    new_coverage: u32,
    coverage_per_km: f32,
    constructability_multiplier: f64,
    effective_coverage_score: f64,
}

struct GreedyContext<'a> {
    hub: (usize, usize),
    urban_r: f32,
    committed_chords: &'a [((usize, usize), (usize, usize))],
    /// Anchors already serving as a terminus on a previously committed
    /// radial. Banning reuse here prevents the "two radials sharing a
    /// terminus and one taking a southern bypass arc" failure mode
    /// observed on Samawah, where lines 2 and 3 both started at the
    /// same west anchor and one was routed around the city centre.
    committed_termini: &'a HashSet<usize>,
    /// Angular bearings (radians, atan2 of cell offset from hub) of the
    /// peripheral endpoints of every previously committed radial.
    /// Candidates whose peripheral endpoint sits within
    /// `min_angular_separation_rad` of any committed bearing are skipped,
    /// forcing radials to spread around the compass. Without this, a
    /// demand-following greedy stacks 3 NE radials and leaves the eastern
    /// satellite suburbs (Nahrawan for Baghdad) with no service.
    committed_terminus_angles: &'a [f32],
    min_angular_separation_rad: f32,
    parallel_proximity_cells: f32,
    parallelism_strength: f32,
    hub_proximity_cells: f32,
    peripheral_factor_cap: f32,
    require_peripheral_endpoint: bool,
}

fn find_best_candidate(
    grid: &Grid,
    anchors: &[Anchor],
    usable: &[usize],
    demand_w: DemandWeight,
    cross_mask: &[f32],
    covered: &[bool],
    budget: &GreedyBudget,
    radius_cells: usize,
    ctx: &GreedyContext,
) -> Result<Option<Candidate>, TopologyError> {
    let cell_m = grid.reference.cell_m as f32;
    // Chord length is a *lower bound* on routed length — Dijkstra can
    // only ever return ≥ chord cells. Bound chord above by the line cap
    // (with a 5% safety margin) so we don't run Dijkstras that always
    // land outside the length filter.
    let min_chord_cells = (budget.min_line_length_m as f32 / cell_m) * 0.90;
    let max_chord_cells = (budget.max_line_length_m as f32 / cell_m) * 0.85;
    let peripheral_thr_cells = 0.9 * ctx.urban_r;

    let mut prescored: Vec<(usize, usize, f32)> = Vec::new();
    for i in 0..usable.len() {
        for j in (i + 1)..usable.len() {
            let a = usable[i];
            let b = usable[j];
            // Hard ban on terminus reuse — a radial sharing an endpoint
            // with a previously committed radial collapses the two
            // lines onto one direction, and the second line typically
            // takes a bypass arc to avoid the cross-line penalty,
            // which in turn produces the "line going around the city
            // centre" + orphan-hub-station artefact.
            if ctx.committed_termini.contains(&a) || ctx.committed_termini.contains(&b) {
                continue;
            }
            let chord = dist_from(anchors[a].cell(), anchors[b].cell());
            if chord < min_chord_cells || chord > max_chord_cells {
                continue;
            }
            // Angular-spread filter: each endpoint's bearing from the hub
            // must sit clear of every previously-committed bearing by
            // `min_angular_separation_rad`. Without this the greedy
            // stacks radials in the highest-demand sector and leaves
            // peripheral satellites (Baghdad's Nahrawan) unserved.
            // Endpoints inside a small central core have meaningless
            // bearings — they're skipped (the via-hub branch handles
            // them).
            if ctx.min_angular_separation_rad > 0.0 && !ctx.committed_terminus_angles.is_empty() {
                let ang_thr = (0.20 * ctx.urban_r).max(20.0);
                let mut crowded = false;
                for &aid in &[a, b] {
                    let (ar, ac) = anchors[aid].cell();
                    let dr = ar as f32 - ctx.hub.0 as f32;
                    let dc = ac as f32 - ctx.hub.1 as f32;
                    if (dr * dr + dc * dc).sqrt() < ang_thr {
                        continue;
                    }
                    let ang = dr.atan2(dc);
                    for &committed in ctx.committed_terminus_angles {
                        let mut diff = (ang - committed).abs();
                        if diff > std::f32::consts::PI {
                            diff = 2.0 * std::f32::consts::PI - diff;
                        }
                        if diff < ctx.min_angular_separation_rad {
                            crowded = true;
                            break;
                        }
                    }
                    if crowded {
                        break;
                    }
                }
                if crowded {
                    continue;
                }
            }
            // Phase-2 hard filter: at least one endpoint must sit
            // beyond the urban core. Forces late-stage lines to reach
            // satellite suburbs instead of stacking another central
            // rim-gap radial.
            if ctx.require_peripheral_endpoint {
                let da = dist_from(anchors[a].cell(), ctx.hub);
                let db = dist_from(anchors[b].cell(), ctx.hub);
                if da < peripheral_thr_cells && db < peripheral_thr_cells {
                    continue;
                }
            }
            let raw = chord_coverage_score(
                grid,
                anchors[a].cell(),
                anchors[b].cell(),
                covered,
                radius_cells,
            );
            if raw <= 0.0 {
                continue;
            }
            // Endpoint-weight bonus. Bumped 50 → 400 (2026-04-26
            // operator review): at 50 a residential chord
            // (`place=neighbourhood`, w=0.6) ran 5–10 % more covered
            // cells than a chord terminating at a top-tier POI
            // (`amenity=university` / `amenity=hospital` / `aeroway=
            // aerodrome`, w=0.9–1.0) and won by raw alone, so
            // Samawah's northern university + new hospitals were
            // skipped. At 400 the weight bonus (~720 for a w=0.9
            // pair) is comparable to typical raw scores
            // (500–1500 cells) so the algorithm balances
            // residential coverage against serving headline demand
            // generators.
            // The weight bonus uses the maximum committed-network demand
            // peak in the area as the unit. A high-weight pair
            // (university + hospital, w=1.0+0.9) gets ~2.7×
            // chord_coverage_score worth of bonus — enough to win
            // against a residential-only chord whose raw coverage
            // edged it out by 30 %, but not enough to overrule a
            // chord that genuinely covers 5× the demand.
            let weight_bonus = 1500.0 * (anchors[a].weight + anchors[b].weight);
            // Anchor-density-along-chord factor: count high-weight
            // anchors within the chord buffer and add their weight
            // contribution so the algorithm rewards chords that
            // string MULTIPLE top POIs together (university campus
            // → adjacent hospital → CBD), not just chords whose two
            // ENDPOINTS are high-weight. Without this, line-1 picked
            // a north suburb because the chord between it and a south
            // suburb covered more residential cells, even though a
            // chord through the university campus would have served
            // 4 hospitals + 1 university + 3 colleges.
            let chord_anchor_score = anchor_density_along_chord(anchors, a, b, ctx.urban_r);
            // Endpoint-periphery factor: rewards chords whose endpoints
            // sit beyond the urban core. Combined with phase-2 filtering,
            // this is what pulls late-stage lines out to satellite
            // suburbs once central is covered.
            let endpoint_factor = endpoint_periphery_factor(
                anchors[a].cell(),
                anchors[b].cell(),
                ctx.hub,
                ctx.urban_r,
                ctx.peripheral_factor_cap,
            );
            // Parallelism penalty: discounts chords running roughly
            // parallel to and overlapping with already-committed lines,
            // which is the "ladder" failure mode where two adjacent
            // arterials get committed as separate lines.
            let parallel = chord_parallelism_penalty(
                anchors[a].cell(),
                anchors[b].cell(),
                ctx.committed_chords,
                ctx.parallel_proximity_cells,
            );
            let score = (raw + weight_bonus + chord_anchor_score)
                * endpoint_factor
                * (1.0 - ctx.parallelism_strength * parallel).max(0.05);
            prescored.push((a, b, score));
        }
    }
    if prescored.is_empty() {
        return Ok(None);
    }
    prescored.sort_by(|p, q| q.2.partial_cmp(&p.2).unwrap_or(std::cmp::Ordering::Equal));
    prescored.truncate(budget.top_k);

    let h = grid.reference.height;
    let w = grid.reference.width;
    let mut best: Option<Candidate> = None;
    let mut tried = 0_usize;
    let mut solver_failed = 0_usize;
    let mut length_filtered = 0_usize;
    let mut backtrack_filtered = 0_usize;
    for (a, b, _) in prescored {
        tried += 1;
        let s = anchors[a].cell();
        let g = anchors[b].cell();
        // Chords passing within `hub_proximity_cells` of the demand-
        // weighted hub get routed two-leg via the hub, mirroring the
        // archetype synthesizer's `via_centre`. Without this, the
        // greedy planner picks chord paths that bypass the CBD by a
        // few hundred metres and `force_hub_stations` post-snap creates
        // a visible dogleg — the "lines avoid the city centre" failure
        // mode on Samawah. Other chords are routed directly.
        let route_via_hub = chord_passes_near_hub(s, g, ctx.hub, ctx.hub_proximity_cells);
        let cells_res = if route_via_hub {
            let via_result = solve_via_hub_in_bbox(
                grid,
                s,
                g,
                ctx.hub,
                demand_w,
                cross_mask,
                budget.bbox_margin_frac,
            );
            // In a small or fragmented street grid the bbox-clipped hub leg
            // can be disconnected even though the endpoint pair has a valid
            // direct arterial path. Preserve the centre-first preference, but
            // fall back to that direct path instead of rejecting every city
            // candidate. Infinite-cost water/protected cells remain blocked by
            // the same solver, so this does not weaken buildability safety.
            via_result.or_else(|_| {
                let bbox = chord_bbox(grid, s, g, budget.bbox_margin_frac);
                let mut local_mask = cross_mask.to_vec();
                stamp_corridor(&mut local_mask, s, g, h, w);
                solve_path_in_bbox(grid, s, g, demand_w, Some(&local_mask), Some(bbox))
                    .or_else(|_| solve_path_with_penalty(grid, s, g, demand_w, Some(&local_mask)))
            })
        } else {
            let bbox = chord_bbox(grid, s, g, budget.bbox_margin_frac);
            // Stack a chord-corridor on top of the cross-line mask so
            // the demand reward can't yank the route 1–2 km off-axis.
            let mut local_mask = cross_mask.to_vec();
            stamp_corridor(&mut local_mask, s, g, h, w);
            solve_path_in_bbox(grid, s, g, demand_w, Some(&local_mask), Some(bbox))
                .or_else(|_| solve_path_with_penalty(grid, s, g, demand_w, Some(&local_mask)))
        };
        let cells = match cells_res {
            Ok(c) => c,
            Err(_) => {
                solver_failed += 1;
                continue;
            }
        };
        let length_m = cell_path_length_m(&cells, cell_m as f64);
        if length_m < budget.min_line_length_m || length_m > budget.max_line_length_m {
            length_filtered += 1;
            continue;
        }
        if maximum_axis_backtrack_m(&cells, cell_m as f64) >= MAX_RADIAL_BACKTRACK_M {
            backtrack_filtered += 1;
            continue;
        }
        let new_coverage = count_new_coverage(grid, &cells, covered, radius_cells);
        let length_km = (length_m / 1000.0) as f32;
        let coverage_per_km = if length_km > 0.0 {
            new_coverage as f32 / length_km
        } else {
            0.0
        };
        let constructability_multiplier =
            crate::civil::route_elevated_constructability_multiplier(grid, &cells);
        let effective_coverage_score =
            f64::from(new_coverage) / constructability_multiplier.max(1.0);
        let cand = Candidate {
            a,
            b,
            cells,
            length_m,
            new_coverage,
            coverage_per_km,
            constructability_multiplier,
            effective_coverage_score,
        };
        // Score by absolute new-coverage so longer lines that fan out to
        // suburbs can win over short, dense centre-only corridors.
        // `coverage_per_km` is still tracked as the stop-condition floor.
        match &best {
            None => best = Some(cand),
            Some(prev) if cand.effective_coverage_score > prev.effective_coverage_score => {
                best = Some(cand)
            }
            _ => {}
        }
    }
    if best.is_none() {
        eprintln!(
            "  greedy: no candidate among {} tried (solver_failed={}, length_filtered={}, backtrack_filtered={})",
            tried, solver_failed, length_filtered, backtrack_filtered
        );
    }
    Ok(best)
}

/// Heuristic prescore: count uncovered high-demand cells within
/// `radius_cells` of the straight chord between `start` and `end`.
///
/// Each cell is checked exactly once (via perpendicular projection), so
/// this is exact for the chord — the routed path will deviate, but a
/// chord-aligned corridor is a reasonable upper bound on what any
/// reasonable route through that pair will cover. Used to prune the pair
/// list before running real Dijkstra on the top K.
fn chord_coverage_score(
    grid: &Grid,
    start: (usize, usize),
    end: (usize, usize),
    covered: &[bool],
    radius_cells: usize,
) -> f32 {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let (sr, sc) = (start.0 as f32, start.1 as f32);
    let (er, ec) = (end.0 as f32, end.1 as f32);
    let dr = er - sr;
    let dc = ec - sc;
    let chord_len = (dr * dr + dc * dc).sqrt();
    if chord_len < 1.0 {
        return 0.0;
    }
    let ur = dr / chord_len;
    let uc = dc / chord_len;
    let nr = -uc;
    let nc = ur;
    let radius = radius_cells as f32;

    let r_min = ((sr.min(er) - radius).max(0.0)) as usize;
    let r_max = ((sr.max(er) + radius) as usize).min(h.saturating_sub(1));
    let c_min = ((sc.min(ec) - radius).max(0.0)) as usize;
    let c_max = ((sc.max(ec) + radius) as usize).min(w.saturating_sub(1));

    let mut count = 0_u32;
    for rr in r_min..=r_max {
        for cc in c_min..=c_max {
            let pr = rr as f32 - sr;
            let pc = cc as f32 - sc;
            let t = pr * ur + pc * uc;
            if t < -radius || t > chord_len + radius {
                continue;
            }
            let perp = (pr * nr + pc * nc).abs();
            if perp > radius {
                continue;
            }
            let idx = rr * w + cc;
            if covered[idx] {
                continue;
            }
            if grid.demand_at(rr, cc) >= COVERAGE_DEMAND_THR {
                count += 1;
            }
        }
    }
    count as f32
}

/// Count new high-demand cells covered by routing `cells` (i.e. cells
/// inside the catchment buffer of the path that are not already in
/// `covered`). Dedupes via a per-call HashSet.
fn count_new_coverage(
    grid: &Grid,
    cells: &[(usize, usize)],
    covered: &[bool],
    radius_cells: usize,
) -> u32 {
    use std::collections::HashSet;
    let h = grid.reference.height;
    let w = grid.reference.width;
    let r2 = (radius_cells * radius_cells) as isize;
    // Sample every radius_cells/2 along the path — adjacent discs overlap
    // ~99 %, so exhaustive walks waste work without changing the answer.
    let step = (radius_cells / 2).max(1);
    let mut new_set: HashSet<usize> = HashSet::new();

    let visit = |r: usize, c: usize, set: &mut HashSet<usize>| {
        let r_min = r.saturating_sub(radius_cells);
        let r_max = (r + radius_cells).min(h.saturating_sub(1));
        let c_min = c.saturating_sub(radius_cells);
        let c_max = (c + radius_cells).min(w.saturating_sub(1));
        for rr in r_min..=r_max {
            for cc in c_min..=c_max {
                let dr = rr as isize - r as isize;
                let dc = cc as isize - c as isize;
                if dr * dr + dc * dc > r2 {
                    continue;
                }
                if grid.demand_at(rr, cc) < COVERAGE_DEMAND_THR {
                    continue;
                }
                let idx = rr * w + cc;
                if covered[idx] {
                    continue;
                }
                set.insert(idx);
            }
        }
    };

    let n = cells.len();
    let mut k = 0_usize;
    while k < n {
        let (r, c) = cells[k];
        visit(r, c, &mut new_set);
        k += step;
    }
    if let Some(&(r, c)) = cells.last() {
        visit(r, c, &mut new_set);
    }
    new_set.len() as u32
}

/// Stamp coverage discs around every Nth cell of `cells` into `covered`.
fn update_covered(
    covered: &mut [bool],
    grid: &Grid,
    cells: &[(usize, usize)],
    h: usize,
    w: usize,
    radius_cells: usize,
) {
    let r2 = (radius_cells * radius_cells) as isize;
    let step = (radius_cells / 2).max(1);
    let stamp = |covered: &mut [bool], r: usize, c: usize| {
        let r_min = r.saturating_sub(radius_cells);
        let r_max = (r + radius_cells).min(h.saturating_sub(1));
        let c_min = c.saturating_sub(radius_cells);
        let c_max = (c + radius_cells).min(w.saturating_sub(1));
        for rr in r_min..=r_max {
            for cc in c_min..=c_max {
                let dr = rr as isize - r as isize;
                let dc = cc as isize - c as isize;
                if dr * dr + dc * dc > r2 {
                    continue;
                }
                if grid.demand_at(rr, cc) < COVERAGE_DEMAND_THR {
                    continue;
                }
                let idx = rr * w + cc;
                covered[idx] = true;
            }
        }
    };
    let n = cells.len();
    let mut k = 0_usize;
    while k < n {
        let (r, c) = cells[k];
        stamp(covered, r, c);
        k += step;
    }
    if let Some(&(r, c)) = cells.last() {
        stamp(covered, r, c);
    }
}

/// Bin anchors into `bin_cells`-wide cells and keep the highest-weight
/// representative per bin. Caps the candidate-pair count for large
/// cities (Baghdad has ~1900 anchors → 1.8M pairs without this; with
/// 100-cell bins → ~150 reps → 11k pairs).
fn coalesce_anchors(anchors: &[Anchor], usable: &[usize], bin_cells: usize) -> Vec<usize> {
    use std::collections::HashMap;
    let bin = bin_cells.max(1);
    let mut bins: HashMap<(usize, usize), (usize, f32)> = HashMap::new();
    for &i in usable {
        let key = (anchors[i].row / bin, anchors[i].col / bin);
        let w = anchors[i].weight;
        match bins.get(&key) {
            None => {
                bins.insert(key, (i, w));
            }
            Some(&(_, prev_w)) if w > prev_w => {
                bins.insert(key, (i, w));
            }
            _ => {}
        }
    }
    bins.into_values().map(|(i, _)| i).collect()
}

/// Bounding box around the chord between `start` and `goal`, expanded
/// by `margin_frac × chord_length` on each side and clamped to the
/// grid. The Dijkstra search is restricted to this bbox to avoid
/// expanding the whole grid for every short candidate pair.
fn chord_bbox(
    grid: &Grid,
    start: (usize, usize),
    goal: (usize, usize),
    margin_frac: f32,
) -> ((usize, usize), (usize, usize)) {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let dr = goal.0 as f32 - start.0 as f32;
    let dc = goal.1 as f32 - start.1 as f32;
    let chord = (dr * dr + dc * dc).sqrt();
    // Floor the margin in cells so very short pairs still get some room
    // to detour around obstacles.
    let margin = (margin_frac * chord).max(40.0) as usize;
    let r_min = start.0.min(goal.0).saturating_sub(margin);
    let c_min = start.1.min(goal.1).saturating_sub(margin);
    let r_max = (start.0.max(goal.0) + margin).min(h.saturating_sub(1));
    let c_max = (start.1.max(goal.1) + margin).min(w.saturating_sub(1));
    ((r_min, c_min), (r_max, c_max))
}

/// True if the perpendicular distance from `hub` to the chord segment
/// (clamped to the segment) is below `proximity_cells`.
fn chord_passes_near_hub(
    start: (usize, usize),
    end: (usize, usize),
    hub: (usize, usize),
    proximity_cells: f32,
) -> bool {
    let (sr, sc) = (start.0 as f32, start.1 as f32);
    let (er, ec) = (end.0 as f32, end.1 as f32);
    let dr = er - sr;
    let dc = ec - sc;
    let len = (dr * dr + dc * dc).sqrt();
    if len < 1.0 {
        return false;
    }
    let ur = dr / len;
    let uc = dc / len;
    let qr = hub.0 as f32 - sr;
    let qc = hub.1 as f32 - sc;
    let proj = (qr * ur + qc * uc).clamp(0.0, len);
    let nr = sr + proj * ur;
    let nc = sc + proj * uc;
    let pdr = hub.0 as f32 - nr;
    let pdc = hub.1 as f32 - nc;
    (pdr * pdr + pdc * pdc).sqrt() < proximity_cells
}

/// Returns a value in [0, 1] reflecting how parallel-and-overlapping
/// the candidate chord is with the most-similar already-committed
/// chord. 0 = no conflict; 1 = perfectly parallel and entirely within
/// `proximity_cells` of an existing chord segment.
///
/// Used in the prescore to suppress the "ladder" failure mode where two
/// near-parallel arterials get committed as separate lines because
/// each has high absolute new-coverage but they collectively serve the
/// same neighbourhoods twice.
fn chord_parallelism_penalty(
    cand_start: (usize, usize),
    cand_end: (usize, usize),
    existing: &[((usize, usize), (usize, usize))],
    proximity_cells: f32,
) -> f32 {
    if existing.is_empty() {
        return 0.0;
    }
    let (cs_r, cs_c) = (cand_start.0 as f32, cand_start.1 as f32);
    let (ce_r, ce_c) = (cand_end.0 as f32, cand_end.1 as f32);
    let cdr = ce_r - cs_r;
    let cdc = ce_c - cs_c;
    let clen = (cdr * cdr + cdc * cdc).sqrt();
    if clen < 1.0 {
        return 0.0;
    }
    let cur = cdr / clen;
    let cuc = cdc / clen;

    const SAMPLES: usize = 10;
    let mut worst = 0.0_f32;
    for &(es, ee) in existing {
        let (es_r, es_c) = (es.0 as f32, es.1 as f32);
        let (ee_r, ee_c) = (ee.0 as f32, ee.1 as f32);
        let edr = ee_r - es_r;
        let edc = ee_c - es_c;
        let elen = (edr * edr + edc * edc).sqrt();
        if elen < 1.0 {
            continue;
        }
        let eur = edr / elen;
        let euc = edc / elen;
        // Below 0.6 ≈ chords differ by > 53° — not a "parallel" pair,
        // skip. Cross/diagonal radials should not penalise each other.
        let alignment = (cur * eur + cuc * euc).abs();
        if alignment < 0.6 {
            continue;
        }
        let mut close = 0_u32;
        for k in 0..=SAMPLES {
            let t = k as f32 / SAMPLES as f32;
            let pr = cs_r + t * cdr;
            let pc = cs_c + t * cdc;
            let qr = pr - es_r;
            let qc = pc - es_c;
            let proj = (qr * eur + qc * euc).clamp(0.0, elen);
            let nr = es_r + proj * eur;
            let nc = es_c + proj * euc;
            let dr = pr - nr;
            let dc = pc - nc;
            if (dr * dr + dc * dc).sqrt() < proximity_cells {
                close += 1;
            }
        }
        let overlap = close as f32 / (SAMPLES + 1) as f32;
        let pen = alignment * overlap;
        if pen > worst {
            worst = pen;
        }
    }
    worst
}

/// Multiplier (≥ 1.0) for the chord prescore based on how peripheral
/// the endpoints are. Both endpoints inside `urban_r` → 1.0; both at
/// `cap × urban_r` (deep suburb) → `cap`. Lifts CBD-to-suburb and
/// suburb-to-suburb chords past pure central candidates after the
/// in-city radials are committed.
fn endpoint_periphery_factor(
    a: (usize, usize),
    b: (usize, usize),
    hub: (usize, usize),
    urban_r: f32,
    cap: f32,
) -> f32 {
    if urban_r <= 1.0 {
        return 1.0;
    }
    let f = |p: (usize, usize)| -> f32 {
        let dr = p.0 as f32 - hub.0 as f32;
        let dc = p.1 as f32 - hub.1 as f32;
        let d = (dr * dr + dc * dc).sqrt();
        (d / urban_r).max(1.0).min(cap)
    };
    (f(a) + f(b)) * 0.5
}

/// Two-leg routing through the hub, with chord-corridor masking on
/// each leg and the same hub-radius self-penalty exemption that
/// `via_centre` uses (so both legs may share the central trunk before
/// fanning out). Each leg is bbox-clipped independently for
/// performance on large grids.
///
/// Uses half the caller's `margin_frac` per leg — a 30% per-leg margin
/// would let each leg detour 30% × leg_chord, so the via-hub path
/// could end up 1.3× the through-hub chord and overshoot
/// `max_line_length_m`. Half the margin keeps via-hub paths within
/// ~15% overhead, which fits comfortably inside the length cap.
fn solve_via_hub_in_bbox(
    grid: &Grid,
    a: (usize, usize),
    b: (usize, usize),
    hub: (usize, usize),
    demand_w: DemandWeight,
    cross_mask: &[f32],
    margin_frac: f32,
) -> Result<Vec<(usize, usize)>, SolverError> {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let leg_margin = (margin_frac * 0.5).max(0.10);

    let bbox1 = chord_bbox(grid, a, hub, leg_margin);
    let mut mask1 = cross_mask.to_vec();
    stamp_corridor(&mut mask1, a, hub, h, w);
    let path1 = solve_path_in_bbox(grid, a, hub, demand_w, Some(&mask1), Some(bbox1))?;

    let bbox2 = chord_bbox(grid, hub, b, leg_margin);
    let mut mask2 = cross_mask.to_vec();
    let body: Vec<(usize, usize)> = path1
        .iter()
        .copied()
        .take(path1.len().saturating_sub(1))
        .collect();
    stamp_penalty_excluding_hub(&mut mask2, &body, h, w, SELF_PENALTY, hub, HUB_RADIUS_CELLS);
    stamp_corridor(&mut mask2, hub, b, h, w);
    let path2 = solve_path_in_bbox(grid, hub, b, demand_w, Some(&mask2), Some(bbox2))?;

    let mut path = path1;
    if path.last() == path2.first() {
        path.extend(path2.into_iter().skip(1));
    } else {
        path.extend(path2);
    }
    Ok(path)
}

fn cell_path_length_m(cells: &[(usize, usize)], cell_m: f64) -> f64 {
    let mut total = 0.0_f64;
    for pair in cells.windows(2) {
        let dr = (pair[1].0 as f64 - pair[0].0 as f64).abs();
        let dc = (pair[1].1 as f64 - pair[0].1 as f64).abs();
        let step = if dr > 0.5 && dc > 0.5 {
            std::f64::consts::SQRT_2
        } else {
            1.0
        };
        total += step * cell_m;
    }
    total
}

pub(crate) fn maximum_axis_backtrack_m(cells: &[(usize, usize)], cell_m: f64) -> f64 {
    let (Some(&(start_row, start_col)), Some(&(end_row, end_col))) = (cells.first(), cells.last())
    else {
        return 0.0;
    };
    let dx = end_col as f64 - start_col as f64;
    let dy = end_row as f64 - start_row as f64;
    let axis_length = dx.hypot(dy);
    if axis_length * cell_m < 2_000.0 {
        return 0.0;
    }
    let ux = dx / axis_length;
    let uy = dy / axis_length;
    let mut furthest_progress = 0.0_f64;
    let mut maximum_excursion = 0.0_f64;
    for &(row, col) in cells {
        let projection =
            ((col as f64 - start_col as f64) * ux + (row as f64 - start_row as f64) * uy) * cell_m;
        furthest_progress = furthest_progress.max(projection);
        maximum_excursion = maximum_excursion.max(furthest_progress - projection);
    }
    maximum_excursion
}

/// Trim low-demand cells off both ends of a routed cell sequence.
///
/// Walks inward from each endpoint while local demand is below
/// `TAIL_TRIM_DEMAND_THR`, capped at `TAIL_TRIM_MAX_FRAC` of the
/// original length per side. Returns the trimmed sub-slice indices
/// (start_inclusive, end_inclusive). Ring lines (closed loops) are
/// not trimmed — pass `is_ring=true` to skip.
fn trim_low_demand_tails(
    grid: &Grid,
    cells: &[(usize, usize)],
    is_ring: bool,
) -> Vec<(usize, usize)> {
    if is_ring || cells.len() < 4 {
        return cells.to_vec();
    }
    let max_trim = ((cells.len() as f32) * TAIL_TRIM_MAX_FRAC) as usize;
    let mut start = 0_usize;
    while start < max_trim {
        let (r, c) = cells[start];
        if grid.demand_at(r, c) >= TAIL_TRIM_DEMAND_THR {
            break;
        }
        start += 1;
    }
    let mut end = cells.len().saturating_sub(1);
    let end_floor = cells.len().saturating_sub(1).saturating_sub(max_trim);
    while end > end_floor {
        let (r, c) = cells[end];
        if grid.demand_at(r, c) >= TAIL_TRIM_DEMAND_THR {
            break;
        }
        end -= 1;
    }
    if start >= end {
        return cells.to_vec();
    }
    cells[start..=end].to_vec()
}

/// Stamp a per-cell penalty proportional to perpendicular distance
/// outside the chord-corridor between `start` and `end`. Cells inside
/// the corridor (perp ≤ half-width) are untouched; cells outside add
/// `CORRIDOR_PENALTY_PER_CELL × excess_cells` to the existing mask
/// (max-merged so it composes with other masks).
fn stamp_corridor(
    mask: &mut [f32],
    start: (usize, usize),
    end: (usize, usize),
    h: usize,
    w: usize,
) {
    let (sr, sc) = (start.0 as f32, start.1 as f32);
    let (er, ec) = (end.0 as f32, end.1 as f32);
    let dr = er - sr;
    let dc = ec - sc;
    let chord_len = (dr * dr + dc * dc).sqrt();
    if chord_len < 1.0 {
        return;
    }
    let ur = dr / chord_len;
    let uc = dc / chord_len;
    // Perpendicular unit vector.
    let nr = -uc;
    let nc = ur;
    let half_width = (CORRIDOR_HALF_WIDTH_FRAC * chord_len).min(CORRIDOR_HALF_WIDTH_CAP_CELLS);

    // Bounding box: chord ± (half_width + small margin) along the perp.
    // Sweeping the whole grid is fine for h*w up to ~1.5e6 (300 m grid
    // city), so don't bother with a tight bbox.
    for r in 0..h {
        for c in 0..w {
            let pr = r as f32 - sr;
            let pc = c as f32 - sc;
            // Project onto chord direction.
            let t = pr * ur + pc * uc;
            // Only penalise cells whose projection falls within the
            // chord segment (with a generous overhang of half_width)
            // so endpoints don't get squeezed.
            if t < -half_width || t > chord_len + half_width {
                continue;
            }
            let perp = (pr * nr + pc * nc).abs();
            let excess = perp - half_width;
            if excess > 0.0 {
                let extra = CORRIDOR_PENALTY_PER_CELL * excess;
                let idx = r * w + c;
                if extra > mask[idx] {
                    mask[idx] = extra;
                }
            }
        }
    }
}

/// Add `weight` to every cell within `PENALTY_RADIUS_CELLS` of any cell
/// in `cells` (max-merged so repeat passes don't compound infinitely).
fn stamp_penalty(mask: &mut [f32], cells: &[(usize, usize)], h: usize, w: usize, weight: f32) {
    let radius = PENALTY_RADIUS_CELLS;
    let r2 = (radius * radius) as isize;
    for &(r, c) in cells {
        let r_min = r.saturating_sub(radius);
        let r_max = (r + radius).min(h.saturating_sub(1));
        let c_min = c.saturating_sub(radius);
        let c_max = (c + radius).min(w.saturating_sub(1));
        for rr in r_min..=r_max {
            for cc in c_min..=c_max {
                let dr = rr as isize - r as isize;
                let dc = cc as isize - c as isize;
                if dr * dr + dc * dc <= r2 {
                    let idx = rr * w + cc;
                    let cur = mask[idx];
                    if weight > cur {
                        mask[idx] = weight;
                    }
                }
            }
        }
    }
}

/// Variant of [`stamp_penalty`] with a caller-chosen radius. Used by
/// the greedy synthesizer with a wider radius (~25 cells / 500 m) so
/// the second line is forced onto a parallel-block corridor instead of
/// just a parallel-block trace 160 m off.
fn stamp_penalty_radius(
    mask: &mut [f32],
    cells: &[(usize, usize)],
    h: usize,
    w: usize,
    weight: f32,
    radius: usize,
) {
    let r2 = (radius * radius) as isize;
    for &(r, c) in cells {
        let r_min = r.saturating_sub(radius);
        let r_max = (r + radius).min(h.saturating_sub(1));
        let c_min = c.saturating_sub(radius);
        let c_max = (c + radius).min(w.saturating_sub(1));
        for rr in r_min..=r_max {
            for cc in c_min..=c_max {
                let dr = rr as isize - r as isize;
                let dc = cc as isize - c as isize;
                if dr * dr + dc * dc <= r2 {
                    let idx = rr * w + cc;
                    if weight > mask[idx] {
                        mask[idx] = weight;
                    }
                }
            }
        }
    }
}

/// Same as `stamp_penalty` but skips cells inside the hub circle.
///
/// Used when stamping radial corridors so that *outside* the central
/// hub other lines are kept off the corridor (one line per arterial),
/// but *inside* the hub the central trunk is shared — every radial
/// converges on the same cells in the CBD, and the forced hub station
/// merges them into a single interchange complex.
fn stamp_penalty_excluding_hub(
    mask: &mut [f32],
    cells: &[(usize, usize)],
    h: usize,
    w: usize,
    weight: f32,
    hub: (usize, usize),
    hub_radius_cells: usize,
) {
    let hr2 = (hub_radius_cells * hub_radius_cells) as isize;
    let filtered: Vec<(usize, usize)> = cells
        .iter()
        .copied()
        .filter(|&(r, c)| {
            let dr = r as isize - hub.0 as isize;
            let dc = c as isize - hub.1 as isize;
            dr * dr + dc * dc > hr2
        })
        .collect();
    stamp_penalty(mask, &filtered, h, w, weight);
}

// ---- Helpers ---------------------------------------------------------

#[derive(Clone, Copy)]
enum RingBand {
    Inner,
    Outer,
}

/// Demand-weighted centroid of the grid.
///
/// Off-bbox-centre cities are common (the bbox auto-expands beyond the
/// urban footprint, or the city sits asymmetrically inside a hand-set
/// bbox). The geometric centre then lands in farmland and routing every
/// radial through it forces an L-shape with one arm cutting across empty
/// fields. Demand-weighted centroid puts the pivot in the actual
/// populated core, giving radials a clean axis through downtown.
fn grid_centre(grid: &Grid) -> (usize, usize) {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let mut sum_r = 0.0_f64;
    let mut sum_c = 0.0_f64;
    let mut sum_w = 0.0_f64;
    for r in 0..h {
        for c in 0..w {
            let d = grid.demand_at(r, c) as f64;
            // Threshold of 0.1 keeps low-demand farmland from dragging
            // the centroid off the urban core. Anything below that is
            // dominated by the centre-bias falloff in build_demand_surface
            // (i.e. every cell has *some* demand from the bias term).
            if d > 0.1 {
                sum_r += r as f64 * d;
                sum_c += c as f64 * d;
                sum_w += d;
            }
        }
    }
    if sum_w > 1.0 {
        ((sum_r / sum_w) as usize, (sum_c / sum_w) as usize)
    } else {
        (h / 2, w / 2)
    }
}

/// Effective urban radius from `centre`: smallest radius beyond which
/// the mean demand-bin drops below `URBAN_DEMAND_THR`. Caps ring lines
/// to the populated footprint so they don't loop through farmland on
/// auto-expanded bboxes (Baghdad's outer suburbs end well before the
/// bbox edge; without this the outer ring picks farmland anchors).
fn urban_radius(grid: &Grid, centre: (usize, usize)) -> f32 {
    const URBAN_DEMAND_THR: f32 = 0.18;
    const BINS: usize = 20;
    let h = grid.reference.height;
    let w = grid.reference.width;
    let max_d = dist_from((0, 0), centre)
        .max(dist_from((h, 0), centre))
        .max(dist_from((0, w), centre))
        .max(dist_from((h, w), centre));
    let bin_size = (max_d / BINS as f32).max(1.0);
    let mut sums = [0.0_f64; BINS];
    let mut counts = [0_u64; BINS];
    for r in 0..h {
        for c in 0..w {
            let d_from_c = dist_from((r, c), centre);
            let bin = ((d_from_c / bin_size) as usize).min(BINS - 1);
            sums[bin] += grid.demand_at(r, c) as f64;
            counts[bin] += 1;
        }
    }
    // Skip the first two inner bins — even the centre itself can briefly
    // dip below the threshold from a single non-anchor cell.
    for i in 2..BINS {
        let mean = if counts[i] > 0 {
            (sums[i] / counts[i] as f64) as f32
        } else {
            0.0
        };
        if mean < URBAN_DEMAND_THR {
            return (i as f32 + 0.5) * bin_size;
        }
    }
    max_d
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

/// Pick `count` radial endpoint pairs by angular sector — each pair is
/// one sector and its opposite, so radials are *spread* around the city
/// instead of all clustering on whichever side has the highest-scoring
/// anchors. Without sectoring, a city with one strong satellite cluster
/// (e.g. Baghdad with Abu Ghraib to the W) ends up with 3 of 4 radials
/// pointing at it and the rest of the city uncovered.
///
/// Distance scoring is archetype-aware:
/// * Small cities (count == 1): clamp `d/max_d` at 1.0 — there is no
///   meaningful satellite to reach, so a radial that runs to a desert
///   farm at 1.5× urban_radius is just dead kilometres.
/// * Bigger cities (count ≥ 2): take `sqrt(d/max_d)` so a satellite
///   town at 2× urban_radius (score √2 ≈ 1.41) beats an urban-edge
///   anchor (score 1.0) but the bonus is bounded — a single isolated
///   POI 4× out doesn't dominate the line choice.
///
/// Count high-weight POI anchors that fall within a buffered chord
/// between `a` and `b` (excluding the endpoints themselves), weighted by
/// each anchor's weight. Returns a score scaled to be comparable with
/// the chord-coverage cell count: a buffer of ~600 m around the chord
/// catching 4 hospital anchors (w=0.9) returns 4 × 0.9 × 200 = 720,
/// roughly equivalent to ~720 covered demand cells. This keeps the
/// algorithm honest about chords that "thread the needle" through
/// multiple top demand generators (university campuses, hospital
/// districts, the airport corridor) — it doesn't only count residential
/// cell-density.
fn anchor_density_along_chord(anchors: &[Anchor], a: usize, b: usize, urban_r: f32) -> f32 {
    // Buffer radius — match the typical station-walkshed (600 m at
    // 20 m cells = 30 cells). Anchors further than this from the
    // chord don't count.
    const BUFFER_CELLS: f32 = 30.0;
    // Weight-to-cell-count multiplier. 200 means a w=1.0 anchor on the
    // chord is worth ~200 covered demand cells — comparable to a large
    // anchor blob from the demand surface.
    const WEIGHT_PER_HIT: f32 = 200.0;

    let (ar, ac) = (anchors[a].row as f32, anchors[a].col as f32);
    let (br, bc) = (anchors[b].row as f32, anchors[b].col as f32);
    let chord_dr = br - ar;
    let chord_dc = bc - ac;
    let chord_len_sq = chord_dr * chord_dr + chord_dc * chord_dc;
    if chord_len_sq < 1.0 {
        return 0.0;
    }
    let chord_len = chord_len_sq.sqrt();

    // Skip if the chord is shorter than a typical station walkshed —
    // there isn't really a "buffer" worth scoring then.
    if chord_len < BUFFER_CELLS {
        return 0.0;
    }
    // Skip degenerate chords longer than the urban diameter.
    if chord_len > 4.0 * urban_r {
        return 0.0;
    }

    let mut score = 0.0_f32;
    for (i, anchor) in anchors.iter().enumerate() {
        if i == a || i == b {
            continue;
        }
        if anchor.weight < 0.5 {
            continue; // skip low-weight residential / minor anchors
        }
        let pr = anchor.row as f32 - ar;
        let pc = anchor.col as f32 - ac;
        // Project onto chord direction.
        let proj = (pr * chord_dr + pc * chord_dc) / chord_len_sq;
        // Skip anchors outside [0, 1] along the chord (i.e., past the
        // endpoints).
        if !(0.05..=0.95).contains(&proj) {
            continue;
        }
        // Perpendicular distance to chord line.
        let nr = ar + proj * chord_dr;
        let nc = ac + proj * chord_dc;
        let dr = anchor.row as f32 - nr;
        let dc = anchor.col as f32 - nc;
        let perp_d = (dr * dr + dc * dc).sqrt();
        if perp_d > BUFFER_CELLS {
            continue;
        }
        // Linear falloff from 1.0 at chord centre to 0 at buffer edge.
        let falloff = 1.0 - perp_d / BUFFER_CELLS;
        score += anchor.weight * falloff * WEIGHT_PER_HIT;
    }
    score
}

fn pick_radial_endpoints(
    grid: &Grid,
    anchors: &[Anchor],
    ordered: &[usize],
    count: usize,
) -> Result<(Vec<(usize, usize)>, HashSet<usize>), TopologyError> {
    let centre = grid_centre(grid);
    let centre_r = centre.0 as f32;
    let centre_c = centre.1 as f32;
    let max_d = urban_radius(grid, centre);

    // Peripheral pool: anchors in at least the outer half of the urban
    // footprint. We cast a wider net here than the old picker (was 0.70)
    // because angular sectoring prevents the "all on one side" failure
    // we were guarding against by tightening to the outer 30%.
    //
    // For SingleRadial (count == 1, small cities) we additionally cap the
    // pool *at* `max_d` — there's no satellite to reach in a small city,
    // so a peripheral anchor at 1.3× urban_radius is a desert farm and
    // running a single line out to it just produces dead km. Bigger
    // archetypes (count >= 2) keep the full pool because satellite-town
    // reach is a core requirement.
    let peripheral_thr = 0.50 * max_d;
    let peripheral_max = if count <= 1 { max_d } else { f32::INFINITY };
    let peripheral: Vec<usize> = ordered
        .iter()
        .copied()
        .filter(|&i| {
            let d = dist_from(anchors[i].cell(), centre);
            d > peripheral_thr && d <= peripheral_max
        })
        .collect();
    if peripheral.len() < 2 * count {
        return pick_radial_from_all(anchors, ordered, count);
    }

    let dist_score = |i: usize| -> f32 {
        let d = dist_from(anchors[i].cell(), centre);
        let ratio = if count <= 1 {
            (d / max_d).min(1.0)
        } else {
            (d / max_d).sqrt()
        };
        // Weight contribution bumped 0.15 → 0.6 (2026-04-26 operator
        // review). At 0.15 a `place=neighbourhood` (w=0.6) at 0.95×R
        // outranked an `amenity=university` / `amenity=hospital`
        // (w=0.9–1.0) at 0.85×R purely on distance — Samawah's
        // northern hospital + university cluster lost to a marginally-
        // more-peripheral suburb. At 0.6 a top-weight POI outranks a
        // suburb by ~0.24, enough to offset a 5–10 % distance gap so
        // sector picks favour real demand peaks over suburb edges.
        ratio + 0.6 * anchors[i].weight
    };

    // Divide [-π, π) into 2*count sectors. Each sector keeps the
    // highest-scoring anchor that falls inside it. Pair sector i with
    // sector (i + count), i.e. the diametrically opposite sector.
    let n_sectors = 2 * count;
    let two_pi = 2.0 * std::f32::consts::PI;
    let mut by_sector: Vec<Option<(usize, f32)>> = vec![None; n_sectors];
    for &i in &peripheral {
        let (ar, ac) = anchors[i].cell();
        let angle = (ar as f32 - centre_r).atan2(ac as f32 - centre_c);
        let norm = (angle + std::f32::consts::PI) / two_pi;
        let sec = ((norm * n_sectors as f32).floor() as usize).min(n_sectors - 1);
        let s = dist_score(i);
        match by_sector[sec] {
            None => by_sector[sec] = Some((i, s)),
            Some((_, prev)) if s > prev => by_sector[sec] = Some((i, s)),
            _ => {}
        }
    }

    let mut endpoints: Vec<(usize, usize)> = Vec::new();
    let mut used: HashSet<usize> = HashSet::new();
    for i in 0..count {
        let opp = i + count;
        if let (Some((a, _)), Some((b, _))) = (by_sector[i], by_sector[opp]) {
            if used.contains(&a) || used.contains(&b) || a == b {
                continue;
            }
            used.insert(a);
            used.insert(b);
            endpoints.push((a, b));
        }
    }

    // Sectors may be empty in lopsided cities (e.g. coastal cities with
    // no anchors south). Fill the deficit by greedy farthest-pair, the
    // old picker's behaviour, but using the new dist_score.
    if endpoints.len() < count {
        let mut by_far: Vec<usize> = peripheral
            .iter()
            .copied()
            .filter(|i| !used.contains(i))
            .collect();
        by_far.sort_by(|&a, &b| {
            dist_score(b)
                .partial_cmp(&dist_score(a))
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        for _ in endpoints.len()..count {
            let Some(&a) = by_far.iter().find(|&&i| !used.contains(&i)) else {
                break;
            };
            used.insert(a);
            let (arow, acol) = anchors[a].cell();
            let a_angle = (arow as f32 - centre_r).atan2(acol as f32 - centre_c);
            let mut best: Option<usize> = None;
            let mut best_score = f32::NEG_INFINITY;
            for &b in &peripheral {
                if used.contains(&b) {
                    continue;
                }
                let (br, bc) = anchors[b].cell();
                let b_angle = (br as f32 - centre_r).atan2(bc as f32 - centre_c);
                let mut da = (b_angle - a_angle).abs();
                if da > std::f32::consts::PI {
                    da = 2.0 * std::f32::consts::PI - da;
                }
                let score = da + 1.5 * dist_score(b);
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
    }

    if endpoints.is_empty() {
        return Err(TopologyError::TooFewAnchors {
            min: 2 * count,
            got: 0,
        });
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
///
/// The second leg is solved with a stamped penalty mask covering the
/// neighbourhood of the first leg, so the line cannot fold back on
/// itself across the centre — the failure mode that produced the
/// hairpin "lines that go back on themselves" the user flagged.
fn via_centre(
    grid: &Grid,
    anchors: &[Anchor],
    a: usize,
    b: usize,
    centre: (usize, usize),
    demand_w: DemandWeight,
    cross_mask: &[f32],
) -> Result<Vec<(usize, usize)>, SolverError> {
    // Pick a buildable centre — if the geometric centre lands on a
    // building, walk outward until we find an open cell.
    let centre = nudge_to_buildable(grid, centre).unwrap_or(centre);
    let h = grid.reference.height;
    let w = grid.reference.width;

    // First leg corridor: anchor-a → centre. The corridor penalty is what
    // prevents the demand reward from yanking the leg off-axis (the
    // tortuosity-1.9× backfold seen in early Samawah runs).
    let mut first_mask = cross_mask.to_vec();
    stamp_corridor(&mut first_mask, anchors[a].cell(), centre, h, w);
    let mut path =
        solve_path_with_penalty(grid, anchors[a].cell(), centre, demand_w, Some(&first_mask))?;

    // Stamp the just-routed cells (excluding the centre itself, so the
    // second leg can still depart from it) onto a fresh mask layered
    // over the cross-line baseline. Cells *inside* the hub radius are
    // exempt — both legs of a radial are allowed to share the central
    // trunk so the line presents a clean axis through downtown rather
    // than two narrowly-parallel corridors meeting awkwardly off-centre.
    let mut tail_mask = cross_mask.to_vec();
    let body: Vec<(usize, usize)> = path
        .iter()
        .copied()
        .take(path.len().saturating_sub(1))
        .collect();
    stamp_penalty_excluding_hub(
        &mut tail_mask,
        &body,
        h,
        w,
        SELF_PENALTY,
        centre,
        HUB_RADIUS_CELLS,
    );
    stamp_corridor(&mut tail_mask, centre, anchors[b].cell(), h, w);

    let tail =
        solve_path_with_penalty(grid, centre, anchors[b].cell(), demand_w, Some(&tail_mask))?;
    if path.last() == tail.first() {
        path.extend(tail.into_iter().skip(1));
    } else {
        path.extend(tail);
    }
    Ok(path)
}

/// Demand-weighted hub cell, nudged to a buildable cell. Stable for a
/// given grid — the orchestrator calls this to figure out where to
/// force a single CBD interchange so radials can be merged into one
/// downtown station rather than three closely-spaced ones.
#[must_use]
pub fn hub_cell(grid: &Grid) -> (usize, usize) {
    let centre = grid_centre(grid);
    nudge_to_buildable(grid, centre).unwrap_or(centre)
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
                if nr < h && nc < w && grid.is_buildable(nr, nc) && grid.cost_at(nr, nc).is_finite()
                {
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
    // Cap ring radius by the urban footprint, not the bbox. Without this,
    // an auto-expanded bbox places the outer ring 30 km from a city's
    // centroid where there is only farmland (Baghdad's earlier outer
    // ring ran through fields east of Sadr City).
    let max_d = urban_radius(grid, centre);

    // Rings sit *inside* the urban radius so radial endpoints (picked
    // from the outer 30 % of the urban radius) extend past them. This is
    // what makes the ring a useful bypass: passengers travelling between
    // outer-suburb radial termini can transfer to the ring without ever
    // entering the CBD. A perimeter ring with nothing beyond it is just
    // an awkward circle.
    // Bumped 2026-04-26 — the previous (0.45–0.65) outer band placed
    // Baghdad's circumferential ring at ~12 km from centre, but the
    // city's high-density suburbs (Sadr City to NE, Kadhimiya to NW,
    // Doura to S) reach 14–18 km. The ring missed those northern
    // districts entirely. Widening to (0.55–0.85) lets the ring
    // anchor on suburbs in densely-populated outer rings while
    // still falling back to the full anchor set for sparse cities.
    let (radius_lo_init, radius_hi_init) = match band {
        RingBand::Inner => (0.25 * max_d, 0.50 * max_d),
        RingBand::Outer => (0.55 * max_d, 0.85 * max_d),
    };

    // Try the requested band first; if the small/sparse city does not
    // have enough peripheral anchors to fill it, fall back to the full
    // unused-anchor set. Without the fallback, anchor-poor cities like
    // Samawah hit "need at least 3 anchors" from `pick_ring_anchors_by_radius`
    // when the population threshold lands them in RadialPlusRing.
    let mut buckets: Vec<Option<(usize, f32)>> = vec![None; n];
    let attempts: [(f32, f32); 2] = [(radius_lo_init, radius_hi_init), (0.0, f32::INFINITY)];
    for &(radius_lo, radius_hi) in &attempts {
        buckets = vec![None; n];
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
            let norm = (angle + std::f32::consts::PI) / (2.0 * std::f32::consts::PI);
            let bucket = ((norm * n as f32).floor() as usize).min(n - 1);
            let band_centre = if radius_hi.is_finite() {
                (radius_lo + radius_hi) / 2.0
            } else {
                0.5 * max_d
            };
            let score = anchors[i].weight - 0.0001 * ((d - band_centre).abs());
            match buckets[bucket] {
                None => buckets[bucket] = Some((i, score)),
                Some((_, s)) if score > s => buckets[bucket] = Some((i, score)),
                _ => {}
            }
        }
        let filled = buckets.iter().filter(|b| b.is_some()).count();
        if filled >= 3 {
            break;
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
/// the loop. Each segment is solved with a penalty mask that covers all
/// previous segments of *this* ring (anti-self-loop) plus any cells
/// from earlier emitted lines (anti-overlap).
fn route_ring(
    grid: &Grid,
    anchors: &[Anchor],
    ring_ids: &[usize],
    demand_w: DemandWeight,
    cross_mask: &[f32],
) -> Result<Vec<(usize, usize)>, SolverError> {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let mut cells: Vec<(usize, usize)> = Vec::new();
    let mut self_mask: Vec<f32> = cross_mask.to_vec();
    for pair in ring_ids.windows(2) {
        // Per-segment corridor — keeps each ring chord straight rather
        // than bowing toward off-axis demand clusters. Built on top of
        // the accumulating self/cross mask.
        let mut seg_mask = self_mask.clone();
        let s = anchors[pair[0]].cell();
        let e = anchors[pair[1]].cell();
        stamp_corridor(&mut seg_mask, s, e, h, w);
        let seg = solve_path_with_penalty(grid, s, e, demand_w, Some(&seg_mask))?;
        // Stamp this segment so the next one cannot drift back through it.
        // Skip the last cell so the next segment is allowed to start from it.
        let body: Vec<(usize, usize)> = seg
            .iter()
            .copied()
            .take(seg.len().saturating_sub(1))
            .collect();
        stamp_penalty(&mut self_mask, &body, h, w, SELF_PENALTY);
        append_segment(&mut cells, seg);
    }
    // Close the ring.
    let s = anchors[*ring_ids.last().unwrap()].cell();
    let e = anchors[ring_ids[0]].cell();
    let mut seg_mask = self_mask.clone();
    stamp_corridor(&mut seg_mask, s, e, h, w);
    let seg = solve_path_with_penalty(grid, s, e, demand_w, Some(&seg_mask))?;
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

/// Like [`route_ring`] but bbox-clips each segment's Dijkstra to the
/// chord-aligned rectangle plus a margin. On a Baghdad-sized grid
/// (2668 × 2976) an 8-segment unbounded ring solve takes 30+ s; the
/// bbox-clipped version runs each segment over ~5 % of the cells and
/// finishes in seconds.
fn route_ring_in_bbox(
    grid: &Grid,
    anchors: &[Anchor],
    ring_ids: &[usize],
    demand_w: DemandWeight,
    cross_mask: &[f32],
    bbox_margin_frac: f32,
) -> Result<Vec<(usize, usize)>, SolverError> {
    let h = grid.reference.height;
    let w = grid.reference.width;
    let mut cells: Vec<(usize, usize)> = Vec::new();
    let mut self_mask: Vec<f32> = cross_mask.to_vec();

    let solve_seg = |seg_mask: &[f32], s, e| {
        let bbox = chord_bbox(grid, s, e, bbox_margin_frac);
        solve_path_in_bbox(grid, s, e, demand_w, Some(seg_mask), Some(bbox))
    };

    for pair in ring_ids.windows(2) {
        let mut seg_mask = self_mask.clone();
        let s = anchors[pair[0]].cell();
        let e = anchors[pair[1]].cell();
        stamp_corridor(&mut seg_mask, s, e, h, w);
        let seg = solve_seg(&seg_mask, s, e)?;
        let body: Vec<(usize, usize)> = seg
            .iter()
            .copied()
            .take(seg.len().saturating_sub(1))
            .collect();
        stamp_penalty(&mut self_mask, &body, h, w, SELF_PENALTY);
        append_segment(&mut cells, seg);
    }
    // Close the loop.
    let s = anchors[*ring_ids.last().unwrap()].cell();
    let e = anchors[ring_ids[0]].cell();
    let mut seg_mask = self_mask.clone();
    stamp_corridor(&mut seg_mask, s, e, h, w);
    let seg = solve_seg(&seg_mask, s, e)?;
    append_segment(&mut cells, seg);
    Ok(cells)
}

#[cfg(test)]
mod tests {
    use super::maximum_axis_backtrack_m;

    #[test]
    fn axis_backtrack_ignores_small_street_wiggles() {
        let cells = vec![(0, 0), (0, 100), (0, 80), (0, 200), (0, 180), (0, 400)];
        assert!(maximum_axis_backtrack_m(&cells, 20.0) < 750.0);
    }

    #[test]
    fn axis_backtrack_rejects_a_material_hairpin() {
        let cells = vec![(0, 0), (0, 150), (0, 70), (0, 300)];
        assert!(maximum_axis_backtrack_m(&cells, 20.0) >= 750.0);
    }
}
