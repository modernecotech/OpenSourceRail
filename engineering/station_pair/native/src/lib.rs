//! Conditional, SI, force-driven point-train research. No operating-map admission.
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
pub const MAX_INPUT_BYTES: usize = 8 * 1024 * 1024;
pub const REQUEST_SCHEMA: &str = "osr-journey-request/1";
const G: f64 = 9.80665;
mod feedback;
pub use feedback::{FeedbackControl, FeedbackDiagnostics, stopping_distance_bound};
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Request {
    pub schema: String,
    pub cases: Vec<Case>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct ForcePoint {
    pub speed_m_s: f64,
    pub force_n: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Drive {
    pub points: Vec<ForcePoint>,
    pub windows_m: Vec<[f64; 2]>,
    pub maximum_speed_m_s: f64,
    pub mechanical_power_w: f64,
    pub electrical_efficiency: f64,
    pub grid_power_w: f64,
    pub contact_force_cap_n: f64,
    pub external_mass_kg: f64,
    pub external_resistance_n: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Fault {
    pub power_loss_at_s: Option<f64>,
    pub failed_drive_fraction: f64,
    pub emergency_at_m: Option<f64>,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Thermal {
    pub capacity_j_k: f64,
    pub heat_rejection_w_k: f64,
    pub ambient_c: f64,
    pub initial_c: f64,
    pub maximum_c: f64,
}
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub id: String,
    pub candidate_id: String,
    pub mass_kg: f64,
    pub rotating_equivalent_mass_kg: f64,
    pub distance_m: f64,
    pub grade_fraction: f64,
    pub rolling_coefficient: f64,
    pub air_density_kg_m3: f64,
    pub cd_a_m2: f64,
    pub headwind_m_s: f64,
    pub speed_cap_m_s: f64,
    pub acceleration_request_m_s2: f64,
    pub comfort_jerk_m_s3: f64,
    pub brake_start_m: f64,
    pub berth_tolerance_m: f64,
    pub brake_force_cap_n: f64,
    pub brake_adhesion_force_cap_n: f64,
    pub brake_latency_s: f64,
    pub brake_rise_s: f64,
    pub dt_s: f64,
    pub max_time_s: f64,
    pub dwell_s: f64,
    pub headway_s: f64,
    pub auxiliary_power_w: f64,
    pub drive: Option<Drive>,
    pub fault: Fault,
    pub thermal: Option<Thermal>,
    #[serde(default)]
    pub control: Option<FeedbackControl>,
}
#[derive(Debug, Clone, Serialize)]
pub struct Trace {
    pub time_s: f64,
    pub position_m: f64,
    pub speed_m_s: f64,
    pub acceleration_m_s2: f64,
    pub traction_n: f64,
    pub brake_n: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct Event {
    pub kind: String,
    pub time_s: f64,
    pub position_m: f64,
    pub speed_m_s: f64,
}
#[derive(Debug, Clone, Serialize)]
pub struct ResultRow {
    pub id: String,
    pub candidate_id: String,
    pub state: String,
    pub hold_reason: Option<String>,
    pub final_position_m: f64,
    pub final_speed_m_s: f64,
    pub elapsed_s: f64,
    pub normal_numerical_arrival: bool,
    pub fault_stop_in_route: bool,
    pub standstill_holding: bool,
    pub standstill_brake_margin_n: f64,
    pub rollback_detected: bool,
    pub berth_error_m: f64,
    pub maximum_speed_m_s: f64,
    pub maximum_acceleration_m_s2: f64,
    pub minimum_acceleration_m_s2: f64,
    pub maximum_absolute_jerk_m_s3: f64,
    pub terminal_acceleration_step_m_s2: f64,
    pub terminal_jerk_resolved: bool,
    pub maximum_traction_n: f64,
    pub maximum_brake_n: f64,
    pub maximum_mechanical_power_w: f64,
    pub maximum_grid_power_w: f64,
    pub traction_work_j: f64,
    pub grid_energy_j: f64,
    pub drive_loss_j: f64,
    pub auxiliary_energy_j: f64,
    pub brake_heat_j: f64,
    pub resistance_work_j: f64,
    pub grade_work_j: f64,
    pub external_resistance_work_j: f64,
    pub detached_reset_kinetic_energy_j: f64,
    pub final_kinetic_energy_j: f64,
    pub energy_residual_j: f64,
    pub maximum_temperature_c: Option<f64>,
    pub final_temperature_c: Option<f64>,
    pub journey_plus_dwell_s: f64,
    pub headway_minus_journey_plus_dwell_s: f64,
    pub events: Vec<Event>,
    pub trace: Vec<Trace>,
    pub limitations: Vec<String>,
    pub conditional: bool,
    pub admitted_operating_map: bool,
    pub physical_accepted: bool,
    pub engineering_accepted: bool,
    pub operating_release: bool,
    pub control: Option<FeedbackDiagnostics>,
}
#[derive(Debug, Serialize)]
pub struct BatchResult {
    pub schema: &'static str,
    pub cases: Vec<ResultRow>,
}
fn nonneg(x: f64) -> bool {
    x.is_finite() && x >= 0.
}
fn pos(x: f64) -> bool {
    x.is_finite() && x > 0.
}
fn valid(c: &Case) -> Result<(), String> {
    if c.id.is_empty()
        || c.candidate_id.len() != 64
        || !c.candidate_id.bytes().all(|x| x.is_ascii_hexdigit())
    {
        return Err("Explicit case and 64-hex physical candidate IDs required".into());
    }
    for (n, x) in [
        ("mass", c.mass_kg),
        ("distance", c.distance_m),
        ("speed cap", c.speed_cap_m_s),
        ("acceleration request", c.acceleration_request_m_s2),
        ("jerk", c.comfort_jerk_m_s3),
        ("dt", c.dt_s),
        ("time", c.max_time_s),
        ("headway", c.headway_s),
    ] {
        if !pos(x) {
            return Err(format!("Positive finite SI {n} required"));
        }
    }
    for (n, x) in [
        ("rotating mass", c.rotating_equivalent_mass_kg),
        ("rolling", c.rolling_coefficient),
        ("air density", c.air_density_kg_m3),
        ("CdA", c.cd_a_m2),
        ("brake start", c.brake_start_m),
        ("berth tolerance", c.berth_tolerance_m),
        ("brake force", c.brake_force_cap_n),
        ("brake adhesion", c.brake_adhesion_force_cap_n),
        ("brake latency", c.brake_latency_s),
        ("brake rise", c.brake_rise_s),
        ("dwell", c.dwell_s),
        ("auxiliary power", c.auxiliary_power_w),
    ] {
        if !nonneg(x) {
            return Err(format!("Nonnegative finite SI {n} required"));
        }
    }
    if !c.grade_fraction.is_finite()
        || c.grade_fraction.abs() > 0.1
        || !c.headwind_m_s.is_finite()
        || c.dt_s < 0.001
        || c.dt_s > 0.2
        || c.max_time_s > 3600.
        || c.brake_start_m > c.distance_m
    {
        return Err("Declared numerical/grade/braking domain exceeded".into());
    }
    if !nonneg(c.fault.failed_drive_fraction)
        || c.fault.failed_drive_fraction > 1.
        || c.fault.power_loss_at_s.is_some_and(|x| !nonneg(x))
        || c.fault.emergency_at_m.is_some_and(|x| !nonneg(x))
    {
        return Err("Invalid explicit fault".into());
    }
    if let Some(d) = &c.drive {
        if d.points.len() < 2
            || d.points.len() > 1024
            || d.points[0].speed_m_s != 0.
            || !pos(d.maximum_speed_m_s)
            || !pos(d.electrical_efficiency)
            || d.electrical_efficiency > 1.
            || ![
                d.mechanical_power_w,
                d.grid_power_w,
                d.contact_force_cap_n,
                d.external_mass_kg,
                d.external_resistance_n,
            ]
            .into_iter()
            .all(nonneg)
        {
            return Err("Invalid explicit drive ratings/domain".into());
        }
        if d.points
            .iter()
            .any(|p| !nonneg(p.speed_m_s) || !nonneg(p.force_n))
            || d.points
                .windows(2)
                .any(|p| p[1].speed_m_s <= p[0].speed_m_s)
            || d.points.last().unwrap().speed_m_s < d.maximum_speed_m_s
        {
            return Err(
                "Speed-force samples must cover zero to maximum without extrapolation".into(),
            );
        }
        if d.windows_m.is_empty()
            || d.windows_m.len() > 32
            || d.windows_m
                .iter()
                .any(|w| !nonneg(w[0]) || !pos(w[1]) || w[1] <= w[0] || w[1] > c.distance_m)
            || d.windows_m.windows(2).any(|w| w[1][0] < w[0][1])
        {
            return Err("Sorted disjoint finite front-coordinate windows required".into());
        }
    }
    if let Some(t) = &c.thermal {
        if !pos(t.capacity_j_k)
            || !nonneg(t.heat_rejection_w_k)
            || ![t.ambient_c, t.initial_c, t.maximum_c]
                .into_iter()
                .all(f64::is_finite)
            || t.maximum_c <= t.ambient_c
        {
            return Err("Invalid explicit aggregate thermal RC".into());
        }
    }
    Ok(())
}
fn base(c: &Case) -> ResultRow {
    ResultRow{id:c.id.clone(),candidate_id:c.candidate_id.clone(),state:"held".into(),hold_reason:None,final_position_m:0.,final_speed_m_s:0.,elapsed_s:0.,normal_numerical_arrival:false,fault_stop_in_route:false,standstill_holding:false,standstill_brake_margin_n:0.,rollback_detected:false,berth_error_m:-c.distance_m,maximum_speed_m_s:0.,maximum_acceleration_m_s2:0.,minimum_acceleration_m_s2:0.,maximum_absolute_jerk_m_s3:0.,terminal_acceleration_step_m_s2:0.,terminal_jerk_resolved:false,maximum_traction_n:0.,maximum_brake_n:0.,maximum_mechanical_power_w:0.,maximum_grid_power_w:0.,traction_work_j:0.,grid_energy_j:0.,drive_loss_j:0.,auxiliary_energy_j:0.,brake_heat_j:0.,resistance_work_j:0.,grade_work_j:0.,external_resistance_work_j:0.,detached_reset_kinetic_energy_j:0.,final_kinetic_energy_j:0.,energy_residual_j:0.,maximum_temperature_c:None,final_temperature_c:None,journey_plus_dwell_s:0.,headway_minus_journey_plus_dwell_s:0.,events:vec![],trace:vec![],limitations:vec!["Conditional point-train equipment/engagement hypotheses; no measured actuator, adhesion, coupling, flexible train or protected service proof".into(),"Auxiliary energy is separate electrical demand; battery/charger/source and regenerative recovery are not modelled".into(),"Journey+dwelling is not station resource occupation or safe headway; no timetable, controller or movement authority".into(),"Force discontinuities are retained; jerk uses successive moving-step midpoint acceleration times, including shortened event steps. The terminal acceleration step is reported separately: Coulomb/static/hold transitions are not jerk-qualified".into(),"Aggregate thermal RC is a declared drive-loss hypothesis, not component temperatures or repeated-duty qualification".into(),"Traction power loss conditionally commands independent braking with the input latency/rise; actual control, brake supply independence and standstill retention are not authenticated".into()],conditional:true,admitted_operating_map:false,physical_accepted:false,engineering_accepted:false,operating_release:false,control:None}
}
fn curve(d: &Drive, v: f64) -> f64 {
    if v > d.maximum_speed_m_s {
        return 0.;
    }
    let v = v.max(0.);
    for p in d.points.windows(2) {
        if v <= p[1].speed_m_s {
            return p[0].force_n
                + (p[1].force_n - p[0].force_n) * (v - p[0].speed_m_s)
                    / (p[1].speed_m_s - p[0].speed_m_s);
        }
    }
    0.
}
fn temperature(t: f64, h: f64, q: f64, m: &Thermal) -> f64 {
    if m.heat_rejection_w_k == 0. {
        t + q * h / m.capacity_j_k
    } else {
        let eq = m.ambient_c + q / m.heat_rejection_w_k;
        eq + (t - eq) * (-h * m.heat_rejection_w_k / m.capacity_j_k).exp()
    }
}
fn event(r: &mut ResultRow, k: &str, t: f64, x: f64, v: f64) {
    r.events.push(Event {
        kind: k.into(),
        time_s: t,
        position_m: x,
        speed_m_s: v,
    });
}
/// Integrate actual capped force; position is never reset to a target berth.
pub fn evaluate(c: &Case) -> Result<ResultRow, String> {
    valid(c)?;
    if let Some(control) = &c.control {
        return feedback::evaluate(c, control);
    }
    let mut r = base(c);
    let Some(d) = &c.drive else {
        r.hold_reason = Some("Available source-derived drive profile absent".into());
        return Ok(r);
    };
    if d.external_mass_kg > 0. && (d.windows_m.len() != 1 || d.windows_m[0][0] != 0.) {
        r.hold_reason=Some("Nonzero external mass supports one window starting0 only; later/multiple engagements unsupported".into());
        return Ok(r);
    }
    let m0 = c.mass_kg + c.rotating_equivalent_mass_kg;
    let mut x = 0.;
    let mut v = 0.;
    let mut t = 0.;
    let mut previous_a = 0.;
    let mut command = 0.;
    let mut brake_command = 0.;
    let mut brake_at = None;
    let mut detached = d.external_mass_kg == 0.;
    let mut last_active = false;
    let mut failed = false;
    let mut emergency_seen = false;
    let mut thermal_trip = false;
    let mut temp = c.thermal.as_ref().map(|q| q.initial_c);
    let mut next_trace = 0.;
    let mut previous_h = 0.;
    let gravity = -c.mass_kg * G * c.grade_fraction / (1. + c.grade_fraction.powi(2)).sqrt();
    let rolling = c.mass_kg * G * c.rolling_coefficient / (1. + c.grade_fraction.powi(2)).sqrt();
    r.state = "time-budget".into();
    r.maximum_temperature_c = temp;
    'steps: for _ in 0..200000 {
        if t >= c.max_time_s - 1e-12 {
            break;
        }
        if !detached && x >= d.windows_m[0][1] - 1e-8 {
            r.detached_reset_kinetic_energy_j += 0.5 * d.external_mass_kg * v * v;
            detached = true;
            event(&mut r, "external-mass-detached-energy-export", t, x, v);
        }
        let active = d
            .windows_m
            .iter()
            .any(|w| x >= w[0] - 1e-9 && x < w[1] - 1e-9);
        if !active {
            command = 0.;
        }
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
        if c.fault.power_loss_at_s.is_some_and(|z| t >= z - 1e-10) && !failed {
            failed = true;
            event(&mut r, "traction-power-loss", t, x, v);
            if brake_at.is_none() {
                brake_at = Some(t);
                event(&mut r, "power-loss-independent-brake-command", t, x, v);
            }
        }
        if let (Some(temp), Some(model)) = (temp, c.thermal.as_ref()) {
            if temp >= model.maximum_c && !thermal_trip {
                thermal_trip = true;
                event(&mut r, "thermal-traction-trip", t, x, v);
            }
        }
        let emergency = c.fault.emergency_at_m.is_some_and(|z| x >= z - 1e-9);
        if emergency && !emergency_seen {
            emergency_seen = true;
            event(&mut r, "emergency-position-reached", t, x, v);
        }
        if brake_at.is_none() && (x >= c.brake_start_m - 1e-9 || emergency) {
            brake_at = Some(t);
            event(
                &mut r,
                if emergency {
                    "emergency-brake-command"
                } else {
                    "normal-brake-command"
                },
                t,
                x,
                v,
            );
        }
        let attached = !detached && d.external_mass_kg > 0.;
        let m = m0 + if attached { d.external_mass_kg } else { 0. };
        let ext = if attached {
            d.external_resistance_n
        } else {
            0.
        };
        let mut h = c.dt_s.min(c.max_time_s - t);
        if let Some(z) = c.fault.power_loss_at_s {
            if z > t + 1e-10 {
                h = h.min(z - t);
            }
        }
        let mut boundary = c.distance_m + 1000.;
        for z in d
            .windows_m
            .iter()
            .flat_map(|w| w.iter())
            .copied()
            .chain([c.brake_start_m])
            .chain(c.fault.emergency_at_m)
        {
            if z > x + 1e-8 {
                boundary = boundary.min(z);
            }
        }
        let mut a = previous_a;
        let (mut force, mut b, mut resistance) = (0., 0., 0.);
        let (mut next_command, mut next_brake) = (command, brake_command);
        // Fixed-point midpoint force; repeat after resolving position/zero-speed events.
        let mut event_converged = false;
        for _ in 0..12 {
            let mut converged = false;
            for _ in 0..32 {
                let vm = (v + a * h / 2.).max(0.);
                let aero = 0.5
                    * c.air_density_kg_m3
                    * c.cd_a_m2
                    * (vm + c.headwind_m_s)
                    * (vm + c.headwind_m_s).abs();
                let desired_a = c
                    .acceleration_request_m_s2
                    .min(0.8 * (c.comfort_jerk_m_s3 * (c.speed_cap_m_s - v).max(0.)).sqrt());
                let mut desired = if brake_at.is_some() || !active {
                    0.
                } else {
                    (m * desired_a + rolling + ext + aero - gravity).max(0.)
                };
                if active && brake_at.is_none() {
                    let end = d
                        .windows_m
                        .iter()
                        .find(|w| x >= w[0] - 1e-9 && x < w[1] - 1e-9)
                        .unwrap()[1];
                    // Fastest possible exit gives a conservative command-taper time.
                    // A true source/contact failure still cuts force immediately.
                    let peak = d.points.iter().map(|p| p.force_n).fold(0., f64::max)
                        * (1. - c.fault.failed_drive_fraction);
                    let upper_a = (peak + gravity.abs() + aero.abs()) / m + 1e-12;
                    let distance = (end - x).max(0.);
                    let time_to_exit =
                        2. * distance / (v + (v * v + 2. * upper_a * distance).sqrt()).max(1e-12);
                    desired = desired.min(0.8 * m * c.comfort_jerk_m_s3 / 2. * time_to_exit);
                }
                next_command = command
                    + (desired - command).clamp(
                        -m * c.comfort_jerk_m_s3 * h / 2.,
                        m * c.comfort_jerk_m_s3 * h / 2.,
                    );
                let available = if active && !failed && !thermal_trip && !emergency {
                    let fraction = 1. - c.fault.failed_drive_fraction;
                    (curve(d, vm) * fraction)
                        .min(d.mechanical_power_w * fraction / vm.max(1e-12))
                        .min(d.grid_power_w * d.electrical_efficiency / vm.max(1e-12))
                        .min(d.contact_force_cap_n)
                } else {
                    0.
                };
                force = next_command.min(available);
                let brake_cap = c.brake_force_cap_n.min(c.brake_adhesion_force_cap_n);
                let fraction = brake_at.map_or(0., |at| {
                    let age = t + h / 2. - at - c.brake_latency_s;
                    if age <= 0. {
                        0.
                    } else if c.brake_rise_s == 0. {
                        1.
                    } else {
                        (age / c.brake_rise_s).min(1.)
                    }
                });
                let mut desired_brake = brake_cap * fraction;
                if !emergency && !failed && !thermal_trip && brake_at.is_some() {
                    let smooth_deceleration = 0.8 * (c.comfort_jerk_m_s3 * v.max(0.)).sqrt();
                    // Retain a static gravity holding floor; rolling resistance
                    // is never credited as the standstill retaining brake.
                    let normal_target = (force + gravity - rolling - ext - aero
                        + m * smooth_deceleration)
                        .max(gravity.abs());
                    desired_brake = desired_brake.min(normal_target);
                }
                next_brake = if emergency {
                    desired_brake
                } else {
                    brake_command
                        + (desired_brake - brake_command).clamp(
                            -m * c.comfort_jerk_m_s3 * h / 2.,
                            m * c.comfort_jerk_m_s3 * h / 2.,
                        )
                };
                b = next_brake;
                resistance = rolling + ext + aero;
                // A commanded speed limiter can only reduce supplied traction.
                // Gravity-driven overspeed cannot be removed by inventing force.
                let speed_limited_force =
                    (m * (c.speed_cap_m_s - v).max(0.) / h + resistance + b - gravity).max(0.);
                force = force.min(speed_limited_force);
                let net = if v.abs() < 1e-10 {
                    let pre = force + gravity - aero;
                    pre.signum() * (pre.abs() - rolling - ext - b).max(0.)
                } else {
                    force + gravity - resistance - b
                };
                let next = net / m;
                if (next - a).abs() < 1e-10 {
                    a = next;
                    converged = true;
                    break;
                }
                a = next;
            }
            if !converged {
                r.state = "numerical-midpoint-held".into();
                r.hold_reason =
                    Some("Midpoint force iteration did not converge; no arrival claim".into());
                break 'steps;
            }
            let dx = v * h + 0.5 * a * h * h;
            let mut new_h = h;
            if v > 0. && a < 0. && v + a * h < 0. {
                new_h = new_h.min(-v / a);
            }
            if dx > boundary - x && boundary > x + 1e-8 {
                let disc = (v * v + 2. * a * (boundary - x)).max(0.);
                let denom = v + disc.sqrt();
                if denom > 0. {
                    new_h = new_h.min(2. * (boundary - x) / denom);
                }
            }
            if new_h >= h * (1. - 1e-10) {
                event_converged = true;
                break;
            }
            h = new_h;
        }
        if !event_converged {
            r.state = "numerical-event-held".into();
            r.hold_reason = Some("Window/zero-speed event iteration did not converge".into());
            break;
        }
        if v == 0. && a < -1e-10 {
            r.rollback_detected = true;
            r.state = "incipient-rollback-held".into();
            r.hold_reason=Some("Available drive/brake cannot prevent initial backward acceleration; reverse motion not simulated".into());
            event(&mut r, "incipient-rollback", t, x, v);
            break;
        }
        if h <= 1e-12 {
            r.state = "event-resolution-held".into();
            break;
        }
        let dx = v * h + 0.5 * a * h * h;
        let nv = v + a * h;
        let mid_speed = (v + nv) / 2.;
        let fraction = 1. - c.fault.failed_drive_fraction;
        let allowed = if active && !failed && !thermal_trip && !emergency {
            (curve(d, mid_speed) * fraction)
                .min(d.mechanical_power_w * fraction / mid_speed.max(1e-12))
                .min(d.grid_power_w * d.electrical_efficiency / mid_speed.max(1e-12))
                .min(d.contact_force_cap_n)
        } else {
            0.
        };
        if force > allowed + 1e-8 * allowed.max(1.)
            || b > c.brake_force_cap_n.min(c.brake_adhesion_force_cap_n) + 1e-8
        {
            r.state = "numerical-rating-held".into();
            r.hold_reason =
                Some("Final actual midpoint force exceeds a supplied source/brake rating".into());
            break;
        }
        let work = force * dx;
        let grid = work.max(0.) / d.electrical_efficiency;
        let loss = grid - work;
        r.traction_work_j += work;
        r.grid_energy_j += grid;
        r.drive_loss_j += loss;
        r.brake_heat_j += b * dx.abs();
        r.resistance_work_j += rolling * dx.abs() + (resistance - rolling - ext) * dx;
        r.external_resistance_work_j += ext * dx.abs();
        r.grade_work_j += gravity * dx;
        r.maximum_traction_n = r.maximum_traction_n.max(force);
        r.maximum_brake_n = r.maximum_brake_n.max(b);
        r.maximum_mechanical_power_w = r.maximum_mechanical_power_w.max(force * (v + nv) / 2.);
        r.maximum_grid_power_w = r
            .maximum_grid_power_w
            .max(force * (v + nv) / 2. / d.electrical_efficiency);
        r.maximum_absolute_jerk_m_s3 = r.maximum_absolute_jerk_m_s3.max(
            (a - previous_a).abs()
                / if previous_h > 0. {
                    (previous_h + h) / 2.
                } else {
                    h
                },
        );
        r.maximum_acceleration_m_s2 = r.maximum_acceleration_m_s2.max(a);
        r.minimum_acceleration_m_s2 = r.minimum_acceleration_m_s2.min(a);
        x += dx;
        v = if nv.abs() < 1e-9 { 0. } else { nv };
        t += h;
        command = next_command;
        brake_command = next_brake;
        previous_a = a;
        previous_h = h;
        r.maximum_speed_m_s = r.maximum_speed_m_s.max(v);
        if let (Some(q), Some(model)) = (temp, c.thermal.as_ref()) {
            let q = temperature(q, h, loss / h, model);
            temp = Some(q);
            r.maximum_temperature_c = Some(r.maximum_temperature_c.unwrap().max(q));
        }
        if t >= next_trace || brake_at.is_some() && v == 0. {
            r.trace.push(Trace {
                time_s: t,
                position_m: x,
                speed_m_s: v,
                acceleration_m_s2: a,
                traction_n: force,
                brake_n: b,
            });
            next_trace = t + 1.;
        }
        if v < -1e-7 {
            r.rollback_detected = true;
            r.state = "rollback-detected".into();
            break;
        }
        if brake_at.is_some() && v == 0. {
            r.terminal_acceleration_step_m_s2 = -a;
            r.terminal_jerk_resolved = a.abs() < 1e-6;
            if !r.terminal_jerk_resolved {
                event(
                    &mut r,
                    "terminal-standstill-acceleration-step-unresolved",
                    t,
                    x,
                    v,
                );
            }
            r.state = "stopped".into();
            break;
        }
        if v == 0.
            && force == 0.
            && (curve(d, 0.) == 0.
                || failed
                || thermal_trip
                || c.fault.failed_drive_fraction == 1.
                || !active)
        {
            r.state = "stalled-no-starting-force".into();
            break;
        }
        if x > c.distance_m + c.berth_tolerance_m && brake_at.is_none() {
            r.state = "passed-destination-without-braking".into();
            break;
        }
    }
    if !detached && x >= d.windows_m[0][1] - 1e-8 {
        r.detached_reset_kinetic_energy_j += 0.5 * d.external_mass_kg * v * v;
        detached = true;
        event(&mut r, "external-mass-detached-energy-export", t, x, v);
    }
    if r.state == "time-budget" && t < c.max_time_s - 1e-8 {
        r.state = "step-budget".into();
    }
    r.final_position_m = x;
    r.final_speed_m_s = v;
    r.elapsed_s = t;
    r.berth_error_m = x - c.distance_m;
    let is_fault = c.fault.failed_drive_fraction > 0. || failed || emergency_seen || thermal_trip;
    r.standstill_brake_margin_n = brake_command - gravity.abs();
    r.standstill_holding = r.state == "stopped" && r.standstill_brake_margin_n >= -1e-8;
    r.normal_numerical_arrival = !is_fault
        && r.state == "stopped"
        && r.standstill_holding
        && r.maximum_speed_m_s <= c.speed_cap_m_s + 1e-7
        && r.berth_error_m.abs() <= c.berth_tolerance_m;
    r.fault_stop_in_route = is_fault
        && r.state == "stopped"
        && r.standstill_holding
        && x >= 0.
        && x <= c.distance_m + c.berth_tolerance_m;
    r.final_kinetic_energy_j = 0.5 * (m0 + if !detached { d.external_mass_kg } else { 0. }) * v * v;
    r.energy_residual_j = r.traction_work_j + r.grade_work_j
        - r.resistance_work_j
        - r.external_resistance_work_j
        - r.brake_heat_j
        - r.detached_reset_kinetic_energy_j
        - r.final_kinetic_energy_j;
    if r.energy_residual_j.abs() > 1e-6 * r.traction_work_j.abs().max(r.grade_work_j.abs()).max(1.)
    {
        r.state = "numerical-energy-held".into();
        r.hold_reason =
            Some("Mechanical energy residual exceeds1e-6relative research screen".into());
        r.normal_numerical_arrival = false;
        r.fault_stop_in_route = false;
    }
    if c.thermal
        .as_ref()
        .is_some_and(|q| r.maximum_temperature_c.unwrap_or(q.initial_c) > q.maximum_c)
    {
        r.normal_numerical_arrival = false;
        r.fault_stop_in_route = false;
        r.state = "thermal-envelope-exceeded".into();
    }
    r.journey_plus_dwell_s = t + c.dwell_s;
    r.headway_minus_journey_plus_dwell_s = c.headway_s - r.journey_plus_dwell_s;
    r.auxiliary_energy_j = c.auxiliary_power_w * r.journey_plus_dwell_s;
    if let (Some(q), Some(model)) = (temp, c.thermal.as_ref()) {
        temp = Some(temperature(q, c.dwell_s, 0., model));
        r.maximum_temperature_c = Some(r.maximum_temperature_c.unwrap().max(temp.unwrap()));
    }
    r.final_temperature_c = temp;
    if c.thermal
        .as_ref()
        .is_some_and(|q| r.maximum_temperature_c.unwrap_or(q.initial_c) > q.maximum_c)
    {
        r.normal_numerical_arrival = false;
        r.fault_stop_in_route = false;
        r.state = "thermal-envelope-exceeded".into();
    }
    if d.external_mass_kg > 0. {
        r.limitations.push("External mass is one initially engaged lump with explicit resistance; detached kinetic energy exported for reset, rope elasticity/rotors/return cycle and engagement dynamics unresolved".into());
    }
    Ok(r)
}
pub fn execute(q: Request) -> Result<BatchResult, String> {
    if q.schema != REQUEST_SCHEMA || q.cases.is_empty() || q.cases.len() > 256 {
        return Err("Explicit schema and1..256cases required".into());
    }
    let mut ids = HashSet::new();
    let mut rows = vec![];
    for c in q.cases {
        if !ids.insert(c.id.clone()) {
            return Err("Duplicate case ID".into());
        }
        rows.push(evaluate(&c)?);
    }
    Ok(BatchResult {
        schema: "osr-journey-result/1",
        cases: rows,
    })
}
