use std::{string::String, vec::Vec};

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::{resources::*, Direction, RouteId, SectionId, TrainId};

pub const MODEL_SCHEMA: &str = "osr-tacs-railway/2";
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ResourceDefinition {
    pub id: ResourceId,
    pub section: SectionId,
    pub asset_id: String,
    pub kind: String,
    pub controller: ControllerId,
    pub conflicts: Vec<ResourceId>,
    pub point_asset_id: Option<String>,
    pub clearance_basis: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoppingLocation {
    pub asset_id: String,
    pub at_mm: u64,
    pub platform: ResourceId,
    pub charger_asset_id: String,
    pub minimum_departure_energy_wh: u32,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RouteDefinition {
    pub id: RouteId,
    pub asset_id: String,
    pub direction: Direction,
    pub segments: Vec<Segment>,
    pub stopping_locations: Vec<StoppingLocation>,
    pub leader_required: bool,
    pub operating_scope: String,
}

impl RouteDefinition {
    pub fn view(&self) -> Route<'_> {
        Route {
            id: self.id,
            direction: self.direction,
            segments: &self.segments,
            leader_required: self.leader_required,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TrainDefinition {
    pub asset_id: String,
    pub config: TrainConfig,
    pub integrity_arrangement: String,
    pub braking_evidence: String,
    pub permitted_route: RouteId,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ControllerDefinition {
    pub id: ControllerId,
    pub asset_id: String,
    pub startup_epoch: u64,
    pub restart_reconciliation: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub enum ParticipantRole {
    Train,
    Voter,
    Infrastructure,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Participant {
    pub entity: crate::EntityId,
    pub role: ParticipantRole,
    pub session: u64,
    pub public_key: [u8; 32],
    pub revoked: bool,
    pub resources: Vec<ResourceId>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeProfile {
    pub voters: Vec<crate::EntityId>,
    pub participants: Vec<Participant>,
    pub designed_revision: String,
    pub installed_state: String,
    pub approved_operating_profile: String,
    pub clock_error_ns: u64,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RailwayModel {
    pub runtime: RuntimeProfile,
    pub schema: String,
    pub revision: String,
    pub approval_state: String,
    pub resources: Vec<ResourceDefinition>,
    pub routes: Vec<RouteDefinition>,
    pub trains: Vec<TrainDefinition>,
    pub controllers: Vec<ControllerDefinition>,
    pub protected_work_resources: Vec<ResourceId>,
    pub maintenance_procedure: String,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum WireError {
    Model,
    Configuration,
    Packet,
    Signature,
    IssuerRole,
    Epoch,
    Ownership,
    Time,
    Sequence,
    UnsupportedOperation,
}

pub fn configuration_hash(bytes: &[u8]) -> ConfigurationId {
    Sha256::digest(bytes).into()
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DeploymentConfiguration {
    pub schema: String,
    pub configuration: ConfigurationId,
    pub model_revision: String,
    pub operational_release_ready: bool,
    pub train_startup: Vec<TrainDefinition>,
    pub controller_startup: Vec<ControllerDefinition>,
}

impl RailwayModel {
    pub fn specifications(&self) -> Result<Vec<ResourceSpec>, WireError> {
        if self.resources.is_empty() || self.resources.len() > MAX_RESOURCES {
            return Err(WireError::Model);
        }
        let mut specs = Vec::new();
        for r in &self.resources {
            let mut mask = 0;
            for id in &r.conflicts {
                if usize::from(id.0) >= self.resources.len() || mask & (1_u32 << id.0) != 0 {
                    return Err(WireError::Model);
                }
                mask |= 1_u32 << id.0;
            }
            specs.push(ResourceSpec {
                id: r.id,
                controller: r.controller,
                conflicts: mask,
                points_required: r.point_asset_id.is_some(),
            });
        }
        if !valid_resources(&specs) {
            return Err(WireError::Model);
        }
        Ok(specs)
    }

    pub fn validate(&self) -> Result<(), WireError> {
        if self.schema != MODEL_SCHEMA
            || self.revision.is_empty()
            || self.approval_state != "prototype-unapproved"
            || self.routes.is_empty()
            || self.routes.len() > MAX_RESOURCES
            || self.trains.is_empty()
            || self.trains.len() > MAX_RESOURCES
            || self.controllers.is_empty()
            || self.controllers.len() > MAX_RESOURCES
            || self.maintenance_procedure.is_empty()
        {
            return Err(WireError::Model);
        }
        if self.runtime.participants.len() > 64
            || ![3, 5].contains(&self.runtime.voters.len())
            || self.runtime.installed_state != "not-installed"
            || self.runtime.approved_operating_profile != "prototype-unapproved"
            || self.runtime.clock_error_ns > CLOCK_SKEW_NS
            || self.runtime.designed_revision.is_empty()
        {
            return Err(WireError::Model);
        }
        let mut participants = std::collections::BTreeSet::new();
        for p in &self.runtime.participants {
            if p.entity.0 == 0
                || p.entity.0 > u64::from(u16::MAX)
                || p.resources
                    .iter()
                    .any(|id| usize::from(id.0) >= self.resources.len())
                || p.session == 0
                || p.public_key == [0; 32]
                || !participants.insert(p.entity)
            {
                return Err(WireError::Model);
            }
        }
        if self.runtime.voters.iter().any(|id| {
            !self
                .runtime
                .participants
                .iter()
                .any(|p| p.entity == *id && p.role == ParticipantRole::Voter && !p.revoked)
        }) || self
            .runtime
            .voters
            .iter()
            .collect::<std::collections::BTreeSet<_>>()
            .len()
            != self.runtime.voters.len()
        {
            return Err(WireError::Model);
        }
        let specs = self.specifications()?;
        if self
            .resources
            .iter()
            .map(|r| r.section)
            .collect::<std::collections::BTreeSet<_>>()
            .len()
            != self.resources.len()
        {
            return Err(WireError::Model);
        }
        let mut identities = std::collections::BTreeSet::new();
        for asset in self
            .resources
            .iter()
            .map(|r| &r.asset_id)
            .chain(self.routes.iter().map(|r| &r.asset_id))
            .chain(self.trains.iter().map(|r| &r.asset_id))
            .chain(self.controllers.iter().map(|r| &r.asset_id))
        {
            if asset.is_empty() || asset.len() > 160 || !identities.insert(asset) {
                return Err(WireError::Model);
            }
        }
        let mut controllers = std::collections::BTreeSet::new();
        for c in &self.controllers {
            if c.id.0 == 0
                || c.startup_epoch == 0
                || c.restart_reconciliation.is_empty()
                || !controllers.insert(c.id)
            {
                return Err(WireError::Model);
            }
        }
        for r in &self.resources {
            if !controllers.contains(&r.controller)
                || r.clearance_basis.is_empty()
                || !matches!(
                    r.kind.as_str(),
                    "track" | "junction" | "platform" | "depot-entry" | "work-zone"
                )
            {
                return Err(WireError::Model);
            }
        }
        let mut routes = std::collections::BTreeSet::new();
        let mut covered = std::collections::BTreeSet::new();
        for r in &self.routes {
            if !r.view().valid(&specs)
                || !routes.insert(r.id)
                || r.operating_scope.is_empty()
                || r.stopping_locations.is_empty()
            {
                return Err(WireError::Model);
            }
            for s in &r.segments {
                covered.insert(s.resource);
            }
            for stop in &r.stopping_locations {
                if stop.asset_id.is_empty()
                    || stop.charger_asset_id.is_empty()
                    || stop.minimum_departure_energy_wh == 0
                    || !r.segments.iter().any(|s| {
                        s.resource == stop.platform
                            && s.start_mm <= stop.at_mm
                            && stop.at_mm <= s.end_mm
                    })
                    || self.resources[usize::from(stop.platform.0)].kind != "platform"
                {
                    return Err(WireError::Model);
                }
            }
        }
        if covered.len() != self.resources.len() {
            return Err(WireError::Model);
        }
        if self
            .protected_work_resources
            .iter()
            .any(|id| usize::from(id.0) >= specs.len())
        {
            return Err(WireError::Model);
        }
        let mut trains = std::collections::BTreeSet::new();
        for t in &self.trains {
            // The model describes parameters; the adapter fills its actual byte
            // hash. It cannot self-embed that hash in its source representation.
            let mut config = t.config;
            config.configuration = [1; 32];
            if !self.runtime.participants.iter().any(|p| {
                p.entity.0 == config.owner.train.0
                    && p.role == ParticipantRole::Train
                    && p.session == config.owner.session
                    && !p.revoked
            }) || !config.valid()
                || controllers.contains(&ControllerId(config.owner.train.0))
                || !trains.insert(config.owner.train)
                || !routes.contains(&t.permitted_route)
                || t.integrity_arrangement.is_empty()
                || t.braking_evidence.is_empty()
            {
                return Err(WireError::Model);
            }
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
/// Validated model with immutable internal parameters and configuration identity.
///
/// ```compile_fail
/// use osr_core::deployment::FrozenRailway;
/// fn live_edit(frozen: &mut FrozenRailway) {
///     frozen.model.trains[0].config.length_mm = 1;
/// }
/// ```
pub struct FrozenRailway {
    model: RailwayModel,
    configuration: ConfigurationId,
}

impl FrozenRailway {
    pub fn model(&self) -> &RailwayModel {
        &self.model
    }

    pub const fn configuration(&self) -> ConfigurationId {
        self.configuration
    }

    pub fn deployment(&self) -> DeploymentConfiguration {
        let mut trains = self.model.trains.clone();
        for train in &mut trains {
            train.config.configuration = self.configuration;
        }
        DeploymentConfiguration {
            schema: "osr-tacs-deployment/1".into(),
            configuration: self.configuration,
            model_revision: self.model.revision.clone(),
            operational_release_ready: false,
            train_startup: trains,
            controller_startup: self.model.controllers.clone(),
        }
    }

    pub fn load_deployment(model: &[u8], deployment: &[u8]) -> Result<Self, WireError> {
        let startup: DeploymentConfiguration =
            serde_json::from_slice(deployment).map_err(|_| WireError::Configuration)?;
        let frozen = Self::load(model, startup.configuration)?;
        if startup != frozen.deployment() {
            return Err(WireError::Configuration);
        }
        Ok(frozen)
    }

    pub fn load(bytes: &[u8], expected: ConfigurationId) -> Result<Self, WireError> {
        if bytes.len() > 1_000_000 || expected == [0; 32] || configuration_hash(bytes) != expected {
            return Err(WireError::Configuration);
        }
        let model: RailwayModel = serde_json::from_slice(bytes).map_err(|_| WireError::Model)?;
        model.validate()?;
        Ok(Self {
            model,
            configuration: expected,
        })
    }
    pub fn train_config(&self, id: TrainId) -> Result<TrainConfig, WireError> {
        let mut config = self
            .model
            .trains
            .iter()
            .find(|t| t.config.owner.train == id)
            .ok_or(WireError::Ownership)?
            .config;
        config.configuration = self.configuration;
        Ok(config)
    }
    /// This profile has no physical qualification/independent approval yet.
    pub fn permit_operational_deployment(&self) -> Result<(), WireError> {
        Err(WireError::UnsupportedOperation)
    }
}
