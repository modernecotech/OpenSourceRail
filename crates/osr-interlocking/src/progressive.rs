//! Offline progressive-departure candidate contract, distinct from StationLaunch.
//!
//! Initial authority ends at a proved stopping envelope, not at a remotely
//! reserved arrival berth. Readiness, detector, integrity and brake bounds are
//! unqualified external inputs. This API never commands traction/braking or
//! asserts physical acceptance. Routes have uniform speed limits; live speed
//! restrictions are unsupported and fence authority. Its finite-authority
//! invariant is tested below.
use crate::{
    resource_log::{ResourceEvent, ResourceLedger},
    resources::*,
};
use osr_core::{deployment::RailwayModel, resources::*, Direction, RouteId};
use serde::{Deserialize, Serialize};

pub const PROTOCOL: &str = "osr-progressive-departure/1";
/// Controlled numerical assumptions, not measured or accepted brake/sensor ratings.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgressivePolicy {
    pub maximum_acceleration_mmps2: u32,
    pub maximum_sample_ns: u64,
    pub velocity_error_mmps: u32,
    pub minimum_gap_um: u32,
    pub maximum_gap_um: u32,
}
/// One identified sample; health flags are external assertions. Independent
/// occupied-body detector proofs are also required from the resource ledger.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgressiveReadiness {
    pub configuration: ConfigurationId,
    pub owner: Owner,
    pub epoch: u64,
    pub sequence: u64,
    pub observed_ns: u64,
    pub front_mm: u64,
    pub velocity_mmps: u32,
    pub independent_brake_ready: bool,
    pub integrity_proved: bool,
    pub support_healthy: bool,
    pub minimum_gap_um: u32,
    pub maximum_gap_um: u32,
}
/// A stopped launch at a declared stopping location. This reserves only the
/// initial stopping envelope and does not promise a remotely free arrival berth.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DepartureRequest {
    pub id: u64,
    pub owner: Owner,
    pub route: RouteId,
    pub direction: Direction,
    pub configuration: ConfigurationId,
    pub readiness: ProgressiveReadiness,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum ProgressivePhase {
    Prepared,
    Committed,
    Arrived,
    Held,
    HeldStopped,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum ProgressiveError {
    Model,
    Time,
    Identity,
    Readiness,
    Sequence,
    Motion,
    Ownership,
    Conflict,
    Phase,
    Boundary,
    Proof,
    Overflow,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgressiveDeparture {
    pub request: DepartureRequest,
    pub phase: ProgressivePhase,
    pub last_readiness: ProgressiveReadiness,
    pub last_update_ns: u64,
    pub committed_readiness: Option<ProgressiveReadiness>,
    pub committed_ns: Option<u64>,
    pub protected_end_mm: u64,
    pub stop_required: bool,
    pub hold_reason: Option<ProgressiveError>,
    /// Calculated immediate stopping margin when a fresh extension is refused.
    /// None means current evidence cannot demonstrate the stopping guarantee.
    pub hold_stopping_margin_mm: Option<i64>,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub enum ProgressiveEvent {
    Evidence(ResourceEvent),
    Prepare(DepartureRequest),
    Commit {
        id: u64,
        readiness: ProgressiveReadiness,
    },
    Extend {
        id: u64,
        readiness: ProgressiveReadiness,
    },
    ArriveStopped {
        id: u64,
        readiness: ProgressiveReadiness,
    },
    ObserveHeld {
        id: u64,
        readiness: ProgressiveReadiness,
    },
    Release {
        id: u64,
        readiness: ProgressiveReadiness,
        resource: ResourceId,
        proof: ProtectionProof,
    },
    Restart {
        new_epoch: u64,
    },
}
/// Pure event fold for an explicitly offline candidate. The caller must retain
/// authenticated, durably committed events before acting on any decision.
/// Checksums and serde roundtrips do not establish that external responsibility.
///
/// Deserialization always fences movement, commit and new departure. Restart
/// retains owners and the fence. Snapshot recovery/reconciliation and automatic
/// resumption are deliberately unsupported in this revision.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProgressiveDomain {
    ledger: ResourceLedger,
    policy: ProgressivePolicy,
    departures: Vec<ProgressiveDeparture>,
    last_id: u64,
    last_now_ns: u64,
    /// Deserialised state is an observation, never restored movement authority.
    /// Reconciliation/resumption from snapshots is intentionally unimplemented.
    #[serde(skip, default)]
    live_epoch: bool,
}
impl ProgressiveDomain {
    /// Fresh controlled startup; must not be used to bypass a retained snapshot
    /// or the outstanding recovery/reconciliation requirement after a restart.
    pub fn new(
        model: RailwayModel,
        configuration: ConfigurationId,
        policy: ProgressivePolicy,
        now: u64,
    ) -> Result<Self, ProgressiveError> {
        if policy.maximum_acceleration_mmps2 > 2000
            || policy.maximum_sample_ns == 0
            || policy.maximum_sample_ns > 100_000_000
            || policy.velocity_error_mmps > 1000
            || policy.minimum_gap_um == 0
            || policy.maximum_gap_um <= policy.minimum_gap_um
            || policy.maximum_gap_um > 30000
        {
            return Err(ProgressiveError::Model);
        }
        if model.routes.iter().any(|r| {
            r.segments.first().is_none_or(|first| {
                r.segments
                    .iter()
                    .any(|s| s.speed_limit_mmps != first.speed_limit_mmps)
            })
        }) {
            return Err(ProgressiveError::Model);
        }
        let ledger =
            ResourceLedger::new(model, configuration, now).map_err(|_| ProgressiveError::Model)?;
        Ok(Self {
            ledger,
            policy,
            departures: Vec::new(),
            last_id: 0,
            last_now_ns: now,
            live_epoch: true,
        })
    }
    pub fn ledger(&self) -> &ResourceLedger {
        &self.ledger
    }
    pub fn policy(&self) -> ProgressivePolicy {
        self.policy
    }
    pub fn departures(&self) -> &[ProgressiveDeparture] {
        &self.departures
    }
    pub fn last_now_ns(&self) -> u64 {
        self.last_now_ns
    }
    pub fn restore_fenced(&self) -> bool {
        !self.live_epoch
    }
    pub fn departure(&self, id: u64) -> Option<&ProgressiveDeparture> {
        self.departures.iter().find(|d| d.request.id == id)
    }
    fn index(&self, id: u64) -> Result<usize, ProgressiveError> {
        self.departures
            .iter()
            .position(|d| d.request.id == id)
            .ok_or(ProgressiveError::Identity)
    }
    fn config(&self, owner: Owner) -> Result<TrainConfig, ProgressiveError> {
        self.ledger
            .model
            .trains
            .iter()
            .find(|t| t.config.owner == owner)
            .map(|t| t.config)
            .ok_or(ProgressiveError::Identity)
    }
    fn route(
        &self,
        id: RouteId,
    ) -> Result<&osr_core::deployment::RouteDefinition, ProgressiveError> {
        self.ledger
            .model
            .routes
            .iter()
            .find(|r| r.id == id)
            .ok_or(ProgressiveError::Model)
    }
    fn readiness(
        &self,
        r: ProgressiveReadiness,
        now: u64,
    ) -> Result<TrainConfig, ProgressiveError> {
        let cfg = self.config(r.owner)?;
        if r.configuration != self.ledger.configuration || r.epoch != self.ledger.controller.epoch()
        {
            return Err(ProgressiveError::Identity);
        }
        if r.sequence == 0
            || !fresh(r.observed_ns, now)
            || !r.integrity_proved
            || !r.independent_brake_ready
            || !r.support_healthy
            || self.ledger.integrity.get(&r.owner.train) != Some(&true)
            || r.minimum_gap_um < self.policy.minimum_gap_um
            || r.maximum_gap_um > self.policy.maximum_gap_um
            || r.minimum_gap_um > r.maximum_gap_um
            || r.velocity_mmps > MAX_SPEED_MMPS
            || r.front_mm > MAX_ROUTE_MM
        {
            return Err(ProgressiveError::Readiness);
        }
        let route = self
            .ledger
            .model
            .trains
            .iter()
            .find(|t| t.config.owner == r.owner)
            .ok_or(ProgressiveError::Identity)?
            .permitted_route;
        let rear = r.front_mm.saturating_sub(
            u64::from(cfg.length_mm) + u64::from(cfg.maximum_position_uncertainty_mm),
        );
        let speed_limit = self
            .route(route)?
            .segments
            .iter()
            .filter(|s| {
                s.end_mm >= rear
                    && s.start_mm <= r.front_mm + u64::from(cfg.maximum_position_uncertainty_mm)
            })
            .map(|s| s.speed_limit_mmps)
            .min()
            .ok_or(ProgressiveError::Boundary)?;
        if r.velocity_mmps
            .saturating_add(self.policy.velocity_error_mmps)
            > speed_limit
        {
            return Err(ProgressiveError::Readiness);
        }
        Ok(cfg)
    }
    fn stop_distance(
        &self,
        r: ProgressiveReadiness,
        cfg: TrainConfig,
        route: RouteId,
        now: u64,
        include_next_sample: bool,
    ) -> Result<u64, ProgressiveError> {
        let grade = self
            .route(route)?
            .segments
            .iter()
            .filter(|s| s.end_mm >= r.front_mm)
            .map(|s| s.downhill_permille)
            .max()
            .unwrap_or(0);
        let ceil = |a: u128, b: u128| a.div_ceil(b);
        let t = u128::from(cfg.reaction_time_ms) * 1_000_000
            + u128::from(
                now.checked_sub(r.observed_ns)
                    .ok_or(ProgressiveError::Time)?,
            )
            + u128::from(self.ledger.model.runtime.clock_error_ns)
            + if include_next_sample {
                u128::from(self.policy.maximum_sample_ns)
            } else {
                0
            };
        let v = u128::from(r.velocity_mmps) + u128::from(self.policy.velocity_error_mmps);
        let a = u128::from(self.policy.maximum_acceleration_mmps2);
        let vp = v + ceil(a * t, 1_000_000_000);
        let gravity = ceil(9810 * u128::from(grade), 1000);
        let net = u128::from(cfg.minimum_deceleration_mmps2)
            .checked_sub(gravity)
            .filter(|n| *n > 0)
            .ok_or(ProgressiveError::Model)?;
        u64::try_from(
            ceil(v * t, 1_000_000_000)
                + ceil(a * t * t, 2_000_000_000_000_000_000)
                + ceil(vp * vp, 2 * net)
                + u128::from(cfg.stop_margin_mm)
                + u128::from(cfg.maximum_position_uncertainty_mm),
        )
        .map_err(|_| ProgressiveError::Overflow)
    }
    fn resources(
        &self,
        r: ProgressiveReadiness,
        cfg: TrainConfig,
        route: RouteId,
        now: u64,
    ) -> Result<Vec<ResourceId>, ProgressiveError> {
        let rear = r
            .front_mm
            .checked_sub(u64::from(cfg.length_mm) + u64::from(cfg.maximum_position_uncertainty_mm))
            .ok_or(ProgressiveError::Boundary)?;
        let end = r
            .front_mm
            .checked_add(self.stop_distance(r, cfg, route, now, true)?)
            .ok_or(ProgressiveError::Overflow)?;
        let path = self.route(route)?;
        if end > path.segments.last().ok_or(ProgressiveError::Model)?.end_mm {
            return Err(ProgressiveError::Boundary);
        }
        Ok(path
            .segments
            .iter()
            .filter(|s| s.end_mm >= rear && s.start_mm <= end)
            .map(|s| s.resource)
            .collect())
    }
    fn owned_end(&self, r: ProgressiveReadiness, cfg: TrainConfig, route: RouteId) -> u64 {
        let rear = r.front_mm.saturating_sub(
            u64::from(cfg.length_mm) + u64::from(cfg.maximum_position_uncertainty_mm),
        );
        let mut end = rear;
        if let Ok(path) = self.route(route) {
            for s in path.segments.iter().filter(|s| s.end_mm >= rear) {
                if !self.ledger.controller.records()[usize::from(s.resource.0)]
                    .grant
                    .is_some_and(|g| g.owner == r.owner)
                {
                    break;
                }
                end = s.end_mm;
            }
        }
        end
    }
    fn fresh_progress(
        &self,
        i: usize,
        r: ProgressiveReadiness,
        now: u64,
    ) -> Result<TrainConfig, ProgressiveError> {
        let old = &self.departures[i];
        let cfg = self.readiness(r, now)?;
        if old.request.owner != r.owner {
            return Err(ProgressiveError::Identity);
        }
        if r.sequence <= old.last_readiness.sequence {
            return Err(ProgressiveError::Sequence);
        }
        if now < old.last_update_ns || now - old.last_update_ns > self.policy.maximum_sample_ns {
            return Err(ProgressiveError::Time);
        }
        if r.front_mm < old.last_readiness.front_mm {
            return Err(ProgressiveError::Motion);
        }
        let dt = u128::from(now - old.last_update_ns);
        let prior = u128::from(old.last_readiness.velocity_mmps)
            + u128::from(self.policy.velocity_error_mmps);
        let upper = u128::from(old.last_readiness.front_mm)
            + prior * dt / 1_000_000_000
            + (u128::from(self.policy.maximum_acceleration_mmps2) * dt * dt)
                .div_ceil(2_000_000_000_000_000_000)
            + 2 * u128::from(cfg.maximum_position_uncertainty_mm);
        if u128::from(r.front_mm) > upper {
            return Err(ProgressiveError::Motion);
        }
        let upper_speed = prior
            + (u128::from(self.policy.maximum_acceleration_mmps2) * dt).div_ceil(1_000_000_000)
            + u128::from(self.policy.velocity_error_mmps);
        if u128::from(r.velocity_mmps) > upper_speed {
            return Err(ProgressiveError::Motion);
        }
        Ok(cfg)
    }
    fn allocate(
        &self,
        r: ProgressiveReadiness,
        cfg: TrainConfig,
        route: RouteId,
        direction: Direction,
        now: u64,
    ) -> Result<ResourceLedger, ProgressiveError> {
        let ids = self.resources(r, cfg, route, now)?;
        let mut proposed = self.ledger.clone();
        for resource in ids {
            let p = self.ledger.proofs[usize::from(resource.0)].ok_or(ProgressiveError::Proof)?;
            if !p.occupancy_integrity_proved
                || p.restriction != Restriction::Open
                || (p.clear && !p.clearance_safe)
            {
                return Err(ProgressiveError::Proof);
            }
            let segment = self
                .route(route)?
                .segments
                .iter()
                .find(|s| s.resource == resource)
                .ok_or(ProgressiveError::Model)?;
            let nominal_rear = r.front_mm.saturating_sub(u64::from(cfg.length_mm));
            if segment.start_mm <= r.front_mm && segment.end_mm >= nominal_rear {
                let p =
                    self.ledger.proofs[usize::from(resource.0)].ok_or(ProgressiveError::Proof)?;
                if p.clear || p.occupant != Some(r.owner) || !p.occupancy_integrity_proved {
                    return Err(ProgressiveError::Proof);
                }
            }
            proposed
                .apply(
                    &ResourceEvent::Reserve {
                        owner: r.owner,
                        resource,
                        route,
                        direction,
                    },
                    now,
                )
                .map_err(|e| match e {
                    ResourceError::Conflict => ProgressiveError::Conflict,
                    _ => ProgressiveError::Proof,
                })?;
        }
        Ok(proposed)
    }
    fn hold(&mut self, i: usize, r: ProgressiveReadiness, now: u64, reason: ProgressiveError) {
        let valid_report = self.fresh_progress(i, r, now).is_ok();
        let margin = if valid_report {
            self.readiness(r, now)
                .ok()
                .and_then(|cfg| {
                    self.stop_distance(r, cfg, self.departures[i].request.route, now, false)
                        .ok()
                        .map(|d| (cfg, d))
                })
                .and_then(|(cfg, d)| {
                    i64::try_from(self.owned_end(r, cfg, self.departures[i].request.route))
                        .ok()
                        .zip(i64::try_from(r.front_mm + d).ok())
                        .map(|(end, stop)| end - stop)
                })
        } else {
            None
        };
        let d = &mut self.departures[i];
        if valid_report {
            d.last_readiness = r;
            d.last_update_ns = now;
        }
        d.phase = ProgressivePhase::Held;
        d.stop_required = true;
        d.hold_reason = Some(reason);
        d.hold_stopping_margin_mm = margin;
    }
    pub fn apply(&mut self, event: &ProgressiveEvent, now: u64) -> Result<(), ProgressiveError> {
        if now == 0 || now < self.last_now_ns {
            return Err(ProgressiveError::Time);
        }
        self.last_now_ns = now;
        if !self.live_epoch
            && !matches!(
                event,
                ProgressiveEvent::Restart { .. } | ProgressiveEvent::Evidence(_)
            )
        {
            return Err(ProgressiveError::Phase);
        }
        match event {
            ProgressiveEvent::Evidence(e) => {
                if !matches!(
                    e,
                    ResourceEvent::LocalProof(_)
                        | ResourceEvent::Integrity { .. }
                        | ResourceEvent::Block(_)
                        | ResourceEvent::Clear(_)
                ) {
                    return Err(ProgressiveError::Phase);
                }
                if let ResourceEvent::Clear(id) = e {
                    if self
                        .ledger
                        .controller
                        .records()
                        .get(usize::from(id.0))
                        .is_some_and(|r| r.grant.is_some())
                    {
                        return Err(ProgressiveError::Ownership);
                    }
                }
                self.ledger
                    .apply(e, now)
                    .map_err(|_| ProgressiveError::Proof)?;
                let held: Vec<_> = self
                    .departures
                    .iter()
                    .enumerate()
                    .filter(|(_, d)| {
                        matches!(
                            d.phase,
                            ProgressivePhase::Prepared
                                | ProgressivePhase::Committed
                                | ProgressivePhase::Arrived
                        )
                    })
                    .filter(|(_, d)| match e {
                        ResourceEvent::Integrity { owner, proved } => {
                            *owner == d.request.owner && !*proved
                        }
                        ResourceEvent::Block(id) => self.ledger.controller.records()
                            [usize::from(id.0)]
                        .grant
                        .is_some_and(|g| g.owner == d.request.owner),
                        ResourceEvent::LocalProof(p) => {
                            self.ledger.controller.records()[usize::from(p.resource.0)]
                                .grant
                                .is_some_and(|g| g.owner == d.request.owner)
                                && (!p.owns_or_clear(d.request.owner)
                                    || !p.occupancy_integrity_proved
                                    || !fresh(p.observed_ns, now)
                                    || p.restriction != Restriction::Open
                                    || (p.clear && !p.clearance_safe))
                        }
                        _ => false,
                    })
                    .map(|(i, _)| i)
                    .collect();
                for i in held {
                    let r = self.departures[i].last_readiness;
                    self.hold(i, r, now, ProgressiveError::Proof);
                }
                Ok(())
            }
            ProgressiveEvent::Prepare(request) => {
                if let Some(old) = self.departure(request.id) {
                    return if old.request == *request {
                        Ok(())
                    } else {
                        Err(ProgressiveError::Identity)
                    };
                }
                if request.id <= self.last_id
                    || request.configuration != self.ledger.configuration
                    || request.owner != request.readiness.owner
                {
                    return Err(ProgressiveError::Identity);
                }
                let cfg = self.readiness(request.readiness, now)?;
                let route = self.route(request.route)?;
                if self
                    .ledger
                    .model
                    .trains
                    .iter()
                    .find(|t| t.config.owner == request.owner)
                    .is_none_or(|t| t.permitted_route != request.route)
                    || route.direction != request.direction
                {
                    return Err(ProgressiveError::Identity);
                }
                if request.readiness.velocity_mmps != 0
                    || !route.stopping_locations.iter().any(|s| {
                        s.at_mm.abs_diff(request.readiness.front_mm)
                            <= u64::from(cfg.maximum_position_uncertainty_mm)
                    })
                {
                    return Err(ProgressiveError::Motion);
                }
                if self.departures.iter().any(|d| {
                    d.request.owner == request.owner
                        && matches!(
                            d.phase,
                            ProgressivePhase::Prepared
                                | ProgressivePhase::Committed
                                | ProgressivePhase::Held
                                | ProgressivePhase::HeldStopped
                        )
                }) {
                    return Err(ProgressiveError::Phase);
                }
                if let Some((i, _)) = self
                    .departures
                    .iter()
                    .enumerate()
                    .filter(|(_, d)| d.request.owner == request.owner)
                    .max_by_key(|(_, d)| d.request.id)
                {
                    self.fresh_progress(i, request.readiness, now)?;
                }
                let proposed = self.allocate(
                    request.readiness,
                    cfg,
                    request.route,
                    request.direction,
                    now,
                )?;
                if self.departures.len() >= MAX_RESOURCES {
                    let i = self
                        .departures
                        .iter()
                        .position(|d| {
                            d.phase == ProgressivePhase::Arrived
                                && (d.request.owner == request.owner
                                    || self.departures.iter().any(|later| {
                                        later.request.owner == d.request.owner
                                            && later.request.id > d.request.id
                                    }))
                        })
                        .ok_or(ProgressiveError::Model)?;
                    self.departures.remove(i);
                }
                self.ledger = proposed;
                let end = self.owned_end(request.readiness, cfg, request.route);
                self.departures.push(ProgressiveDeparture {
                    request: *request,
                    phase: ProgressivePhase::Prepared,
                    last_readiness: request.readiness,
                    last_update_ns: now,
                    committed_readiness: None,
                    committed_ns: None,
                    protected_end_mm: end,
                    stop_required: false,
                    hold_reason: None,
                    hold_stopping_margin_mm: None,
                });
                self.last_id = request.id;
                Ok(())
            }
            ProgressiveEvent::Commit { id, readiness } => {
                let i = self.index(*id)?;
                let d = &self.departures[i];
                if d.committed_readiness == Some(*readiness)
                    && matches!(
                        d.phase,
                        ProgressivePhase::Committed | ProgressivePhase::Arrived
                    )
                {
                    return Ok(());
                }
                if d.phase != ProgressivePhase::Prepared {
                    return Err(ProgressiveError::Phase);
                }
                let result = (|| {
                    let cfg = self.fresh_progress(i, *readiness, now)?;
                    if readiness.velocity_mmps != 0
                        || readiness.front_mm != d.request.readiness.front_mm
                    {
                        return Err(ProgressiveError::Motion);
                    }
                    let proposed =
                        self.allocate(*readiness, cfg, d.request.route, d.request.direction, now)?;
                    for resource in self.resources(*readiness, cfg, d.request.route, now)? {
                        let section = proposed.model.resources[usize::from(resource.0)].section;
                        if !proposed.permits(section, readiness.owner.train, now) {
                            return Err(ProgressiveError::Proof);
                        }
                    }
                    Ok(proposed)
                })();
                let proposed = match result {
                    Ok(ledger) => ledger,
                    Err(e) => {
                        self.hold(i, *readiness, now, e);
                        return Err(e);
                    }
                };
                self.ledger = proposed;
                let d = &mut self.departures[i];
                d.phase = ProgressivePhase::Committed;
                d.committed_readiness = Some(*readiness);
                d.committed_ns = Some(now);
                d.last_readiness = *readiness;
                d.last_update_ns = now;
                Ok(())
            }
            ProgressiveEvent::Extend { id, readiness } => {
                let i = self.index(*id)?;
                let d = &self.departures[i];
                if !matches!(
                    d.phase,
                    ProgressivePhase::Committed | ProgressivePhase::Arrived
                ) {
                    return Err(ProgressiveError::Phase);
                }
                if d.last_readiness == *readiness {
                    return Ok(());
                }
                let result = (|| {
                    let cfg = self.fresh_progress(i, *readiness, now)?;
                    if d.phase == ProgressivePhase::Arrived && readiness.velocity_mmps != 0 {
                        return Err(ProgressiveError::Phase);
                    }
                    self.allocate(*readiness, cfg, d.request.route, d.request.direction, now)
                        .map(|ledger| (cfg, ledger))
                })();
                match result {
                    Ok((cfg, ledger)) => {
                        self.ledger = ledger;
                        let end = self.owned_end(*readiness, cfg, self.departures[i].request.route);
                        let d = &mut self.departures[i];
                        d.last_readiness = *readiness;
                        d.last_update_ns = now;
                        d.protected_end_mm = end;
                        Ok(())
                    }
                    Err(e) => {
                        self.hold(i, *readiness, now, e);
                        Err(e)
                    }
                }
            }
            ProgressiveEvent::ArriveStopped { id, readiness } => {
                let i = self.index(*id)?;
                if self.departures[i].phase != ProgressivePhase::Committed {
                    return Err(ProgressiveError::Phase);
                }
                let checked = (|| {
                    let cfg = self.fresh_progress(i, *readiness, now)?;
                    let route = self.departures[i].request.route;
                    if readiness.velocity_mmps != 0
                        || !self.route(route)?.stopping_locations.iter().any(|s| {
                            s.at_mm.abs_diff(readiness.front_mm)
                                <= u64::from(cfg.maximum_position_uncertainty_mm)
                        })
                    {
                        return Err(ProgressiveError::Motion);
                    }
                    self.allocate(
                        *readiness,
                        cfg,
                        route,
                        self.departures[i].request.direction,
                        now,
                    )
                })();
                let proposed = match checked {
                    Ok(proposed) => proposed,
                    Err(e) => {
                        self.hold(i, *readiness, now, e);
                        return Err(e);
                    }
                };
                self.ledger = proposed;
                let d = &mut self.departures[i];
                d.phase = ProgressivePhase::Arrived;
                d.last_readiness = *readiness;
                d.last_update_ns = now;
                Ok(())
            }
            ProgressiveEvent::ObserveHeld { id, readiness } => {
                let i = self.index(*id)?;
                if !matches!(
                    self.departures[i].phase,
                    ProgressivePhase::Held | ProgressivePhase::HeldStopped
                ) {
                    return Err(ProgressiveError::Phase);
                }
                let cfg = self.fresh_progress(i, *readiness, now)?;
                let end = self.owned_end(*readiness, cfg, self.departures[i].request.route);
                if readiness.front_mm + u64::from(cfg.maximum_position_uncertainty_mm) > end {
                    return Err(ProgressiveError::Boundary);
                }
                let d = &mut self.departures[i];
                d.last_readiness = *readiness;
                d.last_update_ns = now;
                if readiness.velocity_mmps == 0 {
                    d.phase = ProgressivePhase::HeldStopped;
                }
                Ok(())
            }
            ProgressiveEvent::Release {
                id,
                readiness,
                resource,
                proof,
            } => {
                let i = self.index(*id)?;
                let d = &self.departures[i];
                let cfg = self.readiness(*readiness, now)?;
                if readiness.owner != d.request.owner
                    || *readiness != d.last_readiness
                    || now.saturating_sub(d.last_update_ns) > self.policy.maximum_sample_ns
                    || self.departures.iter().any(|later| {
                        later.request.owner == d.request.owner && later.request.id > d.request.id
                    })
                {
                    return Err(ProgressiveError::Identity);
                }
                let s = self
                    .route(d.request.route)?
                    .segments
                    .iter()
                    .find(|s| s.resource == *resource)
                    .ok_or(ProgressiveError::Model)?;
                let rear = readiness.front_mm.saturating_sub(
                    u64::from(cfg.length_mm) + u64::from(cfg.maximum_position_uncertainty_mm),
                );
                let tail = rear > s.end_mm;
                let stopped = matches!(
                    d.phase,
                    ProgressivePhase::Arrived | ProgressivePhase::HeldStopped
                ) && readiness.velocity_mmps == 0
                    && readiness.front_mm + u64::from(cfg.maximum_position_uncertainty_mm)
                        < s.start_mm;
                if !tail && !stopped {
                    return Err(ProgressiveError::Motion);
                }
                if !matches!(
                    d.phase,
                    ProgressivePhase::Committed
                        | ProgressivePhase::Arrived
                        | ProgressivePhase::HeldStopped
                ) {
                    return Err(ProgressiveError::Phase);
                }
                if proof.resource != *resource
                    || proof.cleared_owner != Some(readiness.owner)
                    || !proof.clear
                    || !proof.clearance_safe
                    || !proof.occupancy_integrity_proved
                {
                    return Err(ProgressiveError::Proof);
                }
                let grant = self.ledger.controller.records()[usize::from(resource.0)]
                    .grant
                    .filter(|g| g.owner == readiness.owner)
                    .ok_or(ProgressiveError::Ownership)?;
                let mut proposed = self.ledger.clone();
                proposed
                    .apply(&ResourceEvent::Withdraw(grant), now)
                    .map_err(|_| ProgressiveError::Proof)?;
                proposed
                    .apply(&ResourceEvent::LocalProof(*proof), now)
                    .map_err(|_| ProgressiveError::Proof)?;
                proposed
                    .apply(&ResourceEvent::Clear(*resource), now)
                    .map_err(|_| ProgressiveError::Proof)?;
                self.ledger = proposed;
                let end = self.owned_end(*readiness, cfg, self.departures[i].request.route);
                self.departures[i].protected_end_mm = end;
                Ok(())
            }
            ProgressiveEvent::Restart { new_epoch } => {
                self.ledger
                    .apply(&ResourceEvent::Restart(*new_epoch), now)
                    .map_err(|_| ProgressiveError::Proof)?;
                for d in &mut self.departures {
                    if matches!(
                        d.phase,
                        ProgressivePhase::Prepared
                            | ProgressivePhase::Committed
                            | ProgressivePhase::Arrived
                    ) {
                        d.phase = ProgressivePhase::Held;
                        d.stop_required = true;
                        d.hold_reason = Some(ProgressiveError::Phase);
                        d.hold_stopping_margin_mm = None;
                    }
                }
                Ok(())
            }
        }
    }
    /// Assumed stopping bound including reaction, next sample, observation age,
    /// clock error, acceleration, velocity/position error and a stop margin.
    pub fn required_stop_front_mm(&self, id: u64, now: u64) -> Option<u64> {
        let d = self.departure(id)?;
        let cfg = self.readiness(d.last_readiness, now).ok()?;
        d.last_readiness.front_mm.checked_add(
            self.stop_distance(d.last_readiness, cfg, d.request.route, now, true)
                .ok()?,
        )
    }
    /// A bounded offline authority decision. Expired/held/prepared contracts
    /// cannot authorize continued motion even though resource locks remain.
    pub fn may_move(&self, id: u64, now: u64) -> bool {
        if !self.live_epoch {
            return false;
        }
        let Some(d) = self.departure(id) else {
            return false;
        };
        if d.phase != ProgressivePhase::Committed
            || now < d.last_update_ns
            || now - d.last_update_ns > self.policy.maximum_sample_ns
        {
            return false;
        }
        let Ok(cfg) = self.readiness(d.last_readiness, now) else {
            return false;
        };
        let Ok(ids) = self.resources(d.last_readiness, cfg, d.request.route, now) else {
            return false;
        };
        ids.iter().all(|id| {
            let i = usize::from(id.0);
            let Some(p) = self.ledger.proofs[i] else {
                return false;
            };
            if p.restriction != Restriction::Open
                || !p.occupancy_integrity_proved
                || (p.clear && !p.clearance_safe)
            {
                return false;
            }
            let Some(segment) = self
                .ledger
                .model
                .routes
                .iter()
                .find(|r| r.id == d.request.route)
                .and_then(|r| r.segments.iter().find(|s| s.resource == *id))
            else {
                return false;
            };
            let rear = d
                .last_readiness
                .front_mm
                .saturating_sub(u64::from(cfg.length_mm));
            if segment.start_mm <= d.last_readiness.front_mm
                && segment.end_mm >= rear
                && (p.clear || p.occupant != Some(d.request.owner))
            {
                return false;
            }
            self.ledger.permits(
                self.ledger.model.resources[usize::from(id.0)].section,
                d.request.owner.train,
                now,
            )
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{SectionId, TrainId};
    use serde_json::json;
    const CFG: ConfigurationId = [7; 32];
    const NOW: u64 = 1_000_000_000;
    const OWNER: Owner = Owner {
        train: TrainId(101),
        session: 1,
    };
    fn model() -> RailwayModel {
        let edges = [0_u64, 350000, 1000000, 2000000, 2350000, 2425000, 3000000];
        let resources:Vec<_>=(0..6).map(|i|json!({"id":i,"section":100+i,"asset_id":format!("resource-{i}"),"kind":if i==0||i==3{"platform"}else{"track"},"controller":900,"conflicts":[i],"point_asset_id":null,"clearance_basis":"synthetic independent whole-consist detector"})).collect();
        let segments:Vec<_>=(0..6).map(|i|json!({"resource":i,"start_mm":edges[i],"end_mm":edges[i+1],"speed_limit_mmps":22223,"downhill_permille":0})).collect();
        let mut participants:Vec<_>=(1..=3).map(|i|json!({"entity":i,"role":"Voter","session":1,"public_key":vec![i;32],"revoked":false,"resources":[]})).collect();
        for i in 101..=102 {
            participants.push(json!({"entity":i,"role":"Train","session":1,"public_key":vec![i-96;32],"revoked":false,"resources":[]}));
        }
        let trains:Vec<_>=(101..=102).map(|i|json!({"asset_id":format!("train-{i}"),"config":{"owner":{"train":i,"session":1},"configuration":CFG,"length_mm":104500,"minimum_deceleration_mmps2":600,"reaction_time_ms":200,"stop_margin_mm":100000,"maximum_position_uncertainty_mm":500},"integrity_arrangement":"synthetic complete six-car integrity","braking_evidence":"constant unqualified0.6m/s² independent brake","permitted_route":1})).collect();
        serde_json::from_value(json!({"schema":"osr-tacs-railway/2","revision":"progressive-tests-1","approval_state":"prototype-unapproved","runtime":{"voters":[1,2,3],"participants":participants,"designed_revision":"progressive-tests-1","installed_state":"not-installed","approved_operating_profile":"prototype-unapproved","clock_error_ns":0},"resources":resources,"routes":[{"id":1,"asset_id":"fixed-line","direction":"Forward","leader_required":false,"operating_scope":"local offline finite authority study","segments":segments,"stopping_locations":[{"asset_id":"departure","at_mm":300000,"platform":0,"charger_asset_id":"charger-0","minimum_departure_energy_wh":10000},{"asset_id":"arrival","at_mm":2150000,"platform":3,"charger_asset_id":"charger-1","minimum_departure_energy_wh":10000}]}],"trains":trains,"controllers":[{"id":900,"asset_id":"local-controller","startup_epoch":1,"restart_reconciliation":"retain all owners; no automatic motion"}],"protected_work_resources":[],"maintenance_procedure":"offline tests only"})).unwrap()
    }
    fn policy() -> ProgressivePolicy {
        ProgressivePolicy {
            maximum_acceleration_mmps2: 1000,
            maximum_sample_ns: 100_000_000,
            velocity_error_mmps: 0,
            minimum_gap_um: 3000,
            maximum_gap_um: 13000,
        }
    }
    fn ready(seq: u64, now: u64, front: u64, v: u32) -> ProgressiveReadiness {
        ProgressiveReadiness {
            configuration: CFG,
            owner: OWNER,
            epoch: 1,
            sequence: seq,
            observed_ns: now,
            front_mm: front,
            velocity_mmps: v,
            independent_brake_ready: true,
            integrity_proved: true,
            support_healthy: true,
            minimum_gap_um: 6000,
            maximum_gap_um: 8000,
        }
    }
    fn clearproof(i: u8, sequence: u64, now: u64) -> ProtectionProof {
        ProtectionProof {
            resource: ResourceId(i),
            controller: ControllerId(900),
            epoch: 1,
            sequence,
            observed_ns: now,
            clear: true,
            clearance_safe: true,
            cleared_owner: None,
            occupant: None,
            occupancy_integrity_proved: true,
            points_locked_and_proved: false,
            proved_route: None,
            restriction: Restriction::Open,
        }
    }
    fn fixture() -> ProgressiveDomain {
        let mut d = ProgressiveDomain::new(model(), CFG, policy(), NOW).unwrap();
        for train in [101, 102] {
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::Integrity {
                    owner: Owner {
                        train: TrainId(train),
                        session: 1,
                    },
                    proved: true,
                }),
                NOW,
            )
            .unwrap();
        }
        for i in 0..6 {
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(clearproof(i, 1, NOW))),
                NOW,
            )
            .unwrap();
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::Clear(ResourceId(i))),
                NOW,
            )
            .unwrap();
        }
        refresh(&mut d, NOW, 300000);
        d
    }
    fn refresh(d: &mut ProgressiveDomain, now: u64, front: u64) {
        let segments = d.ledger.model.routes[0].segments.clone();
        for s in segments {
            let i = usize::from(s.resource.0);
            let mut p = clearproof(s.resource.0, d.ledger.proofs[i].unwrap().sequence + 1, now);
            if front >= s.start_mm && front.saturating_sub(104500) <= s.end_mm {
                p.clear = false;
                p.occupant = Some(OWNER);
            }
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
                now,
            )
            .unwrap();
        }
    }
    fn request() -> DepartureRequest {
        DepartureRequest {
            id: 1,
            owner: OWNER,
            route: RouteId(1),
            direction: Direction::Forward,
            configuration: CFG,
            readiness: ready(1, NOW, 300000, 0),
        }
    }
    fn launch(d: &mut ProgressiveDomain) {
        d.apply(&ProgressiveEvent::Prepare(request()), NOW).unwrap();
        d.apply(
            &ProgressiveEvent::Commit {
                id: 1,
                readiness: ready(2, NOW, 300000, 0),
            },
            NOW,
        )
        .unwrap();
    }
    #[test]
    fn prepare_is_atomic_and_does_not_reserve_a_receiving_berth() {
        let mut d = fixture();
        d.apply(
            &ProgressiveEvent::Evidence(ResourceEvent::Block(ResourceId(1))),
            NOW,
        )
        .unwrap();
        let old = d.ledger.controller.records().to_vec();
        assert!(d.apply(&ProgressiveEvent::Prepare(request()), NOW).is_err());
        assert_eq!(d.ledger.controller.records(), old);
        assert!(d.departures.is_empty());
        let mut d = fixture();
        d.apply(&ProgressiveEvent::Prepare(request()), NOW).unwrap();
        assert!(!d.may_move(1, NOW));
        assert!(d.ledger.controller.records()[0].grant.is_some());
        assert!(d.ledger.controller.records()[1].grant.is_some());
        assert!(
            d.ledger.controller.records()[3].grant.is_none(),
            "remote receiving berth must not be relabelled as initial stop authority"
        );
        d.apply(
            &ProgressiveEvent::Commit {
                id: 1,
                readiness: ready(2, NOW, 300000, 0),
            },
            NOW,
        )
        .unwrap();
        assert!(d.may_move(1, NOW));
        assert!(!d.may_move(1, NOW + 100_000_001));
    }
    #[test]
    fn readiness_and_clear_body_counterexamples_retain_prepared_locks() {
        for case in 0..5 {
            let mut d = fixture();
            d.apply(&ProgressiveEvent::Prepare(request()), NOW).unwrap();
            let before = d
                .ledger
                .controller
                .records()
                .iter()
                .map(|r| r.grant)
                .collect::<Vec<_>>();
            let mut r = ready(2, NOW, 300000, 0);
            match case {
                0 => r.independent_brake_ready = false,
                1 => r.integrity_proved = false,
                2 => r.minimum_gap_um = 2999,
                3 => r.support_healthy = false,
                _ => {
                    let p = clearproof(0, 99, NOW);
                    d.apply(
                        &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
                        NOW,
                    )
                    .unwrap();
                }
            }
            assert!(d
                .apply(
                    &ProgressiveEvent::Commit {
                        id: 1,
                        readiness: r
                    },
                    NOW
                )
                .is_err());
            assert!(!d.may_move(1, NOW));
            assert_eq!(
                d.ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect::<Vec<_>>(),
                before
            );
        }
    }
    #[test]
    fn snapshots_before_and_after_commit_cannot_resume_after_restart() {
        for commit in [false, true] {
            let mut d = fixture();
            d.apply(&ProgressiveEvent::Prepare(request()), NOW).unwrap();
            if commit {
                d.apply(
                    &ProgressiveEvent::Commit {
                        id: 1,
                        readiness: ready(2, NOW, 300000, 0),
                    },
                    NOW,
                )
                .unwrap();
            }
            let bytes = serde_json::to_vec(&d).unwrap();
            let mut restored: ProgressiveDomain = serde_json::from_slice(&bytes).unwrap();
            assert_eq!(serde_json::to_vec(&restored).unwrap(), bytes);
            assert!(restored.restore_fenced());
            assert!(!restored.may_move(1, NOW));
            assert!(restored
                .apply(
                    &ProgressiveEvent::Commit {
                        id: 1,
                        readiness: ready(2, NOW, 300000, 0)
                    },
                    NOW
                )
                .is_err());
            let owners = restored
                .ledger
                .controller
                .records()
                .iter()
                .map(|r| r.grant)
                .collect::<Vec<_>>();
            restored
                .apply(&ProgressiveEvent::Restart { new_epoch: 2 }, NOW + 1)
                .unwrap();
            assert_eq!(
                owners,
                restored
                    .ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect::<Vec<_>>()
            );
            assert!(!restored.may_move(1, NOW + 1));
            assert!(restored
                .apply(
                    &ProgressiveEvent::Commit {
                        id: 1,
                        readiness: ready(2, NOW, 300000, 0)
                    },
                    NOW + 1
                )
                .is_err());
        }
    }
    #[test]
    fn denied_extension_brakes_inside_previous_owned_authority_without_next_sample_credit() {
        let mut d = fixture();
        launch(&mut d);
        d.apply(
            &ProgressiveEvent::Evidence(ResourceEvent::Block(ResourceId(2))),
            NOW,
        )
        .unwrap();
        let mut denied = None;
        for tick in 1..300 {
            let now = NOW + tick * 100_000_000;
            let t = tick as f64 * 0.1;
            let front = (300000. + 500. * t * t).round() as u64;
            let v = (1000. * t).round() as u32;
            refresh(&mut d, now, front);
            let r = ready(2 + tick, now, front, v);
            if d.apply(
                &ProgressiveEvent::Extend {
                    id: 1,
                    readiness: r,
                },
                now,
            )
            .is_err()
            {
                denied = Some((now, r));
                break;
            }
        }
        let (now, r) = denied.expect("the held downstream block must refuse extension");
        let held = d.departure(1).unwrap();
        assert_eq!(held.phase, ProgressivePhase::Held);
        assert!(held.stop_required);
        assert!(held.hold_stopping_margin_mm.unwrap() >= 0);
        let end = held.protected_end_mm;
        assert!(!d.may_move(1, now));
        let mut x = r.front_mm as f64 / 1000.;
        let mut v = f64::from(r.velocity_mmps) / 1000.;
        let mut elapsed = 0.;
        let mut seq = r.sequence;
        let mut observations = 0;
        // Explicit independent plant: full assumed acceleration over reaction,
        // then the declared minimum brake, with a partial final time step.
        while v > 1e-9 {
            let dt = if elapsed < 0.2 {
                0.1_f64.min(0.2 - elapsed)
            } else {
                0.1_f64.min(v / 0.6)
            };
            let a = if elapsed < 0.2 { 1. } else { -0.6 };
            x += v * dt + 0.5 * a * dt * dt;
            v = (v + a * dt).max(0.);
            elapsed += dt;
            seq += 1;
            assert!(
                x * 1000. + 500. <= end as f64,
                "the braking plant must remain inside retained authority"
            );
            // Observations at the declared sample cadence; final numerical
            // stopping fraction is rounded up to the next observation instant.
            observations += 1;
            let observed = now + observations * 100_000_000;
            let r = ready(
                seq,
                observed,
                (x * 1000.).round() as u64,
                (v * 1000.).round() as u32,
            );
            if observed > d.last_now_ns {
                d.apply(
                    &ProgressiveEvent::ObserveHeld {
                        id: 1,
                        readiness: r,
                    },
                    observed,
                )
                .unwrap();
            }
        }
        assert_eq!(d.departure(1).unwrap().phase, ProgressivePhase::HeldStopped);
        assert!(!d.may_move(1, d.last_now_ns));
        assert!(d.ledger.controller.records()[1].grant.is_some());
    }
    #[test]
    fn release_needs_geometry_identity_and_no_generic_clear_bypass() {
        let mut d = fixture();
        launch(&mut d);
        let before = d.ledger.controller.records().to_vec();
        assert!(d
            .apply(
                &ProgressiveEvent::Evidence(ResourceEvent::Clear(ResourceId(0))),
                NOW
            )
            .is_err());
        assert_eq!(before, d.ledger.controller.records());
        let mut p = clearproof(0, 100, NOW);
        p.cleared_owner = Some(OWNER);
        let r = ready(3, NOW, 300000, 0);
        assert!(d
            .apply(
                &ProgressiveEvent::Release {
                    id: 1,
                    readiness: r,
                    resource: ResourceId(0),
                    proof: p
                },
                NOW
            )
            .is_err());
        assert_eq!(before, d.ledger.controller.records());
    }
    #[test]
    fn raw_proof_and_integrity_faults_hold_without_transfer() {
        for integrity in [false, true] {
            let mut d = fixture();
            launch(&mut d);
            let before = d
                .ledger
                .controller
                .records()
                .iter()
                .map(|r| r.grant)
                .collect::<Vec<_>>();
            if integrity {
                d.apply(
                    &ProgressiveEvent::Evidence(ResourceEvent::Integrity {
                        owner: OWNER,
                        proved: false,
                    }),
                    NOW + 1,
                )
                .unwrap();
            } else {
                let mut p = clearproof(0, 99, NOW + 1);
                p.clear = false;
                p.occupant = Some(Owner {
                    train: TrainId(102),
                    session: 1,
                });
                d.apply(
                    &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
                    NOW + 1,
                )
                .unwrap();
            }
            assert_eq!(d.departure(1).unwrap().phase, ProgressivePhase::Held);
            assert!(!d.may_move(1, NOW + 1));
            assert_eq!(
                before,
                d.ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect::<Vec<_>>()
            );
        }
    }
    #[test]
    fn duplicate_commit_is_idempotent_but_cannot_extend_a_permission() {
        let mut d = fixture();
        launch(&mut d);
        let original = d.departure(1).unwrap().committed_readiness.unwrap();
        let old = d.ledger.clone();
        d.apply(
            &ProgressiveEvent::Commit {
                id: 1,
                readiness: original,
            },
            NOW + 1,
        )
        .unwrap();
        assert_eq!(d.ledger, old);
        assert!(!d.may_move(1, NOW + 100_000_001));
        assert!(!d.ledger.permits(SectionId(103), OWNER.train, NOW));
    }
    #[test]
    fn fabricated_release_pose_and_old_arrived_contract_cannot_clear_current_authority() {
        let mut d = fixture();
        launch(&mut d);
        let initial = d.ledger.controller.records().to_vec();
        let mut p = clearproof(0, 100, NOW);
        p.cleared_owner = Some(OWNER);
        assert_eq!(
            d.apply(
                &ProgressiveEvent::Release {
                    id: 1,
                    readiness: ready(99, NOW, 2150000, 0),
                    resource: ResourceId(0),
                    proof: p
                },
                NOW
            ),
            Err(ProgressiveError::Identity)
        );
        assert_eq!(initial, d.ledger.controller.records());
        let stopped = ready(3, NOW, 300000, 0);
        d.apply(
            &ProgressiveEvent::ArriveStopped {
                id: 1,
                readiness: stopped,
            },
            NOW,
        )
        .unwrap();
        let mut next = request();
        next.id = 2;
        next.readiness = ready(4, NOW, 300000, 0);
        d.apply(&ProgressiveEvent::Prepare(next), NOW).unwrap();
        let current = ready(5, NOW, 300000, 0);
        d.apply(
            &ProgressiveEvent::Commit {
                id: 2,
                readiness: current,
            },
            NOW,
        )
        .unwrap();
        let old = d.ledger.controller.records().to_vec();
        let mut p = clearproof(1, 101, NOW);
        p.cleared_owner = Some(OWNER);
        assert_eq!(
            d.apply(
                &ProgressiveEvent::Release {
                    id: 1,
                    readiness: stopped,
                    resource: ResourceId(1),
                    proof: p
                },
                NOW
            ),
            Err(ProgressiveError::Identity)
        );
        assert!(
            d.apply(
                &ProgressiveEvent::Release {
                    id: 2,
                    readiness: current,
                    resource: ResourceId(1),
                    proof: p
                },
                NOW
            )
            .is_err(),
            "a committed contract must first prove a stopped arrival before forward withdrawal"
        );
        assert_eq!(old, d.ledger.controller.records());
        let stopped = ready(6, NOW, 300000, 0);
        d.apply(
            &ProgressiveEvent::ArriveStopped {
                id: 2,
                readiness: stopped,
            },
            NOW,
        )
        .unwrap();
        d.apply(
            &ProgressiveEvent::Release {
                id: 2,
                readiness: stopped,
                resource: ResourceId(1),
                proof: p,
            },
            NOW,
        )
        .unwrap();
        assert!(d.ledger.controller.records()[1].grant.is_none());
        assert!(!d.may_move(2, NOW));
    }
    #[test]
    fn local_speed_limit_is_enforced_before_general_motion_bounds() {
        let mut d = fixture();
        launch(&mut d);
        let owners = d
            .ledger
            .controller
            .records()
            .iter()
            .map(|r| r.grant)
            .collect::<Vec<_>>();
        assert_eq!(
            d.apply(
                &ProgressiveEvent::Extend {
                    id: 1,
                    readiness: ready(3, NOW + 100000000, 300001, 22224)
                },
                NOW + 100000000
            ),
            Err(ProgressiveError::Readiness)
        );
        assert_eq!(d.departure(1).unwrap().phase, ProgressivePhase::Held);
        assert!(!d.may_move(1, NOW + 100000000));
        assert_eq!(
            owners,
            d.ledger
                .controller
                .records()
                .iter()
                .map(|r| r.grant)
                .collect::<Vec<_>>()
        );
    }
    #[test]
    fn invalid_arrival_evidence_holds_and_retains_the_prior_authority() {
        for fault in 0..3 {
            let mut d = fixture();
            launch(&mut d);
            let owners = d
                .ledger
                .controller
                .records()
                .iter()
                .map(|r| r.grant)
                .collect::<Vec<_>>();
            let mut r = ready(3, NOW, 300000, 0);
            match fault {
                0 => r.independent_brake_ready = false,
                1 => r.integrity_proved = false,
                _ => r.support_healthy = false,
            };
            assert!(d
                .apply(
                    &ProgressiveEvent::ArriveStopped {
                        id: 1,
                        readiness: r
                    },
                    NOW
                )
                .is_err());
            assert_eq!(d.departure(1).unwrap().phase, ProgressivePhase::Held);
            assert!(!d.may_move(1, NOW));
            assert_eq!(
                owners,
                d.ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect::<Vec<_>>()
            );
        }
    }
    #[test]
    fn nonuniform_route_speed_limits_are_outside_this_candidate_contract() {
        let mut m = model();
        m.routes[0].segments[1].speed_limit_mmps = 5000;
        assert_eq!(
            ProgressiveDomain::new(m, CFG, policy(), NOW),
            Err(ProgressiveError::Model)
        );
    }
    #[test]
    fn live_speed_or_missing_body_proof_cannot_authorise_motion() {
        for speed in [false, true] {
            let mut d = fixture();
            launch(&mut d);
            let owners = d
                .ledger
                .controller
                .records()
                .iter()
                .map(|r| r.grant)
                .collect::<Vec<_>>();
            let mut p = clearproof(if speed { 1 } else { 0 }, 99, NOW);
            if speed {
                p.restriction = Restriction::Speed(5000);
            }
            d.apply(
                &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
                NOW,
            )
            .unwrap();
            assert!(!d.may_move(1, NOW));
            if speed {
                assert_eq!(d.departure(1).unwrap().phase, ProgressivePhase::Held);
            }
            assert_eq!(
                owners,
                d.ledger
                    .controller
                    .records()
                    .iter()
                    .map(|r| r.grant)
                    .collect::<Vec<_>>()
            );
        }
        let mut d = fixture();
        let mut p = clearproof(1, 99, NOW);
        p.occupancy_integrity_proved = false;
        d.apply(
            &ProgressiveEvent::Evidence(ResourceEvent::LocalProof(p)),
            NOW,
        )
        .unwrap();
        let old = d.ledger.controller.records().to_vec();
        assert!(d.apply(&ProgressiveEvent::Prepare(request()), NOW).is_err());
        assert_eq!(old, d.ledger.controller.records());
    }
}
