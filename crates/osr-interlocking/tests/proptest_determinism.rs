//! Proptest-level property checks for `derive_state`.
//!
//! The central property — P1 in [RFC 0001 §7.2] — is determinism:
//! `derive_state(prefix)` is a pure function of `prefix`. Two invocations
//! with byte-identical inputs yield byte-identical outputs; batch
//! application is equivalent to incremental application.
//!
//! Kani will verify this formally in M3. Proptest here catches bugs
//! cheaply across larger random inputs.

use osr_core::{
    ConsistDescriptor, Direction, EntityId, EntryId, Position, RegionId, RouteId,
    SectionId, SwitchId, TrackRef, TrainId,
};
use osr_interlocking::{
    derive_state, Confidence, DerivedState, Entry, EntryPayload, Heartbeat,
    MaintenanceOverride, PositionSource, RestrictionReason, RouteGrant, RouteRelease,
    RouteRequest, SpeedRestriction, SwitchCommand, SwitchObservation, SwitchPosition,
    TrainDeparture, TrainPositionReport, TrainRegistration,
};
use osr_interlocking::log::HealthStatus;
use proptest::prelude::*;

// ---------------------------------------------------------------------------
// Strategies — these generate valid-ish Entry instances. We keep the space
// small enough that proptest can meaningfully explore it, but we deliberately
// allow sequences that protocol validation would reject (e.g., position
// reports before registration) so that `derive_state` is verified to be
// total and deterministic even under malformed input.
// ---------------------------------------------------------------------------

fn arb_position() -> impl Strategy<Value = Position> {
    (1u64..8, -10_000i64..10_000, prop::bool::ANY)
        .prop_map(|(section, offset_mm, forward)| Position {
            track_ref: TrackRef {
                section: SectionId::new(section),
                offset_mm,
                direction: if forward { Direction::Forward } else { Direction::Reverse },
            },
            uncertainty_mm: 100,
        })
}

fn arb_train_id() -> impl Strategy<Value = TrainId> {
    (1u64..5).prop_map(TrainId::new)
}

fn arb_switch_id() -> impl Strategy<Value = SwitchId> {
    (1u64..5).prop_map(SwitchId::new)
}

fn arb_route_id() -> impl Strategy<Value = RouteId> {
    (1u64..5).prop_map(RouteId::new)
}

fn arb_entity_id() -> impl Strategy<Value = EntityId> {
    (1u64..5).prop_map(EntityId::new)
}

fn arb_switch_position() -> impl Strategy<Value = SwitchPosition> {
    prop_oneof![
        Just(SwitchPosition::Normal),
        Just(SwitchPosition::Reverse),
        Just(SwitchPosition::Transitioning),
        Just(SwitchPosition::Unknown),
    ]
}

fn arb_confidence() -> impl Strategy<Value = Confidence> {
    prop_oneof![
        Just(Confidence::Locked),
        Just(Confidence::Observed),
        Just(Confidence::Transitioning),
        Just(Confidence::Unknown),
    ]
}

fn arb_health() -> impl Strategy<Value = HealthStatus> {
    prop_oneof![
        Just(HealthStatus::Ok),
        Just(HealthStatus::Degraded),
        Just(HealthStatus::Failing),
    ]
}

fn arb_restriction_reason() -> impl Strategy<Value = RestrictionReason> {
    prop_oneof![
        Just(RestrictionReason::Permanent),
        Just(RestrictionReason::Temporary),
        Just(RestrictionReason::Emergency),
        Just(RestrictionReason::Weather),
        Just(RestrictionReason::InfrastructureFault),
    ]
}

