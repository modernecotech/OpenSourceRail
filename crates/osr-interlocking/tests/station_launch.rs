//! Executable local launch/failure/restart studies; external detector and brake
//! assertions here are synthetic, not physical qualification evidence.
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId, TrainId};
use osr_interlocking::{
    resource_log::{ResourceEvent, ResourceLedger},
    resources::*,
    station::*,
};
use serde_json::json;

const CFG: ConfigurationId = [7; 32];
const OWNER: Owner = Owner {
    train: TrainId(101),
    session: 1,
};
const NOW: u64 = 1_000_000_000;

fn model() -> RailwayModel {
    let resources:Vec<_>=(0..3).map(|i|json!({"id":i,"section":100+i,"asset_id":format!("resource-{i}"),
        "kind":if i==1 {"platform"}else{"track"},"controller":900,"conflicts":[i],"point_asset_id":null,
        "clearance_basis":"synthetic full-consist clearance; not a detector design"})).collect();
    let mut participants: Vec<_> = (1..=3)
        .map(|i| {
            json!({"entity":i,"role":"Voter","session":1,
        "public_key":vec![i;32],"revoked":false,"resources":[]})
        })
        .collect();
    participants.push(json!({"entity":101,"role":"Train","session":1,"public_key":vec![5;32],"revoked":false,"resources":[]}));
    serde_json::from_value(json!({"schema":"osr-tacs-railway/2","revision":"station-local-study-1",
        "approval_state":"prototype-unapproved","runtime":{"voters":[1,2,3],"participants":participants,
            "designed_revision":"station-local-study-1","installed_state":"not-installed","approved_operating_profile":"prototype-unapproved","clock_error_ns":0},
        "resources":resources,
        "routes":[{"id":1,"asset_id":"route-1","direction":"Forward","leader_required":false,"operating_scope":"local three-resource offline study",
            "segments":[{"resource":0,"start_mm":0,"end_mm":1_000_000,"speed_limit_mmps":22222,"downhill_permille":0},
                {"resource":1,"start_mm":1_000_000,"end_mm":1_120_000,"speed_limit_mmps":22222,"downhill_permille":0},
                {"resource":2,"start_mm":1_120_000,"end_mm":1_195_000,"speed_limit_mmps":22222,"downhill_permille":0}],
            "stopping_locations":[{"asset_id":"berth-1","at_mm":1_050_000,"platform":1,"charger_asset_id":"services-charger-1","minimum_departure_energy_wh":10000}]}],
        "trains":[{"asset_id":"train-101","config":{"owner":{"train":101,"session":1},"configuration":vec![7;32],"length_mm":104500,
            "minimum_deceleration_mmps2":800,"reaction_time_ms":100,"stop_margin_mm":1000,"maximum_position_uncertainty_mm":10},
            "integrity_arrangement":"synthetic independent full-tail assertion","braking_evidence":"unqualified study","permitted_route":1}],
        "controllers":[{"id":900,"asset_id":"local-controller-900","startup_epoch":1,"restart_reconciliation":"retain locks and require positive clearance"}],
        "protected_work_resources":[],"maintenance_procedure":"controlled offline study"})).unwrap()
}

