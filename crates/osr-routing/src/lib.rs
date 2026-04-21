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

pub use civil::{classify_segments, CivilClass, CivilSegment};
pub use raster::{Anchor, Grid, GridRef, RasterBundle};
pub use solver::{solve_path, DemandWeight, SolverError};
pub use station::{place_stations, Station};
pub use topology::{synthesize_lines, Line, LineShape, TopologyArchetype, TopologyError};
