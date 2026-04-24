//! Alignment — the civil-contractor-stakeable geometry artefact.
//!
//! `osr-routing` produces a least-cost polyline through cell-space.
//! That's not stakeable by a surveyor: a real civil contractor needs
//! **tangents, circular arcs, and (optionally) transition spirals**
//! with **chainage** at every critical point, a **vertical profile**
//! with gradients + vertical curves, and a **cant (superelevation)
//! schedule**. This crate produces all three.
//!
//! # Scope for v0.1
//!
//! - **Horizontal:** tangent / circular-arc / transition-spiral elements.
//! - **Vertical:** grade segments + parabolic vertical curves.
//! - **Cant:** per-element superelevation derived from design speed +
//!   radius, ramped through transition spirals.
//! - **Chainage:** running mileage from the start of the alignment.
//!
//! # What we don't do
//!
//! - Full alignment *design* (choosing where the PIs land) — that's
//!   `osr-routing`'s job.
//! - Survey-grade optimisation (Trimble Quantm) — we fit to what the
//!   routing already chose.
//! - ETCS / mainline / multi-user alignment — urban-rail only.
//!
//! # Export formats
//!
//! The crate emits a machine-readable JSON document plus a LandXML
//! file that round-trips into OpenRail, Civil 3D, Trimble Business
//! Center — the `osr-alignment-export` CLI binary in this crate.
//!
//! # Design speed → radius → cant
//!
//! For a design speed `V` (km/h), minimum curve radius `R` (m), and
//! maximum cant `C_max` (mm) per [RFC 0009](../../docs/rfcs/0009-track-design-standard.md):
//!
//! - Applied cant: `C = min(C_max, 11.8 · V² / R)` (mm, for standard gauge).
//! - Cant deficiency: `C_d = 11.8 · V² / R − C` (mm), bound to `C_d_max`.
//! - Spiral length: `L_s ≥ max(C / C_rate, C_d / C_d_rate) · V / 3.6` (m),
//!   with `C_rate`, `C_d_rate` per RFC 0009.
//!
//! Standard-gauge 1 435 mm, so the 11.8 constant is the standard
//! `V²/(127·R)` formula converted to mm. For the urban-rail design
//! speeds we target (≤ 100 km/h) + the minimum radii at each geometry
//! preset, cant rarely exceeds 120 mm — well inside the 160 mm ceiling.

#![forbid(unsafe_code)]

pub mod alignment;
pub mod cant;
pub mod chainage;
pub mod earthworks;
pub mod landxml;
pub mod railml;
pub mod trackside;

pub use alignment::{
    Alignment, AlignmentError, HorizontalElement, TurnDirection, VerticalElement,
};
pub use cant::{cant_design, CantSchedule};
pub use chainage::{station_at, StationedPoint};
pub use earthworks::{
    compute_quantities, format_summary, CivilSection, EarthworksQuantities,
    EarthworksSample, PermanentWayParams,
};
pub use trackside::{place_assets, Asset, AssetKind, PlacementRules};
