use osr_core::{
    deployment::{configuration_hash, FrozenRailway},
    resources::*,
    *,
};
use osr_interlocking::{
    resource_log::{ResourceEvent, ResourceLedger},
    resources::*,
    *,
};
fn fixture() -> (DerivedState, Network) {
    let bytes = include_bytes!("../../../engineering/assurance/tacs/railway-model.json");
    let f = FrozenRailway::load(bytes, configuration_hash(bytes)).unwrap();
    let mut state = DerivedState::default();
    let mut ledger = ResourceLedger::new(f.model().clone(), f.configuration(), 100).unwrap();
    let owner = f.train_config(TrainId(101)).unwrap().owner;
    ledger
        .apply(
            &ResourceEvent::Integrity {
                owner,
                proved: true,
            },
            100,
        )
        .unwrap();
    for r in 0..7 {
        let p = ProtectionProof {
            resource: ResourceId(r),
            controller: ControllerId(900),
            epoch: 1,
            sequence: 1,
            observed_ns: 100,
            clear: true,
            clearance_safe: true,
            cleared_owner: None,
            occupant: None,
            occupancy_integrity_proved: true,
            points_locked_and_proved: true,
            proved_route: Some(RouteId(1)),
            restriction: Restriction::Open,
        };
        ledger.apply(&ResourceEvent::LocalProof(p), 100).unwrap();
        ledger
            .apply(&ResourceEvent::Clear(ResourceId(r)), 100)
            .unwrap();
        if [0, 4].contains(&r) {
            ledger
                .apply(
                    &ResourceEvent::Reserve {
                        owner,
                        resource: ResourceId(r),
                        route: RouteId(1),
                        direction: Direction::Forward,
                    },
                    100,
                )
                .unwrap();
        }
    }
    ledger
        .apply(
            &ResourceEvent::Reserve {
                owner,
                resource: ResourceId(2),
                route: RouteId(1),
                direction: Direction::Forward,
            },
            100,
        )
        .unwrap();
    state.resources = Some(ledger);
    let head = Position {
        track_ref: TrackRef {
            section: SectionId(100),
            offset_mm: 50000,
            direction: Direction::Forward,
        },
        uncertainty_mm: 100,
    };
    let mut consist = ConsistDescriptor::reference_3car();
    consist.length_mm = 10000;
    state.apply(&Entry {
        entry_id: EntryId(1),
        term: 1,
        timestamp_ns: 100,
        payload: EntryPayload::TrainRegistration(TrainRegistration {
            train_id: TrainId(101),
            consist,
            initial_position: head,
        }),
    });
    state.apply(&Entry {
        entry_id: EntryId(2),
        term: 1,
        timestamp_ns: 100,
        payload: EntryPayload::TrainPositionReport(TrainPositionReport {
            train_id: TrainId(101),
            head_position: head,
            tail_position: Position {
                track_ref: TrackRef {
                    offset_mm: 40000,
                    ..head.track_ref
                },
                ..head
            },
            speed_mmps: 1000,
            speed_uncertainty_mmps: 10,
            heading: Direction::Forward,
            contributing_sources: vec![PositionSource::Odometry],
            onboard_time_ns: 100,
            pack_soc_ppt: 800,
        }),
    });
    for r in [0, 2, 4] {
        state.apply(&Entry {
            entry_id: EntryId(3 + r),
            term: 1,
            timestamp_ns: 100,
            payload: EntryPayload::SectionIntrusion(SectionIntrusion {
                section: SectionId(100 + r),
                state: IntrusionState::Clear,
                issued_by: EntityId(900),
                observed_at_ns: 100,
            }),
        });
    }
    (state, osr_runtime::network(&f).unwrap())
}
#[test]
fn recalculation_cannot_refresh_original_evidence_and_integrity_loss_cannot_extend() {
    let (mut s, n) = fixture();
    let a = compute_self_ma_from_state(TrainId(101), &s, &n, 101, Some(EntryId(7)));
    assert_eq!(a.end.section, SectionId(104));
    assert_eq!(a.valid_until_ns, 1_000_000_100);
    let later = compute_self_ma_from_state(TrainId(101), &s, &n, 500_000_000, Some(EntryId(7)));
    assert_eq!(later.valid_until_ns, a.valid_until_ns);
    let stale = compute_self_ma_from_state(TrainId(101), &s, &n, 1_000_000_101, Some(EntryId(7)));
    assert_eq!(stale.end.section, SectionId(100));
    assert_eq!(stale.end.offset_mm, 50000);
    s.resources
        .as_mut()
        .unwrap()
        .integrity
        .insert(TrainId(101), false);
    let lost = compute_self_ma_from_state(TrainId(101), &s, &n, 101, Some(EntryId(7)));
    assert_eq!(lost.end, stale.end);
}
#[test]
fn civil_speed_proof_reaches_the_existing_atp_restriction_contract() {
    let (mut s, n) = fixture();
    s.resources.as_mut().unwrap().proofs[2]
        .as_mut()
        .unwrap()
        .restriction = Restriction::Speed(2000);
    let a = compute_self_ma_from_state(TrainId(101), &s, &n, 101, Some(EntryId(7)));
    assert!(a
        .applicable_restrictions
        .iter()
        .any(|r| r.section == SectionId(102) && r.max_speed_mmps == 2000));
}
