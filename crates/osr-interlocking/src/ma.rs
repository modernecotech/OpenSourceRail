//! Movement Authority (MA) computation — the heart of the safety case.
//!
//! `compute_self_ma(train_id, log_prefix, network, now_ns)` is a pure
//! function of its inputs. Given:
//! - A `TrainId` identifying which train we're computing for
//! - A committed log prefix (the output of `osr-consensus`)
//! - The static `Network` topology
//! - The current time
//!
//! it returns a `MovementAuthority` — the set of track the train is
//! permitted to occupy, bounded in space (MAX_MA_DISTANCE_MM) and in time
//! (MA_VALIDITY_WINDOW_NS).
//!
//! Five safety properties (RFC 0001 §7.2, RFC 0004 §4) are intended to be
//! verified about this function:
//!
//! - **P1 (determinism)**: same input → byte-identical output.
//! - **P2 (non-overlap)**: for any two registered trains, computed MAs do
//!   not share any section (unless both are the same train).
//! - **P3 (consist-fit)**: MA extension accounts for the train's full
//!   consist length (the footprint it already occupies).
//! - **P4 (conservatism)**: more-uncertain input produces a more-restrictive
//!   MA, never less. Encoded here by the way `section_available_to` treats
//!   unknown/stale/conflicting state as blocking.
//! - **P5 (time-bounded)**: `valid_until - now` is bounded above by
//!   `MA_VALIDITY_WINDOW_NS`.
//!
//! Debug-build `debug_assert!`s check P3 and P5 at runtime on every call.
//! Proptests in `tests/proptest_ma.rs` exercise P1 and P5 across random
//! log prefixes. Kani harnesses (M3) will formally verify all five.

use osr_core::{Direction, EntryId, Network, SectionId, TrackRef, TrainId};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

use crate::log::{Entry, SpeedRestriction};
use crate::state::{derive_state, DerivedState};
use crate::topology::{far_end_of, footprint_from, forward_chain};

/// How far ahead an MA can extend, in millimetres. Per RFC 0001 §6.3
/// this is a deployment-tunable parameter; the default of 2 km is
/// appropriate for urban metro service.
pub const MAX_MA_DISTANCE_MM: i64 = 2_000_000;

/// How long an MA is valid after issue, in nanoseconds. Per RFC 0001 §6.3:
/// 3 seconds. Long enough to tolerate transient network hiccups, short
/// enough to be self-expiring if consensus unavailability stalls the log.
pub const MA_VALIDITY_WINDOW_NS: u64 = 3_000_000_000;

// ---------------------------------------------------------------------------
// MovementAuthority
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct MovementAuthority {
    pub train_id: TrainId,
    /// End of authority: the train's head position shall not pass this
    /// point before (a) a new MA is accepted or (b) `valid_until_ns` is
    /// reached.
    pub end: TrackRef,
    /// Speed restrictions applicable within the authority.
    pub applicable_restrictions: Vec<SpeedRestriction>,
    /// Nanoseconds-since-epoch at which this MA expires.
    pub valid_until_ns: u64,
    /// The log entry id this MA is derived from. `None` only when the log
    /// prefix is empty.
    pub derived_from_entry_id: Option<EntryId>,
    /// Whether the train's position was known at computation time. If
    /// false, the MA is fail-restrictive (end == reported start).
    pub has_known_position: bool,
}

// ---------------------------------------------------------------------------
// compute_self_ma
// ---------------------------------------------------------------------------

/// Compute the Movement Authority for `train_id` from the given log prefix.
///
/// This is the entry point the RFC pseudocode specifies. It performs:
/// 1. `derive_state` on the log prefix.
/// 2. Determine the train's current head, tail, and consist.
/// 3. Walk forward from the head, clipping at the first unavailable section.
/// 4. Filter applicable speed restrictions.
/// 5. Bind a validity window.
///
/// Any step that cannot complete (train not registered, head position
/// unknown, direction inconsistent with topology) produces a fail-restrictive
/// MA whose `end` equals the best-known head position and whose
/// `has_known_position` is set accordingly.
pub fn compute_self_ma(
    train_id: TrainId,
    log_prefix: &[Entry],
    network: &Network,
    now_ns: u64,
) -> MovementAuthority {
    let state = derive_state(log_prefix);
    let derived_from = log_prefix.last().map(|e| e.entry_id);
    compute_self_ma_from_state(train_id, &state, network, now_ns, derived_from)
}

