//! Independent stationary alpha/beta group circuits. The caller provides the
//! geometry-derived flux derivative; this plant supplies voltages and currents,
//! never a commanded mechanical force. Refusals retain freewheel/dump currents.
use super::{CurrentState, rl_step, stored};
use osr_maglev_control::drives::{Demand, Frame, Mode, Params, Role, evaluate};

pub const MAX_GROUPS: usize = 200;

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Group {
    pub state: CurrentState,
    pub current_ab_a: [f64; 2],
    pub resistance_ohm: f64,
    pub inductance_h: f64,
    pub phase_rad: f64,
    pub speed_rad_s: f64,
    pub flux_wb: f64,
    pub demanded_q_a: f64,
    pub emf_ab_v: [f64; 2],
    pub temperature_c: f64,
    pub copper_mass_kg: f64,
    pub current_limit_a: f64,
    pub bus_v: f64,
    pub mode: u32,
    pub gates: u32,
    pub unavailable: u32,
    pub phase_error_mdeg: u32,
}
#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct Input {
    pub configuration: [u8; 32],
    pub first_sequence: u64,
    pub step_ns: u64,
    pub substeps: u32,
    pub count: u32,
    pub kp: f64,
    pub ki: f64,
    pub dump_resistance_ohm: f64,
    pub groups: [Group; MAX_GROUPS],
}
#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub struct Output {
    pub status: u32,
    pub physical_output_authorised: u32,
    pub groups: [Group; MAX_GROUPS],
    pub average_current_ab_a: [[f64; 2]; MAX_GROUPS],
    pub dc_j: f64,
    pub copper_heat_j: f64,
    pub dump_heat_j: f64,
    pub emf_work_j: f64,
    pub field_change_j: f64,
    pub maximum_residual_j: f64,
    pub maximum_voltage_v: f64,
    pub refused_microsteps: u64,
}
impl Default for Output {
    fn default() -> Self {
        Self {
            status: 0,
            physical_output_authorised: 0,
            groups: [Group::default(); MAX_GROUPS],
            average_current_ab_a: [[0.; 2]; MAX_GROUPS],
            dc_j: 0.,
            copper_heat_j: 0.,
            dump_heat_j: 0.,
            emf_work_j: 0.,
            field_change_j: 0.,
            maximum_residual_j: 0.,
            maximum_voltage_v: 0.,
            refused_microsteps: 0,
        }
    }
}
pub fn step(input: &Input) -> Output {
    let mut out = Output::default();
    if input.configuration == [0; 32]
        || input.first_sequence == 0
        || input.step_ns != 50_000
        || !(1..=100).contains(&input.substeps)
        || !(1..=MAX_GROUPS as u32).contains(&input.count)
        || ![input.kp, input.ki, input.dump_resistance_ohm]
            .iter()
            .all(|x| x.is_finite() && *x > 0.)
        || input
            .first_sequence
            .checked_add(u64::from(input.substeps))
            .and_then(|s| s.checked_mul(input.step_ns))
            .is_none()
    {
        out.status = 1;
        return out;
    }
    let count = input.count as usize;
    for g in &input.groups[..count] {
        if ![
            g.resistance_ohm,
            g.inductance_h,
            g.copper_mass_kg,
            g.current_limit_a,
            g.bus_v,
        ]
        .iter()
        .all(|v| v.is_finite() && *v > 0.)
            || !g
                .current_ab_a
                .iter()
                .chain(&g.emf_ab_v)
                .chain([
                    &g.phase_rad,
                    &g.speed_rad_s,
                    &g.flux_wb,
                    &g.demanded_q_a,
                    &g.temperature_c,
                ])
                .all(|v| v.is_finite())
            || g.flux_wb < 0.
            || g.mode > 2
            || g.gates > 15
            || g.unavailable > 1
        {
            out.status = 2;
            return out;
        }
    }
    out.groups = input.groups;
    let dt = input.step_ns as f64 * 1e-9;
    for sub in 0..input.substeps {
        let seq = input.first_sequence + u64::from(sub);
        let now = seq * input.step_ns;
        for (index, g) in out.groups[..count].iter_mut().enumerate() {
            let old = g.current_ab_a;
            let phase = g.phase_rad + g.speed_rad_s * (f64::from(sub) + 0.5) * dt;
            let phase_mdeg =
                (phase.to_degrees() * 1000.).rem_euclid(360000.).round() as u32 % 360000;
            let p = Params {
                configuration: input.configuration,
                role: Role::Wayside,
                resistance_ohm: g.resistance_ohm,
                inductance_h: g.inductance_h,
                kp_v_per_a: input.kp,
                ki_v_per_a_s: input.ki,
                maximum_current_a: g.current_limit_a,
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
            let frame = Frame {
                configuration: input.configuration,
                sequence: seq,
                observed_ns: now,
                measured_a: abc,
                independent_measured_a: abc,
                bus_v: g.bus_v,
                winding_temperature_c: g.temperature_c,
                sensors_healthy: true,
                drive_healthy: g.unavailable == 0,
                authority_protected: g.gates & 1 != 0,
                launch_committed: g.gates & 2 != 0,
                receiver_ready: g.gates & 4 != 0,
                resistor_ready: g.gates & 8 != 0,
                moving: g.speed_rad_s.abs() > 0.01,
                stopped_and_secured: false,
                reset_requested: false,
            };
            let demand = Demand {
                mode: match g.mode {
                    0 => Mode::Launch,
                    1 => Mode::Receive,
                    _ => Mode::Coast,
                },
                d_a: 0.,
                q_a: g.demanded_q_a,
                electrical_phase_mdeg: phase_mdeg,
                phase_error_mdeg: g.phase_error_mdeg,
                electrical_speed_rad_s: g.speed_rad_s,
                flux_linkage_wb: g.flux_wb,
            };
            let result = evaluate(g.state.core(), frame, demand, now, p);
            g.state = CurrentState::from_core(result.state);
            if result.physical_output_authorised {
                out.status = 3;
                return out;
            }
            let (voltage, dump) = if result.study_duties.is_some() {
                let (s, c) = phase.sin_cos();
                let [d, q] = result.study_dq_voltage_v;
                ([d * c - q * s, d * s + q * c], 0.)
            } else {
                out.refused_microsteps += 1;
                ([0.; 2], input.dump_resistance_ohm)
            };
            let l = [g.inductance_h, 0., 0., g.inductance_h];
            let next = rl_step(
                old,
                voltage,
                g.emf_ab_v,
                [g.resistance_ohm + dump; 2],
                l,
                dt,
            );
            let mut dc = 0.;
            let mut copper = 0.;
            let mut diverted = 0.;
            let mut emf = 0.;
            for axis in 0..2 {
                let mid = (old[axis] + next[axis]) / 2.;
                dc += 1.5 * voltage[axis] * mid * dt;
                copper += 1.5 * g.resistance_ohm * mid * mid * dt;
                diverted += 1.5 * dump * mid * mid * dt;
                emf += 1.5 * g.emf_ab_v[axis] * mid * dt;
                out.average_current_ab_a[index][axis] += mid / f64::from(input.substeps);
                out.maximum_voltage_v = out.maximum_voltage_v.max(voltage[axis].abs());
            }
            let field = 1.5 * (stored(next, l) - stored(old, l));
            out.maximum_residual_j = out
                .maximum_residual_j
                .max((dc - copper - diverted - emf - field).abs());
            out.dc_j += dc;
            out.copper_heat_j += copper;
            out.dump_heat_j += diverted;
            out.emf_work_j += emf;
            out.field_change_j += field;
            g.current_ab_a = next;
            g.temperature_c += copper / (g.copper_mass_kg * 385.);
            if next.iter().any(|v| !v.is_finite()) || !g.temperature_c.is_finite() {
                out.status = 4;
                return out;
            }
        }
    }
    out
}
#[allow(unsafe_code)]
#[unsafe(no_mangle)]
pub extern "C" fn osr_full_dynamics_groups_v1(input: Input) -> Output {
    step(&input)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn invalid_count_refused_without_physical_output() {
        let input = Input {
            configuration: [1; 32],
            first_sequence: 1,
            step_ns: 50000,
            substeps: 20,
            count: 201,
            kp: 1.,
            ki: 1.,
            dump_resistance_ohm: 0.5,
            groups: [Group::default(); MAX_GROUPS],
        };
        let output = step(&input);
        assert_eq!(output.status, 1);
        assert_eq!(output.physical_output_authorised, 0);
    }
}
