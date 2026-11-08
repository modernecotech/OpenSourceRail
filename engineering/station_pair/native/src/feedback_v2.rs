//! Explicit research strategy. No authenticated brake/torque/zero-speed signal.
use super::*;

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ResearchFeedbackV2 {
    pub strategy: String,
    /// Nominal berth centre, distinct from the physically declared track domain.
    pub berth_target_m: f64,
    /// Retained service-brake command during powered creeping, not free holding.
    pub brake_floor_n: f64,
    pub creep_speed_m_s: f64,
}

#[derive(Debug, Clone, Serialize)]
pub struct ResearchFeedbackV2Diagnostics {
    pub berth_target_m: f64,
    pub modeled_track_end_m: f64,
    pub declared_end_of_authority_m: f64,
    pub brake_floor_n: f64,
    pub command_history_guaranteed_brake_n: f64,
    pub brake_force_observed: bool,
    pub static_domain_supported: bool,
    pub domain_holds: Vec<String>,
    pub zero_speed_brake_free_bound_m: f64,
    pub available_docking_clearance_m: f64,
    pub traction_preload_target_n: f64,
    pub full_brake_required_for_preload_n: f64,
    pub final_state: String,
    pub speed_governor_steps: u64,
    pub conditional_only: bool,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub(super) enum State {
    BrakeHold,
    TractionPreload,
    ReleasePending,
    Cruise,
    BrakeApproach,
    Creep,
    FinalHold,
}
impl State {
    pub(super) fn name(self) -> &'static str {
        match self {
            Self::BrakeHold => "BrakeHold",
            Self::TractionPreload => "TractionPreload",
            Self::ReleasePending => "ReleasePending",
            Self::Cruise => "Cruise",
            Self::BrakeApproach => "BrakeApproach",
            Self::Creep => "Creep",
            Self::FinalHold => "FinalHold",
        }
    }
}

pub(super) struct Runtime {
    pub spec: ResearchFeedbackV2,
    pub state: State,
    pub guaranteed_brake_n: f64,
    pub preload_target_n: f64,
    pub governor_steps: u64,
    pub governor_active: bool,
    zero_bound: f64,
    available_clearance: f64,
    preload_hold: f64,
    pub holds: Vec<String>,
}

