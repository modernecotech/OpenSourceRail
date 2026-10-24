//! Live local resource decisions consumed by the numerical six-car plant.
//! Detector/readiness assertions are synthetic. No physical motion authority.
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId, TrainId};
use osr_interlocking::{
    resource_log::{ResourceEvent, ResourceLedger},
    resources::*,
    station::*,
};
use serde::Deserialize;
use serde_json::json;
use std::io::{self, BufRead, Write};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Initial {
    model: RailwayModel,
    configuration: [u8; 32],
    stops_m: Vec<f64>,
}
#[derive(Deserialize)]
#[serde(tag = "kind", deny_unknown_fields)]
enum Command {
    #[serde(rename = "prepare")]
    Prepare {
        now_ns: u64,
        leg: usize,
        receiver_ready: bool,
        resistor_ready: bool,
        reserve_ready: bool,
        doors_closed: bool,
        train_healthy: bool,
    },
    #[serde(rename = "sample")]
    Sample {
        now_ns: u64,
        front_m: f64,
        tail_m: f64,
        speed_m_s: f64,
        receiver_failed: bool,
        resistor_ready: bool,
    },
}
const BASE: u64 = 1_000_000_000;
const OWNER: Owner = Owner {
    train: TrainId(101),
    session: 1,
};
fn proof(resource: u8, sequence: u64, now: u64) -> ProtectionProof {
    ProtectionProof {
        resource: ResourceId(resource),
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
fn ready(id: u64, seq: u64, now: u64, cfg: [u8; 32], healthy: bool) -> StationReadiness {
    StationReadiness {
        launch_id: id,
        configuration: cfg,
        owner: OWNER,
        epoch: 1,
        sequence: seq,
        observed_ns: now,
        receive_brake_ready: healthy,
        arrival_reserve_ready: healthy,
        doors_closed: healthy,
        services_reserve_ready: healthy,
        route_ready: healthy,
        train_healthy: healthy,
    }
}
fn send(value: serde_json::Value) {
    println!("{value}");
    io::stdout().flush().unwrap();
}
fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let first = lines.next().expect("initial model").unwrap();
    assert!(first.len() <= 1024 * 1024);
    let init: Initial = serde_json::from_str(&first).unwrap();
    assert!((2..=10).contains(&init.stops_m.len()));
    assert!(
        init.stops_m.iter().all(|s| s.is_finite()) && init.stops_m.windows(2).all(|s| s[1] > s[0])
    );
    let cfg = init.configuration;
    let mut ledger = ResourceLedger::new(init.model, cfg, BASE).unwrap();
    ledger
        .apply(
            &ResourceEvent::Integrity {
                owner: OWNER,
                proved: true,
            },
            BASE,
        )
        .unwrap();
    for id in 0..3 * (init.stops_m.len() - 1) {
        ledger
            .apply(&ResourceEvent::LocalProof(proof(id as u8, 1, BASE)), BASE)
            .unwrap();
        ledger
            .apply(&ResourceEvent::Clear(ResourceId(id as u8)), BASE)
            .unwrap();
    }
    let (mut sequence, mut last_time, mut last_requested, mut current, mut failed) =
        (0_u64, BASE, BASE, None::<usize>, false);
    send(json!({"ready":true,"physical_output_authorised":false}));
    for line in lines {
        let line = line.unwrap();
        if line.len() > 16384 {
            break;
        }
        let parsed = serde_json::from_str::<Command>(&line);
        let Ok(command) = parsed else {
            send(
                json!({"ok":false,"error":"invalid bounded command","physical_output_authorised":false}),
            );
            continue;
        };
        sequence += 1;
        assert!(sequence <= 500_000);
        let requested = match command {
            Command::Prepare { now_ns, .. } | Command::Sample { now_ns, .. } => now_ns,
        };
        if requested < last_requested || requested > BASE + 3_600_000_000_000 {
            send(
                json!({"ok":false,"error":"nonmonotone/out-of-range time","sequence":sequence,"physical_output_authorised":false}),
            );
            continue;
        }
        last_requested = requested;
        let now = requested.max(last_time + 2);
        last_time = now;
        if ledger.controller.advance_time(now).is_err() {
            send(json!({"ok":false,"error":"ledger clock","physical_output_authorised":false}));
            continue;
        }
        let mut error = None;
        let mut cleared = Vec::new();
        let mut receiver = true;
        let resistor;
        match command {
            Command::Prepare {
                leg,
                receiver_ready,
                resistor_ready,
                reserve_ready,
                doors_closed,
                train_healthy,
                ..
            } => {
                receiver = receiver_ready;
                resistor = resistor_ready;
                if leg >= init.stops_m.len() - 1
                    || current.map_or(leg != 0, |n| leg != n && leg != n + 1)
                {
                    error = Some("leg order".to_string());
                } else {
                    let id = leg as u64 + 1;
                    let base = (leg * 3) as u8;
                    for resource in base..base + 3 {
                        if ledger
                            .apply(
                                &ResourceEvent::LocalProof(proof(resource, sequence + 1, now)),
                                now,
                            )
                            .is_err()
                        {
                            error = Some("readiness proof".to_string());
                        }
                    }
                    if error.is_none() {
                        let request = StationLaunchRequest {
                            id,
                            configuration: cfg,
                            owner: OWNER,
                            route: RouteId(1),
                            direction: Direction::Forward,
                            corridor: ResourceId(base),
                            receiving_berth: ResourceId(base + 1),
                            overlap: ResourceId(base + 2),
                            consist_length_mm: 104500,
                            permission_expires_ns: now + LEASE_NS,
                        };
                        let healthy = receiver_ready
                            && resistor_ready
                            && reserve_ready
                            && doors_closed
                            && train_healthy;
                        match ledger.apply(
                            &ResourceEvent::PrepareStationLaunch {
                                request,
                                readiness: ready(id, 1, now, cfg, healthy),
                            },
                            now,
                        ) {
                            Ok(()) => {
                                match ledger.apply(
                                    &ResourceEvent::CommitStationLaunch {
                                        id,
                                        readiness: ready(id, 2, now + 1, cfg, healthy),
                                    },
                                    now + 1,
                                ) {
                                    Ok(()) => {
                                        current = Some(leg);
                                        failed = false;
                                        last_time = now + 1;
                                    }
                                    Err(e) => error = Some(format!("commit:{e:?}")),
                                }
                            }
                            Err(e) => error = Some(format!("prepare:{e:?}")),
                        }
                    }
                }
            }
            Command::Sample {
                front_m,
                tail_m,
                speed_m_s,
                receiver_failed,
                resistor_ready,
                ..
            } => {
                resistor = resistor_ready;
                if ![front_m, tail_m, speed_m_s].iter().all(|x| x.is_finite())
                    || front_m < tail_m
                    || ((front_m - tail_m) - 104.5).abs() > 0.25
                {
                    error = Some("actual full-consist pose/length".to_string());
                } else if let Some(leg) = current {
                    let id = leg as u64 + 1;
                    if receiver_failed && !failed {
                        let fault = StationFault {
                            launch_id: id,
                            configuration: cfg,
                            owner: OWNER,
                            epoch: 1,
                            sequence,
                            observed_ns: now,
                            reason: StationFaultReason::ReceiverUnavailable,
                        };
                        if let Err(e) = ledger.apply(&ResourceEvent::HoldStationLaunch(fault), now)
                        {
                            error = Some(format!("fault:{e:?}"));
                        } else {
                            failed = true;
                        }
                    }
                    receiver = !failed;
                    // Arrival locks are never cleared by a forecast or by a
                    // stationary train still occupying its receiving berth.
                    for prior in 0..leg {
                        if tail_m > init.stops_m[prior + 1] + 200.5
                            && ledger
                                .station_launch(prior as u64 + 1)
                                .is_some_and(|v| v.phase != LaunchPhase::Cleared)
                        {
                            let base = (prior * 3) as u8;
                            let clearance = StationClearance {
                                launch_id: prior as u64 + 1,
                                configuration: cfg,
                                owner: OWNER,
                                epoch: 1,
                                sequence,
                                observed_ns: now,
                                consist_length_mm: 104500,
                                tail_integrity_proved: true,
                                all_cars_accounted_for: true,
                                proofs: core::array::from_fn(|j| {
                                    proof(base + j as u8, sequence + 2, now)
                                }),
                            };
                            match ledger
                                .apply(&ResourceEvent::ClearStationLaunch(Box::new(clearance)), now)
                            {
                                Ok(()) => cleared.push(prior),
                                Err(e) => error = Some(format!("clearance:{e:?}")),
                            }
                        }
                    }
                } else {
                    receiver = false;
                }
            }
        }
        let id = current.map(|v| v as u64 + 1);
        let protected = id.is_some_and(|v| ledger.station_arrival_protected(v));
        let committed = id.is_some_and(|v| {
            ledger
                .station_launch(v)
                .is_some_and(|l| l.committed_ns.is_some())
        });
        send(
            json!({"ok":error.is_none(),"error":error,"sequence":sequence,"now_ns":last_time,"leg":current,
            "protected":protected,"committed":committed,"receiver_ready":receiver,"resistor_ready":resistor,
            "cleared_previous_legs":cleared,"configuration":cfg,"physical_output_authorised":false,
            "scope":"Actual local ledger; numerical pose/readiness assertions, no authenticated physical detectors"}),
        );
    }
}