fn proof(id: u8, seq: u64, epoch: u64, now: u64) -> ProtectionProof {
    ProtectionProof {
        resource: ResourceId(id),
        controller: ControllerId(900),
        epoch,
        sequence: seq,
        observed_ns: now,
        clear: true,
        clearance_safe: true,
        cleared_owner: Some(OWNER),
        occupant: None,
        occupancy_integrity_proved: true,
        points_locked_and_proved: false,
        proved_route: None,
        restriction: Restriction::Open,
    }
}
fn request() -> StationLaunchRequest {
    StationLaunchRequest {
        id: 1,
        configuration: CFG,
        owner: OWNER,
        route: RouteId(1),
        direction: Direction::Forward,
        corridor: ResourceId(0),
        receiving_berth: ResourceId(1),
        overlap: ResourceId(2),
        consist_length_mm: 104500,
        permission_expires_ns: NOW + LEASE_NS,
    }
}
fn ready(seq: u64, now: u64) -> StationReadiness {
    StationReadiness {
        launch_id: 1,
        configuration: CFG,
        owner: OWNER,
        epoch: 1,
        sequence: seq,
        observed_ns: now,
        receive_brake_ready: true,
        arrival_reserve_ready: true,
        doors_closed: true,
        services_reserve_ready: true,
        route_ready: true,
        train_healthy: true,
    }
}
fn ledger() -> ResourceLedger {
    reconciled_model(model())
}
fn reconciled_model(model: RailwayModel) -> ResourceLedger {
    let mut value = ResourceLedger::new(model, CFG, NOW).unwrap();
    value
        .apply(
            &ResourceEvent::Integrity {
                owner: OWNER,
                proved: true,
            },
            NOW,
        )
        .unwrap();
    for i in 0..3 {
        let mut p = proof(i, 1, 1, NOW);
        if value.model.resources[usize::from(i)]
            .point_asset_id
            .is_some()
        {
            p.points_locked_and_proved = true;
            p.proved_route = Some(RouteId(1));
        }
        value.apply(&ResourceEvent::LocalProof(p), NOW).unwrap();
        value
            .apply(&ResourceEvent::Clear(ResourceId(i)), NOW)
            .unwrap();
    }
    value
}
fn prepare(value: &mut ResourceLedger) {
    value
        .apply(
            &ResourceEvent::PrepareStationLaunch {
                request: request(),
                readiness: ready(1, NOW + 1),
            },
            NOW + 1,
        )
        .unwrap();
}
fn commit(value: &mut ResourceLedger) {
    prepare(value);
    value
        .apply(
            &ResourceEvent::CommitStationLaunch {
                id: 1,
                readiness: ready(2, NOW + 2),
            },
            NOW + 2,
        )
        .unwrap();
}
fn clearance(epoch: u64, now: u64) -> StationClearance {
    StationClearance {
        launch_id: 1,
        configuration: CFG,
        owner: OWNER,
        epoch,
        sequence: 1,
        observed_ns: now,
        consist_length_mm: 104500,
        tail_integrity_proved: true,
        all_cars_accounted_for: true,
        proofs: core::array::from_fn(|i| proof(i as u8, 2, epoch, now)),
    }
}

#[test]
fn preparation_is_atomic_and_an_unavailable_receiver_does_not_allocate() {
    let mut value = ledger();
    value
        .apply(&ResourceEvent::Block(ResourceId(2)), NOW)
        .unwrap();
    let before = value.controller.records().to_vec();
    assert!(value
        .apply(
            &ResourceEvent::PrepareStationLaunch {
                request: request(),
                readiness: ready(1, NOW)
            },
            NOW
        )
        .is_err());
    assert_eq!(before, value.controller.records());
    assert!(value.station_launches.is_empty());
    let mut value = ledger();
    let mut readiness = ready(1, NOW);
    readiness.receive_brake_ready = false;
    assert!(value
        .apply(
            &ResourceEvent::PrepareStationLaunch {
                request: request(),
                readiness
            },
            NOW
        )
        .is_err());
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Available));
}

#[test]
fn expiry_before_commit_prevents_departure_without_releasing_ownership() {
    let mut value = ledger();
    prepare(&mut value);
    let now = request().permission_expires_ns;
    assert!(value
        .apply(
            &ResourceEvent::CommitStationLaunch {
                id: 1,
                readiness: ready(2, now)
            },
            now
        )
        .is_err());
    assert!(!value.station_arrival_protected(1));
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.grant.is_some() && r.phase != Phase::Available));
}

