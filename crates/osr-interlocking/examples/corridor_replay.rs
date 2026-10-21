//! Bounded offline fixed-stator corridor replay. Actual local interlocking and
//! station SI kernel; synthetic positions, ideal circuit and no physical I/O.
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
    id: u32,
    start_mm: i64,
    end_mm: i64,
    origin_mm: i64,
    force_density_n_m: f64,
    force_constant_n_a: f64,
    resistance_ohm: f64,
    inductance_h: f64,
    maximum_current_a: f64,
    maximum_voltage_v: f64,
    maximum_copper_loss_w: f64,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Geometry {
    cars: u32,
    body_mm: u32,
    gap_mm: u32,
    band_mm: u32,
    section_mm: u32,
    warmup_ns: u64,
    lookahead_ns: u64,
    maximum_tick_ns: u64,
    downstream_overlap_mm: u32,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Frame {
    now_ns: u64,
    observed_ns: u64,
    sequence: u64,
    active_zone: u32,
    mode: u8,
    position_mm: i64,
    velocity_mmps: i32,
    force_n: f64,
    position_uncertainty_um: u32,
    timestamp_uncertainty_ns: u32,
    receiver_healthy: bool,
    sensors_healthy: bool,
    resistor_ready: bool,
    failed_zone: u32,
    extra_warmup_ns: u64,
    outgoing: bool,
    full_tail_clear: bool,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    model: RailwayModel,
    configuration: [u8; 32],
    geometry: Geometry,
    motors: Vec<Motor>,
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
    for resource in base..base + 3 {
        ledger
            .apply(&ResourceEvent::LocalProof(proof(resource, 2, now)), now)
            .unwrap();
    }
    ledger
        .apply(
            &ResourceEvent::PrepareStationLaunch {
                request: StationLaunchRequest {
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
                },
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
fn overlap(front: i64, start: i64, end: i64, g: &Geometry) -> u32 {
    let offset = i64::from((g.body_mm - g.band_mm) / 2);
    let pitch = i64::from(g.body_mm + g.gap_mm);
    (0..g.cars)
        .map(|i| {
            let right = front - offset - i64::from(i) * pitch;
            let left = right - i64::from(g.band_mm);
            (right.min(end) - left.max(start)).max(0) as u32
        })
        .sum()
}
fn main() {
    let mut raw = String::new();
    io::stdin()
        .take(64 * 1024 * 1024 + 1)
        .read_to_string(&mut raw)
        .unwrap();
    assert!(raw.len() <= 64 * 1024 * 1024);
    let input: Input = serde_json::from_str(&raw).unwrap();
    let g = &input.geometry;
    assert!(
        (1..=12).contains(&g.cars)
            && g.band_mm <= g.body_mm
            && g.section_mm > 0
            && g.section_mm <= 50000
    );
    assert!(
        g.warmup_ns <= 1_000_000_000
            && g.lookahead_ns <= 1_000_000_000
            && g.maximum_tick_ns <= 100_000_000
    );
    assert!(
        (2..=3).contains(&input.motors.len())
            && !input.frames.is_empty()
            && input.frames.len() <= 100000
    );
    let cfg = input.configuration;
    let length = g.cars * g.body_mm + (g.cars - 1) * g.gap_mm;
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
    launch(&mut ledger, 1, BASE + 1, cfg, length, input.initial_commit);
    let mut states = vec![StationState::default(); input.motors.len()];
    let mut arms = vec![vec![None; 64]; input.motors.len()];
    let mut outgoing = false;
    let mut cleared = false;
    let mut fault_held = false;
    let mut first_fault = None;
    let mut observations = Vec::new();
    let mut frames = 0;
    let mut max_current: f64 = 0.;
    let mut max_voltage: f64 = 0.;
    let mut max_loss: f64 = 0.;
    let mut power_error: f64 = 0.;
    let mut switchovers = 0;
    for f in input.frames {
        frames += 1;
        assert!(
            f.now_ns > BASE + 2
                && f.active_zone <= input.motors.len() as u32
                && f.extra_warmup_ns <= 10_000_000_000
        );
        if f.outgoing && !outgoing {
            launch(&mut ledger, 2, f.now_ns - 2, cfg, length, true);
            outgoing = true;
        }
        ledger.controller.advance_time(f.now_ns).unwrap();
        let launch_id = if outgoing { 2 } else { 1 };
        let protected = ledger.station_arrival_protected(launch_id);
        let committed = ledger
            .station_launch(launch_id)
            .is_some_and(|r| r.committed_ns.is_some());
        let mut active_result = None;
        let mut any_fault = false;
        for (index, m) in input.motors.iter().enumerate() {
            assert!(m.id == index as u32 + 1 && m.end_mm > m.start_mm);
            let count = ((m.end_mm - m.start_mm) as u64).div_ceil(u64::from(g.section_mm)) as usize;
            assert!(count <= 64);
            let mut available = 0u32;
            for (section, armed) in arms[index].iter_mut().enumerate().take(count) {
                let start = m.start_mm + section as i64 * i64::from(g.section_mm);
                let end = (start + i64::from(g.section_mm)).min(m.end_mm);
                let present = overlap(f.position_mm, start, end, g);
                let predicted = f.position_mm
                    + i64::from(f.velocity_mmps) * (g.lookahead_ns as i64) / 1_000_000_000;
                let approaching = overlap(predicted, start, end, g) > 0;
                if committed && protected && (present > 0 || approaching) && armed.is_none() {
                    *armed = Some(f.now_ns);
                    switchovers += 1;
                }
                if armed.is_some_and(|at| {
                    f.now_ns.saturating_sub(at) >= g.warmup_ns + f.extra_warmup_ns
                }) {
                    available += present;
                }
                // Positive full-consist position clears energisation after passage;
                // this is not a resource release or an expiry-based clearance.
                if f.position_mm - i64::from(length) > end {
                    *armed = None;
                }
            }
            let active = f.active_zone == m.id;
            let force = if active { f.force_n } else { 0. };
            let p = StationParams {
                configuration: cfg,
                zone_id: m.id,
                zone_start_mm: m.start_mm - m.origin_mm,
                zone_end_mm: m.end_mm - m.origin_mm,
                train_envelope_mm: length,
                pole_pitch_um: 250000,
                maximum_age_ns: 100000,
                maximum_tick_ns: g.maximum_tick_ns,
                maximum_phase_uncertainty_mdeg: 5000,
                force_density_n_per_envelope_m: m.force_density_n_m,
                force_constant_n_per_a: m.force_constant_n_a,
                resistance_ohm: m.resistance_ohm,
                inductance_h: m.inductance_h,
                flux_linkage_wb: m.force_constant_n_a * 0.5 / core::f64::consts::TAU,
                maximum_current_a: m.maximum_current_a,
                maximum_phase_voltage_v: m.maximum_voltage_v,
                maximum_copper_loss_w: m.maximum_copper_loss_w,
            };
            let mode = if !active {
                StationMode::Coast
            } else {
                match f.mode {
                    0 => StationMode::Launch,
                    1 => StationMode::Coast,
                    2 => StationMode::Receive,
                    3 => StationMode::Secured,
                    4 => StationMode::Berth,
                    _ => panic!("mode"),
                }
            };
            let frame = StationFrame {
                configuration: cfg,
                zone_id: m.id,
                sequence: f.sequence,
                observed_ns: f.observed_ns,
                position_mm: f.position_mm - m.origin_mm,
                velocity_mmps: f.velocity_mmps,
                position_uncertainty_um: f.position_uncertainty_um,
                timestamp_uncertainty_ns: f.timestamp_uncertainty_ns,
                phase_offset_mdeg: 0,
                overlap_mm: available,
                force_demand_n: force,
                mode,
                launch_committed: committed,
                arrival_resources_protected: protected,
                receiver_healthy: f.receiver_healthy,
                sensors_healthy: f.sensors_healthy,
                drive_healthy: f.failed_zone != m.id,
                brake_resistor_ready: f.resistor_ready,
            };
            let output = evaluate_station(states[index], frame, f.now_ns, p);
            states[index] = output.state;
            assert!(
                !output.physical_output_authorised && !output.onboard_support_shutdown_requested
            );
            max_current = max_current.max(output.study_current_a.abs());
            max_voltage = max_voltage.max(output.study_voltage_bound_v);
            max_loss = max_loss.max(output.study_copper_loss_w);
            let speed = f64::from(f.velocity_mmps) / 1000.;
            let mechanical = output.study_force_n * speed;
            let electrical = m.force_constant_n_a * speed * output.study_current_a;
            power_error = power_error.max((mechanical - electrical).abs());
            if !output.study_command_feasible {
                any_fault = true;
                if first_fault.is_none() {
                    first_fault = Some(
                        json!({"sequence":f.sequence,"zone":m.id,"fault":format!("{:?}",output.state.latched_fault)}),
                    );
                }
            }
            if active {
                active_result = Some(
                    json!({"zone":m.id,"force_n":output.study_force_n,"current_a":output.study_current_a,"voltage_v":output.study_voltage_bound_v,
                "copper_loss_w":output.study_copper_loss_w,"energized_overlap_mm":available,"feasible":output.study_command_feasible,"phase_uncertainty_mdeg":output.phase_uncertainty_mdeg}),
                );
            }
        }
        if any_fault && !fault_held {
            ledger
                .apply(
                    &ResourceEvent::HoldStationLaunch(StationFault {
                        launch_id,
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
            fault_held = true;
        }
        if f.full_tail_clear && !cleared {
            let arrival = input.motors.last().unwrap();
            assert!(
                outgoing
                    && !fault_held
                    && f.position_mm - i64::from(length)
                        > arrival.end_mm + i64::from(g.downstream_overlap_mm)
            );
            let clearance = StationClearance {
                launch_id: 1,
                configuration: cfg,
                owner: OWNER,
                epoch: 1,
                sequence: 1,
                observed_ns: f.now_ns,
                consist_length_mm: length,
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
        if f.sequence % 10 == 1 || any_fault || f.full_tail_clear {
            observations.push(json!({"sequence":f.sequence,"now_ns":f.now_ns,"position_mm":f.position_mm,"velocity_mmps":f.velocity_mmps,
            "active":active_result,"incoming_protected":ledger.station_arrival_protected(1),"incoming_cleared":cleared,"fault_held":fault_held}));
        }
        if any_fault {
            break;
        }
    }
    println!(
        "{}",
        json!({"schema":"osr-fixed-corridor-rust-replay/1","configuration":cfg,"executed_frames":frames,"observations":observations,
        "first_fault":first_fault,"fault_held":fault_held,"incoming_cleared":cleared,"outgoing_committed":outgoing,
        "incoming_protected":ledger.station_arrival_protected(1),"peak_current_a":max_current,"peak_voltage_v":max_voltage,"peak_copper_loss_w":max_loss,
        "power_conservation_max_residual_w":power_error,"section_arming_events":switchovers,"physical_output_authorised":false,
        "scope":"One local six-resource controller domain; synthetic full-consist detectors, finite section warm-up, ideal power-consistent circuit; not hardware or distributed authority"})
    );
}
