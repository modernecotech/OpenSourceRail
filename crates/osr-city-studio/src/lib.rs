//! Git-backed city design and service-planning model used by OSR City Studio.

mod jobs;
pub mod model;
mod project;
pub mod server;

pub use project::CityProject;
