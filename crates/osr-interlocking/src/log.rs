//! Entry schema — Rust mirror of `osr-core/proto/track_state.proto`.
//!
//! Integer-only in the safety path. Floats are only used for sensor-input
//! fields that are inherently fractional (speed_mps, speed_uncertainty_mps,
//! pack_state_of_charge); they do not participate in the MA-computation
//! path's authoritative arithmetic.

use osr_core::{
    ConsistDescriptor, EntityId, EntryId, RegionId, RouteId, SectionId, SwitchId,
    TrainId,
};
use osr_core::{Direction, Position, TrackRef};
use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Top-level envelope
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Entry {
    pub entry_id: EntryId,
    /// Raft term at which the entry was committed (RFC 0001 §6.4).
    pub term: u64,
    /// Leader's PTP-synced TAI clock, ns since epoch, at commit.
    pub timestamp_ns: u64,
    pub payload: EntryPayload,
}

/// Sum type over all entry variants. The discriminants here match the
/// protobuf `oneof` payload field numbers (10..21).
///
/// `Hash`/`Eq` are not derived because `TrainRegistration` contains a
/// `ConsistDescriptor` with `f32` fields (max_speed_mps, braking curve
/// points). Use `PartialEq` for structural comparison.
#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum EntryPayload {
    TrainPositionReport(TrainPositionReport),
    SwitchCommand(SwitchCommand),
    SwitchObservation(SwitchObservation),
    RouteRequest(RouteRequest),
    RouteGrant(RouteGrant),
    RouteRelease(RouteRelease),
    SpeedRestriction(SpeedRestriction),
    TrainRegistration(TrainRegistration),
    TrainDeparture(TrainDeparture),
    Heartbeat(Heartbeat),
    MaintenanceOverride(MaintenanceOverride),
    FormatVersion(FormatVersion),
}

// ---------------------------------------------------------------------------
// Position report
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum PositionSource {
    Gnss,
    Imu,
    Odometry,
    Beacon,
    LegacyTrackCircuit,
    LegacyAxleCounter,
}

/// Primary sensor-fusion output, 5 Hz nominal.
/// Speed/uncertainty fields are retained as mm/s i64 values so MA arithmetic
/// stays integer.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct TrainPositionReport {
    pub train_id: TrainId,
    pub head_position: Position,
    pub tail_position: Position,
    /// Millimetres per second (positive in Direction::Forward along the line).
    pub speed_mmps: i64,
    /// Half-width 95% CI on speed, in mm/s.
    pub speed_uncertainty_mmps: u32,
    pub heading: Direction,
    pub contributing_sources: Vec<PositionSource>,
    /// TAI ns on the train's own clock.
    pub onboard_time_ns: u64,
    /// 0..=1000 — encoded as parts-per-thousand to stay integer.
    pub pack_soc_ppt: u16,
}

// ---------------------------------------------------------------------------
// Switches
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SwitchPosition {
    Normal,
    Reverse,
    Transitioning,
    /// Fail-restrictive default — treat as unsafe until an Observation
    /// says otherwise.
    Unknown,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Confidence {
    Locked,
    Observed,
    Transitioning,
    Unknown,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SwitchCommand {
    pub switch_id: SwitchId,
    pub requested_position: SwitchPosition,
    pub requested_by: EntityId,
    pub lock_until: Option<EntryId>,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SwitchObservation {
    pub switch_id: SwitchId,
    pub observed_position: SwitchPosition,
    pub confidence: Confidence,
    pub observed_at_ns: u64,
}

// ---------------------------------------------------------------------------
// Routes
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct RouteRequest {
    pub route_id: RouteId,
    pub requested_by: EntityId,
    pub entry_point: TrackRef,
    pub exit_point: TrackRef,
    pub train_id: Option<TrainId>,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct RouteGrant {
    pub route_id: RouteId,
    pub train_id: TrainId,
    pub locked_switches: Vec<SwitchId>,
    pub locked_sections: Vec<SectionId>,
    pub expires_at_ns: u64,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct RouteRelease {
    pub route_id: RouteId,
    pub reason: String,
}

// ---------------------------------------------------------------------------
// Speed restrictions
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum RestrictionReason {
    Permanent,
    Temporary,
    Emergency,
    Weather,
    InfrastructureFault,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SpeedRestriction {
    pub section: SectionId,
    pub from_offset_mm: i64,
    pub to_offset_mm: i64,
    /// Max allowable speed in mm/s.
    pub max_speed_mmps: i64,
    pub reason: RestrictionReason,
    pub effective_from_ns: u64,
    /// `None` means indefinite.
    pub effective_until_ns: Option<u64>,
    pub issued_by: EntityId,
}

// ---------------------------------------------------------------------------
// Train registration / departure
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct TrainRegistration {
    pub train_id: TrainId,
    pub consist: ConsistDescriptor,
    pub initial_position: Position,
    // Cert chain omitted for the in-memory representation; the signed wire
    // form carries it. The signature is verified before an Entry enters
    // the log, not inside derive_state.
}

// `TrainRegistration` contains `ConsistDescriptor`, which has `f32`
// fields (max_speed_mps, braking curve). `PartialEq` composes through to
// `f32` equality — this is imperfect (NaN, -0.0) but acceptable for
// derived-state comparison of well-formed registrations. We intentionally
// do not derive `Eq` or `Hash` for `TrainRegistration` for this reason.

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct TrainDeparture {
    pub train_id: TrainId,
    /// The region this train is handed off to. `None` means leaving the
    /// federated network entirely.
    pub handed_off_to: Option<RegionId>,
    pub handoff_time_ns: u64,
}

// ---------------------------------------------------------------------------
// Liveness & overrides
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum HealthStatus {
    Ok,
    Degraded,
    Failing,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Heartbeat {
    pub from_entity: EntityId,
    pub health: HealthStatus,
    pub monotonic_seq: u64,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct MaintenanceOverride {
    pub section: SectionId,
    pub from_offset_mm: i64,
    pub to_offset_mm: i64,
    pub granted_to: EntityId,
    pub granted_until_ns: u64,
    pub rationale: String,
    // Signatures omitted in the derived-state representation for the same
    // reason as TrainRegistration's cert chain.
}

// ---------------------------------------------------------------------------
// Format version
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct FormatVersion {
    pub current: u32,
    pub min_compatible: u32,
    pub schema_sha256_hex: String,
}