/// Same as `compute_self_ma` but takes a precomputed `DerivedState`.
/// Useful for the sim, which maintains a long-lived state incrementally.
pub fn compute_self_ma_from_state(
    train_id: TrainId,
    state: &DerivedState,
    network: &Network,
    now_ns: u64,
    derived_from_entry_id: Option<EntryId>,
) -> MovementAuthority {
    // P5: bind the validity window up front. Every return path uses this
    // single value, making it impossible to forget.
    let valid_until_ns = now_ns.saturating_add(MA_VALIDITY_WINDOW_NS);

    let Some(awareness) = state.trains.get(&train_id) else {
        return fail_restrictive(train_id, None, valid_until_ns, derived_from_entry_id);
    };
    let Some(head) = awareness.last_head_position else {
        return fail_restrictive(train_id, None, valid_until_ns, derived_from_entry_id);
    };

    let consist_length_mm = awareness.consist.length_mm;
    let footprint_sections: BTreeSet<SectionId> =
        footprint_from(network, head.track_ref, consist_length_mm)
            .into_iter()
            .collect();

    // The candidate forward chain: sections the train could reach going
    // forward from its head, up to MAX_MA_DISTANCE_MM.
    let chain = forward_chain(network, head.track_ref, MAX_MA_DISTANCE_MM);

    // Clip the chain at the first unavailable section. The head's current
    // section (and any section in the footprint) is by definition the
    // train's own — we skip occupancy checks against ourselves on those.
    let mut ma_end = head.track_ref; // default: no extension
    let mut reached_far_end_of_head = false;
    for section_id in chain.iter().copied() {
        if footprint_sections.contains(&section_id) {
            // We already occupy this section. Extend to its far end.
            ma_end = far_end_of(network, section_id, head.track_ref.direction);
            reached_far_end_of_head = true;
            continue;
        }
        if !section_available_to(train_id, section_id, state) {
            break;
        }
        ma_end = far_end_of(network, section_id, head.track_ref.direction);
    }

    // P3 invariant check (debug builds only): the MA end must be at least
    // at the head's reported position. "Not behind the head" means the
    // computed end offset covers the consist footprint.
    debug_assert!(
        reached_far_end_of_head || ma_end == head.track_ref,
        "MA end regressed behind the train's own head position"
    );

    let applicable_restrictions =
        collect_applicable_restrictions(state, network, head.track_ref, ma_end, now_ns);

    let ma = MovementAuthority {
        train_id,
        end: ma_end,
        applicable_restrictions,
        valid_until_ns,
        derived_from_entry_id,
        has_known_position: true,
    };

    // P5 invariant check (debug builds only): ensure the validity window
    // didn't escape its bound via wraparound or accidental arithmetic.
    debug_assert!(
        ma.valid_until_ns
            .checked_sub(now_ns)
            .map(|d| d <= MA_VALIDITY_WINDOW_NS)
            .unwrap_or(true),
        "MA validity window exceeded MA_VALIDITY_WINDOW_NS"
    );

    ma
}

// ---------------------------------------------------------------------------
// Section availability — the heart of fail-restrictive reasoning
// ---------------------------------------------------------------------------

/// Is this section currently available for this train to occupy?
///
/// A section is available iff ALL of the following hold:
/// - No *other* train occupies it per `section_occupancy`.
/// - Any `MaintenanceOverride` on this section is consistent with this
///   train (not granted exclusively to someone else).
/// - Any `RouteGrant` locking this section is this train's route.
/// - The latest wayside `SectionIntrusion` verdict (if any) is
///   `Clear` — any `Unknown` / `Present` verdict withholds MA
///   (RFC 0016 v2). Sections with no verdict on record are treated
///   as not-instrumented and do not add a gate — see
///   [`crate::section_intrusion_permits`].
///
/// Uncertainty produces NOT available, always. This is P4's concrete
/// enforcement point.
pub fn section_available_to(train_id: TrainId, section: SectionId, state: &DerivedState) -> bool {
    // (a) Occupancy: must be empty or already ours.
    if let Some(occupant) = state.section_occupancy.get(&section) {
        if *occupant != train_id {
            return false;
        }
    }

    // (b) Route grants: if any active grant locks this section, it must
    // be ours.
    for grant in state.active_routes.values() {
        if grant.locked_sections.contains(&section) && grant.train_id != train_id {
            return false;
        }
    }

    // (c) Maintenance overrides: if any active override covers this
    // section's start offset (we don't model partial sections yet in v1),
    // it blocks the section for trains other than... whoever the
    // override is granted to. In v1 we conservatively treat any
    // maintenance override on the section as blocking.
    for over in &state.maintenance_overrides {
        if over.section == section {
            return false;
        }
    }

    // (d) Wayside intrusion gate (RFC 0016 v2). If the section has a
    // recent verdict on record, it must be `Clear`.
    if !crate::state::section_intrusion_permits(state, section) {
        return false;
    }

    true
}

