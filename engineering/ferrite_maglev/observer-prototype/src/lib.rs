//! Standalone offline research observer, without device or movement authority.
//!
//! Observations use the previous accepted virtual map/current frame. Identical-map
//! calibration, sensing, field age in real hardware and execution timing remain
//! unqualified. The C ABI passes complete bounded values; it takes no pointers.

pub const ABI_VERSION: u32 = 1;
pub const CARS: usize = 6;
pub const MODULES: usize = 24;
pub const MAX_GROUPS: usize = 200;
pub const STEP_NS: u64 = 1_000_000;
pub const SUPPORT_MAX_N: f64 = 20_000.0;
pub const MODULE_X_M: [f64; MODULES] = [
    -5.5, -5.5, -4.5, -4.5, -3.5, -3.5, -2.5, -2.5, -1.5, -1.5, -0.5, -0.5, 0.5, 0.5, 1.5, 1.5,
    2.5, 2.5, 3.5, 3.5, 4.5, 4.5, 5.5, 5.5,
];
pub const MODULE_Y_M: [f64; MODULES] = [
    -0.88, 0.88, -0.88, 0.88, -0.88, 0.88, -0.88, 0.88, -0.88, 0.88, -0.88, 0.88, -0.88, 0.88,
    -0.88, 0.88, -0.88, 0.88, -0.88, 0.88, -0.88, 0.88, -0.88, 0.88,
];

/// Stable refusal codes. A nonzero code returns no candidate support request and
/// leaves the supplied state unchanged. No status authorises physical output.
#[repr(u32)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Status {
    Ok = 0,
    InvalidConfiguration = 1,
    InvalidState = 2,
    Sequence = 3,
    Clock = 4,
    MissingSample = 5,
    UnexpectedStartupSample = 6,
    ConfigurationIdentity = 7,
    SampleSequence = 8,
    SampleAge = 9,
    GroupCount = 10,
    NonFinite = 11,
    NegativeFluxAmplitude = 12,
    Arithmetic = 13,
    SupportBounds = 14,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ObserverConfig {
    pub abi_version: u32,
    pub groups: u32,
    pub configuration_sha256: [u8; 32],
    pub wave_number_rad_per_m: f64,
    pub estimator_scale: f64,
    pub step_ns: u64,
}