fn arb_payload() -> BoxedStrategy<EntryPayload> {
    prop_oneof![
        (arb_train_id(), arb_position()).prop_map(|(train_id, initial_position)| {
            EntryPayload::TrainRegistration(TrainRegistration {
                train_id,
                consist: ConsistDescriptor::reference_3car(),
                initial_position,
            })
        }),
        (
            arb_train_id(),
            arb_position(),
            arb_position(),
            -30_000i64..30_000,
        )
            .prop_map(|(train_id, head, tail, speed)| {
                EntryPayload::TrainPositionReport(TrainPositionReport {
                    train_id,
                    head_position: head,
                    tail_position: tail,
                    speed_mmps: speed,
                    speed_uncertainty_mmps: 500,
                    heading: Direction::Forward,
                    contributing_sources: vec![PositionSource::Gnss, PositionSource::Odometry],
                    onboard_time_ns: 100,
                    pack_soc_ppt: 800,
                })
            }),
        (arb_switch_id(), arb_switch_position(), arb_confidence()).prop_map(
            |(switch_id, position, confidence)| {
                EntryPayload::SwitchObservation(SwitchObservation {
                    switch_id,
                    observed_position: position,
                    confidence,
                    observed_at_ns: 1,
                })
            }
        ),
        (arb_switch_id(), arb_switch_position(), arb_entity_id()).prop_map(
            |(switch_id, requested_position, requested_by)| {
                EntryPayload::SwitchCommand(SwitchCommand {
                    switch_id,
                    requested_position,
                    requested_by,
                    lock_until: None,
                })
            }
        ),
        (arb_route_id(), arb_train_id()).prop_map(|(route_id, train_id)| {
            EntryPayload::RouteGrant(RouteGrant {
                route_id,
                train_id,
                locked_switches: vec![],
                locked_sections: vec![SectionId::new(1), SectionId::new(2)],
                expires_at_ns: 1_000,
            })
        }),
        (arb_route_id()).prop_map(|route_id| {
            EntryPayload::RouteRelease(RouteRelease {
                route_id,
                reason: "test".to_string(),
            })
        }),
        (arb_route_id(), arb_entity_id(), arb_position(), arb_position(), arb_train_id())
            .prop_map(|(route_id, requested_by, entry_point, exit_point, train_id)| {
                EntryPayload::RouteRequest(RouteRequest {
                    route_id,
                    requested_by,
                    entry_point: entry_point.track_ref,
                    exit_point: exit_point.track_ref,
                    train_id: Some(train_id),
                })
            }),
        (arb_restriction_reason(), arb_entity_id()).prop_map(|(reason, issued_by)| {
            EntryPayload::SpeedRestriction(SpeedRestriction {
                section: SectionId::new(1),
                from_offset_mm: 0,
                to_offset_mm: 10_000,
                max_speed_mmps: 10_000,
                reason,
                effective_from_ns: 0,
                effective_until_ns: None,
                issued_by,
            })
        }),
        (arb_entity_id(), arb_health(), 0u64..1000).prop_map(
            |(from_entity, health, seq)| EntryPayload::Heartbeat(Heartbeat {
                from_entity,
                health,
                monotonic_seq: seq,
            })
        ),
        arb_train_id().prop_map(|train_id| {
            EntryPayload::TrainDeparture(TrainDeparture {
                train_id,
                handed_off_to: Some(RegionId::new(1)),
                handoff_time_ns: 0,
            })
        }),
        (arb_entity_id()).prop_map(|granted_to| {
            EntryPayload::MaintenanceOverride(MaintenanceOverride {
                section: SectionId::new(1),
                from_offset_mm: 0,
                to_offset_mm: 5_000,
                granted_to,
                granted_until_ns: 1_000,
                rationale: "rescue".to_string(),
            })
        }),
    ]
    .boxed()
}

fn arb_log_prefix(max_len: usize) -> impl Strategy<Value = Vec<Entry>> {
    prop::collection::vec(arb_payload(), 0..max_len)
        .prop_map(|payloads| {
            payloads
                .into_iter()
                .enumerate()
                .map(|(i, payload)| Entry {
                    entry_id: EntryId::new(i as u64 + 1),
                    term: 1,
                    timestamp_ns: (i as u64 + 1) * 100,
                    payload,
                })
                .collect()
        })
}

// ---------------------------------------------------------------------------
// P1 — determinism
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    /// P1: derive_state is a pure function of the log prefix.
    /// Two invocations on the same prefix produce equal states.
    #[test]
    fn derive_state_is_pure(log in arb_log_prefix(40)) {
        let s1 = derive_state(&log);
        let s2 = derive_state(&log);
        prop_assert_eq!(s1, s2);
    }

    /// Composition: batch application equals incremental application.
    #[test]
    fn batch_equals_incremental(log in arb_log_prefix(40)) {
        let batch = derive_state(&log);
        let mut incremental = DerivedState::default();
        for entry in &log {
            incremental.apply(entry);
        }
        prop_assert_eq!(batch, incremental);
    }

    /// Prefix monotonicity: state after `n+1` entries is produced from the
    /// state after `n` entries by applying a single entry. Guards against
    /// subtle apply_entry bugs that only show up mid-sequence.
    #[test]
    fn prefix_extension_is_incremental(log in arb_log_prefix(20)) {
        if log.is_empty() { return Ok(()); }
        for n in 0..log.len() {
            let prefix_before = &log[..n];
            let prefix_after = &log[..=n];
            let state_before = derive_state(prefix_before);
            let state_after_batch = derive_state(prefix_after);
            let mut state_after_incremental = state_before.clone();
            state_after_incremental.apply(&log[n]);
            prop_assert_eq!(state_after_batch, state_after_incremental);
        }
    }

    /// derive_state is total: it never panics, for any input sequence.
    /// Demonstrated by merely running it to completion over random input.
    #[test]
    fn derive_state_is_total(log in arb_log_prefix(50)) {
        let _ = derive_state(&log);
    }
}
