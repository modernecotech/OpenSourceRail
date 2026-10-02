use osr_core::{resources::*, Direction, RouteId, TrainId};
use osr_interlocking::resources::*;

const CFG: ConfigurationId = [7; 32];
const C: ControllerId = ControllerId(900);
const A: Owner = Owner {
    train: TrainId(101),
    session: 1,
};
const B: Owner = Owner {
    train: TrainId(102),
    session: 1,
};
const R: RouteId = RouteId(1);
const SPECS: [ResourceSpec; 2] = [
    ResourceSpec {
        id: ResourceId(0),
        controller: C,
        conflicts: 3,
        points_required: true,
    },
    ResourceSpec {
        id: ResourceId(1),
        controller: C,
        conflicts: 3,
        points_required: true,
    },
];
fn proof(resource: u8, seq: u64, epoch: u64, now: u64) -> ProtectionProof {
    ProtectionProof {
        resource: ResourceId(resource),
        controller: C,
        epoch,
        sequence: seq,
        observed_ns: now,
        clear: true,
        clearance_safe: true,
        cleared_owner: Some(A),
        occupant: None,
        occupancy_integrity_proved: true,
        points_locked_and_proved: true,
        proved_route: Some(R),
        restriction: Restriction::Open,
    }
}
fn reconciled() -> ResourceController {
    let mut c = ResourceController::boot(CFG, C, 1, SPECS, 1).unwrap();
    for i in 0..2 {
        c.verified_clear(proof(i, 1, 1, 1), 1).unwrap();
    }
    c
}

#[test]
fn timeout_retains_conflicting_lock_and_clearance_is_verified() {
    let mut c = reconciled();
    let g = c
        .request(A, R, Direction::Forward, proof(0, 2, 1, 2), 2)
        .unwrap();
    c.occupied(g, 2).unwrap();
    c.advance_time(g.valid_until_ns).unwrap();
    assert_eq!(c.records()[0].phase, Phase::ReleasePending);
    assert_eq!(c.records()[0].grant.unwrap().owner, A);
    assert_eq!(
        c.request(
            B,
            R,
            Direction::Forward,
            proof(1, 3, 1, g.valid_until_ns),
            g.valid_until_ns
        ),
        Err(ResourceError::Conflict)
    );
    let mut no_integrity = proof(0, 3, 1, g.valid_until_ns);
    no_integrity.clear = false;
    assert_eq!(
        c.verified_clear(no_integrity, g.valid_until_ns),
        Err(ResourceError::Proof)
    );
    c.verified_clear(proof(0, 3, 1, g.valid_until_ns), g.valid_until_ns)
        .unwrap();
    assert!(c
        .request(
            B,
            R,
            Direction::Forward,
            proof(1, 4, 1, g.valid_until_ns),
            g.valid_until_ns
        )
        .is_ok());
}

#[test]
fn restart_and_replayed_clearance_cannot_open_track() {
    let mut c = reconciled();
    let g = c
        .request(A, R, Direction::Forward, proof(0, 2, 1, 2), 2)
        .unwrap();
    c.restart(2, 3).unwrap();
    assert_eq!(c.records()[0].phase, Phase::Unknown);
    assert_eq!(c.records()[0].grant, Some(g));
    assert_eq!(
        c.request(B, R, Direction::Forward, proof(1, 3, 2, 3), 3),
        Err(ResourceError::Conflict)
    );
    assert_eq!(
        c.verified_clear(proof(0, 3, 1, 3), 3),
        Err(ResourceError::Proof)
    );
    assert_eq!(
        c.verified_clear(proof(0, 2, 2, 3), 3),
        Err(ResourceError::Proof)
    );
    let ready = 3 + LEASE_NS + CLOCK_SKEW_NS;
    c.verified_clear(proof(0, 3, 2, ready), ready).unwrap();
    c.verified_clear(proof(1, 3, 2, ready), ready).unwrap();
    assert!(c
        .request(B, R, Direction::Forward, proof(1, 4, 2, ready), ready)
        .is_ok());
    assert_eq!(c.begin_release(g, ready), Err(ResourceError::Ownership));
    assert_eq!(c.restart(2, ready), Err(ResourceError::Epoch));
}

#[test]
fn active_reservation_cannot_be_cleared_or_transferred_by_session_route_or_direction() {
    let mut c = reconciled();
    let g = c
        .request(A, R, Direction::Forward, proof(0, 2, 1, 2), 2)
        .unwrap();
    assert_eq!(
        c.verified_clear(proof(0, 3, 1, 3), 3),
        Err(ResourceError::Phase)
    );
    assert_eq!(
        c.request(
            Owner { session: 2, ..A },
            R,
            Direction::Forward,
            proof(0, 3, 1, 3),
            3
        ),
        Err(ResourceError::Conflict)
    );
    assert_eq!(
        c.request(A, R, Direction::Reverse, proof(0, 3, 1, 3), 3),
        Err(ResourceError::Conflict)
    );
    assert_eq!(
        c.request(A, RouteId(2), Direction::Forward, proof(0, 3, 1, 3), 3),
        Err(ResourceError::Proof)
    );
    c.begin_release(g, 3).unwrap();
    assert_eq!(c.records()[0].phase, Phase::ReleasePending);
    assert_eq!(
        c.request(B, R, Direction::Forward, proof(1, 4, 1, 4), 4),
        Err(ResourceError::Conflict)
    );
}