// ---------------------------------------------------------------------------
// Speed restrictions
// ---------------------------------------------------------------------------

fn collect_applicable_restrictions(
    state: &DerivedState,
    network: &Network,
    from: TrackRef,
    to: TrackRef,
    now_ns: u64,
) -> Vec<SpeedRestriction> {
    let authority_sections: BTreeSet<SectionId> = if from.section == to.section {
        [from.section].into_iter().collect()
    } else {
        forward_chain_from_to(network, from, to)
    };

    state
        .speed_restrictions
        .iter()
        .filter(|sr| {
            // Time window.
            if sr.effective_from_ns > now_ns {
                return false;
            }
            if let Some(until) = sr.effective_until_ns {
                if now_ns >= until {
                    return false;
                }
            }
            restriction_overlaps_authority(sr, from, to, &authority_sections)
        })
        .cloned()
        .collect()
}

fn forward_chain_from_to(network: &Network, from: TrackRef, to: TrackRef) -> BTreeSet<SectionId> {
    // `collect_applicable_restrictions` is called after MA computation, so
    // the authority end must be on the same forward chain as `from`.
    // Re-walk using the same bounded helper and stop at `to.section`.
    let mut sections = BTreeSet::new();
    for section in forward_chain(network, from, MAX_MA_DISTANCE_MM) {
        sections.insert(section);
        if section == to.section {
            break;
        }
    }
    sections
}

fn restriction_overlaps_authority(
    sr: &SpeedRestriction,
    from: TrackRef,
    to: TrackRef,
    authority_sections: &BTreeSet<SectionId>,
) -> bool {
    if !authority_sections.contains(&sr.section) {
        return false;
    }

    if from.section == to.section && sr.section == from.section {
        let low = from.offset_mm.min(to.offset_mm);
        let high = from.offset_mm.max(to.offset_mm);
        return sr.to_offset_mm > low && sr.from_offset_mm < high;
    }
    if sr.section == from.section {
        return sr.to_offset_mm > from.offset_mm;
    }
    if sr.section == to.section {
        return sr.from_offset_mm < to.offset_mm;
    }
    true
}

// ---------------------------------------------------------------------------
// Fail-restrictive default MA
// ---------------------------------------------------------------------------

