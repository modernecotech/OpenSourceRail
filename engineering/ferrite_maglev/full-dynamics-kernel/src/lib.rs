//! Offline continued-fault voltage/current adapter, without hardware I/O.
//! Existing public Rust allocation/current kernels supply every command. The
//! independent coupled RL plant continues when either controller refuses output.
use osr_maglev_control::array::{Availability, Forces, Station, Wrench, allocate, resultant};
use osr_maglev_control::drives::{Demand, Fault, Frame, Mode, Params, Role, State, evaluate};
pub mod groups;

pub const MODULES: usize = 144;
pub const CARS: usize = 6;

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct CurrentState {
    pub sequence: u64,
    pub now_ns: u64,
    pub observed_ns: u64,
    pub integral_v: [f64; 2],
    pub fault: u32,
    pub initialized: u32,
}
fn fault(n: u32) -> Option<Fault> {
    match n {
        0 => None,
        1 => Some(Fault::Parameters),
        2 => Some(Fault::Identity),
        3 => Some(Fault::Time),
        4 => Some(Fault::Sensor),
        5 => Some(Fault::Current),
        6 => Some(Fault::Temperature),
        7 => Some(Fault::Bus),
        8 => Some(Fault::Authority),
        9 => Some(Fault::Receiver),
        10 => Some(Fault::Phase),
        11 => Some(Fault::Mode),
        _ => Some(Fault::Latched),
    }
}
fn code(f: Option<Fault>) -> u32 {
    match f {
        None => 0,
        Some(Fault::Parameters) => 1,
        Some(Fault::Identity) => 2,
        Some(Fault::Time) => 3,
        Some(Fault::Sensor) => 4,
        Some(Fault::Current) => 5,
        Some(Fault::Temperature) => 6,
        Some(Fault::Bus) => 7,
        Some(Fault::Authority) => 8,
        Some(Fault::Receiver) => 9,
        Some(Fault::Phase) => 10,
        Some(Fault::Mode) => 11,
        Some(Fault::Latched) => 12,
    }
}
impl CurrentState {
    fn core(self) -> State {
        State {
            last_sequence: (self.initialized == 1).then_some(self.sequence),
            last_now_ns: (self.initialized == 1).then_some(self.now_ns),
            last_observed_ns: (self.initialized == 1).then_some(self.observed_ns),
            integral_v: self.integral_v,
            fault: fault(self.fault),
        }
    }
    fn from_core(state: State) -> Self {
        Self {
            sequence: state.last_sequence.unwrap_or(0),
            now_ns: state.last_now_ns.unwrap_or(0),
            observed_ns: state.last_observed_ns.unwrap_or(0),
            integral_v: state.integral_v,
            fault: code(state.fault),
            initialized: u32::from(state.last_now_ns.is_some()),
        }
    }
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Module {
    pub resistance_ohm: [f64; 2],
    /// Row-major symmetric incremental inductance, including mutual terms.
    pub inductance_h: [f64; 4],
    pub motional_emf_v: [f64; 2],
    pub primary_target_a: [f64; 2],
    pub reserve_target_a: [f64; 2],
    pub current_a: [f64; 2],
    pub temperature_c: [f64; 2],
    pub copper_mass_kg: [f64; 2],
    pub cooling_w_k: [f64; 2],
    pub primary: [CurrentState; 2],
    pub reserve: [CurrentState; 2],
    /// 1 bus loss;2 sensor dropout;4 disagreement;8 inverter loss;16 stale
    /// primary;32 reserve sensing loss;64 reserve disagreement;128 reserve
    /// disconnect;256 current-sensor overrange;512 reserve-transfer delay.
    pub faults: u32,
    pub car: u32,
}

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct ElectricalInput {
    pub configuration: [u8; 32],
    pub first_sequence: u64,
    pub step_ns: u64,
    pub substeps: u32,
    pub count: u32,
    pub primary_bus_v: f64,
    pub reserve_bus_v: f64,
    pub maximum_current_a: f64,
    pub kp_v_per_a: f64,
    pub ki_v_per_a_s: f64,
    pub maximum_temperature_c: f64,
    pub ambient_c: f64,
    pub copper_cp_j_kg_k: f64,
    pub reserve_efficiency: f64,
    pub reserve_remaining_j: [f64; CARS],
    pub reserve_auxiliary_w: [f64; CARS],
    pub modules: [Module; MODULES],
}
impl Default for ElectricalInput {
    fn default() -> Self {
        Self {
            configuration: [0; 32],
            first_sequence: 0,
            step_ns: 0,
            substeps: 0,
            count: 0,
            primary_bus_v: 0.,
            reserve_bus_v: 0.,
            maximum_current_a: 0.,
            kp_v_per_a: 0.,
            ki_v_per_a_s: 0.,
            maximum_temperature_c: 0.,
            ambient_c: 0.,
            copper_cp_j_kg_k: 0.,
            reserve_efficiency: 0.,
            reserve_remaining_j: [0.; CARS],
            reserve_auxiliary_w: [0.; CARS],
            modules: [Module::default(); MODULES],
        }
    }
}
#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct ElectricalOutput {
    pub status: u32,
    pub physical_output_authorised: u32,
    pub modules: [Module; MODULES],
    pub reserve_remaining_j: [f64; CARS],
    pub last_voltage_v: [[f64; 2]; MODULES],
    pub primary_fault_channels: u32,
    pub reserve_used_channels: u32,
    pub reserve_depleted_cars: u32,
    pub voltage_limited_microsteps: u32,
    pub primary_dc_j: f64,
    pub reserve_dc_j: f64,
    pub reserve_draw_j: f64,
    pub copper_heat_j: f64,
    pub rejected_cooling_j: f64,
    pub emf_work_j: f64,
    pub field_change_j: f64,
    pub maximum_rl_residual_j: f64,
    pub peak_current_a: f64,
    pub peak_voltage_v: f64,
}
impl Default for ElectricalOutput {
    fn default() -> Self {
        Self {
            status: 0,
            physical_output_authorised: 0,
            modules: [Module::default(); MODULES],
            reserve_remaining_j: [0.; CARS],
            last_voltage_v: [[0.; 2]; MODULES],
            primary_fault_channels: 0,
            reserve_used_channels: 0,
            reserve_depleted_cars: 0,
            voltage_limited_microsteps: 0,
            primary_dc_j: 0.,
            reserve_dc_j: 0.,
            reserve_draw_j: 0.,
            copper_heat_j: 0.,
            rejected_cooling_j: 0.,
            emf_work_j: 0.,
            field_change_j: 0.,
            maximum_rl_residual_j: 0.,
            peak_current_a: 0.,
            peak_voltage_v: 0.,
        }
    }
}

