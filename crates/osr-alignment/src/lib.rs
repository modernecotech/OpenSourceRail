//! Generic horizontal/vertical alignment and chainage geometry.
//!
//! Tangents, arcs, transition spirals, grades and vertical curves can be
//! exchanged through LandXML/railML. These geometry helpers do not select
//! guideway banking, structural members, sensor hardware or operating limits.
//! Inputs require survey, clearance, comfort and vehicle-dynamics review.
//! CLI polyline fitting currently preserves straight segments only; it does
//! not resolve corner transitions or produce an approved setting-out design.
#![forbid(unsafe_code)]

pub mod alignment;
pub mod chainage;
pub mod landxml;
pub mod railml;

pub use alignment::{Alignment, AlignmentError, HorizontalElement, TurnDirection, VerticalElement};
pub use chainage::{station_at, StationedPoint};