#[test]
fn commit_survives_expired_permissions_and_duplicate_events_are_idempotent() {
    let mut value = ledger();
    commit(&mut value);
    value
        .apply(
            &ResourceEvent::PrepareStationLaunch {
                request: request(),
                readiness: ready(1, NOW + 1),
            },
            NOW + 3,
        )
        .unwrap();
    value
        .apply(
            &ResourceEvent::CommitStationLaunch {
                id: 1,
                readiness: ready(2, NOW + 2),
            },
            NOW + 3,
        )
        .unwrap();
    assert_eq!(value.station_launches.len(), 1);
    value.controller.advance_time(NOW + 90_000_000_000).unwrap();
    assert!(value.station_arrival_protected(1));
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Committed && r.grant.unwrap().owner == OWNER));
    // Old moving-authority semantics are not silently widened by this protocol.
    assert!(!value.permits(osr_core::SectionId(100), OWNER.train, NOW + 90_000_000_000));
}

#[test]
fn receiver_fault_after_commit_holds_the_entire_arrival_path() {
    let mut value = ledger();
    commit(&mut value);
    let fault = StationFault {
        launch_id: 1,
        configuration: CFG,
        owner: OWNER,
        epoch: 1,
        sequence: 1,
        observed_ns: NOW + 3,
        reason: StationFaultReason::ReceiverUnavailable,
    };
    value
        .apply(&ResourceEvent::HoldStationLaunch(fault), NOW + 3)
        .unwrap();
    value
        .apply(&ResourceEvent::HoldStationLaunch(fault), NOW + 3)
        .unwrap();
    assert_eq!(value.station_launch(1).unwrap().phase, LaunchPhase::Held);
    assert!(value.station_arrival_protected(1));
    assert!(value
        .apply(&ResourceEvent::Clear(ResourceId(0)), NOW + 4)
        .is_err());
    let g = value.controller.records()[0].grant.unwrap();
    assert!(value.apply(&ResourceEvent::Withdraw(g), NOW + 4).is_err());
    assert!(value.controller.records().iter().all(|r| r.grant.is_some()));
}

#[test]
fn missing_tail_integrity_and_partial_or_replayed_proofs_cannot_clear() {
    let mut value = ledger();
    commit(&mut value);
    for bad in 0..5 {
        let mut evidence = clearance(1, NOW + 3);
        match bad {
            0 => evidence.all_cars_accounted_for = false,
            1 => evidence.tail_integrity_proved = false,
            2 => evidence.consist_length_mm -= 17000,
            3 => evidence.proofs[2].sequence = 1,
            _ => evidence.proofs[2].clearance_safe = false,
        }
        assert!(value
            .apply(
                &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
                NOW + 3
            )
            .is_err());
        assert!(value.station_arrival_protected(1));
        assert!(value
            .controller
            .records()
            .iter()
            .all(|r| r.phase == Phase::Committed));
    }
    let evidence = clearance(1, NOW + 4);
    value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 4,
        )
        .unwrap();
    value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 4,
        )
        .unwrap();
    assert!(!value.station_arrival_protected(1));
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Available));
}

#[test]
fn delayed_prelaunch_clearance_cannot_release_committed_arrival() {
    let mut value = ledger();
    commit(&mut value);
    // Every proof has a valid newer sequence and remains within the freshness
    // window, but its observation predates the committed launch at NOW+2.
    let mut evidence = clearance(1, NOW + 1);
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 3
        )
        .is_err());
    evidence.observed_ns = NOW + 3; // a fresh envelope cannot refresh old observations
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 3
        )
        .is_err());
    evidence = clearance(1, NOW + 3);
    evidence.observed_ns = NOW + 1;
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 3
        )
        .is_err());
    assert!(value.station_arrival_protected(1));
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Committed));
    value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(clearance(1, NOW + 4))),
            NOW + 4,
        )
        .unwrap();
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Available));
}