/// Crank-Nicolson for a frozen-geometry reciprocal two-circuit RL system.
/// Its midpoint electrical work identity is exact to floating point roundoff.
pub fn rl_step(
    current: [f64; 2],
    voltage: [f64; 2],
    emf: [f64; 2],
    r: [f64; 2],
    l: [f64; 4],
    dt: f64,
) -> [f64; 2] {
    let a = l[0] + r[0] * dt / 2.;
    let b = l[1];
    let d = l[3] + r[1] * dt / 2.;
    let rhs = [
        (l[0] - r[0] * dt / 2.) * current[0] + l[1] * current[1] + (voltage[0] - emf[0]) * dt,
        l[2] * current[0] + (l[3] - r[1] * dt / 2.) * current[1] + (voltage[1] - emf[1]) * dt,
    ];
    let determinant = a * d - b * b;
    [
        (d * rhs[0] - b * rhs[1]) / determinant,
        (a * rhs[1] - b * rhs[0]) / determinant,
    ]
}
fn stored(i: [f64; 2], l: [f64; 4]) -> f64 {
    0.5 * (i[0] * (l[0] * i[0] + l[1] * i[1]) + i[1] * (l[2] * i[0] + l[3] * i[1]))
}
fn module_valid(m: &Module) -> bool {
    let l = m.inductance_h;
    m.car < CARS as u32
        && m.faults < 1024
        && l.iter().all(|x| x.is_finite())
        && l[0] > 0.
        && l[3] > 0.
        && (l[1] - l[2]).abs() < 1e-10
        && l[0] * l[3] - l[1] * l[2] > 1e-14
        && m.resistance_ohm
            .iter()
            .chain(&m.copper_mass_kg)
            .all(|x| x.is_finite() && *x > 0.)
        && m.cooling_w_k.iter().all(|x| x.is_finite() && *x >= 0.)
        && m.current_a
            .iter()
            .chain(&m.temperature_c)
            .chain(&m.motional_emf_v)
            .chain(&m.primary_target_a)
            .chain(&m.reserve_target_a)
            .all(|x| x.is_finite())
        && m.primary
            .iter()
            .chain(&m.reserve)
            .all(|s| s.initialized <= 1 && s.fault <= 12)
}
pub fn electrical(input: &ElectricalInput) -> ElectricalOutput {
    let mut out = ElectricalOutput::default();
    if input.configuration == [0; 32]
        || input.count == 0
        || input.count > MODULES as u32
        || input.step_ns != 50_000
        || !(1..=100).contains(&input.substeps)
        || input.first_sequence == 0
        || ![
            input.primary_bus_v,
            input.reserve_bus_v,
            input.maximum_current_a,
            input.kp_v_per_a,
            input.ki_v_per_a_s,
            input.maximum_temperature_c,
            input.copper_cp_j_kg_k,
            input.reserve_efficiency,
        ]
        .iter()
        .all(|x| x.is_finite() && *x > 0.)
        || input.reserve_efficiency > 1.
        || !input.ambient_c.is_finite()
        || input
            .reserve_remaining_j
            .iter()
            .chain(&input.reserve_auxiliary_w)
            .any(|x| !x.is_finite() || *x < 0.)
        || input.modules[..input.count as usize]
            .iter()
            .any(|m| !module_valid(m))
        || input
            .first_sequence
            .checked_add(input.substeps as u64)
            .and_then(|s| s.checked_mul(input.step_ns))
            .is_none()
    {
        out.status = 1;
        return out;
    }
    out.modules = input.modules;
    out.reserve_remaining_j = input.reserve_remaining_j;
    let dt = input.step_ns as f64 * 1e-9;
    for sub in 0..input.substeps {
        let sequence = input.first_sequence + sub as u64;
        let now = sequence * input.step_ns;
        let mut car_reserve = [false; CARS];
        for n in 0..input.count as usize {
            let m = &mut out.modules[n];
            let car = m.car as usize;
            let initial = m.current_a;
            let mut voltage = [0.; 2];
            let mut reserve = [false; 2];
            for axis in 0..2 {
                let r = m.resistance_ohm[axis];
                let params = Params {
                    configuration: input.configuration,
                    role: Role::Support,
                    resistance_ohm: r,
                    inductance_h: m.inductance_h[axis * 3],
                    kp_v_per_a: input.kp_v_per_a,
                    ki_v_per_a_s: input.ki_v_per_a_s,
                    maximum_current_a: input.maximum_current_a,
                    current_disagreement_a: 1.,
                    maximum_temperature_c: input.maximum_temperature_c,
                    minimum_bus_v: 40.,
                    maximum_bus_v: 4000.,
                    maximum_age_ns: input.step_ns,
                    maximum_tick_ns: input.step_ns,
                    maximum_phase_error_mdeg: 5000,
                };
                for source in 0..2 {
                    let faults = m.faults;
                    let sensor_bad = if source == 0 {
                        faults & 2 != 0
                    } else {
                        faults & 32 != 0
                    };
                    let discrepancy = if source == 0 {
                        faults & 4 != 0
                    } else {
                        faults & 64 != 0
                    };
                    let power_bad = if source == 0 {
                        faults & 1 != 0
                    } else {
                        faults & 128 != 0
                            || out.reserve_remaining_j[car] <= 0.
                            || out.reserve_depleted_cars & (1 << car) != 0
                    };
                    let measured = initial[axis]
                        + if source == 0 && faults & 256 != 0 {
                            input.maximum_current_a * 2.
                        } else {
                            0.
                        };
                    let frame = Frame {
                        configuration: input.configuration,
                        sequence,
                        observed_ns: if source == 0 && faults & 16 != 0 {
                            now.saturating_sub(2 * input.step_ns)
                        } else {
                            now
                        },
                        measured_a: [measured, 0., 0.],
                        independent_measured_a: [
                            measured + if discrepancy { 2. } else { 0. },
                            0.,
                            0.,
                        ],
                        bus_v: if power_bad {
                            0.
                        } else if source == 0 {
                            input.primary_bus_v
                        } else {
                            input.reserve_bus_v
                        },
                        winding_temperature_c: m.temperature_c[axis],
                        sensors_healthy: !sensor_bad,
                        drive_healthy: source != 0 || faults & 8 == 0,
                        authority_protected: true,
                        receiver_ready: true,
                        resistor_ready: true,
                        launch_committed: false,
                        moving: true,
                        stopped_and_secured: false,
                        reset_requested: false,
                    };
                    let target = if source == 0 {
                        m.primary_target_a[axis]
                    } else {
                        m.reserve_target_a[axis]
                    };
                    let demand = Demand {
                        mode: Mode::Support,
                        d_a: target,
                        q_a: 0.,
                        electrical_phase_mdeg: 0,
                        phase_error_mdeg: 0,
                        electrical_speed_rad_s: 0.,
                        flux_linkage_wb: 0.,
                    };
                    let state = if source == 0 {
                        m.primary[axis]
                    } else {
                        m.reserve[axis]
                    };
                    let result = evaluate(state.core(), frame, demand, now, params);
                    if result.physical_output_authorised {
                        out.status = 2;
                        return out;
                    }
                    if source == 0 {
                        m.primary[axis] = CurrentState::from_core(result.state);
                    } else {
                        m.reserve[axis] = CurrentState::from_core(result.state);
                    }
                    if result.voltage_limited {
                        out.voltage_limited_microsteps += 1;
                    }
                    if source == 0 {
                        if result.study_duties.is_some() {
                            voltage[axis] = result.study_dq_voltage_v[0];
                            break;
                        }
                        out.primary_fault_channels += 1;
                    } else if result.study_duties.is_some() && faults & 512 == 0 {
                        voltage[axis] = result.study_dq_voltage_v[0];
                        reserve[axis] = true;
                        out.reserve_used_channels += 1;
                        car_reserve[car] = true;
                    }
                }
            }
            let mut next = rl_step(
                initial,
                voltage,
                m.motional_emf_v,
                m.resistance_ohm,
                m.inductance_h,
                dt,
            );
            let mut reserve_work = 0.;
            for axis in 0..2 {
                if reserve[axis] {
                    reserve_work += (voltage[axis] * (initial[axis] + next[axis]) / 2. * dt)
                        .max(0.)
                        / input.reserve_efficiency;
                }
            }
            if reserve_work > out.reserve_remaining_j[car] {
                // A source cannot supply energy it does not contain. Its switch
                // opens; the declared short/freewheel path and mutual RL state
                // continue. Existing current and PM force do not disappear.
                for axis in 0..2 {
                    if reserve[axis] {
                        voltage[axis] = 0.;
                    }
                }
                next = rl_step(
                    initial,
                    voltage,
                    m.motional_emf_v,
                    m.resistance_ohm,
                    m.inductance_h,
                    dt,
                );
                reserve_work = 0.;
                out.reserve_depleted_cars |= 1 << car;
            }
            out.reserve_remaining_j[car] -= reserve_work;
            out.reserve_draw_j += reserve_work;
            let field = stored(next, m.inductance_h) - stored(initial, m.inductance_h);
            let mut work = 0.;
            let mut heat = 0.;
            let mut emf = 0.;
            for axis in 0..2 {
                let mid = (initial[axis] + next[axis]) / 2.;
                let dc = voltage[axis] * mid * dt;
                if reserve[axis] {
                    out.reserve_dc_j += dc;
                } else {
                    out.primary_dc_j += dc;
                }
                let q = m.resistance_ohm[axis] * mid * mid * dt;
                let cooling =
                    (m.cooling_w_k[axis] * (m.temperature_c[axis] - input.ambient_c) * dt).max(0.);
                m.temperature_c[axis] +=
                    (q - cooling) / (m.copper_mass_kg[axis] * input.copper_cp_j_kg_k);
                out.rejected_cooling_j += cooling;
                work += dc;
                heat += q;
                emf += m.motional_emf_v[axis] * mid * dt;
                out.peak_current_a = out.peak_current_a.max(next[axis].abs());
                out.peak_voltage_v = out.peak_voltage_v.max(voltage[axis].abs());
            }
            if next.iter().any(|x| !x.is_finite()) {
                out.status = 3;
                return out;
            }
            out.maximum_rl_residual_j = out
                .maximum_rl_residual_j
                .max((work - heat - emf - field).abs());
            out.copper_heat_j += heat;
            out.emf_work_j += emf;
            out.field_change_j += field;
            m.current_a = next;
            out.last_voltage_v[n] = voltage;
        }
        for (car, used) in car_reserve.iter().enumerate() {
            if *used {
                let auxiliary =
                    (input.reserve_auxiliary_w[car] * dt).min(out.reserve_remaining_j[car]);
                out.reserve_remaining_j[car] -= auxiliary;
                out.reserve_draw_j += auxiliary;
                if out.reserve_remaining_j[car] == 0. {
                    out.reserve_depleted_cars |= 1 << car;
                }
            }
        }
    }
    out
}

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct AllocationInput {
    pub positions_m: [[f64; 3]; 24],
    pub modes: [f64; 5],
    pub velocities: [f64; 5],
    pub gains: [f64; 5],
    pub damping: [f64; 5],
    pub mass_kg: f64,
    pub gravity: f64,
    pub curve_acceleration_m_s2: f64,
    pub maximum_upward_n: f64,
    pub maximum_lateral_n: f64,
    pub maximum_slew_n_s: f64,
    pub step_s: f64,
    pub previous: [[f64; 2]; 24],
    pub preferred_upward_n: [f64; 24],
    pub preferred_enabled: u32,
    pub physical_upward_limits_n: [[f64; 2]; 24],
    pub physical_limits_enabled: u32,
}
#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct AllocationOutput {
    pub status: u32,
    pub at_limit: u32,
    pub forces: [[f64; 2]; 24],
    pub residual: [f64; 6],
    pub physical_output_authorised: u32,
}
pub fn distribution(input: &AllocationInput) -> AllocationOutput {
    let mut out = AllocationOutput::default();
    if input
        .positions_m
        .iter()
        .flatten()
        .chain(&input.modes)
        .chain(&input.velocities)
        .chain(&input.gains)
        .chain(&input.damping)
        .chain(input.previous.iter().flatten())
        .chain(&input.preferred_upward_n)
        .chain(input.physical_upward_limits_n.iter().flatten())
        .any(|v| !v.is_finite())
        || ![
            input.mass_kg,
            input.gravity,
            input.maximum_upward_n,
            input.maximum_lateral_n,
            input.maximum_slew_n_s,
            input.step_s,
        ]
        .iter()
        .all(|v| v.is_finite() && *v > 0.)
        || !input.curve_acceleration_m_s2.is_finite()
        || input.preferred_enabled > 1
        || input.physical_limits_enabled > 1
    {
        out.status = 1;
        return out;
    }
    let effort: [f64; 5] = core::array::from_fn(|i| {
        input.gains[i] * input.modes[i] + input.damping[i] * input.velocities[i]
    });
    let demand = Wrench {
        force_n: [
            0.,
            input.mass_kg * input.curve_acceleration_m_s2 - effort[3],
            input.mass_kg * input.gravity + effort[0],
        ],
        moment_nm: [-effort[1], -effort[2], -effort[4]],
    };
    if input.physical_limits_enabled == 1
        && input
            .physical_upward_limits_n
            .iter()
            .any(|v| v[0] < 0. || v[1] <= v[0] || v[1] > input.maximum_upward_n)
    {
        out.status = 1;
        return out;
    }
    let stations = core::array::from_fn(|i| Station {
        position_m: input.positions_m[i],
        minimum_upward_n: if input.physical_limits_enabled == 1 {
            input.physical_upward_limits_n[i][0]
        } else {
            0.
        },
        maximum_upward_n: if input.physical_limits_enabled == 1 {
            input.physical_upward_limits_n[i][1]
        } else {
            input.maximum_upward_n
        },
        maximum_lateral_n: input.maximum_lateral_n,
        maximum_slew_n_s: input.maximum_slew_n_s,
    });
    let previous = core::array::from_fn(|i| Forces {
        upward_n: input.previous[i][0],
        leftward_n: input.previous[i][1],
    });
    if input.preferred_enabled == 1 {
        return preferred_distribution(input, demand, &stations, &previous);
    }
    let a = allocate(
        &stations,
        &[Availability::Available; 24],
        demand,
        Some(&previous),
        input.step_s,
        20.,
        50.,
    );
    out.status = if a.valid && a.within_tolerance { 0 } else { 2 };
    out.at_limit = u32::from(a.at_limit);
    out.forces = core::array::from_fn(|i| [a.forces[i].upward_n, a.forces[i].leftward_n]);
    out.residual = [
        a.residual.force_n[0],
        a.residual.force_n[1],
        a.residual.force_n[2],
        a.residual.moment_nm[0],
        a.residual.moment_nm[1],
        a.residual.moment_nm[2],
    ];
    out
}

