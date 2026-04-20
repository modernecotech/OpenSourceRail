//! Derived state: the pure fold of a committed log prefix.
//!
//! `derive_state(log_prefix)` is deterministic — the same prefix always
//! produces the same state. This property (P1 in RFC 0001 §7.2) is tested
//! by proptest here and will be formally verified with Kani in M3.
//!
//! The state is intentionally conservative: every uncertain input makes
//! the state *more* restrictive, never less (P4 in RFC 0001 §7.2). This
//! property is enforced by the way `apply_entry` handles each variant
//! and will also be verified with Kani in M3.

use crate::log::{
    Confidence, Entry, EntryPayload, Heartbeat, HealthStatus, MaintenanceOverride,
    RouteGrant, SpeedRestriction, SwitchPosition, TrainDeparture, TrainPositionReport,
    TrainRegistration,
};
use osr_core::{
    ConsistDescriptor, EntityId, Position, RouteId, SectionId, SwitchId, TrainId,
};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

// ---------------------------------------------------------------------------
// Top-level state
// ---------------------------------------------------------------------------

/// Authoritative snapshot of the rail state machine derived from a log
/// prefix. BTreeMap (not HashMap) is used so that structural equality is
/// deterministic — two states with the same content compare equal regardless
/// of insertion order.
#[derive(Clone, Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct DerivedState {
    /// For each section currently occupied by a train, the occupying train's
    /// id. Absence = section is unoccupied *per the log*; that does not
    /// mean it is safe to enter (route grants, switch positions, and
    /// uncertainty may still block it — that's the MA computer's job).
    pub section_occupancy: BTreeMap<SectionId, TrainId>,

    /// Observed switch positions with confidence.
    pub switches: BTreeMap<SwitchId, SwitchState>,

    /// Known trains and their latest awareness.
    pub trains: BTreeMap<TrainId, TrainAwareness>,

    /// Active route grants — route_id → grant.
    pub active_routes: BTreeMap<RouteId, RouteGrant>,

    /// Active speed restrictions. Kept as a sequence because a section can
    /// have multiple overlapping restrictions (permanent + temporary).
    pub speed_restrictions: Vec<SpeedRestriction>,

    /// Active maintenance overrides. Same reasoning as speed_restrictions.
    pub maintenance_overrides: Vec<MaintenanceOverride>,

    /// Last-seen monotonic sequence per entity, for stale-heartbeat detection.
    pub entity_liveness: BTreeMap<EntityId, EntityLiveness>,

    /// The latest accepted format version. `None` before any FormatVersion
    /// entry is seen.
    pub format_version: Option<u32>,

    /// The `timestamp_ns` of the last entry applied. Useful for MA validity
    /// computations.
    pub last_entry_time_ns: u64,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SwitchState {
    pub position: SwitchPosition,
    pub confidence: Confidence,
    pub observed_at_ns: u64,
}