#[test]
fn newer_occupancy_or_conflicting_proofs_disqualify_delayed_clearance() {
    let mut value = ledger();
    commit(&mut value);
    let mut latest = proof(0, 3, 1, NOW + 4);
    latest.clear = false;
    latest.occupant = Some(Owner {
        train: TrainId(102),
        session: 1,
    });
    value
        .apply(&ResourceEvent::LocalProof(latest), NOW + 4)
        .unwrap();
    assert_eq!(value.station_launch(1).unwrap().phase, LaunchPhase::Held);
    let mut evidence = clearance(1, NOW + 3); // after commit, before the new occupancy
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 5
        )
        .is_err());
    evidence.proofs[0].sequence = latest.sequence;
    evidence.proofs[0].observed_ns = latest.observed_ns; // same sequence cannot change occupied to clear
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 5
        )
        .is_err());
    evidence.proofs[0].sequence = 4;
    evidence.proofs[0].observed_ns = NOW + 3;
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(evidence)),
            NOW + 5
        )
        .is_err());
    assert!(value.station_arrival_protected(1));
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Committed));
    let mut current = clearance(1, NOW + 6);
    current.proofs[0].sequence = 4;
    value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(current)),
            NOW + 6,
        )
        .unwrap();
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Available));
}

#[test]
fn changed_point_route_is_held_and_cannot_commit_station_launch() {
    let with_points = || {
        let mut m = model();
        m.resources[0].kind = "junction".into();
        m.resources[0].point_asset_id = Some("local-point".into());
        reconciled_model(m)
    };
    let mut value = with_points();
    prepare(&mut value);
    let mut wrong = proof(0, 2, 1, NOW + 2);
    wrong.points_locked_and_proved = true;
    wrong.proved_route = Some(RouteId(2));
    value
        .apply(&ResourceEvent::LocalProof(wrong), NOW + 2)
        .unwrap();
    assert_eq!(value.station_launch(1).unwrap().phase, LaunchPhase::Held);
    assert!(value
        .apply(
            &ResourceEvent::CommitStationLaunch {
                id: 1,
                readiness: ready(2, NOW + 3)
            },
            NOW + 3
        )
        .is_err());
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Reserved));
    // Independently recheck the protection view at commit, even without a
    // preceding hold transition (fault-injected reconstructed snapshot).
    let mut value = with_points();
    prepare(&mut value);
    value.proofs[0] = Some(wrong);
    assert!(value
        .apply(
            &ResourceEvent::CommitStationLaunch {
                id: 1,
                readiness: ready(2, NOW + 3)
            },
            NOW + 3
        )
        .is_err());
    assert_eq!(
        value.station_launch(1).unwrap().phase,
        LaunchPhase::Prepared
    );
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Reserved));
}

#[test]
fn serialized_restart_retains_bundle_and_requires_new_epoch_complete_clearance() {
    let mut value = ledger();
    commit(&mut value);
    let retained = serde_json::to_vec(&value).unwrap();
    let mut value: ResourceLedger = serde_json::from_slice(&retained).unwrap();
    value.apply(&ResourceEvent::Restart(2), NOW + 3).unwrap();
    assert!(value.station_arrival_protected(1));
    assert_eq!(value.station_launch(1).unwrap().phase, LaunchPhase::Held);
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Unknown && r.grant.is_some()));
    let now = NOW + 3 + LEASE_NS + CLOCK_SKEW_NS;
    assert!(value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(clearance(1, now))),
            now
        )
        .is_err());
    value
        .apply(
            &ResourceEvent::ClearStationLaunch(Box::new(clearance(2, now))),
            now,
        )
        .unwrap();
    assert!(value
        .controller
        .records()
        .iter()
        .all(|r| r.phase == Phase::Available));
}

