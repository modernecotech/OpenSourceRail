//! OpenSourceRail — shared domain types.
//!
//! Types here mirror the protobuf schema in `proto/track_state.proto`, which
//! is the persistent wire format consumed by the consensus layer. The Rust
//! types are hand-written (not prost-generated) because the early simulator
//! does not touch the wire format. When `osr-consensus` comes online we will
//! either switch to generated types or maintain a mapping — either way, the
//! proto file remains the canonical schema.

pub mod geometry;
pub mod ids;
pub mod consist;
pub mod topology;

pub use consist::{BrakingCurve, ConsistDescriptor, TrainClass};
pub use geometry::{Direction, Position, TrackRef};
pub use ids::{EntityId, EntryId, RegionId, RouteId, SectionId, StationId, SwitchId, TrainId};
pub use topology::{Line, Network, Section, Station};
