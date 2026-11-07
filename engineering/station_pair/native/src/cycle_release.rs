//! Opt-in finite-slew substitution of station-store energy for grid traction.
//! This is an assumed controlled transmission, not a measured flow/current law.
use super::*;
use crate::cycle::{Leg, Station};

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ReleaseControl {
    pub mode: String,
    pub force_slew_n_s: f64,
    pub maximum_traction_share: f64,
    pub reserve_factor: f64,
    #[serde(default, skip_serializing_if = "audit_disabled")]
    pub cutoff_audit: bool,
}
fn audit_disabled(v: &bool) -> bool {
    !*v
}
impl ReleaseControl {
    pub(crate) fn validate(&self) -> Result<(), String> {
        if !matches!(
            self.mode.as_str(),
            "grid-substitution-slew/1" | "grid-substitution-slew/2"
        ) || !pos(self.force_slew_n_s)
            || !pos(self.maximum_traction_share)
            || self.maximum_traction_share > 1.
            || !self.reserve_factor.is_finite()
            || self.reserve_factor < 1.
            || self.reserve_factor > 100.
        {
            return Err("Explicit finite-slew grid-substitution policy with positive rate, share<=1 and reserve factor1..100 required".into());
        }
        Ok(())
    }
}
#[derive(Debug, Clone, Serialize)]
pub struct ForceTransition {
    pub time_s: f64,
    pub position_m: f64,
    pub entry_speed_m_s: f64,
    pub exit_speed_m_s: f64,
    pub previous_acceleration_m_s2: f64,
    pub acceleration_m_s2: f64,
    pub previous_step_s: f64,
    pub step_s: f64,
    pub previous_traction_n: f64,
    pub traction_n: f64,
    pub previous_brake_n: f64,
    pub brake_n: f64,
    pub point_step_jerk_m_s3: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct CutoffAudit {
    pub time_s: f64,
    pub position_m: f64,
    pub entry_speed_m_s: f64,
    pub exit_speed_m_s: f64,
    pub previous_force_n: f64,
    pub start_force_n: f64,
    pub end_force_n: f64,
    pub active_duration_s: f64,
    pub step_s: f64,
    pub energy_at_start_j: f64,
    pub usable_j: f64,
    pub unclipped_work_j: f64,
    pub delivered_work_j: f64,
    pub commanded_target_n: f64,
    pub traction_demand_n: f64,
    pub physical_force_cap_n: f64,
    pub store_force_rate_n_s: f64,
    pub forced_cutoff: bool,
    pub reasons: Vec<String>,
}
#[derive(Debug, Clone, Default, Serialize)]
pub struct ContinuousReserveDiagnostics {
    pub maximum_store_boundary_jump_n: f64,
    pub force_boundary_discontinuities: u64,
    pub current_and_future_reserve_interventions: u64,
    pub early_zero_segments: u64,
    pub minimum_current_and_future_energy_margin_j: f64,
}
#[derive(Debug, Clone, Default, Serialize)]
pub struct ReleaseDiagnostics {
    pub mode: String,
    pub force_slew_limit_n_s: f64,
    pub maximum_store_force_rate_n_s: f64,
    pub maximum_grid_force_rate_n_s: f64,
    pub maximum_store_peak_power_w: f64,
    pub maximum_grid_peak_power_w: f64,
    pub forced_cutoffs: u64,
    pub slew_limit_exceeded: bool,
    pub energy_reserve_interventions: u64,
    pub spatial_reserve_interventions: u64,
    pub controller_state_observations_assumed: bool,
    pub current_and_flow_dynamics_validated: bool,
    pub maximum_point_step_jerk_transition: Option<ForceTransition>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cutoff_details: Option<Vec<CutoffAudit>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cutoff_details_truncated: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub continuous_reserve: Option<ContinuousReserveDiagnostics>,
}
#[derive(Debug, Clone, Serialize)]
pub struct ReleaseSample {
    pub store_start_force_n: f64,
    pub store_end_force_n: f64,
    pub grid_start_force_n: f64,
    pub grid_end_force_n: f64,
    pub store_force_rate_n_s: f64,
    pub grid_force_rate_n_s: f64,
    pub forced_cutoff: bool,
    pub active_duration_s: f64,
}
#[derive(Debug, Clone)]
pub(crate) struct ReleaseRuntime {
    pub policy: ReleaseControl,
    pub diagnostics: ReleaseDiagnostics,
    force_n: f64,
    previous_grid_n: f64,
    previous_h: f64,
    pub last_sample: Option<ReleaseSample>,
    pub last_grid_peak_power_w: f64,
    previous_total_force_n: f64,
    previous_brake_n: f64,
    release_complete: bool,
}
#[derive(Debug, Clone)]
pub(crate) struct Allocation {
    pub work_j: f64,
    pub peak_force_n: f64,
    pub peak_power_w: f64,
    pub equivalent_force_n: f64,
}
fn product_peak(f0: f64, f1: f64, v0: f64, v1: f64) -> f64 {
    let df = f1 - f0;
    let dv = v1 - v0;
    let mut peak = (f0 * v0).max(f1 * v1);
    let q = df * dv;
    if q < 0. {
        let u = -(f0 * dv + v0 * df) / (2. * q);
        if u > 0. && u < 1. {
            peak = peak.max((f0 + df * u) * (v0 + dv * u));
        }
    }
    peak
}
fn work(f0: f64, f1: f64, v0: f64, v1: f64, h: f64) -> f64 {
    h * (f0 * v0 + (f0 * (v1 - v0) + (f1 - f0) * v0) / 2. + (f1 - f0) * (v1 - v0) / 3.)
}
// Solve alpha + beta*F1 + gamma*F1² <= actual usable energy.
// alpha+beta*F1 is the exact current linear-force/linear-velocity
// integral. gamma*F1² funds the entire later finite ramp. The stable
// positive root avoids cancellation for nearly exhausted stores.
fn endpoint_force_budget(f0: f64, v0: f64, v1: f64, h: f64, energy: f64, gamma: f64) -> f64 {
    let alpha = work(f0, 0., v0, v1, h).max(0.);
    let beta = (h * (v0 + 2. * v1) / 6.).max(0.);
    let c = energy - alpha;
    if c <= 0. {
        return 0.;
    }
    let denominator = beta + (beta * beta + 4. * gamma * c).sqrt();
    if denominator == 0. {
        return 0.;
    }
    let mut result = (2. * c / denominator).max(0.).next_down().max(0.);
    // Literal floating-point ledger inequality, not a relaxed acceptance limit.
    while result > 0. && work(f0, result, v0, v1, h) + gamma * result * result > energy {
        result = result.next_down();
    }
    result
}
impl ReleaseRuntime {
    pub(crate) fn new(policy: ReleaseControl) -> Self {
        Self {
            diagnostics: ReleaseDiagnostics {
                mode: policy.mode.clone(),
                continuous_reserve: if policy.mode == "grid-substitution-slew/2" {
                    Some(ContinuousReserveDiagnostics::default())
                } else {
                    None
                },
                force_slew_limit_n_s: policy.force_slew_n_s,
                controller_state_observations_assumed: true,
                cutoff_details_truncated: if policy.cutoff_audit { Some(0) } else { None },
                cutoff_details: if policy.cutoff_audit {
                    Some(vec![])
                } else {
                    None
                },
                ..Default::default()
            },
            policy,
            force_n: 0.,
            previous_grid_n: 0.,
            previous_h: 0.,
            last_sample: None,
            last_grid_peak_power_w: 0.,
            previous_total_force_n: 0.,
            previous_brake_n: 0.,
            release_complete: false,
        }
    }
    #[allow(clippy::too_many_arguments)]
    pub fn observe_motion(
        &mut self,
        t: f64,
        x: f64,
        v0: f64,
        v1: f64,
        h: f64,
        ph: f64,
        pa: f64,
        a: f64,
        force: f64,
        brake: f64,
    ) {
        let jerk = (a - pa).abs() / if ph > 0. { (ph + h) / 2. } else { h };
        if self
            .diagnostics
            .maximum_point_step_jerk_transition
            .as_ref()
            .is_none_or(|q| jerk > q.point_step_jerk_m_s3)
        {
            self.diagnostics.maximum_point_step_jerk_transition = Some(ForceTransition {
                time_s: t,
                position_m: x,
                entry_speed_m_s: v0,
                exit_speed_m_s: v1,
                previous_acceleration_m_s2: pa,
                acceleration_m_s2: a,
                previous_step_s: ph,
                step_s: h,
                previous_traction_n: self.previous_total_force_n,
                traction_n: force,
                previous_brake_n: self.previous_brake_n,
                brake_n: brake,
                point_step_jerk_m_s3: jerk,
            });
        }
        self.previous_total_force_n = force;
        self.previous_brake_n = brake;
    }
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn allocate(
        &mut self,
        s: &Station,
        l: &Leg,
        energy_j: f64,
        time_s: f64,
        x: f64,
        v0: f64,
        v1: f64,
        dx: f64,
        h: f64,
        traction: f64,
        fault: bool,
    ) -> Allocation {
        let p = &self.policy;
        let q = &s.release;
        let control = l.journey.control.as_ref().unwrap();
        let acceleration_upper = control.positive_acceleration_bound_m_s2;
        let speed_upper = l.journey.speed_cap_m_s.max(v0).max(v1)
            + acceleration_upper * q.max_force_n / p.force_slew_n_s;
        let physical = q.max_force_n.min(q.max_power_w / speed_upper.max(1e-12));
        let usable_j = energy_j * (-s.store.leakage_per_s * h).exp() * s.store.release_efficiency;
        // Reserve enough usable energy to ramp the command to zero at the
        // declared slew, assuming the conservative upper velocity throughout.
        let energy_cap =
            (2. * p.force_slew_n_s * usable_j / (p.reserve_factor * speed_upper.max(1e-12))).sqrt();
        let observed_x = x + control.position_bias_m + control.position_error_bound_m;
        let observed_v = (v0 + control.speed_bias_m_s + control.speed_error_bound_m_s).max(0.);
        // The next endpoint command reserves its entire following ramp, using
        // observed position/speed plus declared uncertainty and acceleration.
        let predicted_end_x = observed_x + observed_v * h + 0.5 * acceleration_upper * h * h;
        let predicted_end_v = observed_v + acceleration_upper * h;
        let remaining = (q.end_m - predicted_end_x).max(0.);
        let exit_time = if acceleration_upper > 0. {
            2. * remaining
                / (predicted_end_v
                    + (predicted_end_v * predicted_end_v + 2. * acceleration_upper * remaining)
                        .sqrt())
                .max(1e-12)
        } else {
            remaining / predicted_end_v.max(1e-12)
        };
        let spatial_cap = p.force_slew_n_s * exit_time / p.reserve_factor;
        // Tie sharing to a bound on the existing normal total-command taper.
        // V2 also leaves one accepted-step control interval of headroom, so
        // its endpoint force can remain literal when total traction decreases.
        // Only declared controller and source-envelope bounds are used here.
        let continuous = p.mode == "grid-substitution-slew/2";
        let normal_total_slew = 0.5 * control.mass_lower_kg * l.journey.comfort_jerk_m_s3;
        let total_slew_bound = if continuous && l.journey.drive.is_some() {
            let drive = l.journey.drive.as_ref().unwrap();
            let source_slope = drive
                .points
                .windows(2)
                .map(|q| (q[1].force_n - q[0].force_n).abs() / (q[1].speed_m_s - q[0].speed_m_s))
                .fold(0., f64::max);
            let max_force = drive
                .points
                .iter()
                .map(|q| q.force_n)
                .fold(0., f64::max)
                .min(drive.contact_force_cap_n);
            let power = drive
                .mechanical_power_w
                .min(drive.grid_power_w * drive.electrical_efficiency);
            normal_total_slew
                .max(source_slope * acceleration_upper)
                .max(acceleration_upper * max_force * max_force / power.max(1e-12))
        } else {
            normal_total_slew
        };
        let share = p
            .maximum_traction_share
            .min(p.force_slew_n_s / (p.reserve_factor * total_slew_bound.max(1e-12)));
        let transferable_traction = if continuous {
            (traction - total_slew_bound * h).max(0.)
        } else {
            traction
        };
        let enabled = !(continuous && self.release_complete)
            && !fault
            && !l.release_failed
            && l.departure_authorized
            && x >= q.start_m
            && x < q.end_m
            && usable_j > 0.;
        let target = if enabled {
            physical
                .min(energy_cap)
                .min(spatial_cap)
                .min(share * transferable_traction)
        } else {
            0.
        };
        if enabled && energy_cap < physical.min(share * transferable_traction) {
            self.diagnostics.energy_reserve_interventions += 1;
        }
        if enabled && spatial_cap < physical.min(share * transferable_traction) {
            self.diagnostics.spatial_reserve_interventions += 1;
        }
        let previous = self.force_n;
        let mut cutoff_reasons = vec![];
        let mut f0 = previous.min(traction);
        let mut f1 = (previous
            + (target - previous).clamp(-p.force_slew_n_s * h, p.force_slew_n_s * h))
        .min(traction);
        let mut forced = previous - f0 > p.force_slew_n_s * h * (1. + 1e-8);
        if forced {
            cutoff_reasons.push(
                "Total traction demand cannot retain previous store force within declared slew"
                    .into(),
            );
        }
        if !enabled {
            if previous > 0. {
                cutoff_reasons.push(
                    if fault {
                        "Traction power/emergency/thermal fault"
                    } else if l.release_failed {
                        "Release unavailable or shared resource not owned"
                    } else if !l.departure_authorized {
                        "Departure not authorized"
                    } else if x < q.start_m || x >= q.end_m {
                        "Outside mechanical engagement window"
                    } else {
                        "Usable stored energy exhausted"
                    }
                    .into(),
                );
            }
            forced |= previous > 0.;
            f0 = 0.;
            f1 = 0.;
        }
        // Integrate a literal finite ramp on the part of this accepted step
        // inside the mechanical window; no whole-step cutoff or post-window work.
        let mut active_h = h;
        if enabled && x + dx > q.end_m {
            let distance = (q.end_m - x).max(0.);
            let a = (v1 - v0) / h;
            active_h = (2. * distance
                / (v0 + (v0 * v0 + 2. * a * distance).max(0.).sqrt()).max(1e-12))
            .min(h);
            f1 = 0.;
            if f0 / active_h.max(1e-12) > p.force_slew_n_s * (1. + 1e-8) {
                forced = true;
                cutoff_reasons
                    .push("Engagement exit reached before finite slew can complete".into());
            }
        }
        // Version 1 is a retained evaluation. Version 2 additionally funds this
        // literal accepted-step ramp before reserving its following ramp to zero.
        // The reserve uses declared velocity/acceleration and leakage bounds;
        // it is not a forecast of future arrival energy or an actuator law.
        let mut early_zero = false;
        let future_gamma = if continuous {
            p.reserve_factor * speed_upper.max(1e-12) / (2. * p.force_slew_n_s)
                * (s.store.leakage_per_s * q.max_force_n / p.force_slew_n_s).exp()
        } else {
            0.
        };
        if continuous && enabled {
            let active_v1 = v0 + (v1 - v0) * (active_h / h);
            let safe = endpoint_force_budget(f0, v0, active_v1, active_h, usable_j, future_gamma);
            if f1 > safe || work(f0, f1, v0, active_v1, active_h) > usable_j {
                self.diagnostics
                    .continuous_reserve
                    .as_mut()
                    .unwrap()
                    .current_and_future_reserve_interventions += 1;
                let minimum_endpoint = (f0 - p.force_slew_n_s * active_h).max(0.);
                if safe >= minimum_endpoint && work(f0, 0., v0, active_v1, active_h) <= usable_j {
                    f1 = safe;
                } else if f0 / p.force_slew_n_s <= active_h {
                    // A whole-step straight ramp would overspend even with a
                    // zero endpoint. Reach zero at the finite maximum slew,
                    // then remain zero for the remainder of this step and leg.
                    // Positive unused energy stays in the station ledger.
                    active_h = f0 / p.force_slew_n_s;
                    f1 = 0.;
                    early_zero = true;
                    self.release_complete = true;
                    self.diagnostics
                        .continuous_reserve
                        .as_mut()
                        .unwrap()
                        .early_zero_segments += 1;
                    cutoff_reasons
                        .push("Energy-reserved finite ramp reaches zero before step end".into());
                } else {
                    // An inconsistent prior state or fault can make continuous
                    // delivery impossible. Keep its failure visible; the later
                    // physical/energy cap still prevents invented work.
                    f1 = minimum_endpoint;
                    forced = true;
                    cutoff_reasons.push(
                        "Actual energy cannot fund the minimum slew-limited current ramp".into(),
                    );
                }
            }
        }
        let active_v1 = v0 + (v1 - v0) * (active_h / h);
        let cap_now = q.max_force_n.min(q.max_power_w / v0.max(v1).max(1e-12));
        if f0 > cap_now || f1 > cap_now {
            forced = true;
            cutoff_reasons.push("Physical transfer force/power cap below retained command".into());
            f0 = f0.min(cap_now);
            f1 = f1.min(cap_now);
        }
        let mut delivered = work(f0, f1, v0, active_v1, active_h).max(0.);
        let unclipped_work_j = delivered;
        if delivered > usable_j {
            forced = true;
            cutoff_reasons.push("Current step ramp work exceeds actual usable store energy".into());
            let scale = if delivered > 0. {
                usable_j / delivered
            } else {
                0.
            };
            f0 *= scale;
            f1 *= scale;
            delivered = work(f0, f1, v0, active_v1, active_h).max(0.);
        }
        if continuous {
            let d = self.diagnostics.continuous_reserve.as_mut().unwrap();
            let jump = (f0 - previous).abs();
            d.maximum_store_boundary_jump_n = d.maximum_store_boundary_jump_n.max(jump);
            d.force_boundary_discontinuities += u64::from(jump > 0.);
            if jump > 0. {
                forced = true;
                cutoff_reasons
                    .push("Literal store force discontinuity at accepted-step boundary".into());
            }
            let future_reserve = if f1 == 0. { 0. } else { future_gamma * f1 * f1 };
            let margin = usable_j - delivered - future_reserve;
            d.minimum_current_and_future_energy_margin_j =
                d.minimum_current_and_future_energy_margin_j.min(margin);
        }
        let store_rate = ((f1 - previous).abs() / h)
            .max((f1 - f0).abs() / active_h.max(1e-12))
            .max((f0 - previous).abs() / h);
        let grid0 = (traction - f0).max(0.);
        let grid1 = (traction - f1).max(0.);
        let sample_dt = if self.previous_h > 0. {
            (self.previous_h + h) / 2.
        } else {
            h
        };
        let grid_rate = ((grid1 - grid0).abs() / active_h.max(1e-12))
            .max((grid0 - self.previous_grid_n).abs() / sample_dt);
        let peak_power = product_peak(f0, f1, v0, active_v1);
        self.last_grid_peak_power_w = product_peak(grid0, grid1, v0, active_v1);
        if active_h < h {
            self.last_grid_peak_power_w = self.last_grid_peak_power_w.max(traction * v1);
        }
        self.diagnostics.maximum_store_force_rate_n_s = self
            .diagnostics
            .maximum_store_force_rate_n_s
            .max(store_rate);
        self.diagnostics.maximum_grid_force_rate_n_s =
            self.diagnostics.maximum_grid_force_rate_n_s.max(grid_rate);
        self.diagnostics.maximum_store_peak_power_w =
            self.diagnostics.maximum_store_peak_power_w.max(peak_power);
        self.diagnostics.maximum_grid_peak_power_w = self
            .diagnostics
            .maximum_grid_peak_power_w
            .max(self.last_grid_peak_power_w);
        self.diagnostics.slew_limit_exceeded |= store_rate > p.force_slew_n_s * (1. + 1e-8);
        self.diagnostics.forced_cutoffs += u64::from(forced);
        if forced || f0 != previous || early_zero {
            if let Some(details) = self.diagnostics.cutoff_details.as_mut() {
                if details.len() < 256 {
                    details.push(CutoffAudit {
                        time_s,
                        position_m: x,
                        entry_speed_m_s: v0,
                        exit_speed_m_s: v1,
                        previous_force_n: previous,
                        start_force_n: f0,
                        end_force_n: f1,
                        active_duration_s: active_h,
                        step_s: h,
                        energy_at_start_j: energy_j,
                        usable_j,
                        unclipped_work_j,
                        delivered_work_j: delivered,
                        commanded_target_n: target,
                        traction_demand_n: traction,
                        physical_force_cap_n: cap_now,
                        store_force_rate_n_s: store_rate,
                        forced_cutoff: forced,
                        reasons: cutoff_reasons,
                    });
                } else {
                    *self.diagnostics.cutoff_details_truncated.as_mut().unwrap() += 1;
                }
            }
        }
        self.force_n = f1;
        self.previous_grid_n = grid1;
        self.previous_h = h;
        self.last_sample = Some(ReleaseSample {
            store_start_force_n: f0,
            store_end_force_n: f1,
            grid_start_force_n: grid0,
            grid_end_force_n: grid1,
            store_force_rate_n_s: store_rate,
            grid_force_rate_n_s: grid_rate,
            forced_cutoff: forced,
            active_duration_s: active_h,
        });
        Allocation {
            work_j: delivered,
            peak_force_n: f0.max(f1),
            peak_power_w: peak_power,
            equivalent_force_n: if dx > 0. { delivered / dx } else { 0. },
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn endpoint_budget_pays_current_work_before_reserving_later_ramp() {
        for speed in [0.01, 5., 9.8, 20.] {
            for f0 in [0., 1., 30., 198.3614250030702] {
                for h in [0.05, 0.025, 0.0125] {
                    for e in [1e-8, 25.389257261000147, 100., 1e6] {
                        let gamma = 2. * 40. / (2. * 10000.);
                        let f1 = endpoint_force_budget(f0, speed, speed + h, h, e, gamma);
                        if work(f0, 0., speed, speed + h, h) <= e {
                            assert!(work(f0, f1, speed, speed + h, h) + gamma * f1 * f1 <= e);
                        } else {
                            assert_eq!(f1, 0.);
                        }
                    }
                }
            }
        }
    }
    #[test]
    fn linear_force_velocity_work_and_peak_are_actual_integrals() {
        assert!((work(10., 0., 0., 10., 2.) - 100. / 3.).abs() < 1e-12);
        assert!((product_peak(10., 0., 0., 10.) - 25.).abs() < 1e-12);
        assert_eq!(product_peak(10., 20., 2., 4.), 80.);
    }
}