#[test]
fn block_and_missing_proving_survive_timer_and_restart() {
    let mut c = reconciled();
    c.block(ResourceId(0)).unwrap();
    c.restart(2, 3).unwrap();
    assert_eq!(
        c.verified_clear(
            proof(0, 5, 2, 3 + LEASE_NS + CLOCK_SKEW_NS),
            3 + LEASE_NS + CLOCK_SKEW_NS
        ),
        Err(ResourceError::Phase)
    );
    let now = 4 + LEASE_NS + CLOCK_SKEW_NS;
    let mut p = proof(1, 6, 2, now);
    p.points_locked_and_proved = false;
    assert_eq!(
        c.request(B, R, Direction::Forward, p, now),
        Err(ResourceError::Proof)
    );
    assert_eq!(c.advance_time(5), Err(ResourceError::Time));
}

#[test]
fn an_empty_detector_and_restart_timeout_are_not_proofs_of_safe_release() {
    let mut c = reconciled();
    let g = c
        .request(A, R, Direction::Forward, proof(0, 2, 1, 2), 2)
        .unwrap();
    c.begin_release(g, 3).unwrap();
    let mut p = proof(0, 3, 1, 3);
    p.clearance_safe = false;
    assert_eq!(c.verified_clear(p, 3), Err(ResourceError::Proof));
    p.clearance_safe = true;
    p.cleared_owner = Some(B);
    assert_eq!(c.verified_clear(p, 3), Err(ResourceError::Proof));
    c.restart(2, 4).unwrap();
    assert_eq!(
        c.verified_clear(proof(0, 4, 2, 5), 5),
        Err(ResourceError::Time)
    );
    c.advance_time(4 + LEASE_NS + CLOCK_SKEW_NS).unwrap();
    assert_eq!(c.records()[0].phase, Phase::Unknown);
    assert_eq!(c.records()[0].grant.unwrap().owner, A);
}

#[test]
fn restart_reconciliation_returns_permission_only_to_verified_retained_owner() {
    let mut c = reconciled();
    let g = c
        .request(A, R, Direction::Forward, proof(0, 2, 1, 2), 2)
        .unwrap();
    c.occupied(g, 2).unwrap();
    c.restart(2, 3).unwrap();
    let mut p = proof(0, 3, 2, 4);
    p.clear = false;
    p.occupant = Some(B);
    assert_eq!(c.reconcile_owner(p, 4), Err(ResourceError::Proof));
    p.occupant = Some(A);
    p.occupancy_integrity_proved = false;
    assert_eq!(c.reconcile_owner(p, 4), Err(ResourceError::Proof));
    p.occupancy_integrity_proved = true;
    let fresh = c.reconcile_owner(p, 4).unwrap();
    assert_eq!(fresh.owner, A);
    assert_eq!(fresh.epoch, 2);
    assert_eq!(c.records()[0].phase, Phase::Occupied);
    assert_eq!(
        c.request(B, R, Direction::Forward, proof(1, 4, 2, 4), 4),
        Err(ResourceError::Conflict)
    );
}

#[test]
fn exhaustive_bounded_schedules_keep_mutual_exclusion() {
    // Explore actual Rust transitions, including all orderings of requests,
    // occupancy, expiry, release, clear proofs, blocking and restart. This is
    // bounded exploration, not an unbounded distributed refinement proof.
    fn explore(c: ResourceController, now: u64, depth: u8) -> usize {
        let occupied: Vec<_> = c
            .records()
            .iter()
            .filter(|r| r.phase != Phase::Available && r.grant.is_some())
            .collect();
        assert!(
            occupied.len() <= 1,
            "conflicting resources both locked: {c:?}"
        );
        if depth == 0 {
            return 1;
        }
        let mut visits = 1;
        for action in 0..10 {
            let mut next = c.clone();
            let time = now + 1;
            let sequence = next
                .records()
                .iter()
                .map(|r| r.last_proof_sequence)
                .max()
                .unwrap()
                + 1;
            let epoch = next.epoch();
            match action {
                0 | 1 => {
                    let _ = next.request(
                        if action == 0 { A } else { B },
                        R,
                        Direction::Forward,
                        proof(action as u8, sequence, epoch, time),
                        time,
                    );
                }
                2 | 3 => {
                    if let Some(g) = next.records()[action - 2].grant {
                        let _ = next.occupied(g, time);
                    }
                }
                4 => {
                    let _ = next.advance_time(time + LEASE_NS);
                }
                5 => {
                    for i in 0..2 {
                        if let Some(g) = next.records()[i].grant {
                            let _ = next.begin_release(g, time);
                        }
                    }
                }
                6 | 7 => {
                    let mut p = proof((action - 6) as u8, sequence, epoch, time);
                    p.cleared_owner = next.records()[action - 6].grant.map(|g| g.owner);
                    let _ = next.verified_clear(p, time);
                }
                8 => {
                    let _ = next.restart(epoch + 1, time);
                }
                _ => {
                    let _ = next.block(ResourceId(0));
                }
            }
            visits += explore(
                next,
                if action == 4 { time + LEASE_NS } else { time },
                depth - 1,
            );
        }
        visits
    }
    assert_eq!(explore(reconciled(), 1, 5), 111_111);
}
