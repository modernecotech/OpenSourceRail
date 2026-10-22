//! Provisional, allocation-free maglev controller for simulation and SBC replay.
//!
//! The original single-module current hypothesis and the separate 24-module
//! force-allocation/ideal-plant study use upward attraction and active guidance.
//! No measured magnetic map, physical current adapter, target timing or railway
//! acceptance is supplied. Commands are study outputs, never a hardware enable.
#![no_std]
#![forbid(unsafe_code)]

pub mod array;
pub mod drives;
pub mod egress;
pub mod ideal;
pub mod io;
pub mod station;

/// Example controller parameters: units are explicit and gains require plant identification.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Params {
    pub target_gap_um: u32,
    pub minimum_gap_um: u32,
    pub maximum_gap_um: u32,
    pub sensor_disagreement_um: u32,
    pub maximum_age_ns: u64,
    pub maximum_tick_ns: u64,
    pub bias_current_ma: i32,
    pub minimum_current_ma: i32,
    pub maximum_current_ma: i32,
    pub proportional_ma_per_um: u32,
    pub derivative_ma_per_um_s: u32,
}

impl Params {
    pub fn valid(self) -> bool {
        self.minimum_gap_um > 0
            && self.minimum_gap_um < self.target_gap_um
            && self.target_gap_um < self.maximum_gap_um
            && self.sensor_disagreement_um > 0
            && self.maximum_age_ns > 0
            && self.maximum_tick_ns > 0
            && self.minimum_current_ma <= self.bias_current_ma
            && self.bias_current_ma <= self.maximum_current_ma
            && self.minimum_current_ma < self.maximum_current_ma
    }
}

/// Two externally timestamped measurements. Their hardware independence is unproved.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Inputs {
    pub issued_ns: u64,
    pub sequence: u64,
    pub gap_a_um: u32,
    pub gap_b_um: u32,
    pub sensors_healthy: bool,
    pub drive_healthy: bool,
    pub support_power_available: bool,
    pub traction_requested: bool,
    pub stop_requested: bool,
    /// Externally verified capture/support and zero-speed conditions are separate inputs.
    pub secured: bool,
    pub stopped: bool,
    pub reset_requested: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Fault {
    InvalidParameters,
    ClockOrReplay,
    Deadline,
    Sensor,
    GapEnvelope,
    SupportPower,
    Drive,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Support {
    /// Hypothetical current setpoint; no physical actuation is implemented.
    StudyCurrentMa(i32),
    /// A separately engineered local fallback must take over; never hold stale PWM.
    LocalFallbackRequired,
    /// Physical support/capture is reported secure and the vehicle is stopped.
    Secured,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct State {
    pub last_now_ns: Option<u64>,
    pub last_issued_ns: Option<u64>,
    pub last_sequence: Option<u64>,
    pub last_gap_um: Option<u32>,
    pub latched_fault: Option<Fault>,
    pub stop_latched: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Output {
    pub state: State,
    pub support: Support,
    pub traction_permitted_in_study: bool,
    pub controlled_stop_required: bool,
    pub current_saturated: bool,
    pub physical_output_authorised: bool,
}

/// One deterministic study tick. Wall-clock/OS/I/O ownership remains with the host.
pub fn evaluate(previous: State, input: Inputs, now_ns: u64, params: Params) -> Output {
    let temporal = previous.last_now_ns.is_none_or(|v| now_ns > v)
        && previous.last_issued_ns.is_none_or(|v| input.issued_ns > v)
        && previous.last_sequence.is_none_or(|v| input.sequence > v)
        && input.issued_ns <= now_ns;
    let fresh = now_ns
        .checked_sub(input.issued_ns)
        .is_some_and(|v| v <= params.maximum_age_ns);
    let timely = previous.last_now_ns.is_none_or(|v| {
        now_ns
            .checked_sub(v)
            .is_some_and(|d| d > 0 && d <= params.maximum_tick_ns)
    });
    let sensors = input.sensors_healthy
        && input.gap_a_um.abs_diff(input.gap_b_um) <= params.sensor_disagreement_um;
    // Each sensor must lie inside the envelope; averaging cannot conceal contact.
    let gap_ok = [input.gap_a_um, input.gap_b_um]
        .iter()
        .all(|g| *g >= params.minimum_gap_um && *g <= params.maximum_gap_um);
    let fault = if !params.valid() {
        Some(Fault::InvalidParameters)
    } else if !temporal {
        Some(Fault::ClockOrReplay)
    } else if !fresh || !timely {
        Some(Fault::Deadline)
    } else if !sensors {
        Some(Fault::Sensor)
    } else if !gap_ok {
        Some(Fault::GapEnvelope)
    } else if !input.support_power_available {
        Some(Fault::SupportPower)
    } else if !input.drive_healthy {
        Some(Fault::Drive)
    } else {
        None
    };
    let gap = ((u64::from(input.gap_a_um) + u64::from(input.gap_b_um)) / 2) as u32;
    let mut state = previous;
    state.latched_fault = previous.latched_fault.or(fault);
    state.stop_latched |= input.stop_requested || fault.is_some();
    if input.reset_requested && input.stopped && input.secured && fault.is_none() {
        state.latched_fault = None;
        state.stop_latched = input.stop_requested;
    }
    let usable = fault.is_none();
    let mut saturated = false;
    let support = if input.secured && input.stopped {
        Support::Secured
    } else if usable {
        // Derivative uses measurement timestamps, never caller scheduling intervals.
        let velocity_um_s = match (previous.last_gap_um, previous.last_issued_ns) {
            (Some(old), Some(time)) => {
                (i128::from(gap) - i128::from(old)) * 1_000_000_000
                    / i128::from(input.issued_ns - time)
            }
            _ => 0,
        };
        let current = i128::from(params.bias_current_ma)
            + i128::from(params.proportional_ma_per_um)
                * (i128::from(gap) - i128::from(params.target_gap_um))
            + i128::from(params.derivative_ma_per_um_s) * velocity_um_s;
        let clamped = current.clamp(
            i128::from(params.minimum_current_ma),
            i128::from(params.maximum_current_ma),
        );
        saturated = current != clamped;
        Support::StudyCurrentMa(clamped as i32)
    } else {
        Support::LocalFallbackRequired
    };
    // Reject corrupt/replayed samples without poisoning the last good measurement.
    // Advance the host tick for monotonic calls so an old deadline cannot be reset.
    if temporal {
        state.last_now_ns = Some(now_ns);
        state.last_issued_ns = Some(input.issued_ns);
        state.last_sequence = Some(input.sequence);
        state.last_gap_um = if usable { Some(gap) } else { None };
    }
    // Saturation means the requested support correction is unavailable. Even in
    // this idealised study it cannot silently permit continued traction.
    state.stop_latched |= saturated;
    let stop = state.stop_latched || state.latched_fault.is_some();
    Output {
        state,
        support,
        traction_permitted_in_study: usable && !stop && !input.secured && input.traction_requested,
        controlled_stop_required: stop && !(input.stopped && input.secured),
        current_saturated: saturated,
        physical_output_authorised: false,
    }
}
