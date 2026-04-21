//! OpenSourceRail wire types for the track-state log.
//!
//! These are hand-written Rust structs that mirror the canonical
//! protobuf schema in
//! [`osr-core/proto/track_state.proto`](../../../crates/osr-core/proto/track_state.proto).
//! The proto file is the normative reference; this crate is the
//! pragmatic Rust view of it used by `osr-consensus` and the
//! various agents that log events.
//!
//! Phase 2f infrastructure crate per
//! [RFC 0005 §4.9](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! No SIL tier — this is a data-model crate; encoding errors surface
//! as `DecodeError` rather than silent misinterpretation.
//!
//! # Encoding
//!
//! v1 uses `bincode` for its compact, deterministic output and
//! zero-glue encoding of Rust enums. A follow-up will bring in
//! `prost` when we need genuine cross-language wire compatibility.
//! The schema evolution rules in the `.proto` header (never reuse
//! a field number, etc.) still apply — breaking wire changes in
//! this crate require a matching schema bump.
//!
//! # Properties (proptest-verified)
//!
//! - **PR1 round-trip:** for every supported payload, `decode(encode(x)) == x`.
//! - **PR2 encoding determinism:** same input → same bytes.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Identifiers — mirror of the proto `*Id { fixed64 value = 1; }` messages.
// ---------------------------------------------------------------------------

macro_rules! id_type {
    ($name:ident, $ty:ty) => {
        #[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Default, Serialize, Deserialize)]
        pub struct $name(pub $ty);
    };
}

