//! Executed average-voltage RL/current-control study, not switched hardware.
use osr_maglev_control::drives::*;
fn params(role: Role) -> Params {
    Params {
        configuration: [9; 32],
        role,
        resistance_ohm: 0.05,
        inductance_h: 0.002,
        kp_v_per_a: 2.,
        ki_v_per_a_s: 50.,
        maximum_current_a: 150.,
        current_disagreement_a: 1.,
        maximum_temperature_c: 120.,
        minimum_bus_v: 40.,
        maximum_bus_v: 1100.,
        maximum_age_ns: 50000,
        maximum_tick_ns: 50000,
        maximum_phase_error_mdeg: 5000,
    }
}
fn frame(k: u64) -> Frame {
    Frame {
        configuration: [9; 32],
        sequence: k,
        observed_ns: k * 50000,
        measured_a: [0.; 3],
        independent_measured_a: [0.; 3],
        bus_v: 96.,
        winding_temperature_c: 40.,
        sensors_healthy: true,
        drive_healthy: true,
        authority_protected: true,
        receiver_ready: true,
        resistor_ready: true,
        launch_committed: true,
        moving: true,
        stopped_and_secured: false,
        reset_requested: false,
    }
}
fn demand(mode: Mode) -> Demand {
    Demand {
        mode,
        d_a: if mode == Mode::Support { 40. } else { 0. },
        q_a: if mode == Mode::Receive {
            -40.
        } else if mode == Mode::Launch {
            40.
        } else {
            0.
        },
        electrical_phase_mdeg: 0,
        phase_error_mdeg: 1000,
        electrical_speed_rad_s: 0.,
        flux_linkage_wb: 0.05,
    }
}
fn main() {
    println!("case,frames,tracking_error_a,voltage_limited_frames,control_pass,physical_output_authorised");
    for mode in [Mode::Support, Mode::Launch, Mode::Receive] {
        let p = params(if mode == Mode::Support {
            Role::Support
        } else {
            Role::Wayside
        });
        let mut state = State::default();
        let mut abc = [0.; 3];
        let mut last_error = 0.;
        let mut limited = 0;
        for k in 1..=4000 {
            let time = k as f64 * 0.00005;
            let angle = if mode == Mode::Support {
                0.
            } else {
                200. * time
            };
            let mut f = frame(k);
            f.bus_v = if mode == Mode::Support { 96. } else { 1000. };
            f.measured_a = abc;
            f.independent_measured_a = abc;
            let mut d = demand(mode);
            d.electrical_speed_rad_s = if mode == Mode::Support { 0. } else { 200. };
            d.electrical_phase_mdeg = ((angle.to_degrees() % 360.) * 1000.).round() as u32 % 360000;
            let out = evaluate(state, f, d, f.observed_ns, p);
            assert!(out.study_duties.is_some() && !out.physical_output_authorised);
            limited += u32::from(out.voltage_limited);
            if mode == Mode::Support {
                let decay = (-p.resistance_ohm * 0.00005 / p.inductance_h).exp();
                abc[0] =
                    decay * abc[0] + (1. - decay) * out.study_dq_voltage_v[0] / p.resistance_ohm;
                last_error = (abc[0] - d.d_a).abs();
            } else {
                // Independent stationary-alpha/beta exact RL integration. A
                // standard-library trig oracle rotates the PM back-EMF and
                // each commanded dq voltage; the controller uses its polynomial.
                let v = out.study_dq_voltage_v;
                let (s, c) = angle.sin_cos();
                let applied = [v[0] * c - v[1] * s, v[0] * s + v[1] * c];
                let emf = [-200. * 0.05 * s, 200. * 0.05 * c];
                let alpha = (2. * abc[0] - abc[1] - abc[2]) / 3.;
                let beta = (abc[1] - abc[2]) / 3_f64.sqrt();
                let decay = (-p.resistance_ohm * 0.00005 / p.inductance_h).exp();
                let next = [
                    decay * alpha + (1. - decay) * (applied[0] - emf[0]) / p.resistance_ohm,
                    decay * beta + (1. - decay) * (applied[1] - emf[1]) / p.resistance_ohm,
                ];
                abc = [
                    next[0],
                    -0.5 * next[0] + 3_f64.sqrt() / 2. * next[1],
                    -0.5 * next[0] - 3_f64.sqrt() / 2. * next[1],
                ];
                let theta = angle + 200. * 0.00005;
                let (sn, cs) = theta.sin_cos();
                let actual = [next[0] * cs + next[1] * sn, -next[0] * sn + next[1] * cs];
                last_error = (actual[0] - d.d_a).abs().max((actual[1] - d.q_a).abs());
            }
            state = out.state;
        }
        assert!(last_error < 0.3, "{mode:?}: {last_error}");
        println!("{mode:?},4000,{last_error:0.12},{limited},true,false");
    }
    for case in 0..14 {
        let mut f = frame(1);
        let mut d = demand(Mode::Receive);
        let mut now = f.observed_ns;
        match case {
            0 => f.configuration = [1; 32],
            1 => now += 50001,
            2 => f.sensors_healthy = false,
            3 => f.drive_healthy = false,
            4 => f.bus_v = 10.,
            5 => f.winding_temperature_c = 140.,
            6 => f.measured_a[0] = f64::NAN,
            7 => f.independent_measured_a[0] = 2.,
            8 => f.authority_protected = false,
            9 => f.resistor_ready = false,
            10 => f.receiver_ready = false,
            11 => d.phase_error_mdeg = 5001,
            12 => d.q_a = 151.,
            _ => d.q_a = 40.,
        }
        let out = evaluate(State::default(), f, d, now, params(Role::Wayside));
        assert!(
            out.study_duties.is_none()
                && !out.onboard_support_shutdown_requested
                && !out.physical_output_authorised
        );
        println!("negative-{case},1,0,0,true,false");
    }
}
