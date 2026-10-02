use osr_consensus::disk::DiskJournal;
use osr_core::{
    deployment::{configuration_hash, FrozenRailway},
    resources::*,
    EntityId, TrainId,
};
use osr_interlocking::{resource_log::ResourceEvent, Entry, EntryPayload};
use osr_proto::RuntimeKind;
use osr_runtime::{raft_config, Channel};
fn frozen() -> FrozenRailway {
    let b = include_bytes!("../../../engineering/assurance/tacs/railway-model.json");
    FrozenRailway::load(b, configuration_hash(b)).unwrap()
}
#[test]
fn unknown_version_or_mutated_startup_cannot_interoperate() {
    let b = include_bytes!("../../../engineering/assurance/tacs/railway-model.json");
    let mut model: serde_json::Value = serde_json::from_slice(b).unwrap();
    model["schema"] = "osr-tacs-railway/999".into();
    let changed = serde_json::to_vec(&model).unwrap();
    assert!(FrozenRailway::load(&changed, configuration_hash(&changed)).is_err());
    let f = frozen();
    let mut deployment = f.deployment();
    deployment.train_startup[0].config.length_mm += 1;
    assert!(FrozenRailway::load_deployment(b, &serde_json::to_vec(&deployment).unwrap()).is_err());
    assert!(f.permit_operational_deployment().is_err());
}
#[test]
fn signed_packets_are_role_scoped_fresh_and_replay_fenced_across_restart() {
    let p = std::env::temp_dir().join(format!("osr-runtime-contracts-{}", std::process::id()));
    std::fs::create_dir_all(&p).unwrap();
    let a = Channel::new(frozen(), EntityId(101)).unwrap();
    let b = Channel::new(frozen(), EntityId(1001)).unwrap();
    let (mut send, node_a) = DiskJournal::open(
        p.join("train"),
        raft_config(&a.frozen, a.entity).unwrap(),
        a.frozen.configuration(),
        1,
    )
    .unwrap();
    let (mut receive, node_b) = DiskJournal::open(
        p.join("voter"),
        raft_config(&b.frozen, b.entity).unwrap(),
        b.frozen.configuration(),
        1,
    )
    .unwrap();
    let signed = a
        .sign(RuntimeKind::Proposal, &vec![1_u8], 10, &mut send)
        .unwrap();
    send.persist(&node_a).unwrap();
    b.receive(&signed, 10, &mut receive).unwrap();
    receive.persist(&node_b).unwrap();
    drop(receive);
    let (mut recovered, _) = DiskJournal::open(
        p.join("voter"),
        raft_config(&b.frozen, b.entity).unwrap(),
        b.frozen.configuration(),
        100,
    )
    .unwrap();
    assert!(b.receive(&signed, 100, &mut recovered).is_err());
    let stale = a
        .sign(RuntimeKind::Proposal, &vec![2_u8], 10, &mut send)
        .unwrap();
    assert!(b.receive(&stale, 2_000_000_000, &mut recovered).is_err());
    let wrong = a
        .sign(RuntimeKind::Raft, &vec![3_u8], 100, &mut send)
        .unwrap();
    assert!(b.receive(&wrong, 100, &mut recovered).is_err());
    let event = Entry {
        entry_id: osr_core::EntryId(1),
        term: 0,
        timestamp_ns: 100,
        payload: EntryPayload::ResourceControl(ResourceEvent::Integrity {
            owner: Owner {
                train: TrainId(102),
                session: 1,
            },
            proved: true,
        }),
    };
    assert!(a.validate_entry(a.entity, &event).is_err());
    drop(send);
    drop(recovered);
    std::fs::remove_dir_all(p).unwrap();
}
#[test]
fn legacy_units_unknown_enums_nonfinite_and_unresolved_identifiers_are_checked() {
    let p = osr_proto::Position {
        track_ref: osr_proto::TrackRef {
            section: osr_proto::SectionId(100),
            offset_mm: 50000,
            direction: osr_proto::Direction::Forward,
        },
        uncertainty_mm: 100,
    };
    let wire = osr_proto::TrainPositionReport {
        train_id: osr_proto::TrainId(101),
        head_position: p,
        tail_position: p,
        speed_mps: 1.25,
        speed_uncertainty_mps: 0.1,
        heading: osr_proto::Direction::Forward,
        contributing_sources: vec![osr_proto::PositionSource::Odometry],
        onboard_time_ns: 100,
        pack_state_of_charge: 0.5,
    };
    let r = osr_runtime::legacy::position_report(wire.clone(), &frozen(), 100).unwrap();
    assert_eq!(r.speed_mmps, 1250);
    assert!(r.speed_uncertainty_mmps >= 100);
    for speed in [f32::NAN, f32::INFINITY, -1.0, 101.0] {
        let mut w = wire.clone();
        w.speed_mps = speed;
        assert!(osr_runtime::legacy::position_report(w, &frozen(), 100).is_err());
    }
    let mut w = wire.clone();
    w.heading = osr_proto::Direction::Unspecified;
    assert!(osr_runtime::legacy::position_report(w, &frozen(), 100).is_err());
    let mut w = wire;
    w.head_position.track_ref.section = osr_proto::SectionId(999);
    assert!(osr_runtime::legacy::position_report(w, &frozen(), 100).is_err());
}
#[test]
fn station_port_inhibits_unsafe_charging_and_cannot_grant_movement_or_cross_asset_scope() {
    use osr_ato::station::{StationInputs, StationPhase};
    use osr_runtime::wayside::{Command, Host};
    let path = std::env::temp_dir().join(format!("osr-station-contract-{}", std::process::id()));
    let mut host = Host::new(
        Channel::new(frozen(), EntityId(901)).unwrap(),
        &path.join("journal"),
        1,
    )
    .unwrap();
    let inputs = StationInputs {
        stopped_and_berthed: true,
        secured: true,
        aligned: false,
        doors_closed_and_locked: false,
        charger_isolated: false,
        connector_clear: false,
        charger_healthy: true,
        charge_complete: false,
        energy_sufficient: false,
        departure_requested: false,
        emergency_departure_requested: false,
        authority_valid: false,
    };
    let denied = host
        .handle(Command::StationIo {
            now: 1,
            platform: ResourceId(0),
            phase: StationPhase::Exchange,
            charge_requested: true,
            inputs,
        })
        .unwrap();
    assert!(!denied.charging_enable);
    assert_eq!(denied.commit_index, 0);
    assert!(denied.packets.is_empty());
    let allowed = host
        .handle(Command::StationIo {
            now: 2,
            platform: ResourceId(0),
            phase: StationPhase::Exchange,
            charge_requested: true,
            inputs: StationInputs {
                aligned: true,
                ..inputs
            },
        })
        .unwrap();
    assert!(allowed.charging_enable);
    assert!(allowed.resources.is_none());
    assert!(host
        .handle(Command::StationIo {
            now: 3,
            platform: ResourceId(4),
            phase: StationPhase::Exchange,
            charge_requested: true,
            inputs
        })
        .is_err());
    drop(host);
    std::fs::remove_dir_all(path).unwrap();
}
