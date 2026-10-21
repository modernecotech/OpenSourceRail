//! Local station launch transactions folded through the existing resource log.
//!
//! This is a bounded, single-controller research protocol, not a distributed
//! station interlocking or a detector/brake implementation. Readiness and tail
//! proofs are external assertions requiring qualified, authenticated adapters.
use crate::{resource_log::ResourceLedger, resources::*};
use osr_core::{resources::*, Direction, RouteId};
use serde::{Deserialize, Serialize};

pub const MAX_LAUNCH_RECORDS: usize = MAX_RESOURCES;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationLaunchRequest {
    /// Monotonically increasing within the persistent configuration/domain.
    pub id: u64,
    pub configuration: ConfigurationId,
    pub owner: Owner,
    pub route: RouteId,
    pub direction: Direction,
    pub corridor: ResourceId,
    pub receiving_berth: ResourceId,
    pub overlap: ResourceId,
    pub consist_length_mm: u32,
    pub permission_expires_ns: u64,
}
impl StationLaunchRequest {
    pub const fn resources(self) -> [ResourceId; 3] {
        [self.corridor, self.receiving_berth, self.overlap]
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationReadiness {
    pub launch_id: u64,
    pub configuration: ConfigurationId,
    pub owner: Owner,
    pub epoch: u64,
    pub sequence: u64,
    pub observed_ns: u64,
    pub receive_brake_ready: bool,
    pub arrival_reserve_ready: bool,
    pub doors_closed: bool,
    pub services_reserve_ready: bool,
    pub route_ready: bool,
    pub train_healthy: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum LaunchPhase {
    Prepared,
    Committed,
    Held,
    Cleared,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum StationFaultReason {
    ReceiverUnavailable,
    LostCommunications,
    IntegrityLost,
    Emergency,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationFault {
    pub launch_id: u64,
    pub configuration: ConfigurationId,
    pub owner: Owner,
    pub epoch: u64,
    pub sequence: u64,
    pub observed_ns: u64,
    pub reason: StationFaultReason,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationClearance {
    pub launch_id: u64,
    pub configuration: ConfigurationId,
    pub owner: Owner,
    pub epoch: u64,
    pub sequence: u64,
    pub observed_ns: u64,
    pub consist_length_mm: u32,
    pub tail_integrity_proved: bool,
    pub all_cars_accounted_for: bool,
    pub proofs: [ProtectionProof; 3],
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationLaunch {
    pub request: StationLaunchRequest,
    pub phase: LaunchPhase,
    pub grants: [Grant; 3],
    pub readiness: StationReadiness,
    pub committed_ns: Option<u64>,
    pub fault: Option<StationFault>,
    pub clearance: Option<StationClearance>,
}

impl ResourceLedger {
    pub fn station_launch(&self, id: u64) -> Option<&StationLaunch> {
        self.station_launches.iter().find(|v| v.request.id == id)
    }

    /// Protected ownership, including a held/restarted committed arrival. This
    /// is deliberately NOT movement authority or a claim that a brake works.
    pub fn station_arrival_protected(&self, id: u64) -> bool {
        self.station_launch(id).is_some_and(|launch| {
            launch.committed_ns.is_some()
                && launch.phase != LaunchPhase::Cleared
                && launch.grants.iter().all(|g| {
                    self.controller
                        .records()
                        .get(usize::from(g.resource.0))
                        .is_some_and(|r| r.phase != Phase::Available && r.grant == Some(*g))
                })
        })
    }

    pub(crate) fn station_owns(&self, resource: ResourceId) -> bool {
        self.station_launches.iter().any(|launch| {
            launch.phase != LaunchPhase::Cleared && launch.request.resources().contains(&resource)
        })
    }

    fn valid_readiness(
        &self,
        request: StationLaunchRequest,
        proof: StationReadiness,
        now: u64,
    ) -> bool {
        proof.launch_id == request.id
            && proof.configuration == self.configuration
            && proof.owner == request.owner
            && proof.epoch == self.controller.epoch()
            && proof.sequence > 0
            && fresh(proof.observed_ns, now)
            && proof.receive_brake_ready
            && proof.arrival_reserve_ready
            && proof.doors_closed
            && proof.services_reserve_ready
            && proof.route_ready
            && proof.train_healthy
            && self.integrity.get(&request.owner.train) == Some(&true)
    }

    pub(crate) fn prepare_station_launch(
        &mut self,
        request: StationLaunchRequest,
        readiness: StationReadiness,
        now: u64,
    ) -> Result<(), ResourceError> {
        if let Some(old) = self.station_launch(request.id) {
            return if old.request == request {
                Ok(()) // retry never creates another reservation or launches again
            } else {
                Err(ResourceError::Ownership)
            };
        }
        let train = self
            .model
            .trains
            .iter()
            .find(|t| t.config.owner == request.owner)
            .ok_or(ResourceError::Ownership)?;
        let route = self
            .model
            .routes
            .iter()
            .find(|r| r.id == request.route)
            .ok_or(ResourceError::Model)?;
        let ids = request.resources();
        if request.id <= self.last_station_launch_id
            || request.configuration != self.configuration
            || train.permitted_route != request.route
            || route.direction != request.direction
            || request.consist_length_mm != train.config.length_mm
            || !self.valid_readiness(request, readiness, now)
            || request.permission_expires_ns <= now
            || request.permission_expires_ns
                > now.checked_add(LEASE_NS).ok_or(ResourceError::Overflow)?
            || ids.iter().enumerate().any(|(i, id)| {
                ids[..i].contains(id)
                    || self.station_owns(*id)
                    || !route.segments.iter().any(|s| s.resource == *id)
            })
        {
            return Err(ResourceError::Proof);
        }
        let mut proposed = self.controller.clone();
        let mut grants = Vec::new();
        for id in ids {
            if self
                .controller
                .records()
                .get(usize::from(id.0))
                .is_none_or(|r| r.phase != Phase::Available)
            {
                return Err(ResourceError::Conflict);
            }
            let proof = self.proof(id)?;
            // A new launch needs positively clear receive resources. An owner
            // report cannot substitute for the preceding consist's clearance.
            if !proof.clear || !proof.clearance_safe || !proof.occupancy_integrity_proved {
                return Err(ResourceError::Proof);
            }
            grants.push(proposed.request(
                request.owner,
                request.route,
                request.direction,
                proof,
                now,
            )?);
        }
        let grants: [Grant; 3] = grants.try_into().map_err(|_| ResourceError::Model)?;
        if self.station_launches.len() >= MAX_LAUNCH_RECORDS {
            let i = self
                .station_launches
                .iter()
                .position(|v| v.phase == LaunchPhase::Cleared)
                .ok_or(ResourceError::Model)?;
            self.station_launches.remove(i);
        }
        self.controller = proposed;
        self.last_station_launch_id = request.id;
        self.station_launches.push(StationLaunch {
            request,
            phase: LaunchPhase::Prepared,
            grants,
            readiness,
            committed_ns: None,
            fault: None,
            clearance: None,
        });
        Ok(())
    }

    pub(crate) fn commit_station_launch(
        &mut self,
        id: u64,
        readiness: StationReadiness,
        now: u64,
    ) -> Result<(), ResourceError> {
        let index = self
            .station_launches
            .iter()
            .position(|v| v.request.id == id)
            .ok_or(ResourceError::Ownership)?;
        let launch = &self.station_launches[index];
        if launch.committed_ns.is_some() {
            return if launch.readiness == readiness {
                Ok(())
            } else {
                Err(ResourceError::Phase)
            };
        }
        if launch.phase != LaunchPhase::Prepared
            || now >= launch.request.permission_expires_ns
            || readiness.sequence <= launch.readiness.sequence
            || !self.valid_readiness(launch.request, readiness, now)
        {
            return Err(ResourceError::Proof);
        }
        // Repeat all protection checks at the commit point, after preparing.
        let specs = self
            .model
            .specifications()
            .map_err(|_| ResourceError::Model)?;
        for id in launch.request.resources() {
            let proof = self.proof(id)?;
            if !proof.permits(specs[usize::from(id.0)], self.controller.epoch(), now)
                || !proof.clear
                || !proof.clearance_safe
                || !proof.occupancy_integrity_proved
                || !proof.owns_or_clear(launch.request.owner)
                || (specs[usize::from(id.0)].points_required
                    && proof.proved_route != Some(launch.request.route))
            {
                return Err(ResourceError::Proof);
            }
        }
        self.controller.commit_station_bundle(&launch.grants, now)?;
        let launch = &mut self.station_launches[index];
        launch.phase = LaunchPhase::Committed;
        launch.committed_ns = Some(now);
        launch.readiness = readiness;
        Ok(())
    }

    pub(crate) fn hold_station_launch(
        &mut self,
        fault: StationFault,
        now: u64,
    ) -> Result<(), ResourceError> {
        let epoch = self.controller.epoch();
        let launch = self
            .station_launches
            .iter_mut()
            .find(|v| v.request.id == fault.launch_id)
            .ok_or(ResourceError::Ownership)?;
        if launch.fault == Some(fault) {
            return Ok(());
        }
        if launch.phase == LaunchPhase::Cleared
            || fault.configuration != self.configuration
            || fault.owner != launch.request.owner
            || fault.epoch != epoch
            || fault.sequence == 0
            || launch
                .fault
                .is_some_and(|old| fault.sequence <= old.sequence)
            || !fresh(fault.observed_ns, now)
        {
            return Err(ResourceError::Proof);
        }
        launch.fault = Some(fault);
        launch.phase = LaunchPhase::Held;
        Ok(())
    }

    pub(crate) fn clear_station_launch(
        &mut self,
        evidence: StationClearance,
        now: u64,
    ) -> Result<(), ResourceError> {
        let index = self
            .station_launches
            .iter()
            .position(|v| v.request.id == evidence.launch_id)
            .ok_or(ResourceError::Ownership)?;
        let launch = &self.station_launches[index];
        if launch.phase == LaunchPhase::Cleared {
            return if launch.clearance == Some(evidence) {
                Ok(())
            } else {
                Err(ResourceError::Proof)
            };
        }
        // A later-delivered generic owner proof can still be fresh while
        // describing the track before this launch. Sequence ordering alone
        // does not bind that observation to the committed movement.
        let earliest_observation = launch.committed_ns.unwrap_or(launch.readiness.observed_ns);
        if evidence.configuration != self.configuration
            || evidence.owner != launch.request.owner
            || evidence.epoch != self.controller.epoch()
            || evidence.sequence == 0
            || !fresh(evidence.observed_ns, now)
            || evidence.observed_ns < earliest_observation
            || evidence
                .proofs
                .iter()
                .any(|proof| proof.observed_ns < earliest_observation)
            || !evidence.tail_integrity_proved
            || !evidence.all_cars_accounted_for
            || evidence.consist_length_mm != launch.request.consist_length_mm
        {
            return Err(ResourceError::Proof);
        }
        // Embedded clearance may arrive after a newer occupied/conflicting
        // observation. Compare the complete current protection view, not only
        // the sequence retained when the original reservation was granted.
        for proof in &evidence.proofs {
            if let Some(Some(latest)) = self.proofs.get(usize::from(proof.resource.0)) {
                if latest.epoch == self.controller.epoch()
                    && (proof.sequence < latest.sequence
                        || proof.observed_ns < latest.observed_ns
                        || (proof.sequence == latest.sequence && proof != latest))
                {
                    return Err(ResourceError::Proof);
                }
            }
        }
        self.controller
            .clear_station_bundle(&launch.grants, &evidence.proofs, now)?;
        let launch = &mut self.station_launches[index];
        launch.phase = LaunchPhase::Cleared;
        launch.clearance = Some(evidence);
        Ok(())
    }
}