/// Preferred geometry-derived static reactions, followed by a bounded five-row
/// wrench correction. No unbalanced preferred vector is applied to the plant.
/// This isolated research extension preserves the original uniform allocator.
fn preferred_distribution(
    input: &AllocationInput,
    demand: Wrench,
    stations: &[Station; 24],
    previous: &[Forces; 24],
) -> AllocationOutput {
    let mut out = AllocationOutput::default();
    let total: f64 = input.preferred_upward_n.iter().sum();
    if total <= 0. || input.preferred_upward_n.iter().any(|x| *x < 0.) {
        out.status = 1;
        return out;
    }
    let mut columns = [[0.; 5]; 48];
    let mut lower = [0.; 48];
    let mut upper = [0.; 48];
    let mut values = [0.; 48];
    for i in 0..24 {
        let [x, y, z] = input.positions_m[i];
        columns[2 * i] = [0., 1., y / 6., -x / 6., 0.];
        columns[2 * i + 1] = [1., 0., -z / 6., 0., x / 6.];
        let slew = input.maximum_slew_n_s * input.step_s;
        lower[2 * i] = stations[i]
            .minimum_upward_n
            .max(previous[i].upward_n - slew);
        upper[2 * i] = stations[i]
            .maximum_upward_n
            .min(previous[i].upward_n + slew);
        lower[2 * i + 1] = (-input.maximum_lateral_n).max(previous[i].leftward_n - slew);
        upper[2 * i + 1] = input.maximum_lateral_n.min(previous[i].leftward_n + slew);
        if lower[2 * i] > upper[2 * i] || lower[2 * i + 1] > upper[2 * i + 1] {
            out.status = 1;
            return out;
        }
        values[2 * i] = (input.preferred_upward_n[i] / total * demand.force_n[2])
            .clamp(lower[2 * i], upper[2 * i]);
        values[2 * i + 1] = (demand.force_n[1] / 24.).clamp(lower[2 * i + 1], upper[2 * i + 1]);
    }
    let mut residual = [
        demand.force_n[1],
        demand.force_n[2],
        demand.moment_nm[0] / 6.,
        demand.moment_nm[1] / 6.,
        demand.moment_nm[2] / 6.,
    ];
    for (column, value) in columns.iter().zip(values) {
        for k in 0..5 {
            residual[k] -= column[k] * value;
        }
    }
    for _ in 0..256 {
        for j in 0..48 {
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
    let forces = core::array::from_fn(|i| Forces {
        upward_n: values[2 * i],
        leftward_n: values[2 * i + 1],
    });
    let actual = resultant(stations, &forces);
    out.residual = [
        demand.force_n[0] - actual.force_n[0],
        demand.force_n[1] - actual.force_n[1],
        demand.force_n[2] - actual.force_n[2],
        demand.moment_nm[0] - actual.moment_nm[0],
        demand.moment_nm[1] - actual.moment_nm[1],
        demand.moment_nm[2] - actual.moment_nm[2],
    ];
    out.status = u32::from(
        out.residual[..3].iter().any(|v| v.abs() > 20.)
            || out.residual[3..].iter().any(|v| v.abs() > 50.),
    ) * 2;
    out.at_limit = u32::from(
        values
            .iter()
            .enumerate()
            .any(|(i, v)| (*v - lower[i]).abs() < 1e-6 || (*v - upper[i]).abs() < 1e-6),
    );
    out.forces = core::array::from_fn(|i| [forces[i].upward_n, forces[i].leftward_n]);
    out
}
#[allow(unsafe_code)]
#[unsafe(no_mangle)]
pub extern "C" fn osr_full_dynamics_electrical_v1(input: ElectricalInput) -> ElectricalOutput {
    electrical(&input)
}
#[allow(unsafe_code)]
#[unsafe(no_mangle)]
pub extern "C" fn osr_full_dynamics_allocation_v1(input: AllocationInput) -> AllocationOutput {
    distribution(&input)
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Receiver {
    pub state: CurrentState,
    pub current_dq_a: [f64; 2],
    pub speed_m_s: f64,
    pub requested_brake_n: f64,
    pub temperature_c: f64,
    pub unavailable: u32,
    pub reserved: u32,
}
#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct ReceiverInput {
    pub configuration: [u8; 32],
    pub first_sequence: u64,
    pub step_ns: u64,
    pub substeps: u32,
    pub reserved: u32,
    pub resistance_ohm: f64,
    pub inductance_h: f64,
    pub flux_linkage_wb: f64,
    pub wave_number_rad_m: f64,
    pub bus_v: f64,
    pub maximum_current_a: f64,
    pub fault_dump_resistance_ohm: f64,
    pub receivers: [Receiver; 6],
}
#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct ReceiverOutput {
    pub status: u32,
    pub physical_output_authorised: u32,
    pub receivers: [Receiver; 6],
    pub longitudinal_force_n: [f64; 6],
    pub dc_j: f64,
    pub copper_heat_j: f64,
    pub fault_dump_heat_j: f64,
    pub emf_work_j: f64,
    pub field_change_j: f64,
    pub maximum_residual_j: f64,
    pub refused_microsteps: u64,
}
pub fn receiver(input: &ReceiverInput) -> ReceiverOutput {
    let mut out = ReceiverOutput::default();
    if input.configuration == [0; 32]
        || input.first_sequence == 0
        || input.step_ns != 50_000
        || !(1..=100).contains(&input.substeps)
        || ![
            input.resistance_ohm,
            input.inductance_h,
            input.flux_linkage_wb,
            input.wave_number_rad_m,
            input.bus_v,
            input.maximum_current_a,
            input.fault_dump_resistance_ohm,
        ]
        .iter()
        .all(|v| v.is_finite() && *v > 0.)
        || input.receivers.iter().any(|r| {
            r.current_dq_a
                .iter()
                .chain([&r.speed_m_s, &r.requested_brake_n, &r.temperature_c])
                .any(|v| !v.is_finite())
                || r.unavailable > 1
        })
        || input
            .first_sequence
            .checked_add(input.substeps as u64)
            .and_then(|s| s.checked_mul(input.step_ns))
            .is_none()
    {
        out.status = 1;
        return out;
    }
    out.receivers = input.receivers;
    let dt = input.step_ns as f64 * 1e-9;
    for sub in 0..input.substeps {
        let sequence = input.first_sequence + sub as u64;
        let now = sequence * input.step_ns;
        for (car, r) in out.receivers.iter_mut().enumerate() {
            let omega = input.wave_number_rad_m * r.speed_m_s;
            let old = r.current_dq_a;
            let p = Params {
                configuration: input.configuration,
                role: Role::Wayside,
                resistance_ohm: input.resistance_ohm,
                inductance_h: input.inductance_h,
                kp_v_per_a: 0.25,
                ki_v_per_a_s: 50.,
                maximum_current_a: input.maximum_current_a,
                current_disagreement_a: 5.,
                maximum_temperature_c: 180.,
                minimum_bus_v: 500.,
                maximum_bus_v: 4000.,
                maximum_age_ns: input.step_ns,
                maximum_tick_ns: input.step_ns,
                maximum_phase_error_mdeg: 5000,
            };
            let abc = [
                old[0],
                -0.5 * old[0] + 3_f64.sqrt() / 2. * old[1],
                -0.5 * old[0] - 3_f64.sqrt() / 2. * old[1],
            ];
            let f = Frame {
                configuration: input.configuration,
                sequence,
                observed_ns: now,
                measured_a: abc,
                independent_measured_a: abc,
                bus_v: input.bus_v,
                winding_temperature_c: r.temperature_c,
                sensors_healthy: true,
                drive_healthy: r.unavailable == 0,
                authority_protected: r.reserved & 1 != 0,
                receiver_ready: r.unavailable == 0 && r.reserved & 4 != 0,
                resistor_ready: r.unavailable == 0 && r.reserved & 8 != 0,
                launch_committed: r.reserved & 2 != 0,
                moving: r.speed_m_s.abs() > 0.05,
                stopped_and_secured: false,
                reset_requested: false,
            };
            let target =
                -r.requested_brake_n / (1.5 * input.wave_number_rad_m * input.flux_linkage_wb);
            let d = Demand {
                mode: if r.requested_brake_n < 0. {
                    Mode::Launch
                } else {
                    Mode::Receive
                },
                d_a: 0.,
                q_a: target,
                electrical_phase_mdeg: 0,
                phase_error_mdeg: 0,
                electrical_speed_rad_s: omega,
                flux_linkage_wb: input.flux_linkage_wb,
            };
            let result = evaluate(r.state.core(), f, d, now, p);
            r.state = CurrentState::from_core(result.state);
            if result.physical_output_authorised {
                out.status = 2;
                return out;
            }
            let voltage = if result.study_duties.is_some() {
                result.study_dq_voltage_v
            } else {
                out.refused_microsteps += 1;
                [0.; 2]
            };
            let emf = [
                -omega * input.inductance_h * old[1],
                omega * (input.inductance_h * old[0] + input.flux_linkage_wb),
            ];
            let dump = if result.study_duties.is_none() {
                input.fault_dump_resistance_ohm
            } else {
                0.
            };
            let resistance = input.resistance_ohm + dump;
            let l = [input.inductance_h, 0., 0., input.inductance_h];
            let next = rl_step(old, voltage, emf, [resistance; 2], l, dt);
            let mut dc = 0.;
            let mut copper = 0.;
            let mut diverted = 0.;
            let mut work = 0.;
            for axis in 0..2 {
                let mid = (old[axis] + next[axis]) / 2.;
                dc += 1.5 * voltage[axis] * mid * dt;
                copper += 1.5 * input.resistance_ohm * mid * mid * dt;
                diverted += 1.5 * dump * mid * mid * dt;
                work += 1.5 * emf[axis] * mid * dt;
            }
            let field = 1.5 * (stored(next, l) - stored(old, l));
            out.maximum_residual_j = out
                .maximum_residual_j
                .max((dc - copper - diverted - work - field).abs());
            out.dc_j += dc;
            out.copper_heat_j += copper;
            out.fault_dump_heat_j += diverted;
            out.emf_work_j += work;
            out.field_change_j += field;
            out.longitudinal_force_n[car] +=
                1.5 * input.wave_number_rad_m * input.flux_linkage_wb * (old[1] + next[1])
                    / 2.
                    / input.substeps as f64;
            r.current_dq_a = next;
            if next.iter().any(|v| !v.is_finite()) {
                out.status = 3;
                return out;
            }
        }
    }
    out
}
#[allow(unsafe_code)]
#[unsafe(no_mangle)]
pub extern "C" fn osr_full_dynamics_receiver_v1(input: ReceiverInput) -> ReceiverOutput {
    receiver(&input)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn mutual_rl_energy_identity_and_decay() {
        let l = [0.02, 0.003, 0.003, 0.04];
        let r = [0.1, 0.2];
        let old = [40., -20.];
        let dt = 0.00005;
        let next = rl_step(old, [0.; 2], [0.; 2], r, l, dt);
        let heat = (0..2)
            .map(|a| r[a] * ((old[a] + next[a]) / 2.).powi(2) * dt)
            .sum::<f64>();
        assert!((heat + stored(next, l) - stored(old, l)).abs() < 1e-11);
        assert!(stored(next, l) < stored(old, l));
        assert!(next[0] > 0.);
    }
    #[test]
    fn malformed_batch_never_authorises_physical_output() {
        let out = electrical(&ElectricalInput::default());
        assert_ne!(out.status, 0);
        assert_eq!(out.physical_output_authorised, 0);
    }
}