id_type!(TrainId, u64);
id_type!(SwitchId, u64);
id_type!(RouteId, u64);
id_type!(SectionId, u64);
id_type!(EntityId, u64);
id_type!(EntryId, u64);
id_type!(RegionId, u32);

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum Direction {
    #[default]
    Unspecified,
    Forward,
    Reverse,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub struct TrackRef {
    pub section: SectionId,
    pub offset_mm: i64,
    pub direction: Direction,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub struct Position {
    pub track_ref: TrackRef,
    pub uncertainty_mm: u32,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum PositionSource {
    #[default]
    Unspecified,
    Gnss,
    Imu,
    Odometry,
    Beacon,
    LegacyTrackCircuit,
    LegacyAxleCounter,
}

// ---------------------------------------------------------------------------
// Payload messages — a focused subset covering what consumers actually use
// today (position reports, switch control, route lifecycle, restrictions,
// heartbeats, and the log-format version). The remaining payloads from the
// .proto (train registration, maintenance overrides, etc.) will be added
// when their consumers materialise.
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct TrainPositionReport {
    pub train_id: TrainId,
    pub head_position: Position,
    pub tail_position: Position,
    pub speed_mps: f32,
    pub speed_uncertainty_mps: f32,
    pub heading: Direction,
    pub contributing_sources: Vec<PositionSource>,
    pub onboard_time_ns: u64,
    pub pack_state_of_charge: f32,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum SwitchPosition {
    #[default]
    Unspecified,
    Normal,
    Reverse,
    Transitioning,
    /// Fail-restrictive — consumers treat Unknown as unsafe.
    Unknown,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SwitchCommand {
    pub switch_id: SwitchId,
    pub requested_position: SwitchPosition,
    pub requested_by: EntityId,
    pub lock_until: Option<EntryId>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum Confidence {
    #[default]
    Unspecified,
    Locked,
    Observed,
    Transitioning,
    Unknown,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SwitchObservation {
    pub switch_id: SwitchId,
    pub observed_position: SwitchPosition,
    pub confidence: Confidence,
    pub observed_at_ns: u64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RouteRequest {
    pub route_id: RouteId,
    pub requested_by: EntityId,
    pub entry_point: TrackRef,
    pub exit_point: TrackRef,
    pub train_id: TrainId,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RouteGrant {
    pub route_id: RouteId,
    pub train_id: TrainId,
    pub locked_switches: Vec<SwitchId>,
    pub locked_sections: Vec<SectionId>,
    pub expires_at_ns: u64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum RestrictionReason {
    #[default]
    Unspecified,
    Permanent,
    Temporary,
    Emergency,
    Weather,
    InfrastructureFault,
}

#[derive(Copy, Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SpeedRestriction {
    pub section: SectionId,
    pub from_offset_mm: i64,
    pub to_offset_mm: i64,
    pub max_speed_mps: f32,
    pub reason: RestrictionReason,
    pub effective_from_ns: u64,
    pub effective_until_ns: u64,
    pub issued_by: EntityId,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum HealthStatus {
    #[default]
    Unspecified,
    Ok,
    Degraded,
    Failing,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Heartbeat {
    pub from_entity: EntityId,
    pub health: HealthStatus,
    pub monotonic_seq: u64,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct FormatVersion {
    pub current: u32,
    pub min_compatible: u32,
    pub schema_sha256_hex: String,
}

/// The payload `oneof` from the proto's `Entry` message, as a Rust
/// tagged enum. Declaration order matches the proto field numbers
/// (listed in comments) — do not rearrange without a schema bump.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum Payload {
    /// proto field 10
    TrainPositionReport(TrainPositionReport),
    /// proto field 11
    SwitchCommand(SwitchCommand),
    /// proto field 12
    SwitchObservation(SwitchObservation),
    /// proto field 13
    RouteRequest(RouteRequest),
    /// proto field 14
    RouteGrant(RouteGrant),
    /// proto field 15
    RouteRelease { route_id: RouteId, reason: String },
    /// proto field 16
    SpeedRestriction(SpeedRestriction),
    /// proto field 19
    Heartbeat(Heartbeat),
    /// proto field 21
    FormatVersion(FormatVersion),
}

/// The log entry envelope — the unit of replication in the consensus
/// log. Mirrors the proto `Entry` message.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Entry {
    pub entry_id: EntryId,
    pub term: u64,
    pub timestamp_ns: u64,
    /// ed25519 signature over (entry_id, term, timestamp_ns, payload).
    /// Empty in v1 until `osr-crypto`'s ed25519 surface lands.
    pub leader_signature: Vec<u8>,
    pub payload: Payload,
}

// ---------------------------------------------------------------------------
// Encoding
// ---------------------------------------------------------------------------

#[derive(Debug)]
pub enum DecodeError {
    Bincode(String),
}

impl core::fmt::Display for DecodeError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match self {
            DecodeError::Bincode(s) => write!(f, "bincode decode error: {s}"),
        }
    }
}

impl std::error::Error for DecodeError {}

/// Encode a value with bincode's default options — fixed-width integers,
/// little-endian, no varint compaction. Deterministic by construction.
pub fn encode<T: Serialize>(value: &T) -> Vec<u8> {
    bincode::serialize(value).expect("bincode serialize")
}

pub fn decode<T: for<'a> Deserialize<'a>>(bytes: &[u8]) -> Result<T, DecodeError> {
    bincode::deserialize(bytes).map_err(|e| DecodeError::Bincode(e.to_string()))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample_entry() -> Entry {
        Entry {
            entry_id: EntryId(42),
            term: 3,
            timestamp_ns: 1_700_000_000_000_000_000,
            leader_signature: vec![],
            payload: Payload::SwitchObservation(SwitchObservation {
                switch_id: SwitchId(7),
                observed_position: SwitchPosition::Normal,
                confidence: Confidence::Locked,
                observed_at_ns: 1_700_000_000_000_000_000,
            }),
        }
    }

    #[test]
    fn round_trip_switch_observation() {
        let e = sample_entry();
        let bytes = encode(&e);
        let back: Entry = decode(&bytes).unwrap();
        assert_eq!(e, back);
    }

    #[test]
    fn round_trip_train_position_report() {
        let e = Entry {
            entry_id: EntryId(1),
            term: 1,
            timestamp_ns: 100,
            leader_signature: vec![1, 2, 3],
            payload: Payload::TrainPositionReport(TrainPositionReport {
                train_id: TrainId(9),
                head_position: Position {
                    track_ref: TrackRef {
                        section: SectionId(1),
                        offset_mm: 12_000,
                        direction: Direction::Forward,
                    },
                    uncertainty_mm: 300,
                },
                tail_position: Position::default(),
                speed_mps: 12.5,
                speed_uncertainty_mps: 0.2,
                heading: Direction::Forward,
                contributing_sources: vec![PositionSource::Odometry, PositionSource::Imu],
                onboard_time_ns: 100,
                pack_state_of_charge: 0.75,
            }),
        };
        let bytes = encode(&e);
        let back: Entry = decode(&bytes).unwrap();
        assert_eq!(e, back);
    }

    #[test]
    fn encoding_is_deterministic() {
        let e = sample_entry();
        assert_eq!(encode(&e), encode(&e));
    }

    #[test]
    fn decode_rejects_garbage() {
        let bogus = [0xffu8; 2];
        let result: Result<Entry, _> = decode(&bogus);
        assert!(result.is_err());
    }
}
