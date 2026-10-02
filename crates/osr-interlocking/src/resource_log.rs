//! Resource lifecycle is a committed extension of the existing track-state fold.
use crate::resources::*;
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId, SectionId, TrainId};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub enum ResourceEvent {
    Bootstrap {
        configuration: ConfigurationId,
        model: Box<RailwayModel>,
    },
    LocalProof(ProtectionProof),
    Reserve {
        owner: Owner,
        resource: ResourceId,
        route: RouteId,
        direction: Direction,
    },
    Withdraw(Grant),
    Clear(ResourceId),
    Block(ResourceId),
    Restart(u64),
    Reconcile(ResourceId),
    Integrity {
        owner: Owner,
        proved: bool,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ResourceLedger {
    pub model: RailwayModel,
    pub configuration: ConfigurationId,
    pub controller: ResourceController,
    pub proofs: Vec<Option<ProtectionProof>>,
    pub integrity: std::collections::BTreeMap<TrainId, bool>,
    pub rejected_transitions: u64,
}
impl ResourceLedger {
    pub fn new(
        model: RailwayModel,
        configuration: ConfigurationId,
        now: u64,
    ) -> Result<Self, ResourceError> {
        model.validate().map_err(|_| ResourceError::Model)?;
        // One static consensus group controls one conflict domain in this reference.
        if model.controllers.len() != 1 {
            return Err(ResourceError::Model);
        }
        let specs = model.specifications().map_err(|_| ResourceError::Model)?;
        let controller = ResourceController::boot(
            configuration,
            model.controllers[0].id,
            model.controllers[0].startup_epoch,
            specs,
            now,
        )?;
        Ok(Self {
            proofs: vec![None; model.resources.len()],
            model,
            configuration,
            controller,
            integrity: Default::default(),
            rejected_transitions: 0,
        })
    }
    pub fn apply(&mut self, event: &ResourceEvent, now: u64) -> Result<(), ResourceError> {
        // Commit order may differ from observation order across issuers.
        // Advance the fold monotonically without changing original proof times.
        let now = now.max(self.controller.last_event_time());
        self.controller.advance_time(now)?;
        match event {
            ResourceEvent::Bootstrap { .. } => Err(ResourceError::Phase),
            ResourceEvent::LocalProof(p) => {
                let index = usize::from(p.resource.0);
                if index >= self.proofs.len()
                    || p.controller != self.model.controllers[0].id
                    || p.epoch != self.controller.epoch()
                    || p.sequence == 0
                    || self.proofs[index].is_some_and(|old| p.sequence <= old.sequence)
                {
                    return Err(ResourceError::Proof);
                }
                self.proofs[index] = Some(*p);
                if let Some(g) = self.controller.records()[index].grant {
                    if p.occupant == Some(g.owner) && p.occupancy_integrity_proved {
                        let _ = self.controller.occupied(g, now);
                    }
                }
                Ok(())
            }
            ResourceEvent::Reserve {
                owner,
                resource,
                route,
                direction,
            } => {
                let train = self
                    .model
                    .trains
                    .iter()
                    .find(|t| t.config.owner == *owner)
                    .ok_or(ResourceError::Ownership)?;
                let path = self
                    .model
                    .routes
                    .iter()
                    .find(|r| r.id == *route)
                    .ok_or(ResourceError::Model)?;
                if self.integrity.get(&owner.train) != Some(&true)
                    || train.permitted_route != *route
                    || path.direction != *direction
                    || !path.segments.iter().any(|s| s.resource == *resource)
                {
                    return Err(ResourceError::Ownership);
                }
                let proof = self.proof(*resource)?;
                self.controller
                    .request(*owner, *route, *direction, proof, now)
                    .map(|_| ())
            }
            ResourceEvent::Withdraw(g) => self.controller.begin_release(*g, now),
            ResourceEvent::Clear(resource) => {
                self.controller.verified_clear(self.proof(*resource)?, now)
            }
            ResourceEvent::Block(resource) => self.controller.block(*resource),
            ResourceEvent::Restart(epoch) => {
                self.controller.restart(*epoch, now)?;
                self.proofs.fill(None);
                Ok(())
            }
            ResourceEvent::Reconcile(resource) => self
                .controller
                .reconcile_owner(self.proof(*resource)?, now)
                .map(|_| ()),
            ResourceEvent::Integrity { owner, proved } => {
                if !self.model.trains.iter().any(|t| t.config.owner == *owner) {
                    return Err(ResourceError::Ownership);
                }
                self.integrity.insert(owner.train, *proved);
                Ok(())
            }
        }
    }
    fn proof(&self, resource: ResourceId) -> Result<ProtectionProof, ResourceError> {
        self.proofs
            .get(usize::from(resource.0))
            .copied()
            .flatten()
            .ok_or(ResourceError::Proof)
    }
    pub fn resource_for(&self, section: SectionId) -> Option<usize> {
        self.model
            .resources
            .iter()
            .position(|r| r.section == section)
    }
    pub fn permits(&self, section: SectionId, train: TrainId, now: u64) -> bool {
        let Some(index) = self.resource_for(section) else {
            return false;
        };
        let Some(g) = self.controller.records()[index].grant else {
            return false;
        };
        let Some(p) = self.proofs[index] else {
            return false;
        };
        let Ok(specs) = self.model.specifications() else {
            return false;
        };
        self.integrity.get(&train) == Some(&true)
            && self
                .model
                .trains
                .iter()
                .any(|t| t.config.owner == g.owner && t.permitted_route == g.route)
            && g.owner.train == train
            && g.configuration == self.configuration
            && g.epoch == self.controller.epoch()
            && g.issued_ns <= now
            && now < g.valid_until_ns
            && matches!(
                self.controller.records()[index].phase,
                Phase::Reserved | Phase::Occupied
            )
            && p.permits(specs[index], g.epoch, now)
            && p.owns_or_clear(g.owner)
            && (!specs[index].points_required || p.proved_route == Some(g.route))
    }
    pub fn evidence_deadline(&self, train: TrainId) -> u64 {
        self.controller
            .records()
            .iter()
            .enumerate()
            .filter_map(|(i, r)| {
                r.grant
                    .filter(|g| {
                        g.owner.train == train
                            && matches!(r.phase, Phase::Reserved | Phase::Occupied)
                    })
                    .map(|g| {
                        g.valid_until_ns.min(
                            self.proofs[i]
                                .map_or(0, |p| p.observed_ns.saturating_add(INPUT_MAX_AGE_NS)),
                        )
                    })
            })
            .min()
            .unwrap_or(0)
    }
}