impl Runtime {
    pub fn new(c: &Case, p: &FeedbackControl, spec: &ResearchFeedbackV2) -> Result<Self, String> {
        if spec.strategy != "held-docking-speed-governor/2"
            || !pos(spec.berth_target_m)
            || !nonneg(spec.brake_floor_n)
            || !pos(spec.creep_speed_m_s)
            || spec.creep_speed_m_s > 0.25
            || spec.berth_target_m > p.end_of_authority_m
            || p.end_of_authority_m > c.distance_m
            || spec.berth_target_m < c.berth_tolerance_m
            || spec.brake_floor_n > p.brake_force_lower_bound_n
        {
            return Err("Explicit v2 strategy, bounded berth/authority/track, brake floor and <=0.25m/s creep required".into());
        }
        let grade_abs = (p.grade_estimate_fraction.abs() + p.grade_error_bound).min(0.1);
        let hold = p.mass_upper_kg * G * grade_abs / (1. + grade_abs * grade_abs).sqrt();
        let uphill = (p.grade_estimate_fraction + p.grade_error_bound).max(0.);
        let launch = p.mass_upper_kg * G * uphill / (1. + uphill * uphill).sqrt()
            + p.rolling_resistance_upper_n
            + p.external_resistance_upper_n;
        // A small explicit creep acceleration budget is part of the strategy,
        // not an increased hardware guarantee. The caller's bound is unchanged.
        let preload = spec.brake_floor_n + launch + 0.02 * p.mass_lower_kg;
        let preload_hold = preload + gravity_upper(p);
        let zero = stopping_distance_bound(
            p,
            p.speed_error_bound_m_s,
            f64::INFINITY,
            c.dt_s,
            gravity_upper(p) / p.mass_lower_kg,
        )
        .unwrap_or(f64::MAX)
            + p.position_error_bound_m;
        let available = p.end_of_authority_m - spec.berth_target_m + c.berth_tolerance_m
            - p.position_error_bound_m;
        let mut holds = vec![];
        if spec.brake_floor_n + 1e-8 < hold {
            holds.push("retained brake floor cannot hold the declared grade/mass interval".into());
        }
        if preload > p.start_traction_lower_bound_n + 1e-8 {
            holds.push("declared traction lower bound cannot overcome retained brake floor, grade, rolling and creep budget".into());
        }
        if preload_hold > p.brake_force_lower_bound_n + 1e-8 {
            holds.push("guaranteed full braking cannot retain the planned traction preload against downhill grade".into());
        }
        if zero >= available {
            holds.push("unchanged brake-free zero-speed bound does not fit the explicit berth/authority clearance".into());
        }
        if spec.creep_speed_m_s + p.speed_error_bound_m_s >= 0.5 {
            holds.push(
                "creep request and observation error exceed retained0.5m/s model guard".into(),
            );
        }
        if c.headwind_m_s != 0. {
            holds.push("v2 standstill wind force lacks a controller upper-bound interface; positive headwind remains unsupported".into());
        }
        Ok(Self {
            spec: spec.clone(),
            state: State::BrakeHold,
            guaranteed_brake_n: 0.,
            preload_target_n: preload,
            governor_steps: 0,
            governor_active: false,
            zero_bound: zero,
            available_clearance: available,
            preload_hold,
            holds,
        })
    }
    pub fn report(&self, c: &Case, p: &FeedbackControl) -> ResearchFeedbackV2Diagnostics {
        ResearchFeedbackV2Diagnostics {
            berth_target_m: self.spec.berth_target_m,
            modeled_track_end_m: c.distance_m,
            declared_end_of_authority_m: p.end_of_authority_m,
            brake_floor_n: self.spec.brake_floor_n,
            command_history_guaranteed_brake_n: self.guaranteed_brake_n,
            brake_force_observed: false,
            static_domain_supported: self.holds.is_empty(),
            domain_holds: self.holds.clone(),
            zero_speed_brake_free_bound_m: self.zero_bound,
            available_docking_clearance_m: self.available_clearance,
            traction_preload_target_n: self.preload_target_n,
            full_brake_required_for_preload_n: self.preload_hold,
            final_state: self.state.name().into(),
            speed_governor_steps: self.governor_steps,
            conditional_only: true,
        }
    }
}

/// Under the already-declared force/rise/delay hypotheses, commands continuously
/// above F for reaction+full-rise imply applied braking >=F. No plant value is
/// passed to this controller calculation. A release command invalidates credit.
pub(super) fn history_brake_lower(
    history: &VecDeque<(f64, f64)>,
    t: f64,
    p: &FeedbackControl,
) -> f64 {
    let cutoff = t - p.reaction_time_bound_s - p.brake_rise_time_bound_s;
    let Some(index) = history.iter().rposition(|(at, _)| *at <= cutoff + 1e-12) else {
        return 0.;
    };
    history
        .iter()
        .skip(index)
        .map(|(_, force)| *force)
        .fold(p.brake_force_lower_bound_n, f64::min)
        .min(p.brake_force_lower_bound_n)
        .max(0.)
}

/// Conservative speed-headroom requirement for zero-to-full normal brake ramp
/// plus bounded response. Motor-command rundown contributes its triangular
/// impulse; gravity continues through the entire brake response interval.
pub(super) fn governor_headroom(
    p: &FeedbackControl,
    traction_command: f64,
    jerk: f64,
    dt: f64,
) -> f64 {
    let rate = 0.5 * p.mass_lower_kg * jerk;
    let delay =
        p.reaction_time_bound_s + p.brake_rise_time_bound_s + p.brake_force_lower_bound_n / rate;
    p.speed_error_bound_m_s
        + p.positive_acceleration_bound_m_s2 * dt
        + gravity_upper(p) / p.mass_lower_kg * delay
        + traction_command * traction_command / (2. * rate * p.mass_lower_kg)
}
