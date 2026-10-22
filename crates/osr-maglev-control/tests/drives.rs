use osr_maglev_control::drives::*;
fn p(role: Role) -> Params {
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
fn f() -> Frame {
    Frame {
        configuration: [9; 32],
        sequence: 1,
        observed_ns: 50000,
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
fn d(mode: Mode) -> Demand {
    Demand {
        mode,
        d_a: if mode == Mode::Support { 40. } else { 0. },
        q_a: if mode == Mode::Support { 0. } else { 40. },
        electrical_phase_mdeg: 0,
        phase_error_mdeg: 1000,
        electrical_speed_rad_s: 0.,
        flux_linkage_wb: 0.05,
    }
}

#[test]
fn trigonometry_matches_independent_std_oracle() {
    for angle in (0..720000).step_by(17) {
        let (s, c) = sin_cos_mdeg(angle);
        let a = f64::from(angle % 360000) * std::f64::consts::PI / 180000.;
        assert!((s - a.sin()).abs() < 1e-9);
        assert!((c - a.cos()).abs() < 1e-9);
    }
    for scale in [0., 1e-100, 1., 1e21, 1e100] {
        for a in [-3., -1., 0., 0.1, 1., 3.] {
            for b in [-3., -1., 0., 0.1, 1., 3.] {
                let value: [f64; 2] = [scale * a, scale * b];
                let expected = value[0].hypot(value[1]);
                assert!((vector_magnitude(value) - expected).abs() <= expected * 1e-14);
            }
        }
    }
}
#[test]
fn transforms_reconstruct_currents_and_power_at_all_phases() {
    for a in (0..360000).step_by(311) {
        let i = [12., -19.];
        let v = [-7., 23.];
        let abc = dq_to_abc(i, a);
        let back = abc_to_dq(abc, a);
        assert!((back[0] - i[0]).abs() < 1e-7 && (back[1] - i[1]).abs() < 1e-7);
        let vab = dq_to_abc(v, a);
        let power: f64 = abc.iter().zip(vab).map(|(x, y)| x * y).sum();
        assert!((power - 1.5 * (i[0] * v[0] + i[1] * v[1])).abs() < 1e-6);
    }
}
#[test]
fn support_pi_tracks_exact_rl_plant_and_negative_current() {
    for target in [-40., 40.] {
        let pp = p(Role::Support);
        let mut state = State::default();
        let mut current = 0.;
        for k in 1..=4000 {
            let mut frame = f();
            frame.sequence = k;
            frame.observed_ns = k * 50000;
            frame.measured_a[0] = current;
            frame.independent_measured_a[0] = current;
            let mut demand = d(Mode::Support);
            demand.d_a = target;
            let out = evaluate(state, frame, demand, frame.observed_ns, pp);
            assert!(!out.physical_output_authorised && !out.local_support_fallback_required);
            assert!(!out.onboard_support_shutdown_requested);
            let voltage = out.study_dq_voltage_v[0];
            let decay = (-pp.resistance_ohm * 0.00005 / pp.inductance_h).exp();
            current = decay * current + (1. - decay) * voltage / pp.resistance_ohm;
            state = out.state;
        }
        assert!((current - target).abs() < 0.02);
    }
}
#[test]
fn antiwindup_limits_integral_and_recovers_after_saturation() {
    let pp = p(Role::Support);
    let mut state = State::default();
    let mut demand = d(Mode::Support);
    demand.d_a = 140.;
    for k in 1..1000 {
        let mut frame = f();
        frame.sequence = k;
        frame.observed_ns = k * 50000;
        let out = evaluate(state, frame, demand, frame.observed_ns, pp);
        assert!(out.voltage_limited);
        assert!(out.state.integral_v[0].abs() <= 0.9 * frame.bus_v);
        state = out.state;
    }
    let mut frame = f();
    frame.sequence = 1000;
    frame.observed_ns = 50000000;
    demand.d_a = 0.;
    let out = evaluate(state, frame, demand, frame.observed_ns, pp);
    assert!(!out.voltage_limited);
}
#[test]
fn faults_latch_require_secure_zero_demand_reset_and_do_not_zero_support() {
    let pp = p(Role::Support);
    let mut frame = f();
    frame.sensors_healthy = false;
    let bad = evaluate(State::default(), frame, d(Mode::Support), 50000, pp);
    assert!(bad.local_support_fallback_required && bad.study_duties.is_none());
    frame.sequence = 2;
    frame.observed_ns = 100000;
    frame.sensors_healthy = true;
    let held = evaluate(bad.state, frame, d(Mode::Support), 100000, pp);
    assert!(held.study_duties.is_none());
    frame.sequence = 3;
    frame.observed_ns = 150000;
    frame.reset_requested = true;
    frame.stopped_and_secured = true;
    frame.moving = false;
    let mut zero = d(Mode::Support);
    zero.d_a = 0.;
    let reset = evaluate(held.state, frame, zero, 150000, pp);
    assert!(reset.state.fault.is_none() && reset.study_duties.is_some());
}
#[test]
fn current_sensor_deadline_identity_thermal_and_bus_adversaries_hold() {
    for role in [Role::Support, Role::Wayside] {
        for case in 0..11 {
            let pp = p(role);
            let mut frame = f();
            let demand = d(if role == Role::Support {
                Mode::Support
            } else {
                Mode::Launch
            });
            let mut now = 50000;
            match case {
                0 => frame.configuration = [3; 32],
                1 => now = 100001,
                2 => frame.measured_a[0] = f64::NAN,
                3 => frame.independent_measured_a[0] = 2.,
                4 => {
                    frame.measured_a[0] = 151.;
                    frame.independent_measured_a[0] = 151.;
                }
                5 => frame.winding_temperature_c = 121.,
                6 => frame.bus_v = 20.,
                7 => frame.bus_v = 1200.,
                8 => frame.drive_healthy = false,
                9 => frame.sequence = 0,
                _ => frame.observed_ns = 50001,
            }
            let out = evaluate(State::default(), frame, demand, now, pp);
            assert!(out.study_duties.is_none());
            assert!(!out.physical_output_authorised && !out.onboard_support_shutdown_requested);
            assert_eq!(out.local_support_fallback_required, role == Role::Support);
        }
    }
}
#[test]
fn replay_and_late_ticks_cannot_reset_the_last_good_clock() {
    let pp = p(Role::Support);
    let good = evaluate(State::default(), f(), d(Mode::Support), 50000, pp);
    let replay = evaluate(good.state, f(), d(Mode::Support), 100000, pp);
    assert_eq!(replay.state.last_sequence, Some(1));
    assert!(replay.study_duties.is_none());
    let mut frame = f();
    frame.sequence = 2;
    frame.observed_ns = 200000;
    assert!(evaluate(good.state, frame, d(Mode::Support), 200000, pp)
        .study_duties
        .is_none());
}
#[test]
fn receive_requires_resistor_and_authority_and_never_shuts_down_support() {
    let pp = p(Role::Wayside);
    let mut dd = d(Mode::Receive);
    dd.q_a = -40.;
    for case in 0..5 {
        let mut frame = f();
        let mut demand = dd;
        match case {
            0 => frame.resistor_ready = false,
            1 => frame.authority_protected = false,
            2 => frame.receiver_ready = false,
            3 => demand.phase_error_mdeg = 5001,
            _ => demand.q_a = 40.,
        }
        let out = evaluate(State::default(), frame, demand, 50000, pp);
        assert!(out.study_duties.is_none() && out.independent_stopping_required);
        assert!(!out.onboard_support_shutdown_requested);
    }
    let nominal = evaluate(State::default(), f(), dd, 50000, pp);
    assert!(nominal.study_duties.is_some());
    assert!(nominal.study_dq_voltage_v[1] < 0.);
}
#[test]
fn three_phase_duties_remain_bounded_and_coast_has_no_stator_output() {
    for a in (0..360000).step_by(509) {
        let mut frame = f();
        frame.bus_v = 1000.;
        let mut dd = d(Mode::Launch);
        dd.electrical_phase_mdeg = a;
        let out = evaluate(State::default(), frame, dd, 50000, p(Role::Wayside));
        assert!(out
            .study_duties
            .unwrap()
            .iter()
            .all(|v| *v >= 0. && *v <= 1.));
        assert!(!out.physical_output_authorised);
    }
    let mut saturated = d(Mode::Launch);
    saturated.q_a = 140.;
    saturated.electrical_speed_rad_s = 2000.;
    let out = evaluate(State::default(), f(), saturated, 50000, p(Role::Wayside));
    assert!(out.voltage_limited);
    let measured = out.study_dq_voltage_v[0].hypot(out.study_dq_voltage_v[1]);
    assert!((measured - f().bus_v / 3_f64.sqrt() * 0.95).abs() < 1e-9);
    let mut dd = d(Mode::Coast);
    dd.q_a = 0.;
    let out = evaluate(State::default(), f(), dd, 50000, p(Role::Wayside));
    assert!(out.study_duties.is_none() && !out.onboard_support_shutdown_requested);
}
