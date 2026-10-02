//! Exclusive locks outlive permissions. Timeouts and restarts never prove clear.
use osr_core::{resources::*, Direction, RouteId};

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub enum Phase {
    Available,
    Reserved,
    Occupied,
    ReleasePending,
    Blocked,
    Unknown,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub enum Restriction {
    Open,
    Speed(u32),
    Closed,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProtectionProof {
    pub resource: ResourceId,
    pub controller: ControllerId,
    pub epoch: u64,
    pub sequence: u64,
    pub observed_ns: u64,
    /// Derived from independently validated occupancy/clearance interfaces.
    /// Unknown, missing integrity, or a timer is never a clearance proof.
    pub clear: bool,
    /// Clearance also proves no re-entry from an approach/stopping envelope:
    /// bounded rear beyond the resource, or withdrawn permission AND proved stop.
    /// Merely seeing an empty track circuit cannot set this field.
    pub clearance_safe: bool,
    pub cleared_owner: Option<Owner>,
    pub occupant: Option<Owner>,
    pub occupancy_integrity_proved: bool,
    pub points_locked_and_proved: bool,
    pub proved_route: Option<RouteId>,
    pub restriction: Restriction,
}

impl ProtectionProof {
    pub fn owns_or_clear(self, owner: Owner) -> bool {
        if self.clear {
            self.occupant.is_none()
        } else {
            self.occupant == Some(owner) && self.occupancy_integrity_proved
        }
    }
    pub fn permits(self, spec: ResourceSpec, epoch: u64, now_ns: u64) -> bool {
        self.resource == spec.id
            && self.controller == spec.controller
            && self.epoch == epoch
            && self.sequence > 0
            && fresh(self.observed_ns, now_ns)
            && (!spec.points_required
                || (self.points_locked_and_proved && self.proved_route.is_some()))
            && match self.restriction {
                Restriction::Open => true,
                Restriction::Speed(v) => (1..=MAX_SPEED_MMPS).contains(&v),
                Restriction::Closed => false,
            }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Grant {
    pub resource: ResourceId,
    pub controller: ControllerId,
    pub configuration: ConfigurationId,
    pub epoch: u64,
    pub lease: u64,
    pub owner: Owner,
    pub route: RouteId,
    pub direction: Direction,
    pub issued_ns: u64,
    pub valid_until_ns: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct ResourceRecord {
    pub phase: Phase,
    pub grant: Option<Grant>,
    pub last_proof_sequence: u64,
}

const UNKNOWN: ResourceRecord = ResourceRecord {
    phase: Phase::Unknown,
    grant: None,
    last_proof_sequence: 0,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ResourceError {
    Model,
    Time,
    Proof,
    Conflict,
    Ownership,
    Epoch,
    Phase,
    Overflow,
}

#[derive(Clone, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub struct ResourceController {
    configuration: ConfigurationId,
    controller: ControllerId,
    epoch: u64,
    serial: u64,
    last_now_ns: u64,
    quarantine_until_ns: u64,
    specs: Vec<ResourceSpec>,
    records: Vec<ResourceRecord>,
}

impl ResourceController {
    pub fn boot(
        configuration: ConfigurationId,
        controller: ControllerId,
        epoch: u64,
        specs: impl Into<Vec<ResourceSpec>>,
        now_ns: u64,
    ) -> Result<Self, ResourceError> {
        let specs = specs.into();
        let count = specs.len();
        if configuration == [0; 32] || controller.0 == 0 || epoch == 0 || !valid_resources(&specs) {
            return Err(ResourceError::Model);
        }
        if now_ns == 0 {
            return Err(ResourceError::Time);
        }
        let quarantine_until_ns = if epoch == 1 {
            now_ns
        } else {
            now_ns
                .checked_add(LEASE_NS + CLOCK_SKEW_NS)
                .ok_or(ResourceError::Overflow)?
        };
        Ok(Self {
            configuration,
            controller,
            epoch,
            serial: 0,
            last_now_ns: now_ns,
            quarantine_until_ns,
            specs,
            records: vec![UNKNOWN; count],
        })
    }

    pub const fn last_event_time(&self) -> u64 {
        self.last_now_ns
    }
    pub const fn epoch(&self) -> u64 {
        self.epoch
    }
    pub fn records(&self) -> &[ResourceRecord] {
        &self.records
    }

    fn tick(&mut self, now_ns: u64) -> Result<(), ResourceError> {
        if now_ns == 0 || now_ns < self.last_now_ns {
            return Err(ResourceError::Time);
        }
        self.last_now_ns = now_ns;
        for r in &mut self.records {
            if r.grant.is_some_and(|g| now_ns >= g.valid_until_ns)
                && matches!(r.phase, Phase::Reserved | Phase::Occupied)
            {
                r.phase = Phase::ReleasePending;
            }
        }
        Ok(())
    }

    pub fn advance_time(&mut self, now_ns: u64) -> Result<(), ResourceError> {
        self.tick(now_ns)
    }

    fn index(&self, resource: ResourceId) -> Result<usize, ResourceError> {
        let i = usize::from(resource.0);
        if i >= self.specs.len() || self.specs[i].controller != self.controller {
            return Err(ResourceError::Model);
        }
        Ok(i)
    }

    /// Reconcile unknown startup state or complete an explicit pending release.
    /// The local protection adapter must supply a NEW current-epoch clear proof.
    pub fn verified_clear(
        &mut self,
        proof: ProtectionProof,
        now_ns: u64,
    ) -> Result<(), ResourceError> {
        self.tick(now_ns)?;
        let i = self.index(proof.resource)?;
        let r = self.records[i];
        if !proof.permits(self.specs[i], self.epoch, now_ns)
            || !proof.clear
            || !proof.clearance_safe
            || proof.occupant.is_some()
            || r.grant
                .is_some_and(|g| proof.cleared_owner != Some(g.owner))
            || proof.sequence <= r.last_proof_sequence
        {
            return Err(ResourceError::Proof);
        }
        if r.phase == Phase::Unknown && now_ns < self.quarantine_until_ns {
            return Err(ResourceError::Time);
        }
        if !matches!(
            r.phase,
            Phase::Unknown | Phase::ReleasePending | Phase::Available
        ) {
            return Err(ResourceError::Phase);
        }
        self.records[i] = ResourceRecord {
            phase: Phase::Available,
            grant: None,
            last_proof_sequence: proof.sequence,
        };
        Ok(())
    }

    /// A signed request cannot allocate a conflicting lock, including a lock
    /// whose permission expired. Same-session, same-route active renewal is allowed.
    pub fn request(
        &mut self,
        owner: Owner,
        route: RouteId,
        direction: Direction,
        proof: ProtectionProof,
        now_ns: u64,
    ) -> Result<Grant, ResourceError> {
        self.tick(now_ns)?;
        let i = self.index(proof.resource)?;
        if owner.train.0 == 0 || owner.session == 0 || route.0 == 0 {
            return Err(ResourceError::Ownership);
        }
        if !proof.permits(self.specs[i], self.epoch, now_ns)
            || !proof.owns_or_clear(owner)
            || proof.sequence < self.records[i].last_proof_sequence
        {
            return Err(ResourceError::Proof);
        }
        if self.specs[i].points_required && proof.proved_route != Some(route) {
            return Err(ResourceError::Proof);
        }
        let previous = self.records[i];
        let renewing = previous.grant.is_some_and(|g| {
            g.owner == owner
                && g.route == route
                && g.direction == direction
                && g.epoch == self.epoch
                && matches!(previous.phase, Phase::Reserved | Phase::Occupied)
        });
        if !renewing {
            if previous.phase != Phase::Available {
                return Err(ResourceError::Conflict);
            }
            for (j, r) in self.records.iter().enumerate() {
                if j != i
                    && self.specs[i].conflicts & (1_u32 << j) != 0
                    && r.phase != Phase::Available
                {
                    return Err(ResourceError::Conflict);
                }
            }
        }
        let lease = if renewing {
            previous.grant.ok_or(ResourceError::Ownership)?.lease
        } else {
            self.serial.checked_add(1).ok_or(ResourceError::Overflow)?
        };
        let valid_until_ns = now_ns
            .checked_add(LEASE_NS)
            .ok_or(ResourceError::Overflow)?;
        let grant = Grant {
            resource: proof.resource,
            controller: self.controller,
            configuration: self.configuration,
            epoch: self.epoch,
            lease,
            owner,
            route,
            direction,
            issued_ns: now_ns,
            valid_until_ns,
        };
        self.serial = self.serial.max(lease);
        self.records[i] = ResourceRecord {
            phase: if renewing {
                previous.phase
            } else if proof.clear {
                Phase::Reserved
            } else {
                Phase::Occupied
            },
            grant: Some(grant),
            last_proof_sequence: proof.sequence,
        };
        Ok(grant)
    }

    fn owns(&self, g: Grant, i: usize) -> bool {
        self.records[i].grant.is_some_and(|held| held == g) && g.epoch == self.epoch
    }

    pub fn occupied(&mut self, grant: Grant, now_ns: u64) -> Result<(), ResourceError> {
        self.tick(now_ns)?;
        let i = self.index(grant.resource)?;
        if !self.owns(grant, i) {
            return Err(ResourceError::Ownership);
        }
        if !matches!(self.records[i].phase, Phase::Reserved | Phase::Occupied) {
            return Err(ResourceError::Phase);
        }
        self.records[i].phase = Phase::Occupied;
        Ok(())
    }

    pub fn begin_release(&mut self, grant: Grant, now_ns: u64) -> Result<(), ResourceError> {
        self.tick(now_ns)?;
        let i = self.index(grant.resource)?;
        if !self.owns(grant, i) {
            return Err(ResourceError::Ownership);
        }
        if self.records[i].phase == Phase::Blocked {
            return Err(ResourceError::Phase);
        }
        self.records[i].phase = Phase::ReleasePending;
        Ok(())
    }

    pub fn block(&mut self, resource: ResourceId) -> Result<(), ResourceError> {
        let i = self.index(resource)?;
        self.records[i].phase = Phase::Blocked;
        Ok(())
    }

    /// Reconcile a retained journal owner after restart using fresh identified
    /// occupancy/integrity and local route proving. This issues a new-epoch
    /// permission to THAT owner; it never clears or transfers the lock.
    pub fn reconcile_owner(
        &mut self,
        proof: ProtectionProof,
        now_ns: u64,
    ) -> Result<Grant, ResourceError> {
        self.tick(now_ns)?;
        let i = self.index(proof.resource)?;
        let r = self.records[i];
        let old = r.grant.ok_or(ResourceError::Ownership)?;
        if !((r.phase == Phase::Unknown && old.epoch < self.epoch)
            || (r.phase == Phase::ReleasePending && old.epoch == self.epoch))
        {
            return Err(ResourceError::Phase);
        }
        if !proof.permits(self.specs[i], self.epoch, now_ns)
            || proof.clear
            || !proof.owns_or_clear(old.owner)
            || proof.sequence <= r.last_proof_sequence
            || (self.specs[i].points_required && proof.proved_route != Some(old.route))
        {
            return Err(ResourceError::Proof);
        }
        for (j, other) in self.records.iter().enumerate() {
            if j != i
                && self.specs[i].conflicts & (1_u32 << j) != 0
                && other.grant.is_some_and(|g| g.owner != old.owner)
            {
                return Err(ResourceError::Conflict);
            }
        }
        let grant = Grant {
            epoch: self.epoch,
            issued_ns: now_ns,
            valid_until_ns: now_ns
                .checked_add(LEASE_NS)
                .ok_or(ResourceError::Overflow)?,
            ..old
        };
        self.records[i] = ResourceRecord {
            phase: Phase::Occupied,
            grant: Some(grant),
            last_proof_sequence: proof.sequence,
        };
        Ok(grant)
    }

    /// The caller DURABLY fences this epoch before emitting any response.
    /// Ownership remains unknown/protected until actual clearance is established.
    pub fn restart(&mut self, new_epoch: u64, now_ns: u64) -> Result<(), ResourceError> {
        if new_epoch <= self.epoch {
            return Err(ResourceError::Epoch);
        }
        let quarantine = now_ns
            .checked_add(LEASE_NS + CLOCK_SKEW_NS)
            .ok_or(ResourceError::Overflow)?;
        self.tick(now_ns)?;
        self.quarantine_until_ns = quarantine;
        self.epoch = new_epoch;
        for r in &mut self.records {
            if r.phase != Phase::Blocked {
                r.phase = Phase::Unknown;
            }
        }
        Ok(())
    }
}
