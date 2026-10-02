//! Frozen operational inputs. The simulator/engineering adapter validates and
//! hashes the complete railway description before building these bounded views.
use crate::{Direction, RouteId, TrainId};
pub type ConfigurationId = [u8; 32];
pub const MAX_RESOURCES: usize = 32;
pub const MAX_ROUTE_MM: u64 = 100_000_000;
pub const MAX_SPEED_MMPS: u32 = 100_000;
pub const INPUT_MAX_AGE_NS: u64 = 1_000_000_000;
pub const LEASE_NS: u64 = 3_000_000_000;
/// Prototype clock-skew budget; physical synchronisation evidence is pending.
pub const CLOCK_SKEW_NS: u64 = 100_000_000;

macro_rules! id {
    ($name:ident, $t:ty) => {
        #[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
        #[derive(serde::Serialize, serde::Deserialize)]
        #[serde(transparent)]
        pub struct $name(pub $t);
    };
}
id!(ControllerId, u64);
id!(ResourceId, u8);

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Owner {
    pub train: TrainId,
    /// Persistently fenced train boot session. Division/rescue needs a new
    /// controlled consist/configuration and clearance, never a lease transfer.
    pub session: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ResourceSpec {
    pub id: ResourceId,
    pub controller: ControllerId,
    pub conflicts: u32,
    pub points_required: bool,
}

pub fn valid_resources(resources: &[ResourceSpec]) -> bool {
    !resources.is_empty()
        && resources.len() <= MAX_RESOURCES
        && resources.iter().enumerate().all(|(i, r)| {
            usize::from(r.id.0) == i
                && r.controller.0 != 0
                && r.conflicts & (1_u32 << i) != 0
                && (resources.len() == 32 || r.conflicts >> resources.len() == 0)
                && resources.iter().enumerate().all(|(j, other)| {
                    (r.conflicts & (1_u32 << j) != 0) == (other.conflicts & (1_u32 << i) != 0)
                        && (r.conflicts & (1_u32 << j) == 0 || r.controller == other.controller)
                })
        })
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Segment {
    pub resource: ResourceId,
    /// Coordinates increase in the approved direction of this route. Reverse
    /// working uses a separate approved route, not negated live sensor values.
    pub start_mm: u64,
    pub end_mm: u64,
    pub speed_limit_mmps: u32,
    pub downhill_permille: u16,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Route<'a> {
    pub id: RouteId,
    pub direction: Direction,
    pub segments: &'a [Segment],
    /// When required, loss of peer information stops movement. Optional peer
    /// information cannot extend or replace exclusive resource ownership.
    pub leader_required: bool,
}

impl Route<'_> {
    pub fn valid(&self, resources: &[ResourceSpec]) -> bool {
        self.id.0 != 0
            && !self.segments.is_empty()
            && self.segments.len() <= MAX_RESOURCES
            && self.segments[0].start_mm == 0
            && self.segments.iter().enumerate().all(|(i, s)| {
                usize::from(s.resource.0) < resources.len()
                    && s.end_mm > s.start_mm
                    && s.end_mm <= MAX_ROUTE_MM
                    && (1..=MAX_SPEED_MMPS).contains(&s.speed_limit_mmps)
                    && s.downhill_permille <= 100
                    && (i == 0 || self.segments[i - 1].end_mm == s.start_mm)
                    && !self.segments[..i].iter().any(|p| p.resource == s.resource)
            })
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TrainConfig {
    pub owner: Owner,
    pub configuration: ConfigurationId,
    pub length_mm: u32,
    pub minimum_deceleration_mmps2: u32,
    pub reaction_time_ms: u32,
    pub stop_margin_mm: u32,
    pub maximum_position_uncertainty_mm: u32,
}

impl TrainConfig {
    pub fn valid(self) -> bool {
        self.owner.train.0 != 0
            && self.owner.session != 0
            && self.configuration != [0; 32]
            && (1..=1_000_000).contains(&self.length_mm)
            && (1..=10_000).contains(&self.minimum_deceleration_mmps2)
            && self.reaction_time_ms <= 10_000
            && (1..=1_000_000).contains(&self.stop_margin_mm)
            && self.maximum_position_uncertainty_mm <= 1_000_000
    }
}

pub const fn fresh(observed_ns: u64, now_ns: u64) -> bool {
    observed_ns > 0 && observed_ns <= now_ns && now_ns - observed_ns <= INPUT_MAX_AGE_NS
}
