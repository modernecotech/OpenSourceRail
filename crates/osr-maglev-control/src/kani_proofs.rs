//! Bounded symbolic checks of the current offline interfaces. These properties
//! establish neither target timing nor magnetic stability nor physical release.

#[kani::proof]
#[kani::unwind(40)]
fn kani_maglev_stale_support_requests_fallback() {
    let age: u32 = kani::any();
    kani::assume(age > 1_000_000);
    let p = crate::Params {
        target_gap_um: 10_000,
        minimum_gap_um: 6_000,
        maximum_gap_um: 14_000,
        sensor_disagreement_um: 100,
        maximum_age_ns: 1_000_000,
        maximum_tick_ns: 1_000_000,
        bias_current_ma: 0,
        minimum_current_ma: -20_000,
        maximum_current_ma: 20_000,
        proportional_ma_per_um: 1,
        derivative_ma_per_um_s: 0,
    };
    let input = crate::Inputs {
        issued_ns: 1,
        sequence: 1,
        gap_a_um: 10_000,
        gap_b_um: 10_000,
        sensors_healthy: true,
        drive_healthy: true,
        support_power_available: true,
        traction_requested: true,
        stop_requested: false,
        secured: false,
        stopped: false,
        reset_requested: false,
    };
    let out = crate::evaluate(crate::State::default(), input, 1 + u64::from(age), p);
    assert_eq!(out.state.latched_fault, Some(crate::Fault::Deadline));
    assert_eq!(out.support, crate::Support::LocalFallbackRequired);
    assert!(!out.traction_permitted_in_study && out.controlled_stop_required);
    assert!(!out.physical_output_authorised);
}

#[kani::proof]
#[kani::unwind(40)]
fn kani_maglev_unprotected_launch_has_no_force() {
    use crate::station::*;
    let committed: bool = kani::any();
    let protected: bool = kani::any();
    kani::assume(!committed || !protected);
    let p = StationParams {
        configuration: [1; 32],
        zone_id: 1,
        zone_start_mm: 0,
        zone_end_mm: 350_000,
        train_envelope_mm: 104_500,
        pole_pitch_um: 100_000,
        maximum_age_ns: 100_000,
        maximum_tick_ns: 1_000_000,
        maximum_phase_uncertainty_mdeg: 4_000,
        force_density_n_per_envelope_m: 2_000.,
        force_constant_n_per_a: 10.,
        resistance_ohm: 0.01,
        inductance_h: 0.001,
        flux_linkage_wb: 10. * 0.2 / core::f64::consts::TAU,
        maximum_current_a: 10_000.,
        maximum_phase_voltage_v: 10_000.,
        maximum_copper_loss_w: 1_000_000.,
    };
    let f = StationFrame {
        configuration: [1; 32],
        zone_id: 1,
        sequence: 1,
        observed_ns: 1_000,
        position_mm: 104_500,
        velocity_mmps: 0,
        position_uncertainty_um: 1,
        timestamp_uncertainty_ns: 1,
        phase_offset_mdeg: 0,
        overlap_mm: 104_500,
        force_demand_n: 10_000.,
        mode: StationMode::Launch,
        launch_committed: committed,
        arrival_resources_protected: protected,
        receiver_healthy: true,
        sensors_healthy: true,
        drive_healthy: true,
        brake_resistor_ready: true,
    };
    let out = evaluate_station(StationState::default(), f, 1_000, p);
    assert_eq!(out.state.latched_fault, Some(StationFault::Authority));
    assert_eq!(out.study_force_n, 0.);
    assert_eq!(out.study_current_a, 0.);
    assert!(!out.study_command_feasible);
    assert!(!out.onboard_support_shutdown_requested && !out.physical_output_authorised);
}

#[kani::proof]
#[kani::unwind(40)]
fn kani_maglev_replayed_drive_frame_has_no_duties() {
    use crate::drives::*;
    let last: u64 = kani::any();
    let sequence: u64 = kani::any();
    kani::assume(sequence <= last);
    let p = Params {
        configuration: [1; 32],
        role: Role::Support,
        resistance_ohm: 0.2,
        inductance_h: 0.01,
        kp_v_per_a: 1.,
        ki_v_per_a_s: 1.,
        maximum_current_a: 40.,
        current_disagreement_a: 1.,
        maximum_temperature_c: 120.,
        minimum_bus_v: 20.,
        maximum_bus_v: 100.,
        maximum_age_ns: 100_000,
        maximum_tick_ns: 100_000,
        maximum_phase_error_mdeg: 4_000,
    };
    let f = Frame {
        configuration: [1; 32],
        sequence,
        observed_ns: 1_000,
        measured_a: [0.; 3],
        independent_measured_a: [0.; 3],
        bus_v: 48.,
        winding_temperature_c: 30.,
        sensors_healthy: true,
        drive_healthy: true,
        authority_protected: true,
        receiver_ready: true,
        resistor_ready: true,
        launch_committed: true,
        moving: true,
        stopped_and_secured: false,
        reset_requested: false,
    };
    let d = Demand {
        mode: Mode::Support,
        d_a: 10.,
        q_a: 0.,
        electrical_phase_mdeg: 0,
        phase_error_mdeg: 0,
        electrical_speed_rad_s: 0.,
        flux_linkage_wb: 0.,
    };
    let previous = State {
        last_sequence: Some(last),
        ..State::default()
    };
    let out = evaluate(previous, f, d, 1_000, p);
    assert_eq!(out.state.fault, Some(Fault::Time));
    assert!(out.study_duties.is_none() && out.local_support_fallback_required);
    assert!(!out.onboard_support_shutdown_requested && !out.physical_output_authorised);
}
