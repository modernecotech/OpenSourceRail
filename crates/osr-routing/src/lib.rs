//! Least-cost-path route solver for OpenSourceRail design generation.
//!
//! Inputs are produced by `design-py/osr_geo/` — three aligned rasters
//! (cost, demand, buildability) plus an anchors list — all landing on
//! disk as raw byte arrays with a sidecar `grid.json` describing the
//! geo-reference.
//!
//! Outputs are geometric line polylines (in both grid-cell and lat/lon
//! form), station points with snapped coordinates, and a civil-class
//! assignment per segment.
//!
//! The solver is intentionally modest: Dijkstra on an 8-connected grid,
//! with demand used as a reward that reduces effective traversal cost.
//! A* with an admissible heuristic would be a future optimization —
//! current grids (170k cells) solve well under 100 ms in Rust.

pub mod civil;
pub mod raster;
pub mod solver;
pub mod station;
pub mod topology;

pub use civil::{
    classify_segments, elevated_curve_cost_multiplier, elevated_product_for_geometry, CivilClass,
    CivilSegment, ElevatedViaductProduct, ELEVATED_PREFERRED_RADIUS_M, MAX_FULL_SPAN_U_M,
};
pub use raster::{Anchor, Grid, GridRef, RasterBundle};
pub use solver::{
    solve_path, solve_path_in_bbox, solve_path_with_penalty, DemandWeight, SolverError,
};
pub use station::{
    connect_radial_termini_to_rings, consolidate_inline_station_clusters,
    consolidate_ring_wrap_station_clusters, ensure_endpoint_stations, fill_large_station_gaps,
    force_hub_stations, force_ring_radial_crossings, force_ring_radial_group_ids,
    force_ring_radial_terminal_interchanges, merge_interchanges, place_stations,
    station_layout_issues, Station,
};
pub use topology::{
    budget_for_population, greedy_synthesize_lines, hub_cell, synthesize_lines, GreedyBudget, Line,
    LineShape, TopologyArchetype, TopologyError, HUB_RADIUS_CELLS,
};
