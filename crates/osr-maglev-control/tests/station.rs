use osr_maglev_control::station::*;

fn params() -> StationParams {
    StationParams {
        configuration: [7; 32],
        zone_id: 1,
        zone_start_mm: -125000,
        zone_end_mm: 75000,
        train_envelope_mm: 104500,
        pole_pitch_um: 250000,
        maximum_age_ns: 100000,
        maximum_tick_ns: 2000000,
        maximum_phase_uncertainty_mdeg: 5000,
        force_density_n_per_envelope_m: 4000.,
        force_constant_n_per_a: 50.,
        resistance_ohm: 0.0025,
        inductance_h: 0.000025,
        flux_linkage_wb: 50. * 0.5 / core::f64::consts::TAU,
        maximum_current_a: 4000.,
        maximum_phase_voltage_v: 900.,
        maximum_copper_loss_w: 120000.,
    }
}
fn frame() -> StationFrame {
    StationFrame {
        configuration: [7; 32],
        zone_id: 1,
        sequence: 1,
        observed_ns: 1000000,
        position_mm: 0,
        velocity_mmps: 15000,
        position_uncertainty_um: 100,
        timestamp_uncertainty_ns: 1000,
        phase_offset_mdeg: 0,
        overlap_mm: 72000,
        force_demand_n: 134150.,
        mode: StationMode::Launch,
        launch_committed: true,
        arrival_resources_protected: true,
        receiver_healthy: true,
        sensors_healthy: true,
        drive_healthy: true,
        brake_resistor_ready: true,
    }
}
fn tick(f: StationFrame) -> StationOutput {
    evaluate_station(StationState::default(), f, 1000000, params())
}

#[test]
fn bounded_launch_and_receiving_brake_are_offline_and_do_not_cut_support() {
    let a = tick(frame());
    assert!(a.study_command_feasible);
    assert_eq!(a.study_force_n, 134150.);
    assert_eq!(a.electrical_phase_mdeg, Some(0));
    let mut f = frame();
    f.mode = StationMode::Receive;
    f.force_demand_n = -90000.;
    let b = tick(f);
    assert!(b.study_command_feasible && b.study_current_a < 0.);
    assert!(!b.physical_output_authorised && !b.onboard_support_shutdown_requested);
    f.brake_resistor_ready = false;
    let failed = tick(f);
    assert_eq!(failed.state.latched_fault, Some(StationFault::Receiver));
    assert!(failed.independent_recovery_required);
    assert_eq!(failed.study_force_n, 0.);
}

#[test]
fn phase_uses_predicted_position_with_an_independent_uncertainty_bound() {
    let p = params();
    let mut f = frame();
    f.position_mm = 1;
    let out = evaluate_station(StationState::default(), f, 1050000, p);
    assert_eq!(out.electrical_phase_mdeg, Some(1260)); // 1 mm + 0.75 mm prediction
    f.position_uncertainty_um = 10000;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::StalePhase));
    f = frame();
    f.timestamp_uncertainty_ns = 1_000_000;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::StalePhase));
    let stale = evaluate_station(StationState::default(), frame(), 1100001, p);
    assert_eq!(stale.state.latched_fault, Some(StationFault::StalePhase));
}

#[test]
fn replay_identity_faults_and_uncommitted_arrival_cannot_supply_thrust() {
    let start = tick(frame());
    let replay = evaluate_station(start.state, frame(), 1000001, params());
    assert_eq!(
        replay.state.latched_fault,
        Some(StationFault::ClockOrReplay)
    );
    for bad in 0..4 {
        let mut f = frame();
        match bad {
            0 => f.configuration = [8; 32],
            1 => f.zone_id = 2,
            2 => f.launch_committed = false,
            _ => f.arrival_resources_protected = false,
        }
        assert!(!tick(f).study_command_feasible);
    }
    let mut f = frame();
    f.sequence = 2;
    f.observed_ns = 2000000;
    let later = evaluate_station(replay.state, f, 2000000, params());
    assert_eq!(later.state.latched_fault, Some(StationFault::ClockOrReplay));
}

#[test]
fn no_propulsion_while_coasting_and_overlap_is_checked_against_the_train_envelope() {
    let mut f = frame();
    f.mode = StationMode::Coast;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Direction));
    f.force_demand_n = 0.;
    f.overlap_mm = 0;
    assert!(tick(f).study_command_feasible);
    f = frame();
    f.overlap_mm = 1000;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Overlap));
    f = frame();
    f.position_mm = 500000; // completely beyond the winding
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Overlap));
    f = frame();
    f.velocity_mmps = -1;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Direction));
    f = frame();
    f.mode = StationMode::Receive;
    f.force_demand_n = -1.;
    f.velocity_mmps = 0;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Direction));
}

#[test]
fn current_voltage_and_repeated_heat_hypotheses_are_independent_limits() {
    for bad in 0..3 {
        let mut p = params();
        match bad {
            0 => p.maximum_current_a = 100.,
            1 => p.maximum_phase_voltage_v = 10.,
            _ => p.maximum_copper_loss_w = 10.,
        }
        let out = evaluate_station(StationState::default(), frame(), 1000000, p);
        assert_eq!(
            out.state.latched_fault,
            Some(match bad {
                0 => StationFault::Current,
                1 => StationFault::Voltage,
                _ => StationFault::Thermal,
            })
        );
        assert_eq!(out.study_current_a, 0.);
        assert_eq!(out.study_force_n, 0.);
    }
}

#[test]
fn nonfinite_and_extreme_inputs_remain_bounded_without_a_physical_enable() {
    let mut f = frame();
    f.force_demand_n = f64::NAN;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Sensors));
    f = frame();
    f.position_mm = i64::MIN;
    assert!(!tick(f).study_command_feasible);
    let mut p = params();
    p.force_constant_n_per_a = f64::MIN_POSITIVE;
    let out = evaluate_station(StationState::default(), frame(), 1000000, p);
    assert_eq!(out.state.latched_fault, Some(StationFault::Parameters));
    assert!(!out.physical_output_authorised);
    assert!(out.study_voltage_bound_v.is_finite());
}

#[test]
fn equivalent_motor_constants_preserve_air_gap_power_and_reject_free_energy() {
    let p = params();
    let f = frame();
    let output = tick(f);
    let velocity = f64::from(f.velocity_mmps) / 1000.;
    let emf = p.flux_linkage_wb * core::f64::consts::TAU * velocity
        / (2. * f64::from(p.pole_pitch_um) * 1e-6);
    assert!((emf * output.study_current_a - output.study_force_n * velocity).abs() < 1e-6);
    let mut impossible = p;
    impossible.flux_linkage_wb *= 0.01;
    let rejected = evaluate_station(StationState::default(), f, 1000000, impossible);
    assert_eq!(rejected.state.latched_fault, Some(StationFault::Parameters));
    assert!(!rejected.study_command_feasible && !rejected.physical_output_authorised);
}

#[test]
fn positioning_is_bounded_separately_from_receiving_braking() {
    let mut f = frame();
    f.mode = StationMode::Berth;
    f.position_mm = -100;
    f.velocity_mmps = 100;
    f.force_demand_n = 5000.;
    assert!(tick(f).study_command_feasible);
    for case in 0..3 {
        let mut bad = f;
        match case {
            0 => bad.velocity_mmps = 501,
            1 => bad.position_mm = 2001,
            _ => bad.force_demand_n = 20001.,
        }
        assert_eq!(tick(bad).state.latched_fault, Some(StationFault::Direction));
    }
    f.mode = StationMode::Receive;
    assert_eq!(tick(f).state.latched_fault, Some(StationFault::Direction));
}
