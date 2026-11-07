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
}
impl ReleaseControl {
    pub(crate) fn validate(&self) -> Result<(), String> {
        if self.mode != "grid-substitution-slew/1"
            || !pos(self.force_slew_n_s)
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
impl ReleaseRuntime {
    pub(crate) fn new(policy: ReleaseControl) -> Self {
        Self {
            diagnostics: ReleaseDiagnostics {
                mode: policy.mode.clone(),
                force_slew_limit_n_s: policy.force_slew_n_s,
                controller_state_observations_assumed: true,
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
        let remaining = (q.end_m - observed_x).max(0.);
        let exit_time = if acceleration_upper > 0. {
            2. * remaining
                / (observed_v
                    + (observed_v * observed_v + 2. * acceleration_upper * remaining).sqrt())
                .max(1e-12)
        } else {
            remaining / observed_v.max(1e-12)
        };
        let spatial_cap = p.force_slew_n_s * exit_time / p.reserve_factor;
        // Tie the sharing fraction to the existing normal command slew so a
        // normal total-traction taper need not force a faster store cutoff.
        let normal_total_slew = 0.5 * control.mass_lower_kg * l.journey.comfort_jerk_m_s3;
        let share = p
            .maximum_traction_share
            .min(p.force_slew_n_s / (p.reserve_factor * normal_total_slew.max(1e-12)));
        let enabled = !fault
            && !l.release_failed
            && l.departure_authorized
            && x >= q.start_m
            && x < q.end_m
            && usable_j > 0.;
        let target = if enabled {
            physical
                .min(energy_cap)
                .min(spatial_cap)
                .min(share * traction)
        } else {
            0.
        };
        if enabled && energy_cap < physical.min(share * traction) {
            self.diagnostics.energy_reserve_interventions += 1;
        }
        if enabled && spatial_cap < physical.min(share * traction) {
            self.diagnostics.spatial_reserve_interventions += 1;
        }
        let previous = self.force_n;
        let mut f0 = previous.min(traction);
        let mut f1 = (previous
            + (target - previous).clamp(-p.force_slew_n_s * h, p.force_slew_n_s * h))
        .min(traction);
        let mut forced = previous - f0 > p.force_slew_n_s * h * (1. + 1e-8);
        if !enabled {
            forced |= previous > 0.;
            f0 = 0.;
            f1 = 0.;
        }
        // Spatial taper normally reaches zero in advance. If a fault or an
        // out-of-domain observation defeats the reserve, cut force physically
        // and report its discontinuity; do not supply work beyond the window.
        if x + dx > q.end_m && f1 > 0. {
            forced = true;
            f0 = 0.;
            f1 = 0.;
        }
        let cap_now = q.max_force_n.min(q.max_power_w / v0.max(v1).max(1e-12));
        if f0 > cap_now || f1 > cap_now {
            forced = true;
            f0 = f0.min(cap_now);
            f1 = f1.min(cap_now);
        }
        let mut delivered = work(f0, f1, v0, v1, h).max(0.);
        if delivered > usable_j {
            forced = true;
            let scale = if delivered > 0. {
                usable_j / delivered
            } else {
                0.
            };
            f0 *= scale;
            f1 *= scale;
            delivered = work(f0, f1, v0, v1, h).max(0.);
        }
        let store_rate = ((f1 - previous).abs() / h)
            .max((f1 - f0).abs() / h)
            .max((f0 - previous).abs() / h);
        let grid0 = (traction - f0).max(0.);
        let grid1 = (traction - f1).max(0.);
        let sample_dt = if self.previous_h > 0. {
            (self.previous_h + h) / 2.
        } else {
            h
        };
        let grid_rate =
            ((grid1 - grid0).abs() / h).max((grid0 - self.previous_grid_n).abs() / sample_dt);
        let peak_power = product_peak(f0, f1, v0, v1);
        self.last_grid_peak_power_w = product_peak(grid0, grid1, v0, v1);
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
    fn linear_force_velocity_work_and_peak_are_actual_integrals() {
        assert!((work(10., 0., 0., 10., 2.) - 100. / 3.).abs() < 1e-12);
        assert!((product_peak(10., 0., 0., 10.) - 25.).abs() < 1e-12);
        assert_eq!(product_peak(10., 20., 2., 4.), 80.);
    }
}