impl SwitchState {
    /// Fail-restrictive starting state for a switch: Unknown position,
    /// Unknown confidence. Used when a switch is referenced before being
    /// observed.
    pub fn unknown() -> Self {
        Self {
            position: SwitchPosition::Unknown,
            confidence: Confidence::Unknown,
            observed_at_ns: 0,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct TrainAwareness {
    pub consist: ConsistDescriptor,
    pub last_head_position: Option<Position>,
    pub last_tail_position: Option<Position>,
    pub last_position_onboard_ns: u64,
    pub last_position_log_ns: u64,
    pub speed_mmps: i64,
    pub speed_uncertainty_mmps: u32,
    pub pack_soc_ppt: u16,
}

impl TrainAwareness {
    fn from_registration(reg: &TrainRegistration, log_time_ns: u64) -> Self {
        Self {
            consist: reg.consist.clone(),
            last_head_position: Some(reg.initial_position),
            last_tail_position: None,
            last_position_onboard_ns: 0,
            last_position_log_ns: log_time_ns,
            speed_mmps: 0,
            speed_uncertainty_mmps: 0,
            pack_soc_ppt: 1000,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct EntityLiveness {
    pub health: HealthStatus,
    pub monotonic_seq: u64,
    pub last_entry_time_ns: u64,
}

// ---------------------------------------------------------------------------
// derive_state
// ---------------------------------------------------------------------------

/// Fold a committed log prefix into a `DerivedState`.
///
/// This is a pure function: the same input always produces the same output.
/// See `tests/proptest_determinism.rs` for the property-based check.
pub fn derive_state(log_prefix: &[Entry]) -> DerivedState {
    let mut state = DerivedState::default();
    for entry in log_prefix {
        apply_entry(&mut state, entry);
    }
    state
}

impl DerivedState {
    /// Incrementally advance a state by applying a single entry.
    /// Composition property: `derive_state(prefix)` and calling
    /// `apply` for each entry of `prefix` produce equal states.
    pub fn apply(&mut self, entry: &Entry) {
        apply_entry(self, entry);
    }
}

fn apply_entry(state: &mut DerivedState, entry: &Entry) {
    state.last_entry_time_ns = entry.timestamp_ns;
    match &entry.payload {
        EntryPayload::TrainPositionReport(r) => apply_position(state, r, entry.timestamp_ns),
        EntryPayload::SwitchObservation(o) => {
            state.switches.insert(
                o.switch_id,
                SwitchState {
                    position: o.observed_position,
                    confidence: o.confidence,
                    observed_at_ns: o.observed_at_ns,
                },
            );
        }
        EntryPayload::TrainRegistration(reg) => {
            state.trains.insert(
                reg.train_id,
                TrainAwareness::from_registration(reg, entry.timestamp_ns),
            );
        }
        EntryPayload::TrainDeparture(dep) => apply_departure(state, dep),
        EntryPayload::RouteGrant(g) => {
            state.active_routes.insert(g.route_id, g.clone());
        }
        EntryPayload::RouteRelease(r) => {
            state.active_routes.remove(&r.route_id);
        }
        EntryPayload::SpeedRestriction(sr) => {
            // Restrictions accumulate; they're cleared when their
            // effective_until_ns passes (handled at read time by the MA
            // computer, not here — keeping derive_state append-only).
            state.speed_restrictions.push(sr.clone());
        }
        EntryPayload::MaintenanceOverride(m) => {
            state.maintenance_overrides.push(m.clone());
        }
        EntryPayload::Heartbeat(hb) => apply_heartbeat(state, hb, entry.timestamp_ns),
        EntryPayload::FormatVersion(fv) => {
            state.format_version = Some(fv.current);
        }
        // These don't mutate derived state directly. SwitchCommand is only
        // advisory until a subsequent SwitchObservation confirms; RouteRequest
        // is advisory until a subsequent RouteGrant approves.
        EntryPayload::SwitchCommand(_) | EntryPayload::RouteRequest(_) => {}
    }
}

fn apply_position(state: &mut DerivedState, r: &TrainPositionReport, log_time_ns: u64) {
    // Update or create the train awareness record. Protocol-wise a
    // position report should follow a registration, but derive_state is
    // tolerant: we create a minimal record if we haven't seen one. This
    // keeps the function total (never panics) and deterministic.
    let awareness =
        state
            .trains
            .entry(r.train_id)
            .or_insert_with(|| TrainAwareness {
                consist: ConsistDescriptor::reference_3car(),
                last_head_position: None,
                last_tail_position: None,
                last_position_onboard_ns: 0,
                last_position_log_ns: 0,
                speed_mmps: 0,
                speed_uncertainty_mmps: 0,
                pack_soc_ppt: 1000,
            });
    awareness.last_head_position = Some(r.head_position);
    awareness.last_tail_position = Some(r.tail_position);
    awareness.last_position_onboard_ns = r.onboard_time_ns;
    awareness.last_position_log_ns = log_time_ns;
    awareness.speed_mmps = r.speed_mmps;
    awareness.speed_uncertainty_mmps = r.speed_uncertainty_mmps;
    awareness.pack_soc_ppt = r.pack_soc_ppt.min(1000);

    // Update occupancy. M1 simplification: mark both head and tail
    // sections as occupied by this train; clear any other section this
    // train previously held. The MA computer (M2) will refine this with
    // consist-length footprint and uncertainty padding.
    clear_occupancy_by(state, r.train_id);
    state.section_occupancy.insert(r.head_position.track_ref.section, r.train_id);
    if r.tail_position.track_ref.section != r.head_position.track_ref.section {
        state.section_occupancy.insert(r.tail_position.track_ref.section, r.train_id);
    }
}

fn apply_departure(state: &mut DerivedState, dep: &TrainDeparture) {
    state.trains.remove(&dep.train_id);
    clear_occupancy_by(state, dep.train_id);
    // Also release any active route grants this train held.
    state.active_routes.retain(|_, g| g.train_id != dep.train_id);
}

fn clear_occupancy_by(state: &mut DerivedState, train: TrainId) {
    state.section_occupancy.retain(|_, tid| *tid != train);
}

fn apply_heartbeat(state: &mut DerivedState, hb: &Heartbeat, log_time_ns: u64) {
    // Monotonic sequence must strictly increase for an entity; a
    // replayed/out-of-order heartbeat is ignored (fail-restrictive in
    // the liveness-tracking sense).
    let entry = state
        .entity_liveness
        .entry(hb.from_entity)
        .or_insert(EntityLiveness {
            health: hb.health,
            monotonic_seq: hb.monotonic_seq,
            last_entry_time_ns: log_time_ns,
        });
    if hb.monotonic_seq > entry.monotonic_seq {
        entry.health = hb.health;
        entry.monotonic_seq = hb.monotonic_seq;
        entry.last_entry_time_ns = log_time_ns;
    }
}

// ---------------------------------------------------------------------------
// Unit tests — the proptests live in tests/ alongside this crate
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::log::*;
    use osr_core::{ConsistDescriptor, Direction, Position, SectionId, TrackRef, TrainId};

    fn entry(id: u64, ts: u64, payload: EntryPayload) -> Entry {
        Entry {
            entry_id: osr_core::EntryId::new(id),
            term: 1,
            timestamp_ns: ts,
            payload,
        }
    }

    fn pos(section: u64, offset_mm: i64) -> Position {
        Position {
            track_ref: TrackRef {
                section: SectionId::new(section),
                offset_mm,
                direction: Direction::Forward,
            },
            uncertainty_mm: 0,
        }
    }

    #[test]
    fn empty_prefix_yields_default_state() {
        let s = derive_state(&[]);
        assert_eq!(s, DerivedState::default());
    }

    #[test]
    fn registration_then_position_tracks_train() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1, 0),
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(7),
                    head_position: pos(2, 5_000),
                    tail_position: pos(1, 60_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss, PositionSource::Odometry],
                    onboard_time_ns: 180,
                    pack_soc_ppt: 850,
                }),
            ),
        ];
        let s = derive_state(&log);
        assert_eq!(s.trains.len(), 1);
        let aw = &s.trains[&TrainId::new(7)];
        assert_eq!(aw.speed_mmps, 10_000);
        assert_eq!(aw.pack_soc_ppt, 850);
        // Both head and tail sections occupied by T7.
        assert_eq!(s.section_occupancy[&SectionId::new(1)], TrainId::new(7));
        assert_eq!(s.section_occupancy[&SectionId::new(2)], TrainId::new(7));
    }

    #[test]
    fn departure_clears_train_and_occupancy() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1, 0),
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(7),
                    head_position: pos(2, 5_000),
                    tail_position: pos(1, 60_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 180,
                    pack_soc_ppt: 850,
                }),
            ),
            entry(
                3,
                300,
                EntryPayload::TrainDeparture(TrainDeparture {
                    train_id: TrainId::new(7),
                    handed_off_to: None,
                    handoff_time_ns: 295,
                }),
            ),
        ];
        let s = derive_state(&log);
        assert!(s.trains.is_empty());
        assert!(s.section_occupancy.is_empty());
    }

    #[test]
    fn switch_observation_recorded_with_latest_winning() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::SwitchObservation(SwitchObservation {
                    switch_id: osr_core::SwitchId::new(3),
                    observed_position: SwitchPosition::Normal,
                    confidence: Confidence::Observed,
                    observed_at_ns: 99,
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::SwitchObservation(SwitchObservation {
                    switch_id: osr_core::SwitchId::new(3),
                    observed_position: SwitchPosition::Reverse,
                    confidence: Confidence::Locked,
                    observed_at_ns: 198,
                }),
            ),
        ];
        let s = derive_state(&log);
        let sw = &s.switches[&osr_core::SwitchId::new(3)];
        assert_eq!(sw.position, SwitchPosition::Reverse);
        assert_eq!(sw.confidence, Confidence::Locked);
    }

    #[test]
    fn out_of_order_heartbeat_ignored() {
        let eid = osr_core::EntityId::new(42);
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::Heartbeat(Heartbeat {
                    from_entity: eid,
                    health: HealthStatus::Ok,
                    monotonic_seq: 10,
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::Heartbeat(Heartbeat {
                    from_entity: eid,
                    health: HealthStatus::Failing,
                    monotonic_seq: 5, // older sequence — must be ignored
                }),
            ),
        ];
        let s = derive_state(&log);
        let live = &s.entity_liveness[&eid];
        assert_eq!(live.monotonic_seq, 10);
        assert_eq!(live.health, HealthStatus::Ok);
    }

    #[test]
    fn determinism_batch_matches_incremental() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(1),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1, 0),
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(1),
                    head_position: pos(1, 5_000),
                    tail_position: pos(1, 0),
                    speed_mmps: 5_000,
                    speed_uncertainty_mmps: 100,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 190,
                    pack_soc_ppt: 900,
                }),
            ),
        ];
        let batch = derive_state(&log);
        let mut incremental = DerivedState::default();
        for e in &log {
            incremental.apply(e);
        }
        assert_eq!(batch, incremental);
    }
}
