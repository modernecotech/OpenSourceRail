//! Library crate for the OpenSourceRail simulator. Exports the modules
//! used by the `osr-sim` and `osr-vis` binaries.

pub mod backend_systems;
pub mod balise_systems;
pub mod consensus_log;
pub mod embedded;
pub mod energy;
pub mod fare_systems;
pub mod fault;
pub mod habd_systems;
pub mod infrastructure_systems;
pub mod ma_check;
pub mod onboard;
pub mod physics;
pub mod report;
pub mod scenario_file;
pub mod schedule;
pub mod sim;
pub mod time_sync;
pub mod timeline;
pub mod train;
pub mod vehicle_systems;
pub mod vis;
