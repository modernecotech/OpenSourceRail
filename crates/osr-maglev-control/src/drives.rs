//! Offline winding-current and three-phase commutation kernels. No GPIO/PWM I/O.
//!
//! SBC force allocation is distinct from these proposed local fast loops. R/L,
//! flux, gains, sensor independence and all timing limits need identification.
//! An unavailable support command means external local fallback, not zero lift.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Role {
    Support,
    Wayside,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mode {
    Support,
    Launch,
    Receive,
    Coast,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Fault {
    Parameters,
    Identity,
    Time,
    Sensor,
    Current,
    Temperature,
    Bus,
    Authority,
    Receiver,
    Phase,
    Mode,
    Latched,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {
    pub configuration: [u8; 32],
    pub role: Role,
    pub resistance_ohm: f64,
    pub inductance_h: f64,
    pub kp_v_per_a: f64,
    pub ki_v_per_a_s: f64,
    pub maximum_current_a: f64,
    pub current_disagreement_a: f64,
    pub maximum_temperature_c: f64,
    pub minimum_bus_v: f64,
    pub maximum_bus_v: f64,
    pub maximum_age_ns: u64,
    pub maximum_tick_ns: u64,
    pub maximum_phase_error_mdeg: u32,
}
impl Params {
    pub fn valid(self) -> bool {
        self.configuration != [0; 32]
            && [
                self.resistance_ohm,
                self.inductance_h,
                self.kp_v_per_a,
                self.ki_v_per_a_s,
                self.maximum_current_a,
                self.current_disagreement_a,
                self.maximum_temperature_c,
                self.minimum_bus_v,
                self.maximum_bus_v,
            ]
            .iter()
            .all(|v| v.is_finite() && *v > 0. && *v <= 1e7)
            && self.maximum_bus_v > self.minimum_bus_v
            && self.current_disagreement_a < self.maximum_current_a
            && (1..=1_000_000).contains(&self.maximum_age_ns)
            && (1..=1_000_000).contains(&self.maximum_tick_ns)
            && (1..=30000).contains(&self.maximum_phase_error_mdeg)
    }
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Frame {
    pub configuration: [u8; 32],
    pub sequence: u64,
    pub observed_ns: u64,
    /// Support uses channel 0; wayside uses all three phase-current channels.
    pub measured_a: [f64; 3],
    pub independent_measured_a: [f64; 3],
    pub bus_v: f64,
    pub winding_temperature_c: f64,
    pub sensors_healthy: bool,
    pub drive_healthy: bool,
    pub authority_protected: bool,
    pub receiver_ready: bool,
    pub resistor_ready: bool,
    pub launch_committed: bool,
    pub moving: bool,
    pub stopped_and_secured: bool,
    pub reset_requested: bool,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Demand {
    pub mode: Mode,
    /// Bipolar support current or d-axis current. Wayside d demand is zero here.
    pub d_a: f64,
    pub q_a: f64,
    /// Supplied by the separately configured station position/phase evaluator.
    pub electrical_phase_mdeg: u32,
    /// Whole worst-case phase budget, including mechanical indexing and time.
    pub phase_error_mdeg: u32,
    pub electrical_speed_rad_s: f64,
    pub flux_linkage_wb: f64,
}
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct State {
    pub last_now_ns: Option<u64>,
    pub last_observed_ns: Option<u64>,
    pub last_sequence: Option<u64>,
    pub integral_v: [f64; 2],
    pub fault: Option<Fault>,
}
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Output {
    pub state: State,
    /// Average model bridge duties, never hardware register values.
    pub study_duties: Option<[f64; 3]>,
    pub study_dq_voltage_v: [f64; 2],
    pub measured_dq_a: [f64; 2],
    pub voltage_limited: bool,
    pub local_support_fallback_required: bool,
    pub independent_stopping_required: bool,
    pub onboard_support_shutdown_requested: bool,
    pub physical_output_authorised: bool,
}

/// Bounded polynomial trig; tests compare an independent standard-library oracle.
/// Reduction and degree-15/14 polynomials have <1e-9 absolute error on [0,2pi].
pub fn sin_cos_mdeg(angle: u32) -> (f64, f64) {
    fn sin(x: f64) -> f64 {
        let mut a = x;
        if a > core::f64::consts::PI {
            a -= core::f64::consts::TAU;
        }
        if a > core::f64::consts::FRAC_PI_2 {
            a = core::f64::consts::PI - a;
        }
        if a < -core::f64::consts::FRAC_PI_2 {
            a = -core::f64::consts::PI - a;
        }
        let z = a * a;
        a * (1.
            + z * (-1. / 6.
                + z * (1. / 120.
                    + z * (-1. / 5040.
                        + z * (1. / 362880.
                            + z * (-1. / 39916800.
                                + z * (1. / 6227020800. + z * (-1. / 1307674368000.))))))))
    }
    let a = f64::from(angle % 360000) * core::f64::consts::PI / 180000.;
    (
        sin(a),
        sin((a + core::f64::consts::FRAC_PI_2) % core::f64::consts::TAU),
    )
}
pub fn abc_to_dq(abc: [f64; 3], phase: u32) -> [f64; 2] {
    let alpha = (2. * abc[0] - abc[1] - abc[2]) / 3.;
    let beta = (abc[1] - abc[2]) / 1.7320508075688772;
    let (s, c) = sin_cos_mdeg(phase);
    [alpha * c + beta * s, -alpha * s + beta * c]
}
pub fn dq_to_abc(dq: [f64; 2], phase: u32) -> [f64; 3] {
    let (s, c) = sin_cos_mdeg(phase);
    let a = dq[0] * c - dq[1] * s;
    let b = dq[0] * s + dq[1] * c;
    [
        a,
        -0.5 * a + 0.8660254037844386 * b,
        -0.5 * a - 0.8660254037844386 * b,
    ]
}

/// Overflow-resistant Euclidean norm for the finite bounded controller values.
/// Six Newton steps use a square-root argument in [1,2]; no libm or heap.
pub fn vector_magnitude(v: [f64; 2]) -> f64 {
    let hi = v[0].abs().max(v[1].abs());
    if hi == 0. {
        return 0.;
    }
    let ratio = v[0].abs().min(v[1].abs()) / hi;
    let square = 1. + ratio * ratio;
    let mut root = 1.5;
    for _ in 0..6 {
        root = 0.5 * (root + square / root);
    }
    hi * root
}

pub fn evaluate(previous: State, f: Frame, d: Demand, now: u64, p: Params) -> Output {
    let temporal = now > 0
        && f.observed_ns > 0
        && f.sequence > 0
        && f.observed_ns <= now
        && previous.last_now_ns.is_none_or(|v| now > v)
        && previous.last_observed_ns.is_none_or(|v| f.observed_ns > v)
        && previous.last_sequence.is_none_or(|v| f.sequence > v);
    let channels = if p.role == Role::Support { 1 } else { 3 };
    let mut fault = if !p.valid()
        || !previous
            .integral_v
            .iter()
            .all(|v| v.is_finite() && v.abs() <= p.maximum_bus_v)
    {
        Some(Fault::Parameters)
    } else if f.configuration != p.configuration {
        Some(Fault::Identity)
    } else if !temporal
        || now - f.observed_ns > p.maximum_age_ns
        || previous
            .last_now_ns
            .is_some_and(|v| now - v > p.maximum_tick_ns)
    {
        Some(Fault::Time)
    } else if !f.sensors_healthy
        || !f.drive_healthy
        || (0..channels).any(|i| {
            !f.measured_a[i].is_finite()
                || !f.independent_measured_a[i].is_finite()
                || (f.measured_a[i] - f.independent_measured_a[i]).abs() > p.current_disagreement_a
        })
        || ![d.d_a, d.q_a, d.electrical_speed_rad_s, d.flux_linkage_wb]
            .iter()
            .all(|v| v.is_finite() && v.abs() <= 1e7)
        || (p.role == Role::Wayside
            && f.measured_a.iter().sum::<f64>().abs() > p.current_disagreement_a)
    {
        Some(Fault::Sensor)
    } else if (0..channels).any(|i| {
        f.measured_a[i].abs() > p.maximum_current_a
            || f.independent_measured_a[i].abs() > p.maximum_current_a
    }) || d.d_a.abs() > p.maximum_current_a
        || d.q_a.abs() > p.maximum_current_a
    {
        Some(Fault::Current)
    } else if !f.winding_temperature_c.is_finite()
        || f.winding_temperature_c < -50.
        || f.winding_temperature_c > p.maximum_temperature_c
    {
        Some(Fault::Temperature)
    } else if !f.bus_v.is_finite() || f.bus_v < p.minimum_bus_v || f.bus_v > p.maximum_bus_v {
        Some(Fault::Bus)
    } else if (p.role == Role::Support && (d.mode != Mode::Support || d.q_a != 0.))
        || (p.role == Role::Wayside
            && (d.mode == Mode::Support
                || d.d_a != 0.
                || d.flux_linkage_wb < 0.
                || (d.mode == Mode::Launch && d.q_a < 0.)
                || (d.mode == Mode::Receive && d.q_a > 0.)
                || (d.mode == Mode::Coast && d.q_a != 0.)))
    {
        Some(Fault::Mode)
    } else if p.role == Role::Wayside && (!f.authority_protected || !f.launch_committed) {
        Some(Fault::Authority)
    } else if p.role == Role::Wayside
        && (!f.receiver_ready || (d.mode == Mode::Receive && !f.resistor_ready))
    {
        Some(Fault::Receiver)
    } else if p.role == Role::Wayside
        && (d.electrical_phase_mdeg >= 360000 || d.phase_error_mdeg > p.maximum_phase_error_mdeg)
    {
        Some(Fault::Phase)
    } else {
        None
    };
    let mut state = previous;
    if temporal {
        state.last_now_ns = Some(now);
        state.last_observed_ns = Some(f.observed_ns);
        state.last_sequence = Some(f.sequence);
    }
    state.fault = previous.fault.or(fault);
    if f.reset_requested
        && f.stopped_and_secured
        && !f.moving
        && d.d_a == 0.
        && d.q_a == 0.
        && fault.is_none()
    {
        state.fault = None;
        state.integral_v = [0.; 2];
    }
    if fault.is_none() && state.fault.is_some() {
        fault = Some(Fault::Latched);
    }
    let mut out = Output {
        state,
        study_duties: None,
        study_dq_voltage_v: [0.; 2],
        measured_dq_a: [0.; 2],
        voltage_limited: false,
        local_support_fallback_required: false,
        independent_stopping_required: false,
        onboard_support_shutdown_requested: false,
        physical_output_authorised: false,
    };
    if fault.is_some() {
        out.local_support_fallback_required = p.role == Role::Support;
        out.independent_stopping_required =
            p.role == Role::Wayside && f.launch_committed && f.moving;
        return out;
    }
    if d.mode == Mode::Coast {
        out.state.integral_v = [0.; 2];
        return out;
    }
    let current = if p.role == Role::Support {
        [f.measured_a[0], 0.]
    } else {
        abc_to_dq(f.measured_a, d.electrical_phase_mdeg)
    };
    out.measured_dq_a = current;
    let target = [d.d_a, d.q_a];
    let dt = previous
        .last_observed_ns
        .map_or(p.maximum_tick_ns, |v| f.observed_ns - v) as f64
        * 1e-9;
    let limit = if p.role == Role::Support {
        0.9 * f.bus_v
    } else {
        f.bus_v / 1.7320508075688772 * 0.95
    };
    let feed = if p.role == Role::Support {
        [p.resistance_ohm * target[0], 0.]
    } else {
        [
            p.resistance_ohm * target[0] - d.electrical_speed_rad_s * p.inductance_h * current[1],
            p.resistance_ohm * target[1]
                + d.electrical_speed_rad_s * (p.inductance_h * current[0] + d.flux_linkage_wb),
        ]
    };
    let errors = [target[0] - current[0], target[1] - current[1]];
    let mut voltage = [0.; 2];
    let axes = if p.role == Role::Support { 1 } else { 2 };
    for i in 0..axes {
        let trial = (state.integral_v[i] + p.ki_v_per_a_s * errors[i] * dt).clamp(-limit, limit);
        voltage[i] = feed[i] + p.kp_v_per_a * errors[i] + trial;
    }
    // Use the same phase-peak voltage circle as the winding construction study.
    // Bounded normalized Newton steps avoid a libm dependency in no_std.
    let norm = if axes == 1 {
        voltage[0].abs()
    } else {
        vector_magnitude(voltage)
    };
    let scale = if norm > limit { limit / norm } else { 1. };
    out.voltage_limited = scale < 1.;
    for i in 0..axes {
        let trial = (state.integral_v[i] + p.ki_v_per_a_s * errors[i] * dt).clamp(-limit, limit);
        // Back-calculation is bounded and uses the actually available vector.
        out.state.integral_v[i] = (trial + (scale - 1.) * voltage[i]).clamp(-limit, limit);
        voltage[i] *= scale;
    }
    out.study_dq_voltage_v = voltage;
    out.study_duties = Some(if axes == 1 {
        [
            0.5 + 0.5 * voltage[0] / f.bus_v,
            0.5 - 0.5 * voltage[0] / f.bus_v,
            0.5,
        ]
    } else {
        let abc = dq_to_abc(voltage, d.electrical_phase_mdeg);
        let hi = abc[0].max(abc[1]).max(abc[2]);
        let lo = abc[0].min(abc[1]).min(abc[2]);
        let centre = -(hi + lo) / 2.;
        abc.map(|v| (0.5 + (v + centre) / f.bus_v).clamp(0., 1.))
    });
    out
}
