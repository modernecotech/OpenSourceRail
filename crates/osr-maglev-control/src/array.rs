//! Hypothetical 24-station rigid-body force study, without current or PWM output.
//!
//! Coordinates: x forward, y left, z up, origin at assumed car centre of mass.
//! Vertical force is positive upward attraction; lateral force is signed left.
//! Moments use r cross F (right hand rule). Longitudinal force is unactuated.
//! Independent vertical/lateral force envelopes are an idealisation, not evidence
//! that a shared magnetic circuit can provide them simultaneously.

pub const MODULES: usize = 24;
const CHANNELS: usize = MODULES * 2;

#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct Wrench {
    pub force_n: [f64; 3],
    pub moment_nm: [f64; 3],
}

#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct Forces {
    pub upward_n: f64,
    pub leftward_n: f64,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Station {
    pub position_m: [f64; 3],
    pub minimum_upward_n: f64,
    pub maximum_upward_n: f64,
    pub maximum_lateral_n: f64,
    /// Symmetric force slew envelope in N/s, separately applied to both channels.
    pub maximum_slew_n_s: f64,
}

/// Twelve paired stations spanning 12 m by 1.76 m. This is a declared geometric
/// hypothesis within the 17 m car, not dimensioned magnetic hardware placement.
pub fn illustrative_geometry() -> [Station; MODULES] {
    core::array::from_fn(|i| Station {
        position_m: [
            -5.5 + (i / 2) as f64,
            if i % 2 == 0 { -0.88 } else { 0.88 },
            0.0,
        ],
        minimum_upward_n: 0.0,
        maximum_upward_n: 20_000.0,
        maximum_lateral_n: 4000.0,
        maximum_slew_n_s: 2_000_000.0,
    })
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Availability {
    Available,
    /// Specified residual magnetic force when a channel/station fails. Zero is
    /// only an ideal disconnected actuator hypothesis; PM force need not vanish.
    Failed {
        residual: Forces,
    },
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Allocation {
    pub forces: [Forces; MODULES],
    pub achieved: Wrench,
    /// Requested minus achieved, including unsupported longitudinal demand.
    pub residual: Wrench,
    pub within_tolerance: bool,
    pub at_limit: bool,
    pub valid: bool,
}

pub fn resultant(stations: &[Station; MODULES], forces: &[Forces; MODULES]) -> Wrench {
    let mut w = Wrench::default();
    for (station, force) in stations.iter().zip(forces) {
        let [x, y, z] = station.position_m;
        w.force_n[1] += force.leftward_n;
        w.force_n[2] += force.upward_n;
        w.moment_nm[0] += y * force.upward_n - z * force.leftward_n;
        w.moment_nm[1] -= x * force.upward_n;
        w.moment_nm[2] += x * force.leftward_n;
    }
    w
}

fn bounded(v: f64) -> bool {
    v.is_finite() && v.abs() <= 1.0e9
}
fn valid_station(s: &Station) -> bool {
    s.position_m.iter().all(|v| bounded(*v) && v.abs() <= 100.0)
        && [
            s.minimum_upward_n,
            s.maximum_upward_n,
            s.maximum_lateral_n,
            s.maximum_slew_n_s,
        ]
        .iter()
        .all(|v| bounded(*v))
        && s.minimum_upward_n >= 0.0
        && s.maximum_upward_n > s.minimum_upward_n
        && s.maximum_lateral_n > 0.0
        && s.maximum_slew_n_s > 0.0
}
fn valid_wrench(w: Wrench) -> bool {
    w.force_n
        .iter()
        .chain(w.moment_nm.iter())
        .all(|v| bounded(*v))
}

/// Bounded least-squares allocation of five controlled wrench components. Fixed
/// 256 coordinate sweeps bound work; residuals, not solver completion, determine
/// feasibility. Moment rows are scaled by 6 m to state the objective's units.
/// History-based slew bounds apply only with a supplied previous force frame.
/// This numerical iteration count is not a demonstrated real-time deadline.
pub fn allocate(
    stations: &[Station; MODULES],
    availability: &[Availability; MODULES],
    requested: Wrench,
    previous: Option<&[Forces; MODULES]>,
    dt_s: f64,
    force_tolerance_n: f64,
    moment_tolerance_nm: f64,
) -> Allocation {
    let mut out = Allocation {
        forces: [Forces::default(); MODULES],
        achieved: Wrench::default(),
        residual: requested,
        within_tolerance: false,
        at_limit: false,
        valid: false,
    };
    if !stations.iter().all(valid_station)
        || !valid_wrench(requested)
        || previous.is_some_and(|forces| {
            forces
                .iter()
                .any(|f| !bounded(f.upward_n) || !bounded(f.leftward_n))
        })
        || !dt_s.is_finite()
        || dt_s <= 0.0
        || dt_s > 1.0
        || !bounded(force_tolerance_n)
        || force_tolerance_n <= 0.0
        || !bounded(moment_tolerance_nm)
        || moment_tolerance_nm <= 0.0
    {
        return out;
    }
    let mut columns = [[0.0; 5]; CHANNELS];
    let mut lower = [0.0; CHANNELS];
    let mut upper = [0.0; CHANNELS];
    let mut values = [0.0; CHANNELS];
    for (i, s) in stations.iter().enumerate() {
        let [x, y, z] = s.position_m;
        columns[2 * i] = [0.0, 1.0, y / 6.0, -x / 6.0, 0.0];
        columns[2 * i + 1] = [1.0, 0.0, -z / 6.0, 0.0, x / 6.0];
        lower[2 * i] = s.minimum_upward_n;
        upper[2 * i] = s.maximum_upward_n;
        lower[2 * i + 1] = -s.maximum_lateral_n;
        upper[2 * i + 1] = s.maximum_lateral_n;
        if let Availability::Failed { residual } = availability[i] {
            if !bounded(residual.upward_n) || !bounded(residual.leftward_n) {
                return out;
            }
            lower[2 * i] = residual.upward_n;
            upper[2 * i] = residual.upward_n;
            lower[2 * i + 1] = residual.leftward_n;
            upper[2 * i + 1] = residual.leftward_n;
        } else if let Some(old) = previous {
            for (j, v) in [(2 * i, old[i].upward_n), (2 * i + 1, old[i].leftward_n)] {
                if !bounded(v) {
                    return out;
                }
                lower[j] = lower[j].max(v - s.maximum_slew_n_s * dt_s);
                upper[j] = upper[j].min(v + s.maximum_slew_n_s * dt_s);
                if lower[j] > upper[j] {
                    return out;
                }
            }
        }
        // Rebalance toward uniform loading each frame; a restored channel must
        // not remain unused merely because an old feasible solution exists.
        values[2 * i] = (requested.force_n[2] / MODULES as f64).clamp(lower[2 * i], upper[2 * i]);
        values[2 * i + 1] =
            (requested.force_n[1] / MODULES as f64).clamp(lower[2 * i + 1], upper[2 * i + 1]);
    }
    let mut residual = [
        requested.force_n[1],
        requested.force_n[2],
        requested.moment_nm[0] / 6.0,
        requested.moment_nm[1] / 6.0,
        requested.moment_nm[2] / 6.0,
    ];
    for (column, value) in columns.iter().zip(values) {
        for k in 0..5 {
            residual[k] -= column[k] * value;
        }
    }
    for _ in 0..256 {
        for j in 0..CHANNELS {
            let c = columns[j];
            let norm: f64 = c.iter().map(|v| v * v).sum();
            let projection: f64 = c.iter().zip(residual).map(|(a, b)| a * b).sum();
            let next = (values[j] + projection / norm).clamp(lower[j], upper[j]);
            let delta = next - values[j];
            for k in 0..5 {
                residual[k] -= c[k] * delta;
            }
            values[j] = next;
        }
    }
    for i in 0..MODULES {
        out.forces[i] = Forces {
            upward_n: values[2 * i],
            leftward_n: values[2 * i + 1],
        };
    }
    out.achieved = resultant(stations, &out.forces);
    for k in 0..3 {
        out.residual.force_n[k] = requested.force_n[k] - out.achieved.force_n[k];
        out.residual.moment_nm[k] = requested.moment_nm[k] - out.achieved.moment_nm[k];
    }
    out.within_tolerance = out
        .residual
        .force_n
        .iter()
        .all(|v| v.abs() <= force_tolerance_n)
        && out
            .residual
            .moment_nm
            .iter()
            .all(|v| v.abs() <= moment_tolerance_nm);
    out.at_limit = (0..CHANNELS)
        .any(|i| (values[i] - lower[i]).abs() < 1e-6 || (values[i] - upper[i]).abs() < 1e-6);
    out.valid = true;
    out
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Sample {
    /// Two hypothetical sensing channels; their independence is not asserted.
    pub gap_m: [f64; 2],
    pub lateral_m: [f64; 2],
    pub healthy: bool,
}
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Frame {
    pub issued_ns: u64,
    pub sequence: u64,
    pub samples: [Sample; MODULES],
    pub availability: [Availability; MODULES],
    pub support_power_available: bool,
    pub traction_requested: bool,
    pub stop_requested: bool,
    pub stopped: bool,
    pub secured: bool,
    pub reset_requested: bool,
}
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ArrayParams {
    pub stations: [Station; MODULES],
    pub target_gap_m: f64,
    pub minimum_gap_m: f64,
    pub maximum_gap_m: f64,
    pub maximum_lateral_m: f64,
    pub sensor_disagreement_m: f64,
    pub maximum_age_ns: u64,
    pub maximum_tick_ns: u64,
    pub mass_kg: f64,
    pub gravity_m_s2: f64,
    /// Modes: downward displacement (m), roll (rad), pitch (rad), left
    /// displacement (m), yaw (rad). Gains are N/m or Nm/rad, and damping
    /// N.s/m or Nm.s/rad; the supplied example gains are synthetic.
    pub proportional: [f64; 5],
    pub damping: [f64; 5],
    pub force_tolerance_n: f64,
    pub moment_tolerance_nm: f64,
}
impl ArrayParams {
    pub fn valid(&self) -> bool {
        self.stations.iter().all(valid_station)
            && [
                self.target_gap_m,
                self.minimum_gap_m,
                self.maximum_gap_m,
                self.maximum_lateral_m,
                self.sensor_disagreement_m,
                self.mass_kg,
                self.gravity_m_s2,
                self.force_tolerance_n,
                self.moment_tolerance_nm,
            ]
            .iter()
            .all(|v| bounded(*v) && *v > 0.0)
            && self.minimum_gap_m < self.target_gap_m
            && self.target_gap_m < self.maximum_gap_m
            && self.maximum_tick_ns > 0
            && self.maximum_tick_ns <= 1_000_000_000
            && self.maximum_age_ns > 0
            && bounded(self.mass_kg * self.gravity_m_s2)
            && self
                .proportional
                .iter()
                .chain(self.damping.iter())
                .all(|v| bounded(*v) && *v >= 0.0)
    }
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ArrayFault {
    Parameters,
    ClockOrReplay,
    Deadline,
    Sensor,
    Geometry,
    SupportPower,
    Actuator,
    Allocation,
    Saturation,
}
#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct ArrayState {
    pub last_now_ns: Option<u64>,
    pub last_issued_ns: Option<u64>,
    pub last_sequence: Option<u64>,
    pub last_modes: Option<[f64; 5]>,
    pub last_forces: Option<[Forces; MODULES]>,
    pub latched_fault: Option<ArrayFault>,
    pub stop_latched: bool,
}
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ArraySupport {
    StudyForces,
    LocalFallbackRequired,
    Secured,
}
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ArrayOutput {
    pub state: ArrayState,
    pub modes: Option<[f64; 5]>,
    pub requested: Wrench,
    pub allocation: Option<Allocation>,
    pub support: ArraySupport,
    pub traction_permitted_in_study: bool,
    pub controlled_stop_required: bool,
    pub physical_output_authorised: bool,
}

fn solve<const N: usize>(mut a: [[f64; N]; N], mut b: [f64; N]) -> Option<[f64; N]> {
    for k in 0..N {
        let mut pivot = k;
        for j in k + 1..N {
            if a[j][k].abs() > a[pivot][k].abs() {
                pivot = j;
            }
        }
        if a[pivot][k].abs() < 1e-10 {
            return None;
        }
        a.swap(k, pivot);
        b.swap(k, pivot);
        let divisor = a[k][k];
        for value in a[k].iter_mut().skip(k) {
            *value /= divisor;
        }
        b[k] /= divisor;
        for i in 0..N {
            if i != k {
                let factor = a[i][k];
                let pivot_row = a[k];
                for (value, pivot_value) in a[i].iter_mut().zip(pivot_row).skip(k) {
                    *value -= factor * pivot_value;
                }
                b[i] -= factor * b[k];
            }
        }
    }
    if b.iter().all(|v| v.is_finite()) {
        Some(b)
    } else {
        None
    }
}
fn modes(frame: &Frame, p: &ArrayParams) -> Result<[f64; 5], ArrayFault> {
    let mut a = [[0.0; 3]; 3];
    let mut b = [0.0; 3];
    let mut c = [[0.0; 2]; 2];
    let mut d = [0.0; 2];
    for (s, sample) in p.stations.iter().zip(frame.samples) {
        if !sample.healthy
            || sample
                .gap_m
                .iter()
                .any(|v| !v.is_finite() || *v < p.minimum_gap_m || *v > p.maximum_gap_m)
            || sample
                .lateral_m
                .iter()
                .any(|v| !v.is_finite() || v.abs() > p.maximum_lateral_m)
            || (sample.gap_m[0] - sample.gap_m[1]).abs() > p.sensor_disagreement_m
            || (sample.lateral_m[0] - sample.lateral_m[1]).abs() > p.sensor_disagreement_m
        {
            return Err(ArrayFault::Sensor);
        }
        let [x, y, _z] = s.position_m;
        // Small-angle rigid body: gap = target + down - y*roll + x*pitch.
        let row = [1.0, -y, x];
        let gap = (sample.gap_m[0] + sample.gap_m[1]) * 0.5 - p.target_gap_m;
        for i in 0..3 {
            b[i] += row[i] * gap;
            for j in 0..3 {
                a[i][j] += row[i] * row[j];
            }
        }
        // Lateral = sway + x*yaw - z*roll; subtract roll after vertical fit.
        let lateral = (sample.lateral_m[0] + sample.lateral_m[1]) * 0.5;
        let row = [1.0, x];
        for i in 0..2 {
            d[i] += row[i] * lateral;
            for j in 0..2 {
                c[i][j] += row[i] * row[j];
            }
        }
    }
    let vertical = solve(a, b).ok_or(ArrayFault::Geometry)?;
    // Account for nonzero module height in the signed lateral measurement.
    for s in p.stations {
        d[0] += s.position_m[2] * vertical[1];
        d[1] += s.position_m[0] * s.position_m[2] * vertical[1];
    }
    let lateral = solve(c, d).ok_or(ArrayFault::Geometry)?;
    Ok([
        vertical[0],
        vertical[1],
        vertical[2],
        lateral[0],
        lateral[1],
    ])
}

/// Host-supplied monotonic time and sample sequences; no clock or I/O in the core.
/// Fresh support remains active during a traction stop or a latched prior fault.
/// A failed station triggers a stop even if remaining ideal forces can balance.
/// Missing sensing/power requests external local fallback rather than stale output.
pub fn evaluate_array(
    previous: ArrayState,
    frame: &Frame,
    now_ns: u64,
    p: &ArrayParams,
) -> ArrayOutput {
    let temporal = previous.last_now_ns.is_none_or(|t| now_ns > t)
        && previous.last_issued_ns.is_none_or(|t| frame.issued_ns > t)
        && previous.last_sequence.is_none_or(|s| frame.sequence > s)
        && frame.issued_ns <= now_ns;
    let fresh = now_ns
        .checked_sub(frame.issued_ns)
        .is_some_and(|age| age <= p.maximum_age_ns)
        && previous.last_now_ns.is_none_or(|t| {
            now_ns
                .checked_sub(t)
                .is_some_and(|d| d <= p.maximum_tick_ns)
        });
    let mut fault = if !p.valid() {
        Some(ArrayFault::Parameters)
    } else if !temporal {
        Some(ArrayFault::ClockOrReplay)
    } else if !fresh {
        Some(ArrayFault::Deadline)
    } else if !frame.support_power_available {
        Some(ArrayFault::SupportPower)
    } else {
        None
    };
    let mut measured = None;
    if fault.is_none() {
        match modes(frame, p) {
            Ok(m) => measured = Some(m),
            Err(f) => fault = Some(f),
        }
    }
    let mut demand = Wrench::default();
    let mut allocation = None;
    if let Some(m) = measured {
        let dt = previous
            .last_issued_ns
            .map_or(p.maximum_tick_ns as f64 * 1e-9, |t| {
                (frame.issued_ns - t) as f64 * 1e-9
            });
        let mut effort = [0.0; 5];
        for i in 0..5 {
            let velocity = previous.last_modes.map_or(0.0, |old| (m[i] - old[i]) / dt);
            effort[i] = p.proportional[i] * m[i] + p.damping[i] * velocity;
        }
        demand.force_n = [0.0, -effort[3], p.mass_kg * p.gravity_m_s2 + effort[0]];
        demand.moment_nm = [-effort[1], -effort[2], -effort[4]];
        let a = allocate(
            &p.stations,
            &frame.availability,
            demand,
            previous.last_forces.as_ref(),
            dt,
            p.force_tolerance_n,
            p.moment_tolerance_nm,
        );
        if !a.valid || !a.within_tolerance {
            fault = Some(ArrayFault::Allocation);
        } else if frame
            .availability
            .iter()
            .any(|v| matches!(v, Availability::Failed { .. }))
        {
            fault = Some(ArrayFault::Actuator);
        } else if a.at_limit {
            fault = Some(ArrayFault::Saturation);
        }
        allocation = Some(a);
    }
    let mut state = previous;
    state.latched_fault = previous.latched_fault.or(fault);
    state.stop_latched |= frame.stop_requested || fault.is_some();
    if frame.reset_requested && frame.stopped && frame.secured && fault.is_none() {
        state.latched_fault = None;
        state.stop_latched = frame.stop_requested;
    }
    // Even an infeasible allocation contains bounded fresh support commands;
    // invalid arithmetic, sensing or power requires external fallback instead.
    let usable = allocation.is_some_and(|a| a.valid);
    if temporal {
        state.last_now_ns = Some(now_ns);
        state.last_issued_ns = Some(frame.issued_ns);
        state.last_sequence = Some(frame.sequence);
        state.last_modes = measured;
        state.last_forces = allocation.filter(|a| a.valid).map(|a| a.forces);
    }
    let secured = frame.secured && frame.stopped;
    let stop = state.stop_latched || state.latched_fault.is_some();
    ArrayOutput {
        state,
        modes: measured,
        requested: demand,
        allocation,
        support: if secured {
            ArraySupport::Secured
        } else if usable {
            ArraySupport::StudyForces
        } else {
            ArraySupport::LocalFallbackRequired
        },
        traction_permitted_in_study: usable && !stop && !frame.secured && frame.traction_requested,
        controlled_stop_required: stop && !secured,
        physical_output_authorised: false,
    }
}
