//! Conditional receding-distance control with independently declared bounds.
//! It is a controller research model, not an authenticated train-protection system.
use super::*;
use std::collections::VecDeque;

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct FeedbackControl {
    pub policy_id: String,
    pub mass_lower_kg: f64,
    pub mass_upper_kg: f64,
    pub rotating_mass_upper_kg: f64,
    #[serde(default)]
    pub external_mass_upper_kg: f64,
    pub brake_force_lower_bound_n: f64,
    pub grade_estimate_fraction: f64,
    pub grade_error_bound: f64,
    pub position_error_bound_m: f64,
    pub speed_error_bound_m_s: f64,
    pub acceleration_error_bound_m_s2: f64,
    pub position_bias_m: f64,
    pub speed_bias_m_s: f64,
    pub acceleration_bias_m_s2: f64,
    pub reaction_time_bound_s: f64,
    pub brake_rise_time_bound_s: f64,
    pub stopping_margin_m: f64,
    pub end_of_authority_m: f64,
    pub initial_hold_applied: bool,
    pub start_traction_lower_bound_n: f64,
    pub rolling_resistance_upper_n: f64,
    pub external_resistance_upper_n: f64,
    pub positive_acceleration_bound_m_s2: f64,
    #[serde(default)]
    pub drive_fault_observed: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct FeedbackDiagnostics {
    pub mode: String,
    pub policy_id: String,
    pub bounds_valid: bool,
    pub bound_violations: Vec<String>,
    pub departure_held: bool,
    pub minimum_stopping_margin_m: Option<f64>,
    pub maximum_required_stopping_distance_m: f64,
    pub stopping_deceleration_lower_m_s2: f64,
    pub supervisory_interventions: u64,
    pub observations_assumed: bool,
    pub initial_hold_applied: bool,
    pub protected_service_qualified: bool,
    pub end_of_authority_violated: bool,
    pub docking_attempts: u64,
    pub maximum_docking_speed_m_s: f64,
}

fn gravity_upper(p: &FeedbackControl) -> f64 {
    let downhill = (p.grade_estimate_fraction - p.grade_error_bound).min(0.);
    p.mass_upper_kg * G * (-downhill) / (1. + downhill * downhill).sqrt()
}
fn inertia_upper(p: &FeedbackControl) -> f64 {
    p.mass_upper_kg + p.rotating_mass_upper_kg + p.external_mass_upper_kg
}
fn braking_lower(p: &FeedbackControl) -> f64 {
    (p.brake_force_lower_bound_n - gravity_upper(p)) / inertia_upper(p)
}

/// Pessimistic no-new-braking response interval, then constant lower deceleration.
/// No rolling/aerodynamic resistance is credited. `retained_acceleration` must be
/// a declared upper bound, not the plant's actual next acceleration.
pub fn stopping_distance_bound(
    p: &FeedbackControl,
    speed: f64,
    jerk: f64,
    sample_s: f64,
    retained_acceleration: f64,
) -> Option<f64> {
    let a = braking_lower(p);
    if a <= 1e-9 {
        return None;
    }
    let slew = 2. * p.brake_force_lower_bound_n / (p.mass_lower_kg * jerk);
    let delay = p.reaction_time_bound_s + p.brake_rise_time_bound_s + slew;
    // The independent supervisory hypothesis cuts traction at the next
    // controller sample. Record its discontinuity; do not assume continued
    // propulsive acceleration throughout the subsequent brake buildup.
    let run_on = p.positive_acceleration_bound_m_s2;
    let initial = speed.max(0.);
    let sample_distance = initial * sample_s + 0.5 * run_on * sample_s * sample_s;
    let v = initial + run_on * sample_s;
    let after = v + retained_acceleration * delay;
    Some(
        sample_distance
            + v * delay
            + 0.5 * retained_acceleration * delay * delay
            + after * after / (2. * a)
            + p.stopping_margin_m,
    )
}

fn validate(p: &FeedbackControl) -> Result<(), String> {
    if p.policy_id.is_empty()
        || !pos(p.mass_lower_kg)
        || !pos(p.mass_upper_kg)
        || p.mass_lower_kg > p.mass_upper_kg
        || !pos(p.brake_force_lower_bound_n)
        || !pos(p.positive_acceleration_bound_m_s2)
        || !pos(p.end_of_authority_m)
    {
        return Err(
            "Explicit positive controller policy/mass/brake/acceleration bounds required".into(),
        );
    }
    if ![
        p.rotating_mass_upper_kg,
        p.external_mass_upper_kg,
        p.grade_error_bound,
        p.position_error_bound_m,
        p.speed_error_bound_m_s,
        p.acceleration_error_bound_m_s2,
        p.reaction_time_bound_s,
        p.brake_rise_time_bound_s,
        p.stopping_margin_m,
        p.start_traction_lower_bound_n,
        p.rolling_resistance_upper_n,
        p.external_resistance_upper_n,
    ]
    .into_iter()
    .all(nonneg)
        || ![
            p.grade_estimate_fraction,
            p.position_bias_m,
            p.speed_bias_m_s,
            p.acceleration_bias_m_s2,
        ]
        .into_iter()
        .all(f64::is_finite)
        || p.grade_estimate_fraction.abs() + p.grade_error_bound > 0.1
    {
        return Err(
            "Finite explicit controller observation and uncertainty domain required".into(),
        );
    }
    Ok(())
}

fn diagnostics(c: &Case, p: &FeedbackControl, d: Option<&Drive>) -> FeedbackDiagnostics {
    let mut issues = vec![];
    let start_actual = d.map_or(0., |d| {
        if !d.windows_m.iter().any(|w| w[0] == 0.)
            || c.fault.power_loss_at_s.is_some_and(|t| t == 0.)
            || c.fault.emergency_at_m.is_some_and(|x| x == 0.)
            || c.thermal
                .as_ref()
                .is_some_and(|q| q.initial_c >= q.maximum_c)
        {
            return 0.;
        }
        let fraction = 1. - c.fault.failed_drive_fraction;
        (curve(d, 0.) * fraction)
            .min(d.mechanical_power_w * fraction / 1e-12)
            .min(d.grid_power_w * d.electrical_efficiency / 1e-12)
            .min(d.contact_force_cap_n)
    });
    for (bad, reason) in [
        (
            c.headwind_m_s < 0.,
            "forward aerodynamic assistance is outside this controller model domain",
        ),
        (
            start_actual + 1e-8 < p.start_traction_lower_bound_n,
            "initial available traction is below policy lower bound",
        ),
        (
            c.mass_kg * G * c.rolling_coefficient
                / (1. + c.grade_fraction * c.grade_fraction).sqrt()
                > p.rolling_resistance_upper_n + 1e-8,
            "rolling resistance exceeds policy feedforward bound",
        ),
        (
            d.is_some_and(|d| d.external_resistance_n > p.external_resistance_upper_n + 1e-8),
            "external resistance exceeds policy feedforward bound",
        ),
        (
            c.mass_kg < p.mass_lower_kg || c.mass_kg > p.mass_upper_kg,
            "mass outside declared policy interval",
        ),
        (
            c.rotating_equivalent_mass_kg > p.rotating_mass_upper_kg,
            "rotating inertia exceeds policy bound",
        ),
        (
            d.is_some_and(|x| x.external_mass_kg > p.external_mass_upper_kg),
            "external inertia exceeds policy bound",
        ),
        (
            c.brake_force_cap_n.min(c.brake_adhesion_force_cap_n) < p.brake_force_lower_bound_n,
            "available brake below policy lower bound",
        ),
        (
            (c.grade_fraction - p.grade_estimate_fraction).abs() > p.grade_error_bound + 1e-12,
            "grade observation error exceeds policy bound",
        ),
        (
            p.position_bias_m.abs() > p.position_error_bound_m,
            "position observation error exceeds policy bound",
        ),
        (
            p.speed_bias_m_s.abs() > p.speed_error_bound_m_s,
            "speed observation error exceeds policy bound",
        ),
        (
            p.acceleration_bias_m_s2.abs() > p.acceleration_error_bound_m_s2,
            "acceleration observation error exceeds policy bound",
        ),
        (
            c.brake_latency_s > p.reaction_time_bound_s
                || c.brake_rise_s > p.brake_rise_time_bound_s,
            "brake response exceeds policy bound",
        ),
    ] {
        if bad {
            issues.push(reason.into());
        }
    }
    FeedbackDiagnostics {
        mode: "bounded-distance-feedback/1".into(),
        policy_id: p.policy_id.clone(),
        bounds_valid: issues.is_empty(),
        bound_violations: issues,
        departure_held: false,
        minimum_stopping_margin_m: None,
        maximum_required_stopping_distance_m: 0.,
        stopping_deceleration_lower_m_s2: braking_lower(p),
        supervisory_interventions: 0,
        observations_assumed: true,
        initial_hold_applied: p.initial_hold_applied,
        protected_service_qualified: false,
        end_of_authority_violated: false,
        docking_attempts: 0,
        maximum_docking_speed_m_s: 0.,
    }
}

pub(super) fn evaluate(c: &Case, p: &FeedbackControl) -> Result<ResultRow, String> {
    evaluate_with_recovery(c, p, None)
}
pub(super) fn evaluate_with_recovery(
    c: &Case,
    p: &FeedbackControl,
    mut recovery: Option<&mut cycle::Runtime<'_>>,
) -> Result<ResultRow, String> {
    validate(p)?;
    let quiet_cycle = recovery.as_ref().is_some_and(|q| q.controlled_feedback());
    let mut r = base(c);
    let mut diag = diagnostics(c, p, c.drive.as_ref());
    r.limitations.push("Position/speed/acceleration observations and policy brake/response bounds are declared hypotheses, not authenticated sensors or protection evidence; the controller does not receive actual plant mass/grade/adhesion".into());
    r.limitations.push("Initial holding brake, when selected, is an already-applied t<0 condition. Idle/standstill motor current and heat remain unmodelled".into());
    r.limitations.push("Docking uses an ideal standstill-event observation in addition to biased position/speed/acceleration signals; a real zero-speed detector is not authenticated. The 0.25 m/s docking request has a 0.5 m/s model guard, not a measured physical limit".into());
    let Some(d) = &c.drive else {
        r.hold_reason = Some("Available drive profile absent".into());
        r.control = Some(diag);
        return Ok(r);
    };
    if d.external_mass_kg > 0. && (d.windows_m.len() != 1 || d.windows_m[0][0] != 0.) {
        r.hold_reason = Some("External mass supports one initially engaged window only".into());
        r.control = Some(diag);
        return Ok(r);
    }
    let actual_brake_cap = c.brake_force_cap_n.min(c.brake_adhesion_force_cap_n);
    let gravity =
        -c.mass_kg * G * c.grade_fraction / (1. + c.grade_fraction * c.grade_fraction).sqrt();
    let rolling =
        c.mass_kg * G * c.rolling_coefficient / (1. + c.grade_fraction * c.grade_fraction).sqrt();
    let grade_abs = (p.grade_estimate_fraction.abs() + p.grade_error_bound).min(0.1);
    let hold_required = p.mass_upper_kg * G * grade_abs / (1. + grade_abs * grade_abs).sqrt();
    let uphill = (p.grade_estimate_fraction + p.grade_error_bound).max(0.);
    let launch_required = p.mass_upper_kg * G * uphill / (1. + uphill * uphill).sqrt()
        + p.rolling_resistance_upper_n
        + p.external_resistance_upper_n;
    if p.drive_fault_observed
        || braking_lower(p) <= 1e-9
        || hold_required > p.brake_force_lower_bound_n
        || p.start_traction_lower_bound_n < launch_required
    {
        r.state = "controller-departure-held".into();
        diag.departure_held = true;
        r.hold_reason=Some(if p.drive_fault_observed {"Observed drive fault blocks departure"}else{"Declared braking/holding or initial traction lower bound cannot support departure under policy uncertainty"}.into());
        r.standstill_brake_margin_n = if p.initial_hold_applied {
            p.brake_force_lower_bound_n.min(actual_brake_cap) - gravity.abs()
        } else {
            -gravity.abs()
        };
        r.standstill_holding = p.initial_hold_applied && r.standstill_brake_margin_n >= 0.;
        r.control = Some(diag);
        return Ok(r);
    }
    // The optional station-cycle policy uses a target within the functional
    // berth band. Keep the same independent authority/error/braking bounds.
    let quiet_dock_target = if quiet_cycle {
        let zero_speed_bound = stopping_distance_bound(
            p,
            p.speed_error_bound_m_s,
            f64::INFINITY,
            c.dt_s,
            gravity_upper(p) / p.mass_lower_kg,
        )
        .unwrap()
            + p.position_error_bound_m;
        let berth_edge = c.berth_tolerance_m - p.position_error_bound_m;
        if zero_speed_bound < berth_edge {
            Some(c.distance_m - (zero_speed_bound + berth_edge) / 2.)
        } else {
            None
        }
    } else {
        None
    };
    let m0 = c.mass_kg + c.rotating_equivalent_mass_kg;
    let model_mass = (p.mass_lower_kg + p.mass_upper_kg) / 2. + p.rotating_mass_upper_kg;
    let (mut x, mut v, mut t) = (
        recovery.as_ref().map_or(0., |q| q.initial_position_m),
        0.,
        0.,
    );
    let (mut previous_a, mut previous_h) = (0., 0.);
    let mut traction_command = 0.;
    let mut brake_request = if p.initial_hold_applied {
        hold_required
    } else {
        0.
    };
    let mut actual_brake = brake_request.min(actual_brake_cap);
    let mut brake_history = VecDeque::from([(-10000., brake_request)]);
    let mut detached = d.external_mass_kg == 0.;
    let mut launched = false;
    let mut braking = false;
    let mut docking = false;
    let mut docking_moved = false;
    let mut docking_started = 0.;
    let mut failed = false;
    let mut emergency = false;
    let mut thermal_trip = false;
    let mut last_active = false;
    let mut next_trace = 0.;
    let mut temp = c.thermal.as_ref().map(|z| z.initial_c);
    r.maximum_temperature_c = temp;
    r.state = "time-budget".into();
    for _ in 0..200000 {
        if t >= c.max_time_s - 1e-12 {
            break;
        }
        if !detached && x >= d.windows_m[0][1] - 1e-8 {
            detached = true;
            r.detached_reset_kinetic_energy_j += 0.5 * d.external_mass_kg * v * v;
            event(&mut r, "external-mass-detached-energy-export", t, x, v);
        }
        let active = d
            .windows_m
            .iter()
            .any(|w| x >= w[0] - 1e-9 && x < w[1] - 1e-9);
        if active != last_active {
            event(
                &mut r,
                if active {
                    "drive-window-entry"
                } else {
                    "drive-window-exit"
                },
                t,
                x,
                v,
            );
            last_active = active;
        }
        if c.fault.power_loss_at_s.is_some_and(|at| t >= at - 1e-10) && !failed {
            failed = true;
            event(
                &mut r,
                "traction-power-loss-independent-brake-command",
                t,
                x,
                v,
            );
        }
        if c.fault.emergency_at_m.is_some_and(|at| x >= at - 1e-9) && !emergency {
            emergency = true;
            event(&mut r, "emergency-brake-command", t, x, v);
        }
        if let (Some(z), Some(q)) = (temp, c.thermal.as_ref()) {
            if z >= q.maximum_c && !thermal_trip {
                thermal_trip = true;
                event(&mut r, "thermal-traction-trip", t, x, v);
            }
        }
        let fault = failed || emergency || thermal_trip;
        let observed_x = x + p.position_bias_m;
        let observed_v = (v + p.speed_bias_m_s).max(0.);
        let observed_a = previous_a + p.acceleration_bias_m_s2;
        let planned_window = d.windows_m.iter().find(|w| {
            (observed_x - p.position_error_bound_m).max(0.) >= w[0]
                && (observed_x + p.position_error_bound_m).max(0.) < w[1]
        });
        let planned_active = planned_window.is_some();
        // Explicit research authority boundary is separate from berth target
        // and its acceptance tolerance. No surveyed/safety authority is implied.
        let remaining = (p.end_of_authority_m - observed_x - p.position_error_bound_m).max(0.);
        let response = p.reaction_time_bound_s + p.brake_rise_time_bound_s;
        // No current brake credit: a future command may release it. The
        // independent-cut hypothesis removes traction, leaving worst grade.
        let retained_a = gravity_upper(p) / p.mass_lower_kg;
        let service_required = stopping_distance_bound(
            p,
            observed_v + p.speed_error_bound_m_s,
            c.comfort_jerk_m_s3,
            c.dt_s,
            retained_a,
        )
        .unwrap();
        // Independent full-brake intervention has its own physical rise/delay,
        // and bypasses the advisory normal comfort slew. Its actual resulting
        // jerk is retained. Do not use a full comfort-slew delay near rest.
        let required = stopping_distance_bound(
            p,
            observed_v + p.speed_error_bound_m_s,
            f64::INFINITY,
            c.dt_s,
            retained_a,
        )
        .unwrap();
        let margin = remaining - required;
        diag.minimum_stopping_margin_m = Some(
            diag.minimum_stopping_margin_m
                .map_or(margin, |m| m.min(margin)),
        );
        diag.maximum_required_stopping_distance_m =
            diag.maximum_required_stopping_distance_m.max(required);
        // Enter normal feedback before the hard bound; do not fit a braking point.
        let service_lead = p.reaction_time_bound_s
            + p.brake_rise_time_bound_s
            + 2. * p.brake_force_lower_bound_n / (p.mass_lower_kg * c.comfort_jerk_m_s3);
        if !braking && launched && remaining - service_required < observed_v * service_lead + 2. {
            braking = true;
            event(&mut r, "feedback-normal-brake-command", t, x, v);
        }
        if quiet_cycle
            && !docking
            && braking
            && !fault
            && !p.drive_fault_observed
            && observed_v < 0.3
            && c.distance_m - observed_x < 5.
        {
            if let Some(target) = quiet_dock_target {
                let covered = d.windows_m.iter().any(|w| {
                    observed_x - p.position_error_bound_m >= w[0]
                        && observed_x + p.position_error_bound_m < w[1]
                        && target + p.position_error_bound_m <= w[1]
                });
                if covered {
                    docking = true;
                    docking_moved = true;
                    docking_started = t;
                    diag.docking_attempts += 1;
                    event(&mut r, "bounded-brake-preloaded-berth-approach", t, x, v);
                }
            }
        }
        let hard =
            margin < 0. && launched || docking && observed_v + p.speed_error_bound_m_s >= 0.5;
        if hard {
            diag.supervisory_interventions += 1;
        }
        let h0 = c.dt_s.min(c.max_time_s - t);
        let mut target_traction = 0.;
        if planned_active && !fault && !p.drive_fault_observed && (!braking || docking) {
            let upper_a = traction_command / p.mass_lower_kg + gravity_upper(p) / p.mass_lower_kg;
            let taper_velocity = upper_a * upper_a / c.comfort_jerk_m_s3;
            let speed_gap =
                (c.speed_cap_m_s - p.speed_error_bound_m_s - 0.1 - observed_v - taper_velocity)
                    .max(0.);
            let target_a = c
                .acceleration_request_m_s2
                .min(0.6 * (c.comfort_jerk_m_s3 * speed_gap).sqrt());
            target_traction = (model_mass * target_a
                + p.rolling_resistance_upper_n
                + p.external_resistance_upper_n
                + model_mass * G * p.grade_estimate_fraction)
                .max(0.);
            if speed_gap == 0. {
                target_traction = 0.;
            }
            if docking {
                let goal_speed = if quiet_cycle {
                    (0.15 - p.speed_error_bound_m_s)
                        .max(0.)
                        .min(0.3 * (quiet_dock_target.unwrap_or(c.distance_m) - observed_x).max(0.))
                } else {
                    (0.25 - p.speed_error_bound_m_s).max(0.)
                };
                let goal_acceleration = if quiet_cycle {
                    (0.4 * (goal_speed - observed_v)).clamp(-0.05, 0.05)
                } else {
                    (0.7 * (goal_speed - observed_v)).clamp(-0.1, 0.1)
                };
                target_traction = (traction_command
                    + 0.25 * model_mass * (goal_acceleration - observed_a))
                    .max(0.)
                    .min(p.start_traction_lower_bound_n)
                    .min(
                        model_mass * 0.1
                            + p.rolling_resistance_upper_n
                            + p.external_resistance_upper_n
                            + model_mass * G * p.grade_estimate_fraction.max(0.),
                    );
                if observed_v + upper_a * upper_a / c.comfort_jerk_m_s3 >= goal_speed {
                    target_traction = 0.;
                }
            }
            let end = planned_window.unwrap()[1];
            let time_to_exit = (end - observed_x - p.position_error_bound_m).max(0.)
                / (observed_v + p.positive_acceleration_bound_m_s2 * h0).max(0.1);
            if launched {
                target_traction =
                    target_traction.min(0.2 * p.mass_lower_kg * c.comfort_jerk_m_s3 * time_to_exit);
            }
        }
        let old_traction = traction_command;
        let old_request = brake_request;
        traction_command += (target_traction - traction_command).clamp(
            -0.5 * p.mass_lower_kg * c.comfort_jerk_m_s3 * h0,
            0.5 * p.mass_lower_kg * c.comfort_jerk_m_s3 * h0,
        );
        if !planned_active || fault || p.drive_fault_observed || hard {
            traction_command = 0.;
        }
        if !launched {
            if old_traction >= launch_required && !fault {
                // This policy explicitly assumes the independent lower traction
                // bound can deliver the requested initial effort.
                launched = true;
                event(&mut r, "bounded-hill-start-release", t, x, v);
            }
        }
        let target_brake = if fault || hard || p.drive_fault_observed {
            p.brake_force_lower_bound_n
        } else if !launched {
            hold_required
        } else if docking {
            if quiet_cycle {
                (hold_required + model_mass * 0.04).min(p.brake_force_lower_bound_n)
            } else {
                0.
            }
        } else if braking {
            let rem = (c.distance_m - p.stopping_margin_m * 0.5 - observed_x).max(0.05);
            let target_a =
                -(observed_v * observed_v / (2. * rem)).min(p.positive_acceleration_bound_m_s2);
            (brake_request + 0.25 * model_mass * (observed_a - target_a))
                .clamp(0., p.brake_force_lower_bound_n)
        } else {
            0.
        };
        let rate = 0.5 * p.mass_lower_kg * c.comfort_jerk_m_s3;
        if fault || hard {
            brake_request = target_brake;
        } else {
            brake_request += (target_brake - brake_request).clamp(-rate * h0, rate * h0);
        }
        brake_history.push_back((t, brake_request));
        while brake_history.len() > 2
            && brake_history[1].0 < t - response - c.brake_latency_s - c.dt_s
        {
            brake_history.pop_front();
        }
        let brake_rate = if c.brake_rise_s == 0. {
            f64::INFINITY
        } else {
            actual_brake_cap / c.brake_rise_s
        };
        let mut next_brake = actual_brake;
        let mut midpoint_brake = actual_brake;
        let attached = !detached && d.external_mass_kg > 0.;
        let mass = m0 + if attached { d.external_mass_kg } else { 0. };
        let ext = if attached {
            d.external_resistance_n
        } else {
            0.
        };
        let mut h = h0;
        if let Some(at) = c.fault.power_loss_at_s {
            if at > t + 1e-10 {
                h = h.min(at - t);
            }
        }
        let boundary = d
            .windows_m
            .iter()
            .flat_map(|w| w.iter())
            .copied()
            .chain(c.fault.emergency_at_m)
            .chain(recovery.as_ref().map_or_else(Vec::new, |q| q.boundaries()))
            .filter(|z| *z > x + 1e-8)
            .fold(f64::INFINITY, f64::min);
        let mut acceleration = previous_a;
        let (mut force, mut aero) = (0., 0.);
        let mut converged = false;
        let mut event_converged = false;
        for _ in 0..12 {
            traction_command =
                old_traction + (target_traction - old_traction).clamp(-rate * h, rate * h);
            if !planned_active || fault || p.drive_fault_observed || hard {
                traction_command = 0.;
            }
            brake_request = if fault || hard || p.drive_fault_observed {
                target_brake
            } else {
                old_request + (target_brake - old_request).clamp(-rate * h, rate * h)
            };
            brake_history.back_mut().unwrap().1 = brake_request;
            let delayed = brake_history
                .iter()
                .rev()
                .find(|(at, _)| *at <= t - c.brake_latency_s + 1e-12)
                .map_or(0., |(_, b)| *b);
            next_brake = (actual_brake
                + (delayed.min(actual_brake_cap) - actual_brake)
                    .clamp(-brake_rate * h, brake_rate * h))
            .clamp(0., actual_brake_cap);
            midpoint_brake = (actual_brake + next_brake) / 2.;
            converged = false;
            for _ in 0..32 {
                let vm = (v + acceleration * h / 2.).max(0.);
                aero = 0.5
                    * c.air_density_kg_m3
                    * c.cd_a_m2
                    * (vm + c.headwind_m_s)
                    * (vm + c.headwind_m_s).abs();
                let available = if active && !fault {
                    (curve(d, vm) * (1. - c.fault.failed_drive_fraction))
                        .min(
                            d.mechanical_power_w * (1. - c.fault.failed_drive_fraction)
                                / vm.max(1e-12),
                        )
                        .min(d.grid_power_w * d.electrical_efficiency / vm.max(1e-12))
                        .min(d.contact_force_cap_n)
                } else {
                    0.
                };
                let release_cap = recovery
                    .as_ref()
                    .map_or(0., |q| q.release_cap(x, vm, h, fault));
                force = traction_command.min(available + release_cap);
                let net = if v == 0. {
                    let pre = force + gravity - aero;
                    pre.signum() * (pre.abs() - rolling - ext - midpoint_brake).max(0.)
                } else {
                    force + gravity - rolling - ext - aero - midpoint_brake
                };
                let next = net / mass;
                if (next - acceleration).abs() < 1e-10 {
                    acceleration = next;
                    converged = true;
                    break;
                }
                acceleration = next;
            }
            if !converged {
                break;
            }
            let mut shorter = h;
            if v > 0. && acceleration < 0. && v + acceleration * h < 0. {
                shorter = shorter.min(-v / acceleration);
            }
            let dx = v * h + 0.5 * acceleration * h * h;
            if dx > boundary - x && boundary > x + 1e-8 {
                let denominator = v + (v * v + 2. * acceleration * (boundary - x)).max(0.).sqrt();
                if denominator > 0. {
                    shorter = shorter.min(2. * (boundary - x) / denominator);
                }
            }
            if shorter >= h * (1. - 1e-10) {
                event_converged = true;
                break;
            }
            h = shorter;
        }
        if !converged {
            r.state = "numerical-midpoint-held".into();
            r.hold_reason = Some("Feedback plant midpoint did not converge".into());
            break;
        }
        if !event_converged {
            r.state = "numerical-event-held".into();
            r.hold_reason = Some("Feedback window/zero-speed event did not converge".into());
            break;
        }
        if v == 0. && acceleration < -1e-10 {
            r.rollback_detected = true;
            r.state = "incipient-rollback-held".into();
            event(&mut r, "incipient-rollback", t, x, v);
            break;
        }
        if h <= 1e-12 {
            r.state = "event-resolution-held".into();
            break;
        }
        let dx = v * h + 0.5 * acceleration * h * h;
        let nv = (v + acceleration * h).max(0.);
        let vm = (v + nv) / 2.;
        let fraction = 1. - c.fault.failed_drive_fraction;
        let cap = if active && !fault {
            (curve(d, vm) * fraction)
                .min(d.mechanical_power_w * fraction / vm.max(1e-12))
                .min(d.grid_power_w * d.electrical_efficiency / vm.max(1e-12))
                .min(d.contact_force_cap_n)
        } else {
            0.
        };
        let release_cap = recovery
            .as_ref()
            .map_or(0., |q| q.release_cap(x, vm, h, fault));
        if force > cap + release_cap + 1e-8 * (cap + release_cap).max(1.)
            || midpoint_brake > actual_brake_cap + 1e-8
        {
            r.state = "numerical-rating-held".into();
            break;
        }
        let work = force * dx;
        let (store_work, capture_work) = if let Some(q) = recovery.as_deref_mut() {
            q.commit(
                x,
                vm,
                v.max(nv),
                v,
                nv,
                dx,
                h,
                t + h,
                force,
                midpoint_brake,
                fault,
            )?
        } else {
            (0., 0.)
        };
        let grid = (work - store_work) / d.electrical_efficiency;
        r.traction_work_j += work;
        r.grid_energy_j += grid;
        r.drive_loss_j += grid - (work - store_work);
        r.brake_heat_j += midpoint_brake * dx.abs() - capture_work;
        r.resistance_work_j += rolling * dx.abs() + aero * dx;
        r.external_resistance_work_j += ext * dx.abs();
        r.grade_work_j += gravity * dx;
        r.maximum_traction_n = r.maximum_traction_n.max(force);
        r.maximum_brake_n = r.maximum_brake_n.max(midpoint_brake);
        r.maximum_mechanical_power_w = r.maximum_mechanical_power_w.max(force * (v + nv) / 2.);
        let grid_peak = recovery
            .as_ref()
            .and_then(|q| q.controlled_grid_peak_power_w())
            .map_or((force - release_cap.min(force)) * (v + nv) / 2., |p| p);
        r.maximum_grid_power_w = r
            .maximum_grid_power_w
            .max(grid_peak / d.electrical_efficiency);
        r.maximum_acceleration_m_s2 = r.maximum_acceleration_m_s2.max(acceleration);
        r.minimum_acceleration_m_s2 = r.minimum_acceleration_m_s2.min(acceleration);
        r.maximum_absolute_jerk_m_s3 = r.maximum_absolute_jerk_m_s3.max(
            (acceleration - previous_a).abs()
                / if previous_h > 0. {
                    (previous_h + h) / 2.
                } else {
                    h
                },
        );
        x += dx;
        if docking && dx > 1e-6 {
            docking_moved = true;
        }
        v = if nv < 1e-9 { 0. } else { nv };
        t += h;
        previous_a = acceleration;
        previous_h = h;
        actual_brake = next_brake;
        r.maximum_speed_m_s = r.maximum_speed_m_s.max(v);
        if docking {
            diag.maximum_docking_speed_m_s = diag.maximum_docking_speed_m_s.max(v);
        }
        if let (Some(z), Some(q)) = (temp, c.thermal.as_ref()) {
            let n = temperature(z, h, (grid - (work - store_work)) / h, q);
            temp = Some(n);
            r.maximum_temperature_c = Some(r.maximum_temperature_c.unwrap().max(n));
        }
        if t >= next_trace || v == 0. && launched {
            r.trace.push(Trace {
                time_s: t,
                position_m: x,
                speed_m_s: v,
                acceleration_m_s2: acceleration,
                traction_n: force,
                brake_n: midpoint_brake,
            });
            next_trace = t + 1.;
        }
        if v == 0. && launched && (braking || fault || !active) {
            r.state = "stopped".into();
            r.terminal_acceleration_step_m_s2 = -acceleration;
            r.terminal_jerk_resolved = acceleration.abs() < 1e-6;
            if docking && !docking_moved && !fault && !p.drive_fault_observed {
                if t - docking_started < 30. {
                    continue;
                }
                r.state = "docking-launch-held".into();
                r.hold_reason = Some(
                    "Continuous-drive docking did not establish forward motion within30s".into(),
                );
                break;
            }
            // Apply no imaginary immediate holding force: retain the actual
            // physical brake state already present at this event.
            let observed_stop = x + p.position_bias_m;
            let target = if quiet_cycle {
                quiet_dock_target.unwrap_or(c.distance_m - p.stopping_margin_m * 0.5)
            } else {
                c.distance_m - p.stopping_margin_m * 0.5
            };
            let coverage = d.windows_m.iter().any(|w| {
                observed_stop - p.position_error_bound_m >= w[0]
                    && observed_stop + p.position_error_bound_m < w[1]
                    && target + p.position_error_bound_m <= w[1]
                    && target - p.position_error_bound_m >= w[0]
            });
            let permitted = (!quiet_cycle || quiet_dock_target.is_some())
                && !fault
                && !p.drive_fault_observed
                && coverage
                && p.position_error_bound_m * 2. < c.berth_tolerance_m
                && p.speed_error_bound_m_s < 0.25
                && target + p.position_error_bound_m <= p.end_of_authority_m
                && c.distance_m - observed_stop > c.berth_tolerance_m
                && diag.docking_attempts < 2;
            if permitted {
                docking = true;
                docking_moved = false;
                docking_started = t;
                diag.docking_attempts += 1;
                event(&mut r, "bounded-continuous-drive-docking", t, x, v);
                continue;
            }
            break;
        }
        if !launched && t > 30. {
            r.state = "controller-launch-held".into();
            diag.departure_held = true;
            break;
        }
        if v == 0. && (failed || thermal_trip || !active || curve(d, 0.) == 0.) {
            r.state = if fault && actual_brake >= gravity.abs() {
                "stopped"
            } else {
                "stalled-no-starting-force"
            }
            .into();
            break;
        }
        if x > c.distance_m + c.berth_tolerance_m + 100. {
            r.state = "destination-overrun".into();
            break;
        }
    }
    if !detached && x >= d.windows_m[0][1] - 1e-8 {
        r.detached_reset_kinetic_energy_j += 0.5 * d.external_mass_kg * v * v;
        detached = true;
        event(&mut r, "external-mass-detached-energy-export", t, x, v);
    }
    r.final_position_m = x;
    r.final_speed_m_s = v;
    r.elapsed_s = t;
    r.berth_error_m = x - c.distance_m;
    r.standstill_brake_margin_n = actual_brake - gravity.abs();
    r.standstill_holding = r.state == "stopped" && r.standstill_brake_margin_n >= -1e-8;
    diag.end_of_authority_violated = x > p.end_of_authority_m + 1e-8;
    if r.maximum_acceleration_m_s2 > p.positive_acceleration_bound_m_s2 + 1e-8 {
        diag.bound_violations
            .push("positive acceleration exceeds policy bound".into());
        diag.bounds_valid = false;
    }
    let fault = failed || emergency || thermal_trip || c.fault.failed_drive_fraction > 0.;
    r.normal_numerical_arrival = !fault
        && diag.bounds_valid
        && !diag.end_of_authority_violated
        && diag.maximum_docking_speed_m_s <= 0.5 + 1e-8
        && r.standstill_holding
        && r.maximum_speed_m_s <= c.speed_cap_m_s + 1e-7
        && r.berth_error_m.abs() <= c.berth_tolerance_m;
    r.fault_stop_in_route = fault
        && diag.bounds_valid
        && !diag.end_of_authority_violated
        && r.standstill_holding
        && x >= 0.
        && x <= c.distance_m + c.berth_tolerance_m;
    r.final_kinetic_energy_j = 0.5 * (m0 + if !detached { d.external_mass_kg } else { 0. }) * v * v;
    r.energy_residual_j = r.traction_work_j + r.grade_work_j
        - r.resistance_work_j
        - r.external_resistance_work_j
        - r.brake_heat_j
        - recovery.as_ref().map_or(0., |q| q.energy.capture_work_j)
        - r.detached_reset_kinetic_energy_j
        - r.final_kinetic_energy_j;
    if r.energy_residual_j.abs() > 1e-6 * r.traction_work_j.abs().max(r.grade_work_j.abs()).max(1.)
    {
        r.state = "numerical-energy-held".into();
        r.normal_numerical_arrival = false;
        r.fault_stop_in_route = false;
    }
    r.journey_plus_dwell_s = t + c.dwell_s;
    r.headway_minus_journey_plus_dwell_s = c.headway_s - r.journey_plus_dwell_s;
    r.auxiliary_energy_j = c.auxiliary_power_w * r.journey_plus_dwell_s;
    if let (Some(z), Some(q)) = (temp, c.thermal.as_ref()) {
        temp = Some(temperature(z, c.dwell_s, 0., q));
        r.maximum_temperature_c = Some(r.maximum_temperature_c.unwrap().max(temp.unwrap()));
    }
    r.final_temperature_c = temp;
    if c.thermal
        .as_ref()
        .is_some_and(|q| r.maximum_temperature_c.unwrap_or(q.initial_c) > q.maximum_c)
    {
        r.state = "thermal-envelope-exceeded".into();
        r.normal_numerical_arrival = false;
        r.fault_stop_in_route = false;
    }
    r.control = Some(diag);
    Ok(r)
}