impl Default for ObserverConfig {
    fn default() -> Self {
        Self {
            abi_version: 0,
            groups: 0,
            configuration_sha256: [0; 32],
            wave_number_rad_per_m: 0.0,
            estimator_scale: 0.0,
            step_ns: 0,
        }
    }
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct ObserverState {
    pub initialized: u32,
    /// Must be zero, reserved for an incompatible future ABI.
    pub reserved: u32,
    pub last_sequence: u64,
    pub last_timestamp_ns: u64,
    pub config: ObserverConfig,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct GroupObservation {
    pub flux_linkage_wb: [f64; CARS],
    pub phase_rad: [f64; CARS],
    pub normal_position_m: [f64; CARS],
    pub current_alpha_a: f64,
    pub current_beta_a: f64,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ObserverFrame {
    pub sequence: u64,
    pub timestamp_ns: u64,
    /// Exactly 0 (startup only) or 1 (previous accepted frame required).
    pub sample_present: u32,
    pub sample_groups: u32,
    pub sample_sequence: u64,
    pub sample_timestamp_ns: u64,
    pub sample_configuration_sha256: [u8; 32],
    pub speed_m_s: [f64; CARS],
    pub centres_m: [f64; CARS],
    pub groups: [GroupObservation; MAX_GROUPS],
    pub desired_support_n: [[f64; MODULES]; CARS],
}

impl Default for ObserverFrame {
    fn default() -> Self {
        Self {
            sequence: 0,
            timestamp_ns: 0,
            sample_present: 0,
            sample_groups: 0,
            sample_sequence: 0,
            sample_timestamp_ns: 0,
            sample_configuration_sha256: [0; 32],
            speed_m_s: [0.0; CARS],
            centres_m: [0.0; CARS],
            groups: [GroupObservation::default(); MAX_GROUPS],
            desired_support_n: [[0.0; MODULES]; CARS],
        }
    }
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct ObserverInput {
    pub config: ObserverConfig,
    pub state: ObserverState,
    pub frame: ObserverFrame,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct ObserverOutput {
    pub status: u32,
    /// Always zero, including success: outputs are offline numerical candidates.
    pub physical_output_authorised: u32,
    pub next_state: ObserverState,
    pub raw_wrench_up_roll_pitch: [[f64; 3]; CARS],
    pub scaled_wrench_up_roll_pitch: [[f64; 3]; CARS],
    pub correction_n: [[f64; MODULES]; CARS],
    pub requested_support_n: [[f64; MODULES]; CARS],
    pub maximum_abs_correction_n: f64,
}

fn valid_config(config: &ObserverConfig) -> bool {
    config.abi_version == ABI_VERSION
        && (1..=MAX_GROUPS as u32).contains(&config.groups)
        && config.configuration_sha256 != [0; 32]
        && config.wave_number_rad_per_m.is_finite()
        && config.wave_number_rad_per_m > 0.0
        && [0.9, 1.0, 1.1].contains(&config.estimator_scale)
        && config.step_ns == STEP_NS
}

/// Pure delayed-map estimate. This validates all active channels, including a
/// phase/position whose linkage is zero; missing/nonfinite samples are not masked.
pub fn estimate_wrench(
    groups: &[GroupObservation],
    speed_m_s: &[f64; CARS],
    centres_m: &[f64; CARS],
    wave_number_rad_per_m: f64,
) -> Result<[[f64; 3]; CARS], Status> {
    if groups.is_empty() || groups.len() > MAX_GROUPS {
        return Err(Status::GroupCount);
    }
    if !wave_number_rad_per_m.is_finite() || wave_number_rad_per_m <= 0.0 {
        return Err(Status::InvalidConfiguration);
    }
    if speed_m_s.iter().chain(centres_m).any(|x| !x.is_finite()) {
        return Err(Status::NonFinite);
    }
    let mut result = [[0.0; 3]; CARS];
    for group in groups {
        if group
            .flux_linkage_wb
            .iter()
            .chain(&group.phase_rad)
            .chain(&group.normal_position_m)
            .chain([&group.current_alpha_a, &group.current_beta_a])
            .any(|x| !x.is_finite())
        {
            return Err(Status::NonFinite);
        }
        if group.flux_linkage_wb.iter().any(|x| *x < 0.0) {
            return Err(Status::NegativeFluxAmplitude);
        }
        for car in 0..CARS {
            let angle = group.phase_rad[car] + wave_number_rad_per_m * speed_m_s[car] * 0.001;
            if !angle.is_finite() {
                return Err(Status::Arithmetic);
            }
            let local_real =
                group.current_alpha_a * angle.cos() + group.current_beta_a * angle.sin();
            let term = 1.5 * wave_number_rad_per_m * group.flux_linkage_wb[car] * local_real;
            let pitch = -term * (group.normal_position_m[car] - centres_m[car]);
            result[car][0] += term;
            result[car][2] += pitch;
            if !local_real.is_finite()
                || !term.is_finite()
                || !pitch.is_finite()
                || !result[car][0].is_finite()
                || !result[car][2].is_finite()
            {
                return Err(Status::Arithmetic);
            }
        }
    }
    Ok(result)
}

/// Minimum-norm allocation for the fixed 24 module layout, with wrench rows
/// [1, y, -x]. Symmetry makes M M^T diagonal [24, 24*.88^2, 286].
/// This pure function also accepts nonzero roll for independent balance tests.
pub fn allocate_wrench(wrench: &[[f64; 3]; CARS]) -> Result<[[f64; MODULES]; CARS], Status> {
    let mut correction = [[0.0; MODULES]; CARS];
    for car in 0..CARS {
        if wrench[car].iter().any(|x| !x.is_finite()) {
            return Err(Status::NonFinite);
        }
        for module in 0..MODULES {
            correction[car][module] = -(wrench[car][0] / 24.0
                + wrench[car][1] * MODULE_Y_M[module] / (24.0 * 0.88 * 0.88)
                - wrench[car][2] * MODULE_X_M[module] / 286.0);
            if !correction[car][module].is_finite() {
                return Err(Status::Arithmetic);
            }
        }
    }
    Ok(correction)
}

fn checked_step(input: &ObserverInput) -> Result<ObserverOutput, Status> {
    let config = &input.config;
    let state = &input.state;
    let frame = &input.frame;
    if !valid_config(config) {
        return Err(Status::InvalidConfiguration);
    }
    if state.initialized > 1 || state.reserved != 0 {
        return Err(Status::InvalidState);
    }
    if frame.sample_present > 1 {
        return Err(Status::MissingSample);
    }
    let raw = if state.initialized == 0 {
        if *state != ObserverState::default() {
            return Err(Status::InvalidState);
        }
        if frame.sequence != 1 {
            return Err(Status::Sequence);
        }
        if frame.sample_present != 0 {
            return Err(Status::UnexpectedStartupSample);
        }
        if frame.sample_groups != 0
            || frame.sample_sequence != 0
            || frame.sample_timestamp_ns != 0
            || frame.sample_configuration_sha256 != [0; 32]
        {
            return Err(Status::UnexpectedStartupSample);
        }
        [[0.0; 3]; CARS]
    } else {
        if !valid_config(&state.config) || state.last_sequence == 0 {
            return Err(Status::InvalidState);
        }
        if state.config != *config {
            return Err(Status::ConfigurationIdentity);
        }
        if state.last_sequence.checked_add(1) != Some(frame.sequence) {
            return Err(Status::Sequence);
        }
        if state.last_timestamp_ns.checked_add(STEP_NS) != Some(frame.timestamp_ns) {
            return Err(Status::Clock);
        }
        if frame.sample_present != 1 {
            return Err(Status::MissingSample);
        }
        if frame.sample_configuration_sha256 != config.configuration_sha256 {
            return Err(Status::ConfigurationIdentity);
        }
        if frame.sample_sequence != state.last_sequence {
            return Err(Status::SampleSequence);
        }
        if frame.sample_timestamp_ns != state.last_timestamp_ns
            || frame.sample_timestamp_ns.checked_add(STEP_NS) != Some(frame.timestamp_ns)
        {
            return Err(Status::SampleAge);
        }
        if frame.sample_groups != config.groups {
            return Err(Status::GroupCount);
        }
        estimate_wrench(
            &frame.groups[..config.groups as usize],
            &frame.speed_m_s,
            &frame.centres_m,
            config.wave_number_rad_per_m,
        )?
    };
    let mut scaled = raw;
    for car in &mut scaled {
        for value in car {
            *value *= config.estimator_scale;
        }
    }
    let correction = allocate_wrench(&scaled)?;
    let mut requested = [[0.0; MODULES]; CARS];
    let mut maximum: f64 = 0.0;
    for car in 0..CARS {
        for module in 0..MODULES {
            let desired = frame.desired_support_n[car][module];
            if !desired.is_finite() {
                return Err(Status::NonFinite);
            }
            // Validate the uncorrected input as well as the resulting request. No
            // cancellation may rehabilitate an already invalid support demand.
            if !(0.0..=SUPPORT_MAX_N).contains(&desired) {
                return Err(Status::SupportBounds);
            }
            requested[car][module] = desired + correction[car][module];
            if !requested[car][module].is_finite() {
                return Err(Status::Arithmetic);
            }
            if !(0.0..=SUPPORT_MAX_N).contains(&requested[car][module]) {
                return Err(Status::SupportBounds);
            }
            maximum = maximum.max(correction[car][module].abs());
        }
    }
    Ok(ObserverOutput {
        status: Status::Ok as u32,
        physical_output_authorised: 0,
        next_state: ObserverState {
            initialized: 1,
            reserved: 0,
            last_sequence: frame.sequence,
            last_timestamp_ns: frame.timestamp_ns,
            config: *config,
        },
        raw_wrench_up_roll_pitch: raw,
        scaled_wrench_up_roll_pitch: scaled,
        correction_n: correction,
        requested_support_n: requested,
        maximum_abs_correction_n: maximum,
    })
}

/// Fail-closed, side-effect-free step. Rejection keeps original state and zeros
/// every numerical output; callers must inspect status before consuming results.
pub fn observe(input: &ObserverInput) -> ObserverOutput {
    match checked_step(input) {
        Ok(output) => output,
        Err(status) => ObserverOutput {
            status: status as u32,
            next_state: input.state,
            ..ObserverOutput::default()
        },
    }
}

/// By-value C ABI for offline ctypes/rig simulation. There are no raw-pointer
/// operations. The narrowly allowed unsafe attribute only exports a unique name;
/// the numeric implementation remains safe Rust under the crate's deny lint.
#[allow(unsafe_code)]
#[unsafe(no_mangle)]
pub extern "C" fn osr_research_normal_wrench_v1(input: ObserverInput) -> ObserverOutput {
    observe(&input)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn startup() -> ObserverInput {
        ObserverInput {
            config: ObserverConfig {
                abi_version: ABI_VERSION,
                groups: 1,
                configuration_sha256: [7; 32],
                wave_number_rad_per_m: std::f64::consts::PI / 0.25,
                estimator_scale: 1.0,
                step_ns: STEP_NS,
            },
            frame: ObserverFrame {
                sequence: 1,
                timestamp_ns: 2_000_000,
                desired_support_n: [[12400.0; MODULES]; CARS],
                ..ObserverFrame::default()
            },
            ..ObserverInput::default()
        }
    }
    fn active() -> ObserverInput {
        let mut input = startup();
        input.state = observe(&input).next_state;
        input.frame.sequence = 2;
        input.frame.timestamp_ns += STEP_NS;
        input.frame.sample_present = 1;
        input.frame.sample_groups = 1;
        input.frame.sample_sequence = 1;
        input.frame.sample_timestamp_ns = input.state.last_timestamp_ns;
        input.frame.sample_configuration_sha256 = input.config.configuration_sha256;
        input.frame.groups[0] = GroupObservation {
            flux_linkage_wb: [0.02; CARS],
            normal_position_m: [2.0; CARS],
            current_alpha_a: 100.0,
            ..GroupObservation::default()
        };
        input
    }
    fn refused(input: &ObserverInput, status: Status) {
        let output = observe(input);
        assert_eq!(output.status, status as u32);
        assert_eq!(output.next_state, input.state);
        assert_eq!(output.physical_output_authorised, 0);
        assert_eq!(output.raw_wrench_up_roll_pitch, [[0.0; 3]; CARS]);
        assert_eq!(output.scaled_wrench_up_roll_pitch, [[0.0; 3]; CARS]);
        assert_eq!(output.correction_n, [[0.0; MODULES]; CARS]);
        assert_eq!(output.requested_support_n, [[0.0; MODULES]; CARS]);
        assert_eq!(output.maximum_abs_correction_n, 0.0);
    }
    fn near(a: f64, b: f64) {
        assert!((a - b).abs() <= 1e-10 * b.abs().max(1.0), "{a} != {b}");
    }
    #[test]
    fn startup_zero_observation_never_authorises_hardware() {
        let output = observe(&startup());
        assert_eq!(output.status, 0);
        assert_eq!(output.physical_output_authorised, 0);
        assert_eq!(output.requested_support_n, [[12400.0; MODULES]; CARS]);
        assert_eq!(output.raw_wrench_up_roll_pitch, [[0.0; 3]; CARS]);
    }
    #[test]
    fn analytical_phase_and_pitch_balance() {
        let mut input = active();
        let expected = 1.5 * input.config.wave_number_rad_per_m * 0.02 * 100.0;
        let output = observe(&input);
        assert_eq!(output.status, 0);
        for car in 0..CARS {
            near(output.raw_wrench_up_roll_pitch[car][0], expected);
            near(output.raw_wrench_up_roll_pitch[car][2], -2.0 * expected);
        }
        input.frame.groups[0].current_alpha_a = 0.0;
        input.frame.groups[0].current_beta_a = 100.0;
        input.frame.groups[0].phase_rad = [std::f64::consts::FRAC_PI_2; CARS];
        near(observe(&input).raw_wrench_up_roll_pitch[0][0], expected);
    }
    #[test]
    fn allocation_closes_force_roll_and_pitch() {
        let wrench = [[100.0, -32.0, 430.0]; CARS];
        let result = allocate_wrench(&wrench).unwrap();
        for car in 0..CARS {
            near(result[car].iter().sum(), -wrench[car][0]);
            near(
                result[car].iter().zip(MODULE_Y_M).map(|(f, y)| f * y).sum(),
                -wrench[car][1],
            );
            near(
                result[car]
                    .iter()
                    .zip(MODULE_X_M)
                    .map(|(f, x)| -f * x)
                    .sum(),
                -wrench[car][2],
            );
        }
    }
    #[test]
    fn all_declared_scales_are_applied_before_allocation() {
        for scale in [0.9, 1.0, 1.1] {
            let mut input = active();
            input.config.estimator_scale = scale;
            input.state.config = input.config;
            let output = observe(&input);
            assert_eq!(output.status, 0);
            near(
                output.scaled_wrench_up_roll_pitch[0][0],
                output.raw_wrench_up_roll_pitch[0][0] * scale,
            );
        }
    }
    #[test]
    fn sequence_clock_age_hash_and_group_refusals_do_not_advance() {
        let mut input = active();
        input.frame.sequence = 1;
        refused(&input, Status::Sequence);
        let mut input = active();
        input.frame.timestamp_ns += 1;
        refused(&input, Status::Clock);
        let mut input = active();
        input.frame.sample_timestamp_ns -= 1;
        refused(&input, Status::SampleAge);
        let mut input = active();
        input.frame.sample_timestamp_ns += 1;
        refused(&input, Status::SampleAge);
        let mut input = active();
        input.frame.sample_sequence = 0;
        refused(&input, Status::SampleSequence);
        let mut input = active();
        input.frame.sample_configuration_sha256[0] ^= 1;
        refused(&input, Status::ConfigurationIdentity);
        let mut input = active();
        input.frame.sample_groups = 0;
        refused(&input, Status::GroupCount);
        let mut input = active();
        input.frame.sample_groups = 201;
        refused(&input, Status::GroupCount);
        let mut input = active();
        input.frame.sample_present = 0;
        refused(&input, Status::MissingSample);
        let mut input = active();
        input.frame.sample_present = 2;
        refused(&input, Status::MissingSample);
    }
    #[test]
    fn invalid_numeric_channels_and_overflow_refuse() {
        let mut input = active();
        input.frame.groups[0].phase_rad[0] = f64::NAN;
        refused(&input, Status::NonFinite);
        let mut input = active();
        input.frame.groups[0].current_beta_a = f64::INFINITY;
        refused(&input, Status::NonFinite);
        let mut input = active();
        input.frame.speed_m_s[0] = f64::NAN;
        refused(&input, Status::NonFinite);
        let mut input = active();
        input.frame.centres_m[0] = f64::INFINITY;
        refused(&input, Status::NonFinite);
        let mut input = active();
        input.frame.groups[0].normal_position_m[0] = f64::NAN;
        refused(&input, Status::NonFinite);
        let mut input = active();
        input.frame.groups[0].flux_linkage_wb[0] = -0.01;
        refused(&input, Status::NegativeFluxAmplitude);
        let mut input = active();
        input.frame.groups[0].current_alpha_a = f64::MAX;
        refused(&input, Status::Arithmetic);
        let mut input = active();
        input.frame.desired_support_n[0][0] = f64::NAN;
        refused(&input, Status::NonFinite);
        let mut input = active();
        input.state.last_sequence = u64::MAX;
        refused(&input, Status::Sequence);
        let mut input = active();
        input.state.last_timestamp_ns = u64::MAX;
        refused(&input, Status::Clock);
    }
    #[test]
    fn no_clipping_or_cancellation_of_invalid_input() {
        let mut input = active();
        input.frame.desired_support_n = [[0.0; MODULES]; CARS];
        refused(&input, Status::SupportBounds);
        let mut input = active();
        input.frame.groups[0].current_alpha_a = -100.0;
        input.frame.desired_support_n = [[SUPPORT_MAX_N; MODULES]; CARS];
        refused(&input, Status::SupportBounds);
        let mut input = active();
        input.frame.desired_support_n[0][0] = -0.01;
        refused(&input, Status::SupportBounds);
        let mut input = startup();
        input.frame.desired_support_n[0][0] = SUPPORT_MAX_N + 1.0;
        refused(&input, Status::SupportBounds);
    }
    #[test]
    fn incompatible_configuration_and_initial_state_refuse() {
        let mut input = active();
        input.config.estimator_scale = 0.8;
        refused(&input, Status::InvalidConfiguration);
        let mut input = active();
        input.config.groups = 201;
        refused(&input, Status::InvalidConfiguration);
        let mut input = active();
        input.config.step_ns = STEP_NS + 1;
        refused(&input, Status::InvalidConfiguration);
        let mut input = active();
        input.config.wave_number_rad_per_m = f64::NAN;
        refused(&input, Status::InvalidConfiguration);
        let mut input = active();
        input.config.configuration_sha256 = [0; 32];
        refused(&input, Status::InvalidConfiguration);
        let mut input = active();
        input.config.wave_number_rad_per_m *= 2.0;
        refused(&input, Status::ConfigurationIdentity);
        let mut input = startup();
        input.frame.sample_present = 1;
        refused(&input, Status::UnexpectedStartupSample);
        let mut input = startup();
        input.state.last_sequence = 5;
        refused(&input, Status::InvalidState);
        let mut input = active();
        input.state.reserved = 1;
        refused(&input, Status::InvalidState);
    }
}
