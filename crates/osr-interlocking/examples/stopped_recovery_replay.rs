//! Executable offline stopped-recovery replay. Synthetic observations and an
//! in-memory event transcript are not authenticated installed persistence.
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId};
use osr_interlocking::{progressive::*, resource_log::ResourceEvent, resources::*};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::io::{self, Read};
const START: u64 = 1_000_000_000;
const RECOVER: u64 = START + 1 + LEASE_NS + CLOCK_SKEW_NS;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    model: RailwayModel,
    configuration: ConfigurationId,
    policy: ProgressivePolicy,
    case: String,
    positions: Vec<ProgressiveReadiness>,
}
#[derive(Clone, Serialize)]
enum Action {
    Apply {
        event: Box<ProgressiveEvent>,
        now: u64,
        result: Result<(), ProgressiveError>,
    },
    Restore {
        snapshot: serde_json::Value,
    },
}
fn apply(
    d: &mut ProgressiveDomain,
    log: &mut Vec<Action>,
    event: ProgressiveEvent,
    now: u64,
) -> Result<(), ProgressiveError> {
    let result = d.apply(&event, now);
    log.push(Action::Apply {
        event: Box::new(event),
        now,
        result,
    });
    result
}
fn restore(d: &mut ProgressiveDomain, log: &mut Vec<Action>) {
    let snapshot = serde_json::to_value(&d).unwrap();
    *d = serde_json::from_value(snapshot.clone()).unwrap();
    log.push(Action::Restore { snapshot });
}
fn owner_at(input: &Input, resource: ResourceId) -> Option<Owner> {
    input.positions.iter().find_map(|r| {
        let t = input
            .model
            .trains
            .iter()
            .find(|t| t.config.owner == r.owner)
            .unwrap();
        let route = input
            .model
            .routes
            .iter()
            .find(|p| p.id == t.permitted_route)
            .unwrap();
        let s = route.segments.iter().find(|s| s.resource == resource)?;
        let u = u64::from(t.config.maximum_position_uncertainty_mm);
        let rear = r.front_mm.checked_sub(u64::from(t.config.length_mm) + u)?;
        (s.start_mm <= r.front_mm + u && s.end_mm >= rear).then_some(r.owner)
    })
}
fn proof(
    input: &Input,
    id: ResourceId,
    sequence: u64,
    epoch: u64,
    now: u64,
    occupied: bool,
    cleared: Option<Owner>,
) -> ProtectionProof {
    let occupant = if occupied { owner_at(input, id) } else { None };
    ProtectionProof {
        resource: id,
        controller: input.model.controllers[0].id,
        epoch,
        sequence,
        observed_ns: now,
        clear: occupant.is_none(),
        clearance_safe: true,
        cleared_owner: cleared,
        occupant,
        occupancy_integrity_proved: true,
        points_locked_and_proved: false,
        proved_route: None,
        restriction: Restriction::Open,
    }
}
fn run(input: Input) -> serde_json::Value {
    let cases = [
        "nominal",
        "prepared",
        "two-train",
        "missing-train",
        "duplicate-train",
        "moving",
        "wrong-berth",
        "old-epoch",
        "stale-readiness",
        "stale-proof",
        "wrong-owner",
        "unexplained-occupant",
        "unsafe-clearance",
        "cleared-owner",
        "quarantine",
        "wrong-model",
        "missing-proof",
        "blocked",
        "proof-sequence",
        "second-crash",
        "replayed-reconcile",
        "old-commit",
    ];
    assert!(cases.contains(&input.case.as_str()) && (1..=2).contains(&input.positions.len()));
    let initial = ProgressiveDomain::new(
        input.model.clone(),
        input.configuration,
        input.policy,
        START,
    )
    .unwrap();
    let mut d = initial.clone();
    let mut journal = Vec::new();
    for spec in input.model.specifications().unwrap() {
        apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Evidence(ResourceEvent::LocalProof(proof(
                &input, spec.id, 1, 1, START, false, None,
            ))),
            START,
        )
        .unwrap();
        apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Evidence(ResourceEvent::Clear(spec.id)),
            START,
        )
        .unwrap();
        apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Evidence(ResourceEvent::LocalProof(proof(
                &input, spec.id, 2, 1, START, true, None,
            ))),
            START,
        )
        .unwrap();
    }
    for (i, r) in input.positions.iter().enumerate() {
        apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Evidence(ResourceEvent::Integrity {
                owner: r.owner,
                proved: true,
            }),
            START,
        )
        .unwrap();
        let route = input
            .model
            .trains
            .iter()
            .find(|t| t.config.owner == r.owner)
            .unwrap()
            .permitted_route;
        let request = DepartureRequest {
            id: i as u64 + 1,
            owner: r.owner,
            configuration: input.configuration,
            route,
            direction: Direction::Forward,
            readiness: *r,
        };
        apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Prepare(request),
            START,
        )
        .unwrap();
        if input.case != "prepared" {
            let mut ready = *r;
            ready.sequence += 1;
            apply(
                &mut d,
                &mut journal,
                ProgressiveEvent::Commit {
                    id: request.id,
                    readiness: ready,
                },
                START,
            )
            .unwrap();
        }
    }
    restore(&mut d, &mut journal);
    let snapshot_fenced = d.restore_fenced()
        && d.departures()
            .iter()
            .all(|v| !d.may_move(v.request.id, START));
    let before: Vec<_> = d
        .ledger()
        .controller
        .records()
        .iter()
        .map(|r| r.grant)
        .collect();
    apply(
        &mut d,
        &mut journal,
        ProgressiveEvent::Restart { new_epoch: 2 },
        START + 1,
    )
    .unwrap();
    let forward = before
        .iter()
        .flatten()
        .find(|g| owner_at(&input, g.resource).is_none())
        .unwrap()
        .resource;
    let body = before
        .iter()
        .flatten()
        .find(|g| owner_at(&input, g.resource).is_some())
        .unwrap()
        .resource;
    let unused = before
        .iter()
        .position(Option::is_none)
        .map(|i| ResourceId(i as u8))
        .unwrap();
    let recovery_time = if input.case == "quarantine" {
        RECOVER - 1
    } else {
        RECOVER
    };
    for (i, old) in before.iter().enumerate() {
        let id = ResourceId(i as u8);
        if input.case == "missing-proof" && id == unused {
            continue;
        }
        let sequence = d.ledger().controller.records()[i].last_proof_sequence + 1;
        let mut p = proof(
            &input,
            id,
            sequence,
            2,
            recovery_time,
            true,
            if owner_at(&input, id).is_none() {
                old.map(|g| g.owner)
            } else {
                None
            },
        );
        if input.case == "stale-proof" && id == body {
            p.observed_ns -= input.policy.maximum_sample_ns + 1;
        }
        if input.case == "old-epoch" && id == body {
            p.epoch = 1;
        }
        if input.case == "unsafe-clearance" && id == forward {
            p.clearance_safe = false;
        }
        if input.case == "cleared-owner" && id == forward {
            p.cleared_owner = None;
        }
        if input.case == "proof-sequence" && id == body {
            p.sequence -= 1;
        }
        if input.case == "unexplained-occupant" && id == unused {
            p.clear = false;
            p.occupant = Some(input.positions[0].owner);
        }
        let _ = apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
            recovery_time,
        );
    }
    if input.case == "blocked" {
        apply(
            &mut d,
            &mut journal,
            ProgressiveEvent::Evidence(ResourceEvent::Block(unused)),
            RECOVER,
        )
        .unwrap();
    }
    let mut readiness: Vec<_> = input
        .positions
        .iter()
        .map(|r| ProgressiveReadiness {
            epoch: 2,
            sequence: 100,
            observed_ns: recovery_time,
            ..*r
        })
        .collect();
    match input.case.as_str() {
        "missing-train" => {
            readiness.pop();
        }
        "duplicate-train" => {
            readiness.push(readiness[0]);
        }
        "moving" => {
            readiness[0].velocity_mmps = 1;
        }
        "wrong-berth" => {
            readiness[0].front_mm += 100000;
        }
        "wrong-owner" => {
            readiness[0].owner.session += 1;
        }
        "stale-readiness" => {
            readiness[0].observed_ns -= input.policy.maximum_sample_ns + 1;
        }
        "second-crash" => {
            restore(&mut d, &mut journal);
        }
        _ => {}
    }
    let mut pinned = input.model.clone();
    if input.case == "wrong-model" {
        pinned.revision.push_str("-altered");
    }
    let event = ProgressiveEvent::ReconcileStopped {
        configuration: input.configuration,
        expected_policy: input.policy,
        expected_model: Box::new(pinned),
        readiness: readiness.clone(),
    };
    let before_reconciliation = d.ledger().controller.records().to_vec();
    let result = apply(&mut d, &mut journal, event.clone(), recovery_time);
    let rejected_atomic =
        result.is_err() && d.ledger().controller.records() == before_reconciliation;
    let old_contracts_fenced = d
        .departures()
        .iter()
        .all(|p| !d.may_move(p.request.id, RECOVER));
    let mut new_authorities = 0;
    let mut duplicate_rejected = false;
    let mut old_commit_rejected = false;
    if result.is_ok() {
        if input.case == "replayed-reconcile" {
            duplicate_rejected = apply(&mut d, &mut journal, event, RECOVER).is_err();
        }
        if input.case == "old-commit" {
            old_commit_rejected = apply(
                &mut d,
                &mut journal,
                ProgressiveEvent::Commit {
                    id: 1,
                    readiness: readiness[0],
                },
                RECOVER,
            )
            .is_err();
        }
        for (i, r) in readiness.iter().enumerate() {
            let mut r = *r;
            r.sequence = 101;
            let q = DepartureRequest {
                id: input.positions.len() as u64 + i as u64 + 1,
                owner: r.owner,
                configuration: input.configuration,
                route: RouteId(1),
                direction: Direction::Forward,
                readiness: r,
            };
            apply(&mut d, &mut journal, ProgressiveEvent::Prepare(q), RECOVER).unwrap();
            r.sequence = 102;
            apply(
                &mut d,
                &mut journal,
                ProgressiveEvent::Commit {
                    id: q.id,
                    readiness: r,
                },
                RECOVER,
            )
            .unwrap();
            new_authorities += usize::from(d.may_move(q.id, RECOVER));
        }
    }
    let mut replay = initial;
    for a in &journal {
        match a {
            Action::Apply { event, now, result } => assert_eq!(replay.apply(event, *now), *result),
            Action::Restore { snapshot } => {
                assert_eq!(serde_json::to_value(&replay).unwrap(), *snapshot);
                replay = serde_json::from_value(snapshot.clone()).unwrap();
            }
        }
    }
    json!({"schema":"osr-stopped-recovery-replay/1","protocol":RECOVERY_PROTOCOL,"case":input.case,
        "snapshot_fenced":snapshot_fenced,"old_contracts_fenced":old_contracts_fenced,
        "reconciliation_passed":result.is_ok(),"reconciliation_error":result.err(),"rejection_atomic":rejected_atomic,
        "new_authorities":new_authorities,"duplicate_rejected":duplicate_rejected,"old_commit_rejected":old_commit_rejected,
        "exact_event_replay_equal":replay==d,"transcript":journal,"retained_records":d.ledger().controller.records(),
        "participants":input.positions.len(),"configuration":input.configuration,"physical_output_authorised":false,
        "multi_controller_handover_implemented":false,"authenticated_persistence_implemented":false})
}
fn main() {
    let mut bytes = Vec::new();
    io::stdin()
        .take(4 * 1024 * 1024 + 1)
        .read_to_end(&mut bytes)
        .unwrap();
    assert!(bytes.len() <= 4 * 1024 * 1024);
    let input: Input = serde_json::from_slice(&bytes).unwrap();
    println!("{}", run(input));
}