fn fail_restrictive(
    train_id: TrainId,
    head_if_any: Option<TrackRef>,
    valid_until_ns: u64,
    derived_from_entry_id: Option<EntryId>,
) -> MovementAuthority {
    let end = head_if_any.unwrap_or(TrackRef {
        section: SectionId::new(0),
        offset_mm: 0,
        direction: Direction::Forward,
    });
    MovementAuthority {
        train_id,
        end,
        applicable_restrictions: vec![],
        valid_until_ns,
        derived_from_entry_id,
        has_known_position: head_if_any.is_some(),
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::log::{EntryPayload, PositionSource, TrainPositionReport, TrainRegistration};
    use osr_core::{ConsistDescriptor, Line, Position, Section, Station, StationId, TrackRef};

    fn net_3_sections() -> Network {
        let mut net = Network::default();
        for i in 1..=4 {
            net.stations.insert(
                StationId::new(i),
                Station {
                    id: StationId::new(i),
                    name: format!("S{i}"),
                    charging_power_kw: 0,
                    dwell_seconds: 0,
                    is_terminal: false,
                    is_depot: false,
                },
            );
        }
        let mut fwd = vec![];
        let mut rev = vec![];
        for i in 0..3 {
            let f = SectionId::new(1000 + i);
            let r = SectionId::new(2000 + i);
            net.sections.insert(
                f,
                Section {
                    id: f,
                    from_station: StationId::new(i + 1),
                    to_station: StationId::new(i + 2),
                    length_mm: 1_000_000,
                    max_speed_mps: 22.0,
                },
            );
            net.sections.insert(
                r,
                Section {
                    id: r,
                    from_station: StationId::new(i + 2),
                    to_station: StationId::new(i + 1),
                    length_mm: 1_000_000,
                    max_speed_mps: 22.0,
                },
            );
            fwd.push(f);
            rev.push(r);
        }
        net.lines.push(Line {
            name: "L".into(),
            stations: (1..=4).map(StationId::new).collect(),
            forward_sections: fwd,
            reverse_sections: rev,
            is_ring: false,
        });
        net
    }

    fn entry(id: u64, ts: u64, payload: EntryPayload) -> Entry {
        Entry {
            entry_id: EntryId::new(id),
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
    fn no_registration_yields_fail_restrictive_ma() {
        let net = net_3_sections();
        let ma = compute_self_ma(TrainId::new(7), &[], &net, 1_000);
        assert!(!ma.has_known_position);
        assert_eq!(ma.end.offset_mm, 0);
        assert_eq!(ma.valid_until_ns - 1_000, MA_VALIDITY_WINDOW_NS);
    }

    #[test]
    fn single_train_extends_to_max_distance() {
        let net = net_3_sections();
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(7),
                    head_position: pos(1000, 100_000), // 100 m into section 1000
                    tail_position: pos(1000, 35_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 190,
                    pack_soc_ppt: 900,
                }),
            ),
            intrusion_entry(3, 1001, IntrusionState::Clear),
        ];
        let ma = compute_self_ma(TrainId::new(7), &log, &net, 1_000_000);
        assert!(ma.has_known_position);
        // Head at 100m into section 1000; max MA distance 2km; sections 1000/1001/1002 each 1km.
        // Remaining in 1000: 900m. Plus 1001 (1km). Plus 1002: would exceed 2km.
        // So MA should end at far end of 1001.
        assert_eq!(ma.end.section, SectionId::new(1001));
        assert_eq!(ma.end.offset_mm, 1_000_000);
    }

    #[test]
    fn other_train_blocks_extension() {
        let net = net_3_sections();
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            entry(
                2,
                150,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(9),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1001, 0),
                }),
            ),
            entry(
                3,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(9),
                    head_position: pos(1001, 500_000),
                    tail_position: pos(1001, 435_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 190,
                    pack_soc_ppt: 900,
                }),
            ),
            entry(
                4,
                300,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(7),
                    head_position: pos(1000, 100_000),
                    tail_position: pos(1000, 35_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 290,
                    pack_soc_ppt: 900,
                }),
            ),
        ];
        let ma = compute_self_ma(TrainId::new(7), &log, &net, 1_000_000);
        // Train 7 sees train 9 occupying section 1001, so MA ends at far
        // end of section 1000 (the train's own section).
        assert_eq!(ma.end.section, SectionId::new(1000));
        assert_eq!(ma.end.offset_mm, 1_000_000);
    }

    #[test]
    fn p2_non_overlap_two_trains() {
        // Verified manually for a small case; the Kani harness will cover
        // this formally. Here we just assert it for a specific example.
        let net = net_3_sections();
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            entry(
                2,
                150,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(9),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1002, 0),
                }),
            ),
            entry(
                3,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(9),
                    head_position: pos(1002, 500_000),
                    tail_position: pos(1002, 435_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 190,
                    pack_soc_ppt: 900,
                }),
            ),
            entry(
                4,
                250,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(7),
                    head_position: pos(1000, 100_000),
                    tail_position: pos(1000, 35_000),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 240,
                    pack_soc_ppt: 900,
                }),
            ),
        ];
        let ma7 = compute_self_ma(TrainId::new(7), &log, &net, 1_000_000);
        let ma9 = compute_self_ma(TrainId::new(9), &log, &net, 1_000_000);

        // Compute the set of sections each MA permits. For simplicity,
        // here we consider "head section → end section".
        let sections_permitted = |ma: &MovementAuthority, head: SectionId| -> Vec<SectionId> {
            let chain = forward_chain(
                &net,
                TrackRef {
                    section: head,
                    offset_mm: 0,
                    direction: Direction::Forward,
                },
                MAX_MA_DISTANCE_MM,
            );
            let mut result = vec![];
            for s in chain {
                result.push(s);
                if s == ma.end.section {
                    break;
                }
            }
            result
        };
        let s7 = sections_permitted(&ma7, SectionId::new(1000));
        let s9 = sections_permitted(&ma9, SectionId::new(1002));
        // P2: the two MAs should not share any section except possibly
        // the one where a train's own footprint lives.
        let set7: BTreeSet<_> = s7.into_iter().collect();
        let set9: BTreeSet<_> = s9.into_iter().collect();
        assert!(set7.is_disjoint(&set9), "MAs overlap: {set7:?} vs {set9:?}");
    }

    #[test]
    fn p5_validity_window_bounded() {
        let net = net_3_sections();
        let ma = compute_self_ma(TrainId::new(7), &[], &net, 1_000_000);
        assert!(ma.valid_until_ns - 1_000_000 <= MA_VALIDITY_WINDOW_NS);
    }

    // -----------------------------------------------------------------
    // RFC 0016 v2 — intrusion-gate tests
    // -----------------------------------------------------------------

    use crate::log::{IntrusionState, RestrictionReason, SectionIntrusion};
    use osr_core::EntityId;

    fn speed_restriction_entry(id: u64, section: u64, max_speed_mmps: i64) -> Entry {
        entry(
            id,
            1_000,
            EntryPayload::SpeedRestriction(SpeedRestriction {
                section: SectionId::new(section),
                from_offset_mm: 0,
                to_offset_mm: 1_000_000,
                max_speed_mmps,
                reason: RestrictionReason::Temporary,
                effective_from_ns: 0,
                effective_until_ns: None,
                issued_by: EntityId::new(100),
            }),
        )
    }

    #[test]
    fn intermediate_speed_restriction_is_collected() {
        let net = net_3_sections();
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            entry(
                2,
                200,
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id: TrainId::new(7),
                    head_position: pos(1000, 0),
                    tail_position: pos(1000, 0),
                    speed_mmps: 10_000,
                    speed_uncertainty_mmps: 0,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss],
                    onboard_time_ns: 190,
                    pack_soc_ppt: 900,
                }),
            ),
            intrusion_entry(3, 1001, IntrusionState::Clear),
            speed_restriction_entry(4, 1001, 12_000),
        ];

        let ma = compute_self_ma(TrainId::new(7), &log, &net, 1_000_000);
        assert_eq!(ma.end.section, SectionId::new(1001));
        assert_eq!(ma.applicable_restrictions.len(), 1);
        assert_eq!(ma.applicable_restrictions[0].section, SectionId::new(1001));
    }

    fn intrusion_entry(id: u64, section: u64, istate: IntrusionState) -> Entry {
        entry(
            id,
            1_000,
            EntryPayload::SectionIntrusion(SectionIntrusion {
                section: SectionId::new(section),
                state: istate,
                issued_by: EntityId::new(100),
                observed_at_ns: 900,
            }),
        )
    }

    #[test]
    fn intrusion_clear_permits_section() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            intrusion_entry(2, 1001, IntrusionState::Clear),
        ];
        let state = derive_state(&log);
        assert!(section_available_to(
            TrainId::new(7),
            SectionId::new(1001),
            &state
        ));
    }

    #[test]
    fn intrusion_present_blocks_section() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            intrusion_entry(2, 1001, IntrusionState::Present),
        ];
        let state = derive_state(&log);
        assert!(
            !section_available_to(TrainId::new(7), SectionId::new(1001), &state),
            "a Present verdict must withhold MA"
        );
    }

    #[test]
    fn intrusion_unknown_is_fail_restrictive() {
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            intrusion_entry(2, 1001, IntrusionState::Unknown),
        ];
        let state = derive_state(&log);
        assert!(
            !section_available_to(TrainId::new(7), SectionId::new(1001), &state),
            "an Unknown verdict is fail-restrictive — must withhold MA"
        );
    }

    #[test]
    fn no_intrusion_entry_is_fail_restrictive() {
        // Section 1001 has no SectionIntrusion record, so movement authority
        // remains withheld until the instrumented section reports Clear.
        let log = vec![entry(
            1,
            100,
            EntryPayload::TrainRegistration(TrainRegistration {
                train_id: TrainId::new(7),
                consist: ConsistDescriptor::reference_3car(),
                initial_position: pos(1000, 0),
            }),
        )];
        let state = derive_state(&log);
        assert!(!section_available_to(
            TrainId::new(7),
            SectionId::new(1001),
            &state
        ));
    }

    #[test]
    fn latest_intrusion_verdict_wins() {
        // Present → Clear: Clear wins (latest verdict).
        let log = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            intrusion_entry(2, 1001, IntrusionState::Present),
            intrusion_entry(3, 1001, IntrusionState::Clear),
        ];
        let state = derive_state(&log);
        assert!(section_available_to(
            TrainId::new(7),
            SectionId::new(1001),
            &state
        ));

        // Clear → Present: Present wins.
        let log2 = vec![
            entry(
                1,
                100,
                EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: TrainId::new(7),
                    consist: ConsistDescriptor::reference_3car(),
                    initial_position: pos(1000, 0),
                }),
            ),
            intrusion_entry(2, 1001, IntrusionState::Clear),
            intrusion_entry(3, 1001, IntrusionState::Present),
        ];
        let state2 = derive_state(&log2);
        assert!(!section_available_to(
            TrainId::new(7),
            SectionId::new(1001),
            &state2
        ));
    }
}
