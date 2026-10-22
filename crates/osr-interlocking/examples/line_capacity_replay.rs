//! Bounded offline multi-train fixed-block study using the existing durable ledger.
//! Synthetic detectors and a scalar brake hypothesis; no station-launch protocol
//! substitution, distributed authority, train command, or physical safety claim.
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId, TrainId};
use osr_interlocking::{
    progressive::*,
    resource_log::{ResourceEvent, ResourceLedger},
    resources::*,
    station::*,
};
use serde::Deserialize;
use serde_json::json;
use std::{
    collections::BTreeMap,
    io::{self, Read},
};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Position {
    train: u64,
    front_mm: i64,
    velocity_mmps: u32,
    observed_ns: u64,
    integrity_proved: bool,
    independent_brake_ready: bool,
    #[serde(default)]
    launch_leg: Option<u32>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Frame {
    now_ns: u64,
    positions: Vec<Position>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    model: RailwayModel,
    configuration: [u8; 32],
    frames: Vec<Frame>,
    maximum_acceleration_mmps2: u32,
    sample_ns: u64,
    exclusive_leg: bool,
    delayed_clear_resource: Option<u8>,
    delay_until_ns: u64,
    competing_train: bool,
    #[serde(default)]
    joint: Option<JointInput>,
    #[serde(default)]
    contract: Option<ContractInput>,
}
const BASE: u64 = 1_000_000_000;
fn proof(
    id: u8,
    seq: u64,
    _now: u64,
    observed: u64,
    occupant: Option<Owner>,
    cleared: Option<Owner>,
) -> ProtectionProof {
    ProtectionProof {
        resource: ResourceId(id),
        controller: ControllerId(900),
        epoch: 1,
        sequence: seq,
        observed_ns: observed,
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
fn ceil_div(a: u128, b: u128) -> u128 {
    a.div_ceil(b)
}
fn stopping_mm(
    v: u32,
    cfg: TrainConfig,
    max_acc: u32,
    sample_ns: u64,
    age_ns: u64,
    grade: u16,
) -> u64 {
    // Integer ceiling at each positive operation. Acceleration can continue over
    // reaction, next sample and observation age. Constant deceleration thereafter
    // is a hypothesis, not a measured emergency-brake curve.
    let t =
        u128::from(cfg.reaction_time_ms) * 1_000_000 + u128::from(sample_ns) + u128::from(age_ns);
    let vv = u128::from(v);
    let aa = u128::from(max_acc);
    let vp = vv + ceil_div(aa * t, 1_000_000_000);
    let reaction =
        ceil_div(vv * t, 1_000_000_000) + ceil_div(aa * t * t, 2_000_000_000_000_000_000);
    let gravity = ceil_div(9810 * u128::from(grade), 1000);
    let net = u128::from(cfg.minimum_deceleration_mmps2)
        .checked_sub(gravity)
        .expect("positive net brake");
    assert!(net > 0);
    u64::try_from(
        reaction
            + ceil_div(vp * vp, 2 * net)
            + u128::from(cfg.stop_margin_mm)
            + u128::from(cfg.maximum_position_uncertainty_mm),
    )
    .unwrap()
}
fn main() {
    let mut raw = String::new();
    io::stdin()
        .take(64 * 1024 * 1024 + 1)
        .read_to_string(&mut raw)
        .unwrap();
    assert!(raw.len() <= 64 * 1024 * 1024);
    let input: Input = serde_json::from_str(&raw).unwrap();
    if input.contract.is_some() {
        println!("{}", contract_replay(&input));
        return;
    }
    if input.joint.is_some() {
        println!("{}", joint_replay(&input));
        return;
    }
    assert!(
        !input.frames.is_empty()
            && input.frames.len() <= 30000
            && (1..=100_000_000).contains(&input.sample_ns)
    );
    assert!(input.maximum_acceleration_mmps2 <= 2000);
    let mut ledger = ResourceLedger::new(input.model.clone(), input.configuration, BASE).unwrap();
    let segments = input.model.routes[0].segments.clone();
    let configs: BTreeMap<_, _> = input
        .model
        .trains
        .iter()
        .map(|t| (t.config.owner.train.0, t.config))
        .collect();
    for cfg in configs.values() {
        ledger
            .apply(
                &ResourceEvent::Integrity {
                    owner: cfg.owner,
                    proved: true,
                },
                BASE,
            )
            .unwrap();
    }
    let mut seq = vec![1_u64; segments.len()];
    for (i, s) in segments.iter().enumerate() {
        let p = proof(s.resource.0, seq[i], BASE, BASE, None, None);
        ledger.apply(&ResourceEvent::LocalProof(p), BASE).unwrap();
        ledger
            .apply(&ResourceEvent::Clear(s.resource), BASE)
            .unwrap();
    }
    let platforms: Vec<_> = input
        .model
        .resources
        .iter()
        .enumerate()
        .filter(|(_, r)| r.kind == "platform")
        .map(|(i, _)| segments[i])
        .collect();
    let mut failure = None;
    let mut executed = 0;
    let mut releases = 0;
    let mut stopped_withdrawals = 0;
    let mut renewals = 0;
    let mut reservations = 0;
    let mut max_owned = 0;
    let mut fault_fenced = 0;
    let mut max_active = 0;
    let mut conflict_rejected = false;
    let mut tail_early_rejected = false;
    let mut min_separation: i64 = i64::MAX;
    let mut min_stopping_margin: i64 = i64::MAX;
    let mut max_stopping = 0;
    let mut trace = Vec::new();
    let mut previous_now = BASE;
    let mut previous_front = BTreeMap::new();
    'frames: for f in input.frames {
        assert!(f.now_ns > previous_now && f.now_ns - previous_now <= input.sample_ns + 1);
        previous_now = f.now_ns;
        executed += 1;
        let positions: BTreeMap<_, _> = f.positions.iter().map(|p| (p.train, p)).collect();
        assert_eq!(positions.len(), f.positions.len());
        assert!(positions.len() <= configs.len());
        max_active = max_active.max(positions.len());
        for p in positions.values() {
            assert!(
                configs.contains_key(&p.train)
                    && p.velocity_mmps <= 100000
                    && p.observed_ns <= f.now_ns
            );
            let problem = if !p.integrity_proved {
                Some("consist-integrity-lost")
            } else if !p.independent_brake_ready {
                Some("independent-brake-unavailable")
            } else if previous_front
                .get(&p.train)
                .is_some_and(|old| p.front_mm < *old)
            {
                Some("rollback-observed")
            } else {
                None
            };
            if let Some(kind) = problem {
                if !p.integrity_proved {
                    ledger
                        .apply(
                            &ResourceEvent::Integrity {
                                owner: configs[&p.train].owner,
                                proved: false,
                            },
                            f.now_ns,
                        )
                        .unwrap();
                }
                let held: Vec<_> = ledger
                    .controller
                    .records()
                    .iter()
                    .filter_map(|r| {
                        r.grant
                            .filter(|g| g.owner.train.0 == p.train)
                            .map(|g| g.resource)
                    })
                    .collect();
                for id in held {
                    ledger.apply(&ResourceEvent::Block(id), f.now_ns).unwrap();
                    fault_fenced += 1;
                }
                failure = Some(
                    json!({"kind":kind,"train":p.train,"now_ns":f.now_ns,"ownership_retained":true}),
                );
                break 'frames;
            }
            previous_front.insert(p.train, p.front_mm);
        }
        let mut ordered: Vec<_> = positions.values().collect();
        ordered.sort_by_key(|p| p.front_mm);
        for pair in ordered.windows(2) {
            let rear = pair[1].front_mm - i64::from(configs[&pair[1].train].length_mm);
            min_separation = min_separation.min(rear - pair[0].front_mm);
        }
        // Update only positive full-tail clearances. Permission expiry never frees
        // a lock; a delayed or stale local proof retains its previous owner.
        for (i, s) in segments.iter().enumerate() {
            let old = ledger.controller.records()[i];
            let old_owner = old.grant.map(|g| g.owner);
            let occupant = positions
                .values()
                .filter(|p| {
                    p.front_mm >= s.start_mm as i64
                        && p.front_mm - i64::from(configs[&p.train].length_mm) <= s.end_mm as i64
                })
                .map(|p| configs[&p.train].owner)
                .collect::<Vec<_>>();
            if occupant.len() > 1 {
                failure = Some(json!({"kind":"physical-overlap","resource":i,"now_ns":f.now_ns}));
                break 'frames;
            }
            if let Some(g) = old.grant {
                if let Some(p) = positions.get(&g.owner.train.0) {
                    let cfg = configs[&p.train];
                    let rear = p.front_mm
                        - i64::from(cfg.length_mm)
                        - i64::from(cfg.maximum_position_uncertainty_mm);
                    // The comparison retains a whole leg until its receiving
                    // berth AND75m overlap have a positive complete-tail clear.
                    // It does not reserve the complete multi-leg study route.
                    let release_end = if input.exclusive_leg {
                        platforms
                            .iter()
                            .skip(1)
                            .find(|b| b.end_mm >= s.end_mm)
                            .map_or(s.end_mm, |b| b.end_mm + 75000)
                    } else {
                        s.end_mm
                    };
                    let tail_clear = rear > release_end as i64;
                    let proved_stop_before = !input.exclusive_leg
                        && p.velocity_mmps == 0
                        && p.front_mm + i64::from(cfg.maximum_position_uncertainty_mm)
                            < s.start_mm as i64;
                    if tail_clear || proved_stop_before {
                        if input.delayed_clear_resource == Some(i as u8)
                            && f.now_ns < input.delay_until_ns
                        {
                            continue;
                        }
                        ledger.apply(&ResourceEvent::Withdraw(g), f.now_ns).unwrap();
                        seq[i] += 1;
                        let pr = proof(
                            i as u8,
                            seq[i],
                            f.now_ns,
                            p.observed_ns,
                            None,
                            Some(g.owner),
                        );
                        ledger
                            .apply(&ResourceEvent::LocalProof(pr), f.now_ns)
                            .unwrap();
                        if ledger
                            .apply(&ResourceEvent::Clear(s.resource), f.now_ns)
                            .is_ok()
                        {
                            if tail_clear {
                                releases += 1;
                            } else {
                                stopped_withdrawals += 1;
                            }
                        }
                    } else if occupant.first() == Some(&g.owner) {
                        seq[i] += 1;
                        let pr = proof(
                            i as u8,
                            seq[i],
                            f.now_ns,
                            p.observed_ns,
                            Some(g.owner),
                            None,
                        );
                        ledger
                            .apply(&ResourceEvent::LocalProof(pr), f.now_ns)
                            .unwrap();
                    } else if occupant.is_empty() {
                        seq[i] += 1;
                        let pr = proof(i as u8, seq[i], f.now_ns, p.observed_ns, None, None);
                        ledger
                            .apply(&ResourceEvent::LocalProof(pr), f.now_ns)
                            .unwrap();
                    }
                }
            } else {
                seq[i] += 1;
                let pr = proof(
                    i as u8,
                    seq[i],
                    f.now_ns,
                    f.now_ns,
                    occupant.first().copied(),
                    old_owner,
                );
                ledger
                    .apply(&ResourceEvent::LocalProof(pr), f.now_ns)
                    .unwrap();
            }
        }
        // Lead trains first. Every movement envelope must own all occupied and
        // stopping resources. This is a study adapter, not launch commit logic.
        ordered.reverse();
        for p in ordered {
            let cfg = configs[&p.train];
            let age = f.now_ns - p.observed_ns;
            if age > INPUT_MAX_AGE_NS {
                let held: Vec<_> = ledger
                    .controller
                    .records()
                    .iter()
                    .filter_map(|r| {
                        r.grant
                            .filter(|g| g.owner.train.0 == p.train)
                            .map(|g| g.resource)
                    })
                    .collect();
                for id in held {
                    ledger.apply(&ResourceEvent::Block(id), f.now_ns).unwrap();
                    fault_fenced += 1;
                }
                failure = Some(
                    json!({"kind":"stale-position","train":p.train,"now_ns":f.now_ns,"age_ns":age,"ownership_retained":true}),
                );
                break 'frames;
            }
            let rear = p.front_mm
                - i64::from(cfg.length_mm)
                - i64::from(cfg.maximum_position_uncertainty_mm);
            let grade = segments
                .iter()
                .filter(|s| s.end_mm as i64 >= p.front_mm)
                .map(|s| s.downhill_permille)
                .max()
                .unwrap_or(0);
            let stopping = stopping_mm(
                p.velocity_mmps,
                cfg,
                input.maximum_acceleration_mmps2,
                input.sample_ns,
                age,
                grade,
            );
            max_stopping = max_stopping.max(stopping);
            let end = p.front_mm.checked_add(stopping as i64).unwrap();
            if end > segments.last().unwrap().end_mm as i64 {
                failure = Some(
                    json!({"kind":"unmodelled-authority-boundary","train":p.train,"now_ns":f.now_ns}),
                );
                break 'frames;
            }
            let reserve_end = if input.exclusive_leg && p.velocity_mmps > 0 {
                platforms
                    .iter()
                    .skip(1)
                    .find(|b| (b.start_mm + b.end_mm) / 2 > p.front_mm as u64)
                    .map_or(end, |b| (b.end_mm + 75000) as i64)
                    .max(end)
            } else {
                end
            };
            let required: Vec<_> = segments
                .iter()
                .filter(|s| s.end_mm as i64 >= rear && (s.start_mm as i64) <= reserve_end)
                .collect();
            for s in required {
                let i = usize::from(s.resource.0);
                let before = ledger.controller.records()[i];
                let event = ResourceEvent::Reserve {
                    owner: cfg.owner,
                    resource: s.resource,
                    route: RouteId(1),
                    direction: Direction::Forward,
                };
                if let Err(error) = ledger.apply(&event, f.now_ns) {
                    let available = (s.start_mm as i64) - p.front_mm;
                    failure = Some(
                        json!({"kind":"reservation-rejected","error":format!("{error:?}"),"train":p.train,"resource":i,"now_ns":f.now_ns,
                        "distance_to_denied_resource_mm":available,"stopping_envelope_mm":stopping,"headway_schedule_cannot_continue":true,
                        "owner_retained":ledger.controller.records()[i].grant.map(|g|g.owner.train.0),"denied_before_front_entry":p.front_mm<s.start_mm as i64}),
                    );
                    break 'frames;
                }
                if before.grant.is_some() {
                    renewals += 1;
                } else {
                    reservations += 1;
                }
                if !ledger.permits(input.model.resources[i].section, TrainId(p.train), f.now_ns) {
                    failure = Some(
                        json!({"kind":"permission-missing","train":p.train,"resource":i,"now_ns":f.now_ns}),
                    );
                    break 'frames;
                }
            }
            let authority_end = segments
                .iter()
                .take_while(|s| s.start_mm as i64 <= end)
                .filter(|s| {
                    ledger.controller.records()[usize::from(s.resource.0)]
                        .grant
                        .is_some_and(|g| g.owner == cfg.owner)
                })
                .map(|s| s.end_mm as i64)
                .max()
                .unwrap_or(p.front_mm);
            min_stopping_margin = min_stopping_margin.min(authority_end - end);
        }
        max_owned = max_owned.max(
            ledger
                .controller
                .records()
                .iter()
                .filter(|r| r.grant.is_some())
                .count(),
        );
        if input.competing_train && !conflict_rejected && positions.len() >= 2 {
            let g = ledger
                .controller
                .records()
                .iter()
                .find_map(|r| r.grant)
                .unwrap();
            let other = configs.values().find(|c| c.owner != g.owner).unwrap().owner;
            conflict_rejected = ledger
                .apply(
                    &ResourceEvent::Reserve {
                        owner: other,
                        resource: g.resource,
                        route: RouteId(1),
                        direction: Direction::Forward,
                    },
                    f.now_ns,
                )
                .is_err();
            let mut probe = ledger.clone();
            let before = probe.controller.records()[usize::from(g.resource.0)];
            probe.apply(&ResourceEvent::Withdraw(g), f.now_ns).unwrap();
            // An empty proof which does not identify the cleared owner cannot
            // clear a retained lock, even after permission has been withdrawn.
            let i = usize::from(g.resource.0);
            let pr = proof(g.resource.0, seq[i] + 1, f.now_ns, f.now_ns, None, None);
            probe
                .apply(&ResourceEvent::LocalProof(pr), f.now_ns)
                .unwrap();
            tail_early_rejected = probe
                .apply(&ResourceEvent::Clear(g.resource), f.now_ns)
                .is_err()
                && probe.controller.records()[i].grant == before.grant;
        }
        if executed % 100 == 0 {
            trace.push(json!({"now_ns":f.now_ns,"trains":positions.values().map(|p|json!({"train":p.train,"front_mm":p.front_mm,"speed_mmps":p.velocity_mmps})).collect::<Vec<_>>(),"owners":ledger.controller.records().iter().map(|r|r.grant.map(|g|g.owner.train.0)).collect::<Vec<_>>()}));
        }
    }
    println!(
        "{}",
        json!({"schema":"osr-line-capacity-replay/1","frames_executed":executed,"study_pass":failure.is_none(),"failure":failure,
        "release_count":releases,"stopped_forward_withdrawals":stopped_withdrawals,"fault_fenced_resources":fault_fenced,"reservation_count":reservations,"renewal_count":renewals,"maximum_owned_resources":max_owned,"maximum_active_trains":max_active,
        "minimum_train_separation_mm":(min_separation!=i64::MAX).then_some(min_separation),"minimum_stopping_authority_margin_mm":(min_stopping_margin!=i64::MAX).then_some(min_stopping_margin),
        "maximum_stopping_envelope_mm":max_stopping,"competing_owner_rejected":conflict_rejected,"unidentified_tail_clear_rejected":tail_early_rejected,
        "retained_owners":ledger.controller.records().iter().enumerate().filter_map(|(i,r)|r.grant.map(|g|json!({"resource":i,"train":g.owner.train.0,"phase":r.phase}))).collect::<Vec<_>>(),"trace":trace,
        "whole_line_capacity_accepted":false,"physical_output_authorised":false})
    );
}

#[derive(Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct LaunchBundle {
    leg: u32,
    corridor: u8,
    receiving_berth: u8,
    overlap: u8,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct JointInput {
    control: String,
    fault_at_ns: u64,
    bundles: Vec<LaunchBundle>,
}
#[derive(Clone)]
struct JournalLedger {
    ledger: ResourceLedger,
    records: Vec<(u64, ResourceEvent, bool)>,
}
impl std::ops::Deref for JournalLedger {
    type Target = ResourceLedger;
    fn deref(&self) -> &ResourceLedger {
        &self.ledger
    }
}
impl JournalLedger {
    fn apply(&mut self, event: &ResourceEvent, now: u64) -> Result<(), ResourceError> {
        let outcome = self.ledger.apply(event, now);
        // Rejected attempts also advance monotonic controller time. Retaining
        // their outcome makes replay cover those state transitions as well.
        self.records.push((now, event.clone(), outcome.is_ok()));
        outcome
    }
    fn replay_matches(&self, input: &Input) -> bool {
        let mut replay =
            ResourceLedger::new(input.model.clone(), input.configuration, BASE).unwrap();
        for (now, event, expected) in &self.records {
            if replay.apply(event, *now).is_ok() != *expected {
                return false;
            }
        }
        replay == self.ledger
    }
}
fn ready(request: StationLaunchRequest, sequence: u64, now: u64, epoch: u64) -> StationReadiness {
    StationReadiness {
        launch_id: request.id,
        configuration: request.configuration,
        owner: request.owner,
        epoch,
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
fn station_resource(ledger: &ResourceLedger, id: ResourceId) -> bool {
    ledger
        .station_launches
        .iter()
        .any(|l| l.phase != LaunchPhase::Cleared && l.request.resources().contains(&id))
}
fn protected_permits(
    ledger: &ResourceLedger,
    resource: ResourceId,
    owner: Owner,
    now: u64,
) -> bool {
    let index = usize::from(resource.0);
    let Some(p) = ledger.proofs[index] else {
        return false;
    };
    let Ok(specs) = ledger.model.specifications() else {
        return false;
    };
    ledger.integrity.get(&owner.train) == Some(&true)
        && p.permits(specs[index], ledger.controller.epoch(), now)
        && p.owns_or_clear(owner)
        && p.occupancy_integrity_proved
        && ledger.station_launches.iter().any(|l| {
            l.request.owner == owner
                && l.phase == LaunchPhase::Committed
                && l.request.resources().contains(&resource)
                && ledger.station_arrival_protected(l.request.id)
        })
}
fn clearance(
    ledger: &JournalLedger,
    launch: &StationLaunch,
    seq: &mut [u64],
    now: u64,
) -> StationClearance {
    let proofs = launch.request.resources().map(|id| {
        let i = usize::from(id.0);
        seq[i] += 1;
        let mut p = proof(id.0, seq[i], now, now, None, Some(launch.request.owner));
        p.epoch = ledger.controller.epoch();
        p
    });
    StationClearance {
        launch_id: launch.request.id,
        configuration: launch.request.configuration,
        owner: launch.request.owner,
        epoch: ledger.controller.epoch(),
        sequence: now,
        observed_ns: now,
        consist_length_mm: launch.request.consist_length_mm,
        tail_integrity_proved: true,
        all_cars_accounted_for: true,
        proofs,
    }
}
fn joint_replay(input: &Input) -> serde_json::Value {
    let j = input.joint.as_ref().unwrap();
    let segments = &input.model.routes[0].segments;
    assert!(!input.frames.is_empty() && input.frames.len() <= 30000 && segments.len() <= 32);
    let mut ledger = JournalLedger {
        ledger: ResourceLedger::new(input.model.clone(), input.configuration, BASE).unwrap(),
        records: Vec::new(),
    };
    let configs: BTreeMap<_, _> = input
        .model
        .trains
        .iter()
        .map(|t| (t.config.owner.train.0, t.config))
        .collect();
    for cfg in configs.values() {
        ledger
            .apply(
                &ResourceEvent::Integrity {
                    owner: cfg.owner,
                    proved: true,
                },
                BASE,
            )
            .unwrap();
    }
    let mut seq = vec![1_u64; segments.len()];
    for (i, s) in segments.iter().enumerate() {
        ledger
            .apply(
                &ResourceEvent::LocalProof(proof(s.resource.0, seq[i], BASE, BASE, None, None)),
                BASE,
            )
            .unwrap();
        ledger
            .apply(&ResourceEvent::Clear(s.resource), BASE)
            .unwrap();
    }
    let mut next_id = 1;
    let mut launched: BTreeMap<(u64, u32), u64> = BTreeMap::new();
    let mut failure = None;
    let mut frames = 0;
    let mut prepared = 0;
    let mut committed = 0;
    let mut cleared = 0;
    let mut ordinary_releases = 0;
    let mut forward_withdrawals = 0;
    let mut reservations = 0;
    let mut renewals = 0;
    let mut protected_checks = 0;
    let mut partial_clear_rejected = false;
    let mut bypass_rejected = false;
    let mut conflicting_rejected = false;
    let mut commit_order_rejected = false;
    let mut checkpoint_verified = false;
    let mut checkpoint_digest = None;
    let mut fault_applied = false;
    let mut restart_protected = false;
    let mut stale_proof_held = false;
    let mut min_margin = i64::MAX;
    let mut max_stopping = 0_u64;
    let mut max_active = 0;
    let mut min_separation = i64::MAX;
    let mut trace = Vec::new();
    let mut previous = BASE;
    'frames: for f in &input.frames {
        assert!(f.now_ns > previous && f.now_ns - previous <= input.sample_ns + 1);
        previous = f.now_ns;
        frames += 1;
        let positions: BTreeMap<_, _> = f.positions.iter().map(|p| (p.train, p)).collect();
        assert_eq!(positions.len(), f.positions.len());
        max_active = max_active.max(positions.len());
        let mut ordered: Vec<_> = positions.values().collect();
        ordered.sort_by_key(|p| p.front_mm);
        for pair in ordered.windows(2) {
            min_separation = min_separation.min(
                pair[1].front_mm - i64::from(configs[&pair[1].train].length_mm) - pair[0].front_mm,
            );
        }
        // Positive complete-consist clearance is one atomic StationClearance,
        // never three independent generic clears or a permission timeout.
        for launch in ledger.station_launches.clone() {
            if launch.phase == LaunchPhase::Cleared {
                continue;
            }
            let Some(p) = positions.get(&launch.request.owner.train.0) else {
                continue;
            };
            let cfg = configs[&p.train];
            let rear = p.front_mm
                - i64::from(cfg.length_mm)
                - i64::from(cfg.maximum_position_uncertainty_mm);
            let bound = launch
                .request
                .resources()
                .iter()
                .map(|r| segments[usize::from(r.0)].end_mm)
                .max()
                .unwrap();
            if rear > bound as i64 {
                let clear = clearance(&ledger, &launch, &mut seq, f.now_ns);
                for proof in clear.proofs {
                    ledger
                        .apply(&ResourceEvent::LocalProof(proof), f.now_ns)
                        .unwrap();
                }
                ledger
                    .apply(
                        &ResourceEvent::ClearStationLaunch(Box::new(clear)),
                        f.now_ns,
                    )
                    .unwrap();
                cleared += 1;
            }
        }
        for (i, s) in segments.iter().enumerate() {
            let old = ledger.controller.records()[i];
            let occupants: Vec<_> = positions
                .values()
                .filter(|p| {
                    p.front_mm >= s.start_mm as i64
                        && p.front_mm - i64::from(configs[&p.train].length_mm) <= s.end_mm as i64
                })
                .map(|p| configs[&p.train].owner)
                .collect();
            if occupants.len() > 1 {
                failure = Some(json!({"kind":"physical-overlap","resource":i,"now_ns":f.now_ns}));
                break 'frames;
            }
            if let Some(g) = old.grant {
                if let Some(p) = positions.get(&g.owner.train.0) {
                    let cfg = configs[&p.train];
                    let tail = p.front_mm
                        - i64::from(cfg.length_mm)
                        - i64::from(cfg.maximum_position_uncertainty_mm)
                        > s.end_mm as i64;
                    let stopped = p.velocity_mmps == 0
                        && p.front_mm + i64::from(cfg.maximum_position_uncertainty_mm)
                            < s.start_mm as i64;
                    if !station_resource(&ledger, s.resource) && (tail || stopped) {
                        ledger.apply(&ResourceEvent::Withdraw(g), f.now_ns).unwrap();
                        seq[i] += 1;
                        ledger
                            .apply(
                                &ResourceEvent::LocalProof(proof(
                                    i as u8,
                                    seq[i],
                                    f.now_ns,
                                    f.now_ns,
                                    None,
                                    Some(g.owner),
                                )),
                                f.now_ns,
                            )
                            .unwrap();
                        ledger
                            .apply(&ResourceEvent::Clear(s.resource), f.now_ns)
                            .unwrap();
                        if tail {
                            ordinary_releases += 1;
                        } else {
                            forward_withdrawals += 1;
                        }
                        continue;
                    }
                }
            }
            seq[i] += 1;
            let p = proof(
                i as u8,
                seq[i],
                f.now_ns,
                f.now_ns,
                occupants.first().copied(),
                None,
            );
            ledger
                .apply(&ResourceEvent::LocalProof(p), f.now_ns)
                .unwrap();
        }
        // Launch preparation/commit precedes the first nonzero-velocity frame
        // of each leg. Receiving berth and its true75m physical overlap remain
        // reserved until complete-tail clearance, even with progressive blocks.
        ordered.reverse();
        for p in &ordered {
            let Some(leg) = p.launch_leg else {
                continue;
            };
            if launched.contains_key(&(p.train, leg)) {
                continue;
            }
            assert_eq!(
                p.velocity_mmps, 0,
                "no launch may be invented after motion starts"
            );
            let bundle = j.bundles.iter().find(|b| b.leg == leg).unwrap();
            let cfg = configs[&p.train];
            let request = StationLaunchRequest {
                id: next_id,
                configuration: input.configuration,
                owner: cfg.owner,
                route: RouteId(1),
                direction: Direction::Forward,
                corridor: ResourceId(bundle.corridor),
                receiving_berth: ResourceId(bundle.receiving_berth),
                overlap: ResourceId(bundle.overlap),
                consist_length_mm: cfg.length_mm,
                permission_expires_ns: f.now_ns + LEASE_NS,
            };
            next_id += 1;
            if j.control == "joint-order-commit" && committed == 0 {
                commit_order_rejected = ledger
                    .apply(
                        &ResourceEvent::CommitStationLaunch {
                            id: request.id,
                            readiness: ready(request, 2, f.now_ns, 1),
                        },
                        f.now_ns,
                    )
                    .is_err();
            }
            let before = ledger.controller.records().to_vec();
            if let Err(error) = ledger.apply(
                &ResourceEvent::PrepareStationLaunch {
                    request,
                    readiness: ready(request, 1, f.now_ns, 1),
                },
                f.now_ns,
            ) {
                failure = Some(
                    json!({"kind":"station-prepare-rejected","error":format!("{error:?}"),"train":p.train,"leg":leg,"now_ns":f.now_ns,"stopped_before_departure":p.velocity_mmps==0,"atomic_no_partial_allocation":before==ledger.controller.records(),"headway_schedule_cannot_continue":true}),
                );
                break 'frames;
            }
            prepared += 1;
            if j.control == "joint-prepared-restart" {
                let bytes = serde_json::to_vec(&ledger.ledger).unwrap();
                let restored: ResourceLedger = serde_json::from_slice(&bytes).unwrap();
                checkpoint_verified = restored == ledger.ledger;
                checkpoint_digest = Some(osr_core::deployment::configuration_hash(&bytes));
                ledger.ledger = restored;
                let before: Vec<_> = ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect();
                ledger.apply(&ResourceEvent::Restart(2), f.now_ns).unwrap();
                let rejected = ledger
                    .apply(
                        &ResourceEvent::CommitStationLaunch {
                            id: request.id,
                            readiness: ready(request, 2, f.now_ns, 2),
                        },
                        f.now_ns,
                    )
                    .is_err();
                failure = Some(
                    json!({"kind":"station-prepared-restart-held","now_ns":f.now_ns,
                    "prepared_locks_retained":before==ledger.controller.records().iter().map(|r|r.grant).collect::<Vec<_>>(),
                    "commit_rejected_after_restart":rejected,"stopped_before_departure":p.velocity_mmps==0,
                    "automatic_resumption":false}),
                );
                break 'frames;
            }
            if j.control == "joint-conflicting-launch" && committed == 0 {
                let other = configs.values().find(|c| c.owner != request.owner).unwrap();
                let mut competing = request;
                competing.id = next_id;
                next_id += 1;
                competing.owner = other.owner;
                let before = ledger.controller.records().to_vec();
                conflicting_rejected = ledger
                    .apply(
                        &ResourceEvent::PrepareStationLaunch {
                            request: competing,
                            readiness: ready(competing, 1, f.now_ns, 1),
                        },
                        f.now_ns,
                    )
                    .is_err()
                    && before == ledger.controller.records();
            }
            let mut commit_ready = ready(request, 2, f.now_ns, 1);
            if j.control == "joint-partial-commit" {
                commit_ready.receive_brake_ready = false;
            }
            if let Err(error) = ledger.apply(
                &ResourceEvent::CommitStationLaunch {
                    id: request.id,
                    readiness: commit_ready,
                },
                f.now_ns,
            ) {
                failure = Some(
                    json!({"kind":"station-commit-rejected","error":format!("{error:?}"),"train":p.train,"now_ns":f.now_ns,"stopped_before_departure":true,"prepared_locks_retained":ledger.station_launch(request.id).is_some_and(|l|l.phase==LaunchPhase::Prepared)&&request.resources().iter().all(|r|ledger.controller.records()[usize::from(r.0)].grant.is_some()),"arrival_not_committed":!ledger.station_arrival_protected(request.id)}),
                );
                break 'frames;
            }
            committed += 1;
            launched.insert((p.train, leg), request.id);
            if !bypass_rejected {
                let g = ledger.station_launch(request.id).unwrap().grants[0];
                let before = ledger.controller.records().to_vec();
                bypass_rejected = ledger.apply(&ResourceEvent::Withdraw(g), f.now_ns).is_err()
                    && ledger
                        .apply(&ResourceEvent::Clear(g.resource), f.now_ns)
                        .is_err()
                    && before == ledger.controller.records();
                let launch = ledger.station_launch(request.id).unwrap().clone();
                let mut probe = ledger.clone();
                let mut probe_seq = seq.clone();
                let mut bad = clearance(&probe, &launch, &mut probe_seq, f.now_ns);
                bad.tail_integrity_proved = false;
                partial_clear_rejected = probe
                    .apply(&ResourceEvent::ClearStationLaunch(Box::new(bad)), f.now_ns)
                    .is_err()
                    && probe.station_arrival_protected(request.id);
            }
        }
        if !fault_applied && f.now_ns >= j.fault_at_ns && committed > 0 {
            fault_applied = true;
            let launch = ledger
                .station_launches
                .iter()
                .find(|l| l.phase == LaunchPhase::Committed)
                .unwrap()
                .clone();
            if j.control == "joint-replay" || j.control == "joint-restart" {
                let bytes = serde_json::to_vec(&ledger.ledger).unwrap();
                let restored: ResourceLedger = serde_json::from_slice(&bytes).unwrap();
                checkpoint_verified = restored == ledger.ledger;
                checkpoint_digest = Some(osr_core::deployment::configuration_hash(&bytes));
                ledger.ledger = restored;
            }
            if j.control == "joint-restart" {
                let before: Vec<_> = ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect();
                ledger.apply(&ResourceEvent::Restart(2), f.now_ns).unwrap();
                restart_protected = before
                    == ledger
                        .controller
                        .records()
                        .iter()
                        .map(|r| r.grant)
                        .collect::<Vec<_>>()
                    && ledger.station_arrival_protected(launch.request.id)
                    && ledger.station_launch(launch.request.id).unwrap().phase == LaunchPhase::Held;
                failure = Some(
                    json!({"kind":"station-restart-held","now_ns":f.now_ns,"arrival_protected":restart_protected,"automatic_resumption":false}),
                );
                break 'frames;
            }
            if j.control == "joint-stale-arrival" {
                let id = launch.request.receiving_berth;
                let i = usize::from(id.0);
                seq[i] += 1;
                let stale = proof(
                    id.0,
                    seq[i],
                    f.now_ns,
                    f.now_ns - 2 * INPUT_MAX_AGE_NS,
                    None,
                    None,
                );
                ledger
                    .apply(&ResourceEvent::LocalProof(stale), f.now_ns)
                    .unwrap();
                stale_proof_held = ledger.station_launch(launch.request.id).unwrap().phase
                    == LaunchPhase::Held
                    && ledger.station_arrival_protected(launch.request.id);
                failure = Some(
                    json!({"kind":"station-stale-arrival-held","now_ns":f.now_ns,"arrival_protected":stale_proof_held}),
                );
                break 'frames;
            }
            if j.control == "joint-receiving-fault" {
                ledger
                    .apply(
                        &ResourceEvent::HoldStationLaunch(StationFault {
                            launch_id: launch.request.id,
                            configuration: input.configuration,
                            owner: launch.request.owner,
                            epoch: 1,
                            sequence: 1,
                            observed_ns: f.now_ns,
                            reason: StationFaultReason::ReceiverUnavailable,
                        }),
                        f.now_ns,
                    )
                    .unwrap();
                failure = Some(
                    json!({"kind":"station-receiver-held","now_ns":f.now_ns,"arrival_protected":ledger.station_arrival_protected(launch.request.id),"phase":ledger.station_launch(launch.request.id).unwrap().phase}),
                );
                break 'frames;
            }
        }
        for p in ordered {
            let cfg = configs[&p.train];
            let rear = p.front_mm
                - i64::from(cfg.length_mm)
                - i64::from(cfg.maximum_position_uncertainty_mm);
            let stop = stopping_mm(
                p.velocity_mmps,
                cfg,
                input.maximum_acceleration_mmps2,
                input.sample_ns,
                f.now_ns - p.observed_ns,
                0,
            );
            max_stopping = max_stopping.max(stop);
            let end = p.front_mm + stop as i64;
            if end > segments.last().unwrap().end_mm as i64 {
                failure = Some(
                    json!({"kind":"unmodelled-authority-boundary","train":p.train,"now_ns":f.now_ns}),
                );
                break 'frames;
            }
            for s in segments
                .iter()
                .filter(|s| s.end_mm as i64 >= rear && s.start_mm as i64 <= end)
            {
                let i = usize::from(s.resource.0);
                if station_resource(&ledger, s.resource) {
                    if !protected_permits(&ledger, s.resource, cfg.owner, f.now_ns) {
                        failure = Some(
                            json!({"kind":"station-protection-missing","train":p.train,"resource":i,"now_ns":f.now_ns}),
                        );
                        break 'frames;
                    }
                    protected_checks += 1;
                } else {
                    let before = ledger.controller.records()[i];
                    if let Err(error) = ledger.apply(
                        &ResourceEvent::Reserve {
                            owner: cfg.owner,
                            resource: s.resource,
                            route: RouteId(1),
                            direction: Direction::Forward,
                        },
                        f.now_ns,
                    ) {
                        failure = Some(
                            json!({"kind":"progressive-reservation-rejected","error":format!("{error:?}"),"train":p.train,"resource":i,"now_ns":f.now_ns}),
                        );
                        break 'frames;
                    }
                    if before.grant.is_some() {
                        renewals += 1;
                    } else {
                        reservations += 1;
                    }
                    if !ledger.permits(input.model.resources[i].section, cfg.owner.train, f.now_ns)
                    {
                        failure = Some(
                            json!({"kind":"permission-missing","train":p.train,"resource":i,"now_ns":f.now_ns}),
                        );
                        break 'frames;
                    }
                }
            }
            let authority_end = segments
                .iter()
                .filter(|s| s.start_mm as i64 <= end && s.end_mm as i64 >= rear)
                .map(|s| s.end_mm as i64)
                .max()
                .unwrap();
            min_margin = min_margin.min(authority_end - end);
        }
        if frames % 100 == 0 {
            trace.push(json!({"now_ns":f.now_ns,"trains":positions.values().map(|p|json!({"train":p.train,"front_mm":p.front_mm,"speed_mmps":p.velocity_mmps})).collect::<Vec<_>>(),"station_launches":ledger.station_launches.iter().map(|l|json!({"id":l.request.id,"train":l.request.owner.train.0,"phase":l.phase})).collect::<Vec<_>>() }));
        }
    }
    let replay_equal = ledger.replay_matches(input);
    let journal_bytes = serde_json::to_vec(&ledger.records).unwrap();
    let journal_digest = osr_core::deployment::configuration_hash(&journal_bytes);
    json!({"schema":"osr-line-capacity-joint-replay/1","study_pass":failure.is_none(),"failure":failure,"frames_executed":frames,
        "prepared_launches":prepared,"committed_launches":committed,"cleared_launches":cleared,"ordinary_full_tail_releases":ordinary_releases,"stopped_forward_withdrawals":forward_withdrawals,"progressive_reservations":reservations,"progressive_renewals":renewals,"station_protection_checks":protected_checks,
        "maximum_active_trains":max_active,"minimum_train_separation_mm":(min_separation!=i64::MAX).then_some(min_separation),"minimum_stopping_authority_margin_mm":(min_margin!=i64::MAX).then_some(min_margin),"maximum_stopping_envelope_mm":max_stopping,
        "individual_clear_bypass_rejected":bypass_rejected,"partial_tail_clear_rejected":partial_clear_rejected,"conflicting_launch_rejected":conflicting_rejected,"commit_before_prepare_rejected":commit_order_rejected,
        "checkpoint_verified":checkpoint_verified,"checkpoint_sha256":checkpoint_digest,"restart_arrival_protected":restart_protected,"stale_arrival_held":stale_proof_held,"journal_records":ledger.records.len(),"journal_sha256":journal_digest,"durable_event_replay_equal":replay_equal,
        "retained_launches":ledger.station_launches.iter().filter(|l|l.phase!=LaunchPhase::Cleared).map(|l|json!({"id":l.request.id,"train":l.request.owner.train.0,"phase":l.phase,"arrival_protected":ledger.station_arrival_protected(l.request.id)})).collect::<Vec<_>>(),"trace":trace,
        "whole_line_capacity_accepted":false,"physical_output_authorised":false})
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct ContractInput {
    control: String,
    fault_at_ns: u64,
    receiving_berth: u8,
    policy: ProgressivePolicy,
}
struct ContractJournal {
    domain: ProgressiveDomain,
    records: Vec<(u64, ProgressiveEvent, bool)>,
}
impl ContractJournal {
    fn apply(&mut self, event: ProgressiveEvent, now: u64) -> Result<(), ProgressiveError> {
        let result = self.domain.apply(&event, now);
        self.records.push((now, event, result.is_ok()));
        result
    }
    fn replay_equal(&self, input: &Input) -> bool {
        let policy = input.contract.as_ref().unwrap().policy;
        let mut fold =
            ProgressiveDomain::new(input.model.clone(), input.configuration, policy, BASE).unwrap();
        for (now, event, ok) in &self.records {
            if fold.apply(event, *now).is_ok() != *ok {
                return false;
            }
        }
        fold == self.domain
    }
}
#[derive(Clone)]
struct BrakePlant {
    front_m: f64,
    speed_mps: f64,
    reaction_left_s: f64,
    deceleration_mps2: f64,
    authority_end_mm: u64,
    margin_mm: i64,
    trace: Vec<serde_json::Value>,
}
impl BrakePlant {
    fn step(&mut self, mut dt: f64, max_acc: f64) {
        while dt > 1e-10 {
            let (part, a) = if self.reaction_left_s > 1e-10 {
                (dt.min(self.reaction_left_s), max_acc)
            } else if self.speed_mps > 0. {
                (
                    dt.min(self.speed_mps / self.deceleration_mps2),
                    -self.deceleration_mps2,
                )
            } else {
                break;
            };
            self.front_m += self.speed_mps * part + 0.5 * a * part * part;
            self.speed_mps = (self.speed_mps + a * part).max(0.);
            self.reaction_left_s = (self.reaction_left_s - part).max(0.);
            dt -= part;
        }
    }
}
fn contract_replay(input: &Input) -> serde_json::Value {
    let c = input.contract.as_ref().unwrap();
    let segments = &input.model.routes[0].segments;
    let mut journal = ContractJournal {
        domain: ProgressiveDomain::new(input.model.clone(), input.configuration, c.policy, BASE)
            .unwrap(),
        records: Vec::new(),
    };
    let configs: BTreeMap<_, _> = input
        .model
        .trains
        .iter()
        .map(|t| (t.config.owner.train.0, t.config))
        .collect();
    for cfg in configs.values() {
        journal
            .apply(
                ProgressiveEvent::Evidence(ResourceEvent::Integrity {
                    owner: cfg.owner,
                    proved: true,
                }),
                BASE,
            )
            .unwrap();
    }
    let mut seq = vec![1_u64; segments.len()];
    for (i, s) in segments.iter().enumerate() {
        journal
            .apply(
                ProgressiveEvent::Evidence(ResourceEvent::LocalProof(proof(
                    i as u8, seq[i], BASE, BASE, None, None,
                ))),
                BASE,
            )
            .unwrap();
        journal
            .apply(
                ProgressiveEvent::Evidence(ResourceEvent::Clear(s.resource)),
                BASE,
            )
            .unwrap();
    }
    if c.control == "contract-closed-arrival" {
        journal
            .apply(
                ProgressiveEvent::Evidence(ResourceEvent::Block(ResourceId(c.receiving_berth))),
                BASE,
            )
            .unwrap();
    }
    let mut current: BTreeMap<u64, (u64, u32)> = BTreeMap::new();
    let mut train_seq: BTreeMap<u64, u64> = configs.keys().map(|id| (*id, 0)).collect();
    let mut next_id = 1;
    let mut failure = None;
    let mut frames = 0;
    let mut prepared = 0;
    let mut committed = 0;
    let mut arrived = 0;
    let mut released = 0;
    let mut forward = 0;
    let mut extensions = 0;
    let mut partial_commit_fenced = false;
    let mut order_rejected = false;
    let mut conflict_rejected = false;
    let mut snapshot_fenced = false;
    let mut snapshot_digest = None;
    let mut restart_owners_retained = false;
    let mut fault_done = false;
    let mut brakes: BTreeMap<u64, BrakePlant> = BTreeMap::new();
    let mut max_active = 0;
    let mut min_separation = i64::MAX;
    let mut min_margin = i64::MAX;
    let mut trace = Vec::new();
    let mut previous = BASE;
    'frames: for f in &input.frames {
        assert!(f.now_ns > previous && f.now_ns - previous <= input.sample_ns + 1);
        let dt = (f.now_ns - previous) as f64 / 1e9;
        previous = f.now_ns;
        frames += 1;
        let mut positions: Vec<Position> = f
            .positions
            .iter()
            .map(|p| Position {
                train: p.train,
                front_mm: p.front_mm,
                velocity_mmps: p.velocity_mmps,
                observed_ns: p.observed_ns,
                integrity_proved: p.integrity_proved,
                independent_brake_ready: p.independent_brake_ready,
                launch_leg: p.launch_leg,
            })
            .collect();
        for p in &mut positions {
            if let Some(b) = brakes.get_mut(&p.train) {
                b.step(dt, f64::from(c.policy.maximum_acceleration_mmps2) / 1000.);
                p.front_mm = (b.front_m * 1000.).round() as i64;
                p.velocity_mmps = (b.speed_mps * 1000.).ceil() as u32;
                p.observed_ns = f.now_ns;
                p.launch_leg = None;
                b.trace.push(json!({"now_ns":f.now_ns,"front_m":b.front_m,"speed_m_s":b.speed_mps,"owned_authority_end_mm":b.authority_end_mm}));
                if p.front_mm + i64::from(configs[&p.train].stop_margin_mm)
                    > b.authority_end_mm as i64
                {
                    failure = Some(
                        json!({"kind":"braking-plant-exceeded-owned-authority","train":p.train,"now_ns":f.now_ns}),
                    );
                    break 'frames;
                }
            }
        }
        max_active = max_active.max(positions.len());
        positions.sort_by_key(|p| p.front_mm);
        for pair in positions.windows(2) {
            min_separation = min_separation.min(
                pair[1].front_mm - i64::from(configs[&pair[1].train].length_mm) - pair[0].front_mm,
            );
        }
        for (i, s) in segments.iter().enumerate() {
            let occupants: Vec<_> = positions
                .iter()
                .filter(|p| {
                    p.front_mm >= s.start_mm as i64
                        && p.front_mm - i64::from(configs[&p.train].length_mm) <= s.end_mm as i64
                })
                .map(|p| configs[&p.train].owner)
                .collect();
            if occupants.len() > 1 {
                failure = Some(json!({"kind":"physical-overlap","resource":i,"now_ns":f.now_ns}));
                break 'frames;
            }
            seq[i] += 1;
            let pr = proof(
                i as u8,
                seq[i],
                f.now_ns,
                f.now_ns,
                occupants.first().copied(),
                None,
            );
            journal
                .apply(
                    ProgressiveEvent::Evidence(ResourceEvent::LocalProof(pr)),
                    f.now_ns,
                )
                .unwrap();
        }
        positions.reverse();
        for p in &positions {
            let cfg = configs[&p.train];
            let counter = train_seq.get_mut(&p.train).unwrap();
            *counter += 1;
            let mut r = ProgressiveReadiness {
                configuration: input.configuration,
                owner: cfg.owner,
                epoch: 1,
                sequence: *counter,
                observed_ns: p.observed_ns,
                front_mm: u64::try_from(p.front_mm).unwrap(),
                velocity_mmps: p.velocity_mmps,
                independent_brake_ready: p.independent_brake_ready,
                integrity_proved: p.integrity_proved,
                support_healthy: true,
                minimum_gap_um: 6000,
                maximum_gap_um: 8000,
            };
            let trigger = p.train == 101 && f.now_ns >= c.fault_at_ns;
            if trigger {
                match c.control.as_str() {
                    "contract-stale-ready" => r.observed_ns = f.now_ns - 2 * INPUT_MAX_AGE_NS,
                    "contract-brake-loss" => r.independent_brake_ready = false,
                    "contract-gap-fault" => r.minimum_gap_um = 2999,
                    "contract-rollback" => r.front_mm = r.front_mm.saturating_sub(5000),
                    "contract-integrity-loss" => {
                        r.integrity_proved = false;
                        if !fault_done {
                            journal
                                .apply(
                                    ProgressiveEvent::Evidence(ResourceEvent::Integrity {
                                        owner: cfg.owner,
                                        proved: false,
                                    }),
                                    f.now_ns,
                                )
                                .unwrap();
                            fault_done = true;
                        }
                    }
                    _ => {}
                }
            }
            let old = current.get(&p.train).copied();
            let new_leg = if let Some((id, leg)) = old {
                journal.domain.departure(id).unwrap().phase == ProgressivePhase::Arrived
                    && p.launch_leg.is_some_and(|n| n > leg)
            } else {
                true
            };
            if new_leg {
                assert_eq!(r.velocity_mmps, 0, "departure must prepare before motion");
                let leg = p.launch_leg.unwrap();
                let request = DepartureRequest {
                    id: next_id,
                    owner: cfg.owner,
                    route: RouteId(1),
                    direction: Direction::Forward,
                    configuration: input.configuration,
                    readiness: r,
                };
                next_id += 1;
                if c.control == "contract-order-commit" && committed == 0 {
                    order_rejected = journal
                        .apply(
                            ProgressiveEvent::Commit {
                                id: request.id,
                                readiness: r,
                            },
                            f.now_ns,
                        )
                        .is_err();
                }
                if let Err(e) = journal.apply(ProgressiveEvent::Prepare(request), f.now_ns) {
                    failure = Some(
                        json!({"kind":"progressive-prepare-held","error":format!("{e:?}"),"train":p.train,"now_ns":f.now_ns}),
                    );
                    break 'frames;
                }
                prepared += 1;
                if c.control == "contract-conflicting-prepare" && committed == 0 {
                    let other = configs
                        .values()
                        .find(|v| v.owner != cfg.owner)
                        .unwrap()
                        .owner;
                    let mut competing = request;
                    competing.id = next_id;
                    next_id += 1;
                    competing.owner = other;
                    competing.readiness.owner = other;
                    let before = journal.domain.ledger().controller.records().to_vec();
                    conflict_rejected = journal
                        .apply(ProgressiveEvent::Prepare(competing), f.now_ns)
                        .is_err()
                        && before == journal.domain.ledger().controller.records();
                }
                if c.control == "contract-prepared-restart" {
                    let bytes = serde_json::to_vec(&journal.domain).unwrap();
                    let restored: ProgressiveDomain = serde_json::from_slice(&bytes).unwrap();
                    snapshot_fenced =
                        restored.restore_fenced() && !restored.may_move(request.id, f.now_ns);
                    snapshot_digest = Some(osr_core::deployment::configuration_hash(&bytes));
                    let owners = journal
                        .domain
                        .ledger()
                        .controller
                        .records()
                        .iter()
                        .map(|v| v.grant)
                        .collect::<Vec<_>>();
                    journal
                        .apply(ProgressiveEvent::Restart { new_epoch: 2 }, f.now_ns)
                        .unwrap();
                    restart_owners_retained = owners
                        == journal
                            .domain
                            .ledger()
                            .controller
                            .records()
                            .iter()
                            .map(|v| v.grant)
                            .collect::<Vec<_>>();
                    let rejected = journal
                        .apply(
                            ProgressiveEvent::Commit {
                                id: request.id,
                                readiness: r,
                            },
                            f.now_ns,
                        )
                        .is_err();
                    failure = Some(
                        json!({"kind":"progressive-prepared-restart-held","commit_rejected":rejected,"now_ns":f.now_ns}),
                    );
                    break 'frames;
                }
                *counter += 1;
                r.sequence = *counter;
                if c.control == "contract-partial-commit" {
                    r.independent_brake_ready = false;
                }
                if let Err(e) = journal.apply(
                    ProgressiveEvent::Commit {
                        id: request.id,
                        readiness: r,
                    },
                    f.now_ns,
                ) {
                    partial_commit_fenced = journal.domain.departure(request.id).unwrap().phase
                        == ProgressivePhase::Held
                        && !journal.domain.may_move(request.id, f.now_ns);
                    failure = Some(
                        json!({"kind":"progressive-commit-held","error":format!("{e:?}"),"now_ns":f.now_ns}),
                    );
                    break 'frames;
                }
                committed += 1;
                current.insert(p.train, (request.id, leg));
            } else {
                let (id, _) = old.unwrap();
                let phase = journal.domain.departure(id).unwrap().phase;
                if trigger
                    && !fault_done
                    && (c.control == "contract-journal"
                        || c.control == "contract-committed-restart")
                {
                    fault_done = true;
                    let bytes = serde_json::to_vec(&journal.domain).unwrap();
                    let restored: ProgressiveDomain = serde_json::from_slice(&bytes).unwrap();
                    snapshot_fenced = restored.restore_fenced() && !restored.may_move(id, f.now_ns);
                    snapshot_digest = Some(osr_core::deployment::configuration_hash(&bytes));
                    if c.control == "contract-committed-restart" {
                        let owners = journal
                            .domain
                            .ledger()
                            .controller
                            .records()
                            .iter()
                            .map(|v| v.grant)
                            .collect::<Vec<_>>();
                        journal
                            .apply(ProgressiveEvent::Restart { new_epoch: 2 }, f.now_ns)
                            .unwrap();
                        restart_owners_retained = owners
                            == journal
                                .domain
                                .ledger()
                                .controller
                                .records()
                                .iter()
                                .map(|v| v.grant)
                                .collect::<Vec<_>>();
                        failure = Some(
                            json!({"kind":"progressive-committed-restart-held","now_ns":f.now_ns}),
                        );
                        break 'frames;
                    }
                }
                let event = if brakes.contains_key(&p.train) {
                    ProgressiveEvent::ObserveHeld { id, readiness: r }
                } else if phase == ProgressivePhase::Committed && p.launch_leg.is_none() {
                    ProgressiveEvent::ArriveStopped { id, readiness: r }
                } else {
                    ProgressiveEvent::Extend { id, readiness: r }
                };
                let arrival = matches!(event, ProgressiveEvent::ArriveStopped { .. });
                if let Err(e) = journal.apply(event, f.now_ns) {
                    let held = journal.domain.departure(id).unwrap().clone();
                    if c.control == "contract-closed-arrival"
                        && brakes.is_empty()
                        && held.phase == ProgressivePhase::Held
                        && held.hold_stopping_margin_mm.is_some_and(|v| v >= 0)
                    {
                        let margin = held.hold_stopping_margin_mm.unwrap();
                        brakes.insert(
                            p.train,
                            BrakePlant {
                                front_m: r.front_mm as f64 / 1000.
                                    + f64::from(cfg.maximum_position_uncertainty_mm) / 1000.,
                                speed_mps: (f64::from(r.velocity_mmps)
                                    + f64::from(c.policy.velocity_error_mmps))
                                    / 1000.,
                                reaction_left_s: f64::from(cfg.reaction_time_ms) / 1000.,
                                deceleration_mps2: f64::from(cfg.minimum_deceleration_mmps2)
                                    / 1000.,
                                authority_end_mm: held.protected_end_mm,
                                margin_mm: margin,
                                trace: Vec::new(),
                            },
                        );
                        failure = Some(
                            json!({"kind":"progressive-arrival-authority-held","error":format!("{e:?}"),"train":p.train,"now_ns":f.now_ns,"retained_authority_end_mm":held.protected_end_mm,"immediate_stopping_margin_mm":margin,"stopping_has_no_next_sample_credit":true}),
                        );
                    } else {
                        failure = Some(
                            json!({"kind":"progressive-evidence-held","error":format!("{e:?}"),"train":p.train,"now_ns":f.now_ns,"phase":held.phase,"owners_retained":true}),
                        );
                        break 'frames;
                    }
                } else if arrival {
                    arrived += 1;
                } else {
                    extensions += 1;
                }
            }
            let (id, _) = current[&p.train];
            let state = journal.domain.departure(id).unwrap().clone();
            if state.phase == ProgressivePhase::Committed && !journal.domain.may_move(id, f.now_ns)
            {
                failure = Some(
                    json!({"kind":"progressive-permission-missing","train":p.train,"now_ns":f.now_ns}),
                );
                break 'frames;
            }
            if matches!(
                state.phase,
                ProgressivePhase::Committed | ProgressivePhase::Arrived
            ) {
                let r = state.last_readiness;
                let tail = r.front_mm.saturating_sub(
                    u64::from(cfg.length_mm) + u64::from(cfg.maximum_position_uncertainty_mm),
                );
                let grants: Vec<_> = journal
                    .domain
                    .ledger()
                    .controller
                    .records()
                    .iter()
                    .filter_map(|v| v.grant.filter(|g| g.owner == cfg.owner))
                    .collect();
                for g in grants {
                    let i = usize::from(g.resource.0);
                    let s = segments[i];
                    let full_tail = tail > s.end_mm;
                    let stopped = state.phase == ProgressivePhase::Arrived
                        && r.velocity_mmps == 0
                        && r.front_mm + u64::from(cfg.maximum_position_uncertainty_mm) < s.start_mm;
                    if full_tail || stopped {
                        seq[i] += 1;
                        let clear = proof(
                            g.resource.0,
                            seq[i],
                            f.now_ns,
                            f.now_ns,
                            None,
                            Some(cfg.owner),
                        );
                        journal
                            .apply(
                                ProgressiveEvent::Release {
                                    id,
                                    readiness: r,
                                    resource: g.resource,
                                    proof: clear,
                                },
                                f.now_ns,
                            )
                            .unwrap();
                        if full_tail {
                            released += 1;
                        } else {
                            forward += 1;
                        }
                    }
                }
                if state.phase == ProgressivePhase::Committed {
                    let end = journal.domain.departure(id).unwrap().protected_end_mm;
                    let required = journal.domain.required_stop_front_mm(id, f.now_ns).unwrap();
                    min_margin = min_margin.min(end as i64 - required as i64);
                }
            }
        }
        if frames % 100 == 0 {
            trace.push(json!({"now_ns":f.now_ns,"trains":positions.iter().map(|p|json!({"train":p.train,"front_mm":p.front_mm,"speed_mmps":p.velocity_mmps})).collect::<Vec<_>>(),"contracts":current.values().map(|(id,_)|journal.domain.departure(*id).unwrap()).collect::<Vec<_>>()}));
        }
        if !brakes.is_empty() && brakes.values().all(|b| b.speed_mps <= 1e-9) {
            break;
        }
    }
    let replay = journal.replay_equal(input);
    let bytes = serde_json::to_vec(&journal.records).unwrap();
    let hash = osr_core::deployment::configuration_hash(&bytes);
    let plant_pass = !brakes.is_empty()
        && brakes.iter().all(|(train, b)| {
            b.speed_mps <= 1e-9
                && b.margin_mm >= 0
                && b.front_m * 1000. + f64::from(configs[train].stop_margin_mm)
                    <= b.authority_end_mm as f64
                && journal.domain.departure(current[train].0).unwrap().phase
                    == ProgressivePhase::HeldStopped
        });
    json!({"schema":"osr-progressive-departure-replay/1","protocol":PROTOCOL,"study_pass":failure.is_none(),"failure":failure,"frames_executed":frames,"prepared_departures":prepared,"committed_departures":committed,"stopped_arrivals":arrived,"authority_extensions":extensions,"full_tail_releases":released,"stopped_forward_withdrawals":forward,"maximum_active_trains":max_active,"minimum_train_separation_mm":(min_separation!=i64::MAX).then_some(min_separation),"minimum_stopping_authority_margin_mm":(min_margin!=i64::MAX).then_some(min_margin),
        "partial_commit_fenced":partial_commit_fenced,"commit_order_rejected":order_rejected,"conflicting_prepare_rejected":conflict_rejected,"snapshot_restore_fenced":snapshot_fenced,"snapshot_sha256":snapshot_digest,"restart_owners_retained":restart_owners_retained,"journal_records":journal.records.len(),"journal_sha256":hash,"durable_event_replay_equal":replay,
        "braking_plant_pass":plant_pass,"braking_plants":brakes.iter().map(|(train,b)|json!({"train":train,"initial_hold_margin_mm":b.margin_mm,"final_front_m":b.front_m,"final_speed_m_s":b.speed_mps,"owned_authority_end_mm":b.authority_end_mm,"trace":b.trace})).collect::<Vec<_>>(),"retained_contracts":journal.domain.departures(),"retained_owners":journal.domain.ledger().controller.records().iter().enumerate().filter_map(|(i,v)|v.grant.map(|g|json!({"resource":i,"train":g.owner.train.0,"phase":v.phase}))).collect::<Vec<_>>(),"trace":trace,"whole_line_capacity_accepted":false,"physical_output_authorised":false})
}
