//! Bounded stopped recovery within ONE local conflict domain. No moving
//! recovery, controller-to-controller authority transfer, authenticated storage,
//! detector qualification or physical output is implemented here.
use super::*;
use std::collections::BTreeMap;

pub const RECOVERY_PROTOCOL: &str = "osr-progressive-stopped-recovery/1";

impl ProgressiveDomain {
    pub(super) fn reconcile_stopped(
        &mut self,
        configuration: ConfigurationId,
        expected_policy: ProgressivePolicy,
        expected_model: &RailwayModel,
        observations: &[ProgressiveReadiness],
        now: u64,
    ) -> Result<(), ProgressiveError> {
        let started = self.recovery_started_ns.ok_or(ProgressiveError::Phase)?;
        if self.live_epoch {
            return Err(ProgressiveError::Phase);
        }
        let deadline = started
            .checked_add(LEASE_NS + CLOCK_SKEW_NS)
            .ok_or(ProgressiveError::Overflow)?;
        if now < deadline {
            return Err(ProgressiveError::Time);
        }
        if expected_policy != self.policy
            || !Self::valid_policy(expected_policy)
            || expected_model != &self.ledger.model
            || expected_model.validate().is_err()
            || configuration != self.ledger.configuration
            || expected_model.controllers.len() != 1
            || self.ledger.proofs.len() != expected_model.resources.len()
            || observations.len() > MAX_RESOURCES
        {
            return Err(ProgressiveError::Model);
        }
        let specs = expected_model
            .specifications()
            .map_err(|_| ProgressiveError::Model)?;
        let controller = &self.ledger.controller;
        if !controller.matches_configuration(
            configuration,
            expected_model.controllers[0].id,
            &specs,
        ) || self.departures.len() > MAX_RESOURCES
            || self.departures.iter().enumerate().any(|(i, d)| {
                d.request.id == 0
                    || d.request.id > self.last_id
                    || self.departures[..i]
                        .iter()
                        .any(|p| p.request.id == d.request.id)
            })
        {
            return Err(ProgressiveError::Model);
        }
        // Every retained owner must occur once. A missing train, changed boot
        // session or unexplained occupied resource keeps the WHOLE domain fenced.
        let mut retained = BTreeMap::new();
        for (i, record) in controller.records().iter().enumerate() {
            if record.phase == Phase::Blocked {
                return Err(ProgressiveError::Conflict);
            }
            if let Some(g) = record.grant {
                if record.phase != Phase::Unknown
                    || g.resource != specs[i].id
                    || g.controller != specs[i].controller
                    || g.configuration != configuration
                    || g.epoch >= controller.epoch()
                    || g.lease == 0
                    || g.epoch == 0
                    || g.issued_ns == 0
                    || g.issued_ns >= g.valid_until_ns
                    || expected_model
                        .trains
                        .iter()
                        .all(|t| t.config.owner != g.owner || t.permitted_route != g.route)
                    || expected_model.routes.iter().all(|r| {
                        r.id != g.route
                            || r.direction != g.direction
                            || r.segments.iter().all(|s| s.resource != g.resource)
                    })
                {
                    return Err(ProgressiveError::Ownership);
                }
                if retained
                    .insert(g.owner.train, g.owner)
                    .is_some_and(|old| old != g.owner)
                {
                    return Err(ProgressiveError::Identity);
                }
            }
        }
        if observations.len() != retained.len() {
            return Err(ProgressiveError::Identity);
        }
        let mut seen = BTreeMap::new();
        let mut occupied = BTreeMap::new();
        for r in observations {
            let cfg = self.readiness(*r, now)?;
            if retained.get(&r.owner.train) != Some(&r.owner)
                || seen.insert(r.owner.train, *r).is_some()
                || r.observed_ns < started
                || now - r.observed_ns > self.policy.maximum_sample_ns
                || r.velocity_mmps != 0
                || self
                    .departures
                    .iter()
                    .filter(|d| d.request.owner == r.owner)
                    .any(|d| r.sequence <= d.last_readiness.sequence)
            {
                return Err(ProgressiveError::Readiness);
            }
            let train = expected_model
                .trains
                .iter()
                .find(|t| t.config.owner == r.owner)
                .ok_or(ProgressiveError::Identity)?;
            let route = self.route(train.permitted_route)?;
            let uncertainty = u64::from(cfg.maximum_position_uncertainty_mm);
            let front = r
                .front_mm
                .checked_add(uncertainty)
                .ok_or(ProgressiveError::Overflow)?;
            let rear = r
                .front_mm
                .checked_sub(u64::from(cfg.length_mm) + uncertainty)
                .ok_or(ProgressiveError::Boundary)?;
            if !route.stopping_locations.iter().any(|stop| {
                stop.at_mm.abs_diff(r.front_mm) <= uncertainty
                    && route.segments.iter().any(|s| {
                        s.resource == stop.platform && rear >= s.start_mm && front <= s.end_mm
                    })
            }) {
                return Err(ProgressiveError::Motion);
            }
            for s in &route.segments {
                if s.start_mm <= front && s.end_mm >= rear {
                    let record = controller.records()[usize::from(s.resource.0)];
                    if record.grant.is_none_or(|g| g.owner != r.owner)
                        || occupied.insert(s.resource, r.owner).is_some()
                    {
                        return Err(ProgressiveError::Ownership);
                    }
                }
            }
        }
        // Validate all proofs before mutation. An empty detector alone cannot
        // clear a retained lock: the same identified owner is stopped, its
        // bounded complete body is elsewhere and no re-entry is permitted.
        let mut proposed = self.ledger.clone();
        for (i, spec) in specs.iter().enumerate() {
            let proof = self.ledger.proofs[i].ok_or(ProgressiveError::Proof)?;
            let record = controller.records()[i];
            if !proof.permits(*spec, controller.epoch(), now)
                || proof.observed_ns < started
                || now - proof.observed_ns > self.policy.maximum_sample_ns
                || proof.sequence <= record.last_proof_sequence
                || !proof.occupancy_integrity_proved
                || proof.restriction != Restriction::Open
            {
                return Err(ProgressiveError::Proof);
            }
            if let Some(owner) = occupied.get(&spec.id) {
                if proof.clear || proof.occupant != Some(*owner) {
                    return Err(ProgressiveError::Proof);
                }
                proposed
                    .apply(&ResourceEvent::Reconcile(spec.id), now)
                    .map_err(|_| ProgressiveError::Proof)?;
            } else {
                if !proof.clear
                    || !proof.clearance_safe
                    || proof.occupant.is_some()
                    || proof.cleared_owner != record.grant.map(|g| g.owner)
                {
                    return Err(ProgressiveError::Proof);
                }
                proposed
                    .apply(&ResourceEvent::Clear(spec.id), now)
                    .map_err(|_| ProgressiveError::Proof)?;
            }
        }
        for d in &mut self.departures {
            d.phase = ProgressivePhase::ReconciledStopped;
            d.stop_required = true;
            d.hold_reason = Some(ProgressiveError::Phase);
            d.hold_stopping_margin_mm = None;
            if let Some(r) = seen.get(&d.request.owner.train) {
                d.last_readiness = *r;
                d.last_update_ns = now;
            }
        }
        self.ledger = proposed;
        self.live_epoch = true;
        self.recovery_started_ns = None;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::progressive::tests::{clearproof, fixture, launch, model, policy, ready, request};
    const NOW: u64 = 1_000_000_000;
    const CFG: ConfigurationId = [7; 32];
    const RECOVER: u64 = NOW + 1 + LEASE_NS + CLOCK_SKEW_NS;

    fn recovery_fixture(committed: bool) -> ProgressiveDomain {
        let mut d = fixture();
        if committed {
            launch(&mut d);
        } else {
            d.apply(&ProgressiveEvent::Prepare(request()), NOW).unwrap();
        }
        let mut d: ProgressiveDomain =
            serde_json::from_slice(&serde_json::to_vec(&d).unwrap()).unwrap();
        d.apply(&ProgressiveEvent::Restart { new_epoch: 2 }, NOW + 1)
            .unwrap();
        for i in 0..d.ledger.proofs.len() {
            let record = d.ledger.controller.records()[i];
            let mut p = clearproof(i as u8, record.last_proof_sequence + 1, RECOVER);
            p.epoch = 2;
            p.cleared_owner = record.grant.map(|g| g.owner);
            if i == 0 {
                p.clear = false;
                p.occupant = Some(request().owner);
                p.cleared_owner = None;
            }
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
                RECOVER,
            )
            .unwrap();
        }
        d
    }
    fn event() -> ProgressiveEvent {
        let mut r = ready(100, RECOVER, 300000, 0);
        r.epoch = 2;
        ProgressiveEvent::ReconcileStopped {
            configuration: CFG,
            expected_policy: policy(),
            expected_model: Box::new(model()),
            readiness: vec![r],
        }
    }
    fn observations(e: &mut ProgressiveEvent) -> &mut Vec<ProgressiveReadiness> {
        let ProgressiveEvent::ReconcileStopped { readiness, .. } = e else {
            panic!("recovery event")
        };
        readiness
    }
    #[test]
    fn prepared_and_committed_snapshots_need_new_epoch_and_fresh_contract() {
        for committed in [false, true] {
            let mut d = recovery_fixture(committed);
            let owner = d.ledger.controller.records()[0].grant.unwrap().owner;
            assert!(d.restore_fenced());
            assert!(!d.may_move(1, RECOVER));
            d.apply(&event(), RECOVER).unwrap();
            assert!(!d.restore_fenced());
            assert!(!d.may_move(1, RECOVER));
            assert_eq!(
                d.departure(1).unwrap().phase,
                ProgressivePhase::ReconciledStopped
            );
            assert_eq!(d.ledger.controller.records()[0].grant.unwrap().owner, owner);
            assert_eq!(d.ledger.controller.records()[0].grant.unwrap().epoch, 2);
            assert!(d.ledger.controller.records()[1].grant.is_none());
            assert!(d
                .apply(
                    &ProgressiveEvent::Commit {
                        id: 1,
                        readiness: observations(&mut event())[0]
                    },
                    RECOVER
                )
                .is_err());
            let mut r = observations(&mut event())[0];
            r.sequence += 1;
            let mut q = request();
            q.id = 2;
            q.readiness = r;
            d.apply(&ProgressiveEvent::Prepare(q), RECOVER).unwrap();
            r.sequence += 1;
            d.apply(
                &ProgressiveEvent::Commit {
                    id: 2,
                    readiness: r,
                },
                RECOVER,
            )
            .unwrap();
            assert!(d.may_move(2, RECOVER));
            assert!(!d.may_move(1, RECOVER));
        }
    }
    #[test]
    fn adversarial_reconciliation_is_atomic_and_never_releases_a_retained_owner() {
        for fault in 0..21 {
            let mut d = recovery_fixture(true);
            let mut e = event();
            let mut now = RECOVER;
            match fault {
                0 => {
                    d.recovery_started_ns = None;
                }
                1 => {
                    now -= 1;
                }
                2 => {
                    observations(&mut e)[0].velocity_mmps = 1;
                }
                3 => {
                    observations(&mut e)[0].front_mm = 350000;
                }
                4 => {
                    observations(&mut e).clear();
                }
                5 => {
                    let r = observations(&mut e)[0];
                    observations(&mut e).push(r);
                }
                6 => {
                    observations(&mut e)[0].owner.session += 1;
                }
                7 => {
                    observations(&mut e)[0].epoch = 1;
                }
                8 => {
                    observations(&mut e)[0].observed_ns -= 100_000_001;
                }
                9 => {
                    d.ledger.proofs[0].as_mut().unwrap().epoch = 1;
                }
                10 => {
                    d.ledger.proofs[0].as_mut().unwrap().observed_ns -= 100_000_001;
                }
                11 => {
                    let p = d.ledger.proofs[0].as_mut().unwrap();
                    p.clear = true;
                    p.occupant = None;
                }
                12 => {
                    d.ledger.proofs[1].as_mut().unwrap().clearance_safe = false;
                }
                13 => {
                    d.ledger.proofs[1].as_mut().unwrap().cleared_owner = None;
                }
                14 => {
                    d.apply(
                        &ProgressiveEvent::Evidence(ResourceEvent::Block(ResourceId(2))),
                        RECOVER,
                    )
                    .unwrap();
                }
                15 => {
                    d.ledger.proofs[2] = None;
                }
                16 => {
                    let ProgressiveEvent::ReconcileStopped { expected_model, .. } = &mut e else {
                        unreachable!()
                    };
                    expected_model.revision.push_str("-wrong");
                }
                17 => {
                    let ProgressiveEvent::ReconcileStopped { configuration, .. } = &mut e else {
                        unreachable!()
                    };
                    *configuration = [8; 32];
                }
                18 => {
                    d.ledger.proofs[0].as_mut().unwrap().sequence =
                        d.ledger.controller.records()[0].last_proof_sequence;
                }
                19 => {
                    let p = d.ledger.proofs[2].as_mut().unwrap();
                    p.clear = false;
                    p.occupant = Some(request().owner);
                }
                20 => {
                    observations(&mut e)[0].sequence = 1;
                }
                _ => unreachable!(),
            }
            let records = d.ledger.controller.records().to_vec();
            assert!(d.apply(&e, now).is_err(), "fault {fault}");
            assert_eq!(d.ledger.controller.records(), records, "fault {fault}");
            assert!(d.restore_fenced());
            assert!(!d.may_move(1, now));
        }
    }
    #[test]
    fn every_crash_loses_the_transient_restart_and_reconciliation_witness() {
        for reconciled in [false, true] {
            let mut d = recovery_fixture(true);
            if reconciled {
                d.apply(&event(), RECOVER).unwrap();
            }
            let mut restored: ProgressiveDomain =
                serde_json::from_slice(&serde_json::to_vec(&d).unwrap()).unwrap();
            assert!(restored.restore_fenced());
            assert!(restored.recovery_started_ns.is_none());
            assert!(restored.apply(&event(), RECOVER).is_err());
            assert!(!restored.may_move(1, RECOVER));
        }
    }
    #[test]
    fn restart_of_a_live_domain_also_requires_reconciliation() {
        let mut d = fixture();
        launch(&mut d);
        d.apply(&ProgressiveEvent::Restart { new_epoch: 2 }, NOW + 1)
            .unwrap();
        assert!(d.restore_fenced());
        assert!(!d.may_move(1, NOW + 1));
    }
    #[test]
    fn snapshot_cannot_inject_a_live_or_restart_witness() {
        for name in ["live_epoch", "recovery_started_ns"] {
            let mut value = serde_json::to_value(recovery_fixture(true)).unwrap();
            value[name] = serde_json::json!(true);
            assert!(serde_json::from_value::<ProgressiveDomain>(value).is_err());
        }
    }
    #[test]
    fn two_owners_need_complete_evidence_and_observation_order_does_not_matter() {
        let mut d = fixture();
        launch(&mut d);
        let mut second = ready(1, NOW, 2150000, 0);
        second.owner.train = osr_core::TrainId(102);
        d.apply(
            &ProgressiveEvent::Evidence(ResourceEvent::Integrity {
                owner: second.owner,
                proved: true,
            }),
            NOW,
        )
        .unwrap();
        let mut p = clearproof(3, 3, NOW);
        p.clear = false;
        p.occupant = Some(second.owner);
        d.apply(
            &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
            NOW,
        )
        .unwrap();
        let mut q = request();
        q.id = 2;
        q.owner = second.owner;
        q.readiness = second;
        d.apply(&ProgressiveEvent::Prepare(q), NOW).unwrap();
        second.sequence = 2;
        d.apply(
            &ProgressiveEvent::Commit {
                id: 2,
                readiness: second,
            },
            NOW,
        )
        .unwrap();
        let mut d: ProgressiveDomain =
            serde_json::from_slice(&serde_json::to_vec(&d).unwrap()).unwrap();
        d.apply(&ProgressiveEvent::Restart { new_epoch: 2 }, NOW + 1)
            .unwrap();
        for i in 0..d.ledger.proofs.len() {
            let record = d.ledger.controller.records()[i];
            let mut p = clearproof(i as u8, record.last_proof_sequence + 1, RECOVER);
            p.epoch = 2;
            p.cleared_owner = record.grant.map(|g| g.owner);
            if i == 0 || i == 3 {
                p.clear = false;
                p.occupant = record.grant.map(|g| g.owner);
                p.cleared_owner = None;
            }
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
                RECOVER,
            )
            .unwrap();
        }
        let mut e = event();
        second.sequence = 100;
        second.epoch = 2;
        second.observed_ns = RECOVER;
        let records = d.ledger.controller.records().to_vec();
        assert!(d.apply(&e, RECOVER).is_err());
        assert_eq!(records, d.ledger.controller.records());
        observations(&mut e).push(second);
        let mut reordered = d.clone();
        let mut reverse = e.clone();
        observations(&mut reverse).reverse();
        d.apply(&e, RECOVER).unwrap();
        reordered.apply(&reverse, RECOVER).unwrap();
        assert_eq!(d, reordered);
        assert_eq!(
            d.ledger.controller.records()[3].grant.unwrap().owner,
            second.owner
        );
        assert!(!d.may_move(1, RECOVER));
        assert!(!d.may_move(2, RECOVER));
    }
    #[test]
    fn pinned_model_and_policy_must_match_restored_controller() {
        for corruption in ["specs", "acceleration", "sample-bound"] {
            let d = recovery_fixture(true);
            let mut value = serde_json::to_value(&d).unwrap();
            match corruption {
                "specs" => {
                    value["ledger"]["controller"]["specs"][0]["conflicts"] = serde_json::json!(0)
                }
                "acceleration" => {
                    value["policy"]["maximum_acceleration_mmps2"] = serde_json::json!(0)
                }
                _ => value["policy"]["maximum_sample_ns"] = serde_json::json!(1_000_000_000_u64),
            }
            let pinned = if corruption == "sample-bound" {
                serde_json::from_value(value["policy"].clone()).unwrap()
            } else {
                policy()
            };
            let mut forged: ProgressiveDomain = serde_json::from_value(value).unwrap();
            forged
                .apply(&ProgressiveEvent::Restart { new_epoch: 3 }, RECOVER + 1)
                .unwrap();
            let when = RECOVER + 1 + LEASE_NS + CLOCK_SKEW_NS;
            let mut r = observations(&mut event())[0];
            r.epoch = 3;
            r.observed_ns = when;
            let e = ProgressiveEvent::ReconcileStopped {
                configuration: CFG,
                expected_policy: pinned,
                expected_model: Box::new(model()),
                readiness: vec![r],
            };
            assert_eq!(
                forged.apply(&e, when),
                Err(ProgressiveError::Model),
                "{corruption}"
            );
            assert!(forged.restore_fenced());
        }
    }
}
