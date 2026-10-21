//! Bounded offline station-LSM demand and phase study. No PWM or physical I/O.
//!
//! The scalar force/current and voltage screens are declared hypotheses. They
//! omit saturation, dq cross-coupling, magnetic normal-force interactions and
//! commutation across differently indexed cars. External reservation assertions
//! do not establish a functioning receiver or independent emergency brake.

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct StationParams {
    pub configuration: [u8; 32],
    pub zone_id: u32,
    pub zone_start_mm: i64,
    pub zone_end_mm: i64,
    pub train_envelope_mm: u32,
    pub pole_pitch_um: u32,
    pub maximum_age_ns: u64,
    pub maximum_tick_ns: u64,
    pub maximum_phase_uncertainty_mdeg: u32,
    pub force_density_n_per_envelope_m: f64,
    pub force_constant_n_per_a: f64,
    pub resistance_ohm: f64,
    pub inductance_h: f64,
    pub flux_linkage_wb: f64,
    pub maximum_current_a: f64,
    pub maximum_phase_voltage_v: f64,
    pub maximum_copper_loss_w: f64,
}
impl StationParams {
    pub fn valid(self) -> bool {
        // Equivalent SI circuit: F = K i and e = K v must transfer the same
        // air-gap power. A measured three-phase map is still required.
        let back_emf_constant = self.flux_linkage_wb * core::f64::consts::TAU
            / (2. * f64::from(self.pole_pitch_um) * 1e-6);
        self.configuration != [0; 32]
            && self.zone_id > 0
            && self.zone_start_mm.unsigned_abs() <= 100_000_000
            && self.zone_end_mm.unsigned_abs() <= 100_000_000
            && self.zone_end_mm > self.zone_start_mm
            && (1..=1_000_000).contains(&self.pole_pitch_um)
            && (1..=1_000_000).contains(&self.train_envelope_mm)
            && (1..=1_000_000).contains(&self.maximum_age_ns)
            && (1..=100_000_000).contains(&self.maximum_tick_ns)
            && (1..=30_000).contains(&self.maximum_phase_uncertainty_mdeg)
            && [
                self.force_density_n_per_envelope_m,
                self.force_constant_n_per_a,
                self.resistance_ohm,
                self.inductance_h,
                self.flux_linkage_wb,
                self.maximum_current_a,
                self.maximum_phase_voltage_v,
                self.maximum_copper_loss_w,
            ]
            .iter()
            .all(|v| v.is_finite() && *v >= 1e-9 && *v <= 1e9)
            && (self.force_constant_n_per_a - back_emf_constant).abs()
                <= self.force_constant_n_per_a * 1e-9
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StationMode {
    Launch,
    Coast,
    Receive,
    Secured,
    /// Low-speed positioning within 2 m of the declared berth datum.
    Berth,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct StationFrame {
    pub configuration: [u8; 32],
    pub zone_id: u32,
    pub sequence: u64,
    pub observed_ns: u64,
    /// Consist-front datum; magnetic phase offset is relative to that datum.
    pub position_mm: i64,
    pub velocity_mmps: i32,
    pub position_uncertainty_um: u32,
    pub timestamp_uncertainty_ns: u32,
    pub phase_offset_mdeg: i32,
    /// Actual magnetic-band overlap, externally calculated; must not exceed
    /// the independently bounded whole-consist envelope overlap.
    pub overlap_mm: u32,
    pub force_demand_n: f64,
    pub mode: StationMode,
    pub launch_committed: bool,
    pub arrival_resources_protected: bool,
    pub receiver_healthy: bool,
    pub sensors_healthy: bool,
    pub drive_healthy: bool,
    pub brake_resistor_ready: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StationFault {
    Parameters,
    ClockOrReplay,
    StalePhase,
    Identity,
    Sensors,
    Authority,
    Receiver,
    Direction,
    Overlap,
    Current,
    Voltage,
    Thermal,
}

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct StationState {
    pub last_now_ns: Option<u64>,
    pub last_sequence: Option<u64>,
    pub last_observed_ns: Option<u64>,
    pub last_current_a: f64,
    pub latched_fault: Option<StationFault>,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct StationOutput {
    pub state: StationState,
    pub electrical_phase_mdeg: Option<u32>,
    pub phase_uncertainty_mdeg: Option<u32>,
    pub study_current_a: f64,
    pub study_force_n: f64,
    pub study_voltage_bound_v: f64,
    pub study_copper_loss_w: f64,
    pub study_command_feasible: bool,
    pub independent_recovery_required: bool,
    pub onboard_support_shutdown_requested: bool,
    pub physical_output_authorised: bool,
}

pub fn evaluate_station(
    previous: StationState,
    frame: StationFrame,
    now_ns: u64,
    p: StationParams,
) -> StationOutput {
    let temporal = now_ns > 0
        && previous.last_now_ns.is_none_or(|v| now_ns > v)
        && frame.sequence > 0
        && previous.last_sequence.is_none_or(|v| frame.sequence > v)
        && previous
            .last_observed_ns
            .is_none_or(|v| frame.observed_ns > v)
        && frame.observed_ns <= now_ns;
    let age = now_ns.checked_sub(frame.observed_ns);
    let mut fault = if !p.valid() {
        Some(StationFault::Parameters)
    } else if !temporal {
        Some(StationFault::ClockOrReplay)
    } else if age.is_none_or(|v| v > p.maximum_age_ns)
        || previous
            .last_now_ns
            .is_some_and(|v| now_ns - v > p.maximum_tick_ns)
    {
        Some(StationFault::StalePhase)
    } else if frame.configuration != p.configuration || frame.zone_id != p.zone_id {
        Some(StationFault::Identity)
    } else if !frame.sensors_healthy
        || frame.position_mm.unsigned_abs() > 100_000_000
        || frame.velocity_mmps.unsigned_abs() > 100_000
        || !frame.force_demand_n.is_finite()
        || frame.force_demand_n.abs() > 1e9
        || frame.phase_offset_mdeg.unsigned_abs() > 360_000
        || !previous.last_current_a.is_finite()
    {
        Some(StationFault::Sensors)
    } else if !frame.launch_committed || !frame.arrival_resources_protected {
        Some(StationFault::Authority)
    } else if !frame.receiver_healthy
        || !frame.drive_healthy
        || (frame.mode == StationMode::Receive && !frame.brake_resistor_ready)
    {
        Some(StationFault::Receiver)
    } else {
        None
    };
    let mut phase = None;
    let mut uncertainty = None;
    let mut current = 0.;
    let mut force = 0.;
    let mut voltage = 0.;
    let mut loss = 0.;
    if fault.is_none() {
        let wavelength_um = 2 * u64::from(p.pole_pitch_um);
        let predicted_um = frame.position_mm * 1000
            + i64::from(frame.velocity_mmps) * (age.unwrap_or(0) as i64) / 1_000_000;
        let relative_um = predicted_um - p.zone_start_mm * 1000;
        let raw_phase = relative_um.rem_euclid(wavelength_um as i64) * 360_000
            / wavelength_um as i64
            + i64::from(frame.phase_offset_mdeg);
        phase = Some(raw_phase.rem_euclid(360_000) as u32);
        let positional_uncertainty = u64::from(frame.position_uncertainty_um)
            + u64::from(frame.velocity_mmps.unsigned_abs())
                * u64::from(frame.timestamp_uncertainty_ns)
                / 1_000_000;
        let phase_error = positional_uncertainty
            .saturating_mul(360_000)
            .div_ceil(wavelength_um);
        uncertainty = Some(phase_error.min(u64::from(u32::MAX)) as u32);
        let envelope_overlap = (frame.position_mm.min(p.zone_end_mm)
            - (frame.position_mm - i64::from(p.train_envelope_mm)).max(p.zone_start_mm))
        .max(0) as u64;
        if phase_error > u64::from(p.maximum_phase_uncertainty_mdeg) {
            fault = Some(StationFault::StalePhase);
        } else if matches!(frame.mode, StationMode::Coast | StationMode::Secured)
            && frame.force_demand_n != 0.
            || frame.velocity_mmps < 0
            || (frame.mode == StationMode::Secured && frame.velocity_mmps != 0)
            || (frame.mode == StationMode::Launch && frame.force_demand_n < 0.)
            || (frame.mode == StationMode::Berth
                && (frame.velocity_mmps > 500
                    || frame.position_mm.unsigned_abs() > 2000
                    || frame.force_demand_n.abs() > 20000.))
            || (frame.mode == StationMode::Receive
                && (frame.force_demand_n > 0.
                    || (frame.velocity_mmps == 0 && frame.force_demand_n != 0.)))
        {
            fault = Some(StationFault::Direction);
        } else if frame.force_demand_n != 0.
            && (frame.overlap_mm == 0
                || u64::from(frame.overlap_mm) > (p.zone_end_mm - p.zone_start_mm) as u64
                || u64::from(frame.overlap_mm) > envelope_overlap
                || frame.force_demand_n.abs()
                    > p.force_density_n_per_envelope_m * f64::from(frame.overlap_mm) / 1000.)
        {
            fault = Some(StationFault::Overlap);
        }
        if fault.is_none() && !matches!(frame.mode, StationMode::Coast | StationMode::Secured) {
            current = frame.force_demand_n / p.force_constant_n_per_a;
            let dt = previous
                .last_now_ns
                .map_or(p.maximum_tick_ns as f64, |v| (now_ns - v) as f64)
                * 1e-9;
            let electrical_omega =
                f64::from(frame.velocity_mmps) / 1000. / (wavelength_um as f64 * 1e-6)
                    * core::f64::consts::TAU;
            voltage = (p.resistance_ohm * current).abs()
                + p.inductance_h * ((current - previous.last_current_a) / dt).abs()
                + (p.flux_linkage_wb * electrical_omega).abs();
            // Scalar phase-equivalent screen, not a complete three-phase loss map.
            loss = current * current * p.resistance_ohm;
            if current.abs() > p.maximum_current_a {
                fault = Some(StationFault::Current);
            } else if !voltage.is_finite() || voltage > p.maximum_phase_voltage_v {
                fault = Some(StationFault::Voltage);
            } else if !loss.is_finite() || loss > p.maximum_copper_loss_w {
                fault = Some(StationFault::Thermal);
            } else {
                force = frame.force_demand_n;
            }
        }
    }
    let mut state = previous;
    state.latched_fault = previous.latched_fault.or(fault);
    let feasible = state.latched_fault.is_none();
    if temporal {
        state.last_now_ns = Some(now_ns);
        state.last_sequence = Some(frame.sequence);
        state.last_observed_ns = Some(frame.observed_ns);
        state.last_current_a = if feasible { current } else { 0. };
    }
    StationOutput {
        state,
        electrical_phase_mdeg: phase,
        phase_uncertainty_mdeg: uncertainty,
        study_current_a: if feasible { current } else { 0. },
        study_force_n: if feasible { force } else { 0. },
        study_voltage_bound_v: voltage,
        study_copper_loss_w: loss,
        study_command_feasible: feasible,
        independent_recovery_required: !feasible && frame.launch_committed,
        onboard_support_shutdown_requested: false,
        physical_output_authorised: false,
    }
}
