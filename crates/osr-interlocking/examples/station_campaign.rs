//! Actual local interlocking -> station demand replay; all detector assertions
//! are supplied by an offline numerical plant, never physical authority.
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId, TrainId};
use osr_interlocking::{
    resource_log::{ResourceEvent, ResourceLedger},
    resources::*,
    station::*,
};
use osr_maglev_control::station::{
    evaluate_station, StationFrame, StationMode, StationParams, StationState,
};
use serde::Deserialize;
use serde_json::json;
use std::io::{self, Read};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Motor {
    zone_start_mm: i64,
    zone_end_mm: i64,
    train_envelope_mm: u32,
    pole_pitch_um: u32,
    force_density_n_m: f64,
    force_constant_n_a: f64,
    resistance_ohm: f64,
    inductance_h: f64,
    flux_linkage_wb: f64,
    maximum_current_a: f64,
    maximum_voltage_v: f64,
    maximum_copper_loss_w: f64,
    maximum_tick_ns: u64,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Frame {
    now_ns: u64,
    observed_ns: u64,
    sequence: u64,
    zone: u32,
    mode: u8,
    position_mm: i64,
    velocity_mmps: i32,
    overlap_mm: u32,
    force_n: f64,
    position_uncertainty_um: u32,
    timestamp_uncertainty_ns: u32,
    receiver_healthy: bool,
    sensors_healthy: bool,
    drive_healthy: bool,
    resistor_ready: bool,
    outgoing: bool,
    full_tail_clear: bool,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    model: RailwayModel,
    configuration: [u8; 32],
    motor: Motor,
    frames: Vec<Frame>,
    initial_commit: bool,
}
const OWNER: Owner = Owner {
    train: TrainId(101),
    session: 1,
};
const BASE: u64 = 1_000_000_000;
fn proof(id: u8, sequence: u64, now: u64) -> ProtectionProof {
    ProtectionProof {
        resource: ResourceId(id),
        controller: ControllerId(900),
        epoch: 1,
        sequence,
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
fn ready(id: u64, sequence: u64, now: u64, cfg: [u8; 32]) -> StationReadiness {
    StationReadiness {
        launch_id: id,
        configuration: cfg,
        owner: OWNER,
        epoch: 1,
        sequence,
        observed_ns: now,
        receive_brake_ready: true,
        arrival_reserve_ready: true,
        doors_closed: true,
        services_reserve_ready: true,
        route_ready: true,
        train_healthy: true,
    }
}
fn launch(
    ledger: &mut ResourceLedger,
    id: u64,
    now: u64,
    cfg: [u8; 32],
    length: u32,
    commit: bool,
) {
    let base = if id == 1 { 0 } else { 3 };
    // Refresh every reservation proof immediately before preparation.
    for resource in base..base + 3 {
        ledger
            .apply(&ResourceEvent::LocalProof(proof(resource, 2, now)), now)
            .unwrap();
    }
    let request = StationLaunchRequest {
        id,
        configuration: cfg,
        owner: OWNER,
        route: RouteId(1),
        direction: Direction::Forward,
        corridor: ResourceId(base),
        receiving_berth: ResourceId(base + 1),
        overlap: ResourceId(base + 2),
        consist_length_mm: length,
        permission_expires_ns: now + LEASE_NS,
    };
    ledger
        .apply(
            &ResourceEvent::PrepareStationLaunch {
                request,
                readiness: ready(id, 1, now, cfg),
            },
            now,
        )
        .unwrap();
    if commit {
        ledger
            .apply(
                &ResourceEvent::CommitStationLaunch {
                    id,
                    readiness: ready(id, 2, now + 1, cfg),
                },
                now + 1,
            )
            .unwrap();
    }
}
fn main() {
    let mut raw = String::new();
    io::stdin()
        .take(32 * 1024 * 1024 + 1)
        .read_to_string(&mut raw)
        .unwrap();
    assert!(raw.len() <= 32 * 1024 * 1024, "bounded input required");
    let input: Input = serde_json::from_str(&raw).unwrap();
    assert!(!input.frames.is_empty() && input.frames.len() <= 30000);
    let m = &input.motor;
    let cfg = input.configuration;
    let mut ledger = ResourceLedger::new(input.model, cfg, BASE).unwrap();
    ledger
        .apply(
            &ResourceEvent::Integrity {
                owner: OWNER,
                proved: true,
            },
            BASE,
        )
        .unwrap();
    for id in 0..6 {
        ledger
            .apply(&ResourceEvent::LocalProof(proof(id, 1, BASE)), BASE)
            .unwrap();
        ledger
            .apply(&ResourceEvent::Clear(ResourceId(id)), BASE)
            .unwrap();
    }
    launch(
        &mut ledger,
        1,
        BASE + 1,
        cfg,
        m.train_envelope_mm,
        input.initial_commit,
    );
    let mut states = [StationState::default(); 2];
    let mut outgoing = false;
    let mut cleared = false;
    let mut fault_recorded = false;
    let mut observations = Vec::with_capacity(input.frames.len());
    for f in input.frames {
        assert!((1..=2).contains(&f.zone) && f.now_ns > BASE + 2);
        if f.outgoing && !outgoing {
            launch(&mut ledger, 2, f.now_ns - 2, cfg, m.train_envelope_mm, true);
            outgoing = true;
        }
        ledger.controller.advance_time(f.now_ns).unwrap();
        let id = if f.outgoing { 2 } else { 1 };
        let protected = ledger.station_arrival_protected(id);
        let committed = ledger
            .station_launch(id)
            .is_some_and(|record| record.committed_ns.is_some());
        let p = StationParams {
            configuration: cfg,
            zone_id: f.zone,
            zone_start_mm: m.zone_start_mm,
            zone_end_mm: m.zone_end_mm,
            train_envelope_mm: m.train_envelope_mm,
            pole_pitch_um: m.pole_pitch_um,
            maximum_age_ns: 100000,
            maximum_tick_ns: m.maximum_tick_ns,
            maximum_phase_uncertainty_mdeg: 5000,
            force_density_n_per_envelope_m: m.force_density_n_m,
            force_constant_n_per_a: m.force_constant_n_a,
            resistance_ohm: m.resistance_ohm,
            inductance_h: m.inductance_h,
            flux_linkage_wb: m.flux_linkage_wb,
            maximum_current_a: m.maximum_current_a,
            maximum_phase_voltage_v: m.maximum_voltage_v,
            maximum_copper_loss_w: m.maximum_copper_loss_w,
        };
        let frame = StationFrame {
            configuration: cfg,
            zone_id: f.zone,
            sequence: f.sequence,
            observed_ns: f.observed_ns,
            position_mm: f.position_mm,
            velocity_mmps: f.velocity_mmps,
            position_uncertainty_um: f.position_uncertainty_um,
            timestamp_uncertainty_ns: f.timestamp_uncertainty_ns,
            phase_offset_mdeg: 0,
            overlap_mm: f.overlap_mm,
            force_demand_n: f.force_n,
            mode: match f.mode {
                0 => StationMode::Launch,
                1 => StationMode::Coast,
                2 => StationMode::Receive,
                3 => StationMode::Secured,
                4 => StationMode::Berth,
                _ => panic!("unknown mode"),
            },
            launch_committed: committed,
            arrival_resources_protected: protected,
            receiver_healthy: f.receiver_healthy,
            sensors_healthy: f.sensors_healthy,
            drive_healthy: f.drive_healthy,
            brake_resistor_ready: f.resistor_ready,
        };
        let index = usize::try_from(f.zone - 1).unwrap();
        let output = evaluate_station(states[index], frame, f.now_ns, p);
        states[index] = output.state;
        if output.independent_recovery_required && !fault_recorded {
            ledger
                .apply(
                    &ResourceEvent::HoldStationLaunch(StationFault {
                        launch_id: id,
                        configuration: cfg,
                        owner: OWNER,
                        epoch: 1,
                        sequence: 1,
                        observed_ns: f.now_ns,
                        reason: StationFaultReason::ReceiverUnavailable,
                    }),
                    f.now_ns,
                )
                .unwrap();
            fault_recorded = true;
        }
        if f.full_tail_clear && !cleared {
            assert!(
                outgoing && !fault_recorded,
                "fault/absent departure cannot clear incoming resources"
            );
            // Evidence is supplied by a declared virtual full-consist detector.
            let clearance = StationClearance {
                launch_id: 1,
                configuration: cfg,
                owner: OWNER,
                epoch: 1,
                sequence: 1,
                observed_ns: f.now_ns,
                consist_length_mm: m.train_envelope_mm,
                tail_integrity_proved: true,
                all_cars_accounted_for: true,
                proofs: core::array::from_fn(|i| proof(i as u8, 3, f.now_ns)),
            };
            ledger
                .apply(
                    &ResourceEvent::ClearStationLaunch(Box::new(clearance)),
                    f.now_ns,
                )
                .unwrap();
            cleared = true;
        }
        let velocity = f64::from(f.velocity_mmps) / 1000.;
        let emf = m.flux_linkage_wb * core::f64::consts::TAU * velocity
            / (2. * f64::from(m.pole_pitch_um) * 1e-6);
        observations.push(json!({"sequence":f.sequence,"now_ns":f.now_ns,"mode":f.mode,
            "feasible":output.study_command_feasible,"fault":format!("{:?}",output.state.latched_fault),
            "recovery_required":output.independent_recovery_required,"force_n":output.study_force_n,
            "current_a":output.study_current_a,"voltage_bound_v":output.study_voltage_bound_v,
            "copper_loss_w":output.study_copper_loss_w,"mechanical_power_w":output.study_force_n*velocity,
            "airgap_electrical_power_w":emf*output.study_current_a,
            "incoming_protected":ledger.station_arrival_protected(1),
            "outgoing_protected":ledger.station_arrival_protected(2),"incoming_cleared":cleared,
            "support_shutdown_requested":output.onboard_support_shutdown_requested,
            "physical_output_authorised":output.physical_output_authorised}));
    }
    println!(
        "{}",
        json!({"schema":"osr-integrated-station-replay/1","observations":observations,
        "incoming_cleared":cleared,"outgoing_committed":outgoing,"fault_held":fault_recorded,
        "configuration":cfg,"physical_output_authorised":false,
        "detector_evidence":"synthetic full-consist numerical position, not authenticated physical observations"})
    );
}
