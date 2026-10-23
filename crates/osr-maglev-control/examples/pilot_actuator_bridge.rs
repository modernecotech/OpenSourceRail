//! Offline actual Rust current kernels driving independently integrated RL plants.
//! Bounded text IPC only; no field device addresses or physical output.
use osr_maglev_control::drives::{evaluate, Demand, Frame, Mode, Params, Role, State};
use std::io::{self, BufRead, Read, Write};

struct Channel {
    p: Params,
    state: State,
    ab: [f64; 2],
    temperature: f64,
    copper_mass: f64,
    nominal_l: f64,
}
fn numbers(line: &str) -> Option<Vec<f64>> {
    let v: Vec<f64> = line
        .split_whitespace()
        .map(|s| s.parse().unwrap_or(f64::NAN))
        .collect();
    v.iter().all(|x| x.is_finite()).then_some(v)
}
fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.len() != 5 {
        std::process::exit(2);
    }
    let support = args[0].parse::<usize>().unwrap_or(0);
    let wayside = args[1].parse::<usize>().unwrap_or(999);
    let outer_ns = args[2].parse::<u64>().unwrap_or(0);
    let current_ns = args[3].parse::<u64>().unwrap_or(0);
    let config = &args[4];
    if support != 144
        || wayside > 200
        || outer_ns == 0
        || current_ns != 50_000
        || outer_ns % current_ns != 0
        || outer_ns > 5_000_000
        || config.len() != 64
    {
        std::process::exit(2);
    }
    let mut identity = [0_u8; 32];
    for (j, x) in identity.iter_mut().enumerate() {
        *x = u8::from_str_radix(&config[2 * j..2 * j + 2], 16).unwrap_or(0);
    }
    let stdin = io::stdin();
    let mut input = stdin.lock();
    let stdout = io::stdout();
    let mut output = stdout.lock();
    let mut channels = Vec::with_capacity(support + wayside);
    for j in 0..support + wayside {
        let mut line = String::new();
        input.read_line(&mut line).unwrap();
        let Some(v) = numbers(&line) else {
            std::process::exit(2)
        };
        if v.len() != 8
            || v.iter().any(|x| x.abs() > 1e7)
            || v[6] <= 0.
            || v[7] < -50.
            || v[7] > 120.
        {
            std::process::exit(2);
        }
        let p = Params {
            configuration: identity,
            role: if j < support {
                Role::Support
            } else {
                Role::Wayside
            },
            resistance_ohm: v[0],
            inductance_h: v[1],
            kp_v_per_a: v[2],
            ki_v_per_a_s: v[3],
            maximum_current_a: v[4],
            current_disagreement_a: if j < support { 1. } else { 5. },
            maximum_temperature_c: 120.,
            minimum_bus_v: if j < support { 40. } else { 500. },
            maximum_bus_v: 4000.,
            maximum_age_ns: current_ns,
            maximum_tick_ns: current_ns,
            maximum_phase_error_mdeg: 5000,
        };
        if !p.valid() || v[5].abs() > p.maximum_current_a {
            std::process::exit(2);
        }
        channels.push(Channel {
            p,
            state: State::default(),
            ab: [v[5], 0.],
            temperature: v[7],
            copper_mass: v[6],
            nominal_l: v[1],
        });
    }
    let substeps = outer_ns / current_ns;
    let dt = current_ns as f64 * 1e-9;
    let mut expected = 1_u64;
    let mut sequence = 0_u64;
    for _ in 0..200_000 {
        let mut line = String::new();
        let count = input.by_ref().take(131_073).read_line(&mut line).unwrap();
        if count == 0 {
            break;
        }
        let Some(v) = numbers(&line) else {
            writeln!(output, "ERROR nonfinite").unwrap();
            output.flush().unwrap();
            break;
        };
        if count > 131_072 || v.len() != 4 + support * 3 + wayside * 8 || v[0] != expected as f64 {
            writeln!(output, "ERROR fields-or-sequence").unwrap();
            output.flush().unwrap();
            break;
        }
        expected += 1;
        let fault = v[1] as u32;
        let mut limited = 0_u64;
        let mut heat = 0.;
        let mut dc = 0.;
        let mut emf_work = 0.;
        let mut field_change = 0.;
        let mut residual = 0_f64;
        let mut max_temp = 0_f64;
        let mut peak_current = 0_f64;
        let mut peak_voltage = 0_f64;
        let mut failed = None;
        for sub in 0..substeps {
            sequence += 1;
            let now = sequence * current_ns;
            for (j, c) in channels.iter_mut().enumerate() {
                let is_support = j < support;
                let ix = if is_support {
                    4 + j * 3
                } else {
                    4 + support * 3 + (j - support) * 8
                };
                let mut p = c.p;
                // Resistance is identified at100C; actual copper temperature
                // varies through retained adiabatic heat, not a fixed20C loss.
                p.resistance_ohm *= (1. + 0.00393 * (c.temperature - 20.)) / (1. + 0.00393 * 80.);
                if is_support {
                    p.inductance_h = c.nominal_l * 0.008 / v[ix + 2];
                }
                let rotation = if is_support {
                    0.
                } else {
                    v[ix + 3] * sub as f64 * dt
                };
                let phase = if is_support {
                    0
                } else {
                    (v[ix + 1] + rotation.to_degrees() * 1000.)
                        .rem_euclid(360000.)
                        .round() as u32
                        % 360000
                };
                let abc = if is_support {
                    [c.ab[0], 0., 0.]
                } else {
                    [
                        c.ab[0],
                        -0.5 * c.ab[0] + 3_f64.sqrt() / 2. * c.ab[1],
                        -0.5 * c.ab[0] - 3_f64.sqrt() / 2. * c.ab[1],
                    ]
                };
                let frame = Frame {
                    configuration: identity,
                    sequence,
                    observed_ns: if fault == 7 {
                        now.saturating_sub(100_000)
                    } else {
                        now
                    },
                    measured_a: abc,
                    independent_measured_a: abc,
                    bus_v: if fault == 1 {
                        1.
                    } else if fault == 9 && is_support {
                        40.
                    } else if is_support {
                        v[2]
                    } else {
                        v[3]
                    },
                    winding_temperature_c: if fault == 3 { 130. } else { c.temperature },
                    sensors_healthy: fault != 2,
                    drive_healthy: true,
                    authority_protected: fault != 4,
                    receiver_ready: fault != 5,
                    resistor_ready: fault != 5,
                    launch_committed: true,
                    moving: true,
                    stopped_and_secured: false,
                    reset_requested: false,
                };
                let q = if is_support { 0. } else { v[ix] };
                let demand = Demand {
                    mode: if is_support {
                        Mode::Support
                    } else if q < 0. {
                        Mode::Receive
                    } else {
                        Mode::Launch
                    },
                    d_a: if is_support {
                        if fault == 8 {
                            p.maximum_current_a + 1.
                        } else if fault == 9 {
                            p.maximum_current_a
                        } else {
                            v[ix]
                        }
                    } else {
                        0.
                    },
                    q_a: q,
                    electrical_phase_mdeg: phase,
                    phase_error_mdeg: if fault == 6 {
                        5001
                    } else if is_support {
                        0
                    } else {
                        v[ix + 2].round() as u32
                    },
                    electrical_speed_rad_s: if is_support { 0. } else { v[ix + 3] },
                    flux_linkage_wb: if is_support { 0. } else { v[ix + 4] },
                };
                let result = evaluate(c.state, frame, demand, now, p);
                if result.study_duties.is_none() || result.physical_output_authorised {
                    failed = Some(format!("{j}:{:?}", result.state.fault));
                    break;
                }
                limited += u64::from(result.voltage_limited);
                c.state = result.state;
                let voltage = result.study_dq_voltage_v;
                let (s, co) = (f64::from(phase) * core::f64::consts::PI / 180000.).sin_cos();
                let applied = if is_support {
                    [voltage[0], 0.]
                } else {
                    [
                        voltage[0] * co - voltage[1] * s,
                        voltage[0] * s + voltage[1] * co,
                    ]
                };
                let (rs, rc) = rotation.sin_cos();
                let emf = if is_support {
                    [v[ix + 1], 0.]
                } else {
                    [
                        v[ix + 5] * rc - v[ix + 6] * rs,
                        v[ix + 5] * rs + v[ix + 6] * rc,
                    ]
                };
                let old = c.ab;
                let decay = (-p.resistance_ohm * dt / p.inductance_h).exp();
                let factor = if is_support { 1. } else { 1.5 };
                let mut joules = 0.;
                let mut supplied = 0.;
                let mut magnetic = 0.;
                let mut field = 0.;
                for k in 0..if is_support { 1 } else { 2 } {
                    let equilibrium = (applied[k] - emf[k]) / p.resistance_ohm;
                    let error = old[k] - equilibrium;
                    let tau = p.inductance_h / p.resistance_ohm;
                    c.ab[k] = equilibrium + error * decay;
                    let integral = equilibrium * dt + error * (1. - decay) * tau;
                    let square = equilibrium.powi(2) * dt
                        + 2. * equilibrium * error * (1. - decay) * tau
                        + error.powi(2) * (1. - decay * decay) * tau / 2.;
                    joules += factor * p.resistance_ohm * square.max(0.);
                    supplied += factor * applied[k] * integral;
                    magnetic += factor * emf[k] * integral;
                    field += factor * 0.5 * p.inductance_h * (c.ab[k].powi(2) - old[k].powi(2));
                }
                heat += joules;
                dc += supplied;
                emf_work += magnetic;
                field_change += field;
                residual = residual.max((supplied - joules - magnetic - field).abs());
                c.temperature += joules / (c.copper_mass * 385.);
                max_temp = max_temp.max(c.temperature);
                peak_current = peak_current.max(c.ab[0].hypot(c.ab[1]));
                peak_voltage = peak_voltage.max(voltage[0].hypot(voltage[1]));
            }
            if failed.is_some() {
                break;
            }
        }
        if let Some(message) = failed {
            writeln!(output, "FAULT {message}").unwrap();
            output.flush().unwrap();
            break;
        }
        write!(output,"OK {limited} {heat:.15e} {dc:.15e} {max_temp:.15e} {peak_current:.15e} {peak_voltage:.15e} {emf_work:.15e} {field_change:.15e} {residual:.15e}").unwrap();
        for c in &channels {
            write!(output, " {:.15e} {:.15e}", c.ab[0], c.ab[1]).unwrap();
        }
        writeln!(output).unwrap();
        output.flush().unwrap();
    }
}