#[test]
fn wrong_consist_or_configuration_or_duplicate_bundle_is_rejected() {
    for bad in 0..4 {
        let mut value = ledger();
        let mut r = request();
        match bad {
            0 => r.configuration = [8; 32],
            1 => r.consist_length_mm = 102000,
            2 => r.overlap = r.corridor,
            _ => r.id = 0,
        }
        assert!(value
            .apply(
                &ResourceEvent::PrepareStationLaunch {
                    request: r,
                    readiness: ready(1, NOW)
                },
                NOW
            )
            .is_err());
        assert!(value
            .controller
            .records()
            .iter()
            .all(|v| v.phase == Phase::Available));
    }
}

#[test]
fn committed_log_replay_and_incremental_fold_preserve_the_same_launch() {
    use osr_interlocking::{derive_state, DerivedState, Entry, EntryPayload};
    let mut events = vec![
        ResourceEvent::Bootstrap {
            configuration: CFG,
            model: Box::new(model()),
        },
        ResourceEvent::Integrity {
            owner: OWNER,
            proved: true,
        },
    ];
    for i in 0..3 {
        events.push(ResourceEvent::LocalProof(proof(i, 1, 1, NOW)));
        events.push(ResourceEvent::Clear(ResourceId(i)));
    }
    events.push(ResourceEvent::PrepareStationLaunch {
        request: request(),
        readiness: ready(1, NOW + 8),
    });
    events.push(ResourceEvent::CommitStationLaunch {
        id: 1,
        readiness: ready(2, NOW + 9),
    });
    events.push(ResourceEvent::CommitStationLaunch {
        id: 1,
        readiness: ready(2, NOW + 9),
    });
    events.push(ResourceEvent::Clear(ResourceId(0))); // rejected individual bypass
    events.push(ResourceEvent::Restart(2));
    let entries: Vec<_> = events
        .into_iter()
        .enumerate()
        .map(|(i, event)| Entry {
            entry_id: osr_core::EntryId(i as u64 + 1),
            term: 1,
            timestamp_ns: NOW + i as u64,
            payload: EntryPayload::ResourceControl(event),
        })
        .collect();
    let bytes = serde_json::to_vec(&entries).unwrap();
    let retained: Vec<Entry> = serde_json::from_slice(&bytes).unwrap();
    let batch = derive_state(&retained);
    let mut incremental = DerivedState::default();
    for entry in &retained {
        incremental.apply(entry);
    }
    assert_eq!(batch, incremental);
    let ledger = batch.resources.unwrap();
    assert_eq!(ledger.rejected_transitions, 1);
    assert_eq!(ledger.station_launches.len(), 1);
    assert_eq!(ledger.station_launch(1).unwrap().phase, LaunchPhase::Held);
    assert!(ledger.station_arrival_protected(1));
}

#[test]
fn conflicting_detector_or_lost_integrity_holds_without_releasing() {
    let mut value = ledger();
    commit(&mut value);
    let mut conflict = proof(1, 2, 1, NOW + 3);
    conflict.clear = false;
    conflict.occupant = Some(Owner {
        train: TrainId(102),
        session: 1,
    });
    value
        .apply(&ResourceEvent::LocalProof(conflict), NOW + 3)
        .unwrap();
    assert_eq!(value.station_launch(1).unwrap().phase, LaunchPhase::Held);
    assert!(value.station_arrival_protected(1));
    let mut value = ledger();
    commit(&mut value);
    value
        .apply(
            &ResourceEvent::Integrity {
                owner: OWNER,
                proved: false,
            },
            NOW + 3,
        )
        .unwrap();
    assert_eq!(value.station_launch(1).unwrap().phase, LaunchPhase::Held);
    assert!(value.station_arrival_protected(1));
}

#[test]
fn this_prototype_rejects_cross_controller_atomic_launch_domains() {
    let mut m = model();
    m.controllers
        .push(osr_core::deployment::ControllerDefinition {
            id: ControllerId(901),
            asset_id: "other-domain".into(),
            startup_epoch: 1,
            restart_reconciliation: "external protocol required".into(),
        });
    assert!(ResourceLedger::new(m, CFG, NOW).is_err());
    assert_eq!(MAX_RESOURCES, 32);
}
