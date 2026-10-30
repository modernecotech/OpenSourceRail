//! Git-backed city design and service-planning model used by OSR City Studio.

mod jobs;
pub mod model;
pub mod passenger;
mod project;
pub mod server;

pub use project::CityProject;
