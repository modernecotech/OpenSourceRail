//! Machine-readable offline counterexamples; scalar unmeasured motor maps.
use osr_maglev_control::station::*;

fn main() {
    let p = StationParams {
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
        force_constant_n_per_a: 200.,
        resistance_ohm: 0.01,
        inductance_h: 0.0001,
        flux_linkage_wb: 0.2,
        maximum_current_a: 1000.,
        maximum_phase_voltage_v: 800.,
        maximum_copper_loss_w: 20000.,
    };
    let frame = StationFrame {
        configuration: p.configuration,
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
    };
    let start = evaluate_station(StationState::default(), frame, 1000000, p);
    let replay = evaluate_station(start.state, frame, 1000001, p);
    let stale = evaluate_station(StationState::default(), frame, 1100001, p);
    let mut coast = frame;
    coast.mode = StationMode::Coast;
    coast.force_demand_n = 0.;
    coast.overlap_mm = 0;
    let coast_out = evaluate_station(StationState::default(), coast, 1000000, p);
    let mut receive = frame;
    receive.mode = StationMode::Receive;
    receive.force_demand_n = -90000.;
    let brake = evaluate_station(StationState::default(), receive, 1000000, p);
    receive.brake_resistor_ready = false;
    let failed_receiver = evaluate_station(StationState::default(), receive, 1000000, p);
    let mut uncommitted = frame;
    uncommitted.launch_committed = false;
    let denied = evaluate_station(StationState::default(), uncommitted, 1000000, p);
    let mut short = frame;
    short.overlap_mm = 1000;
    let limited = evaluate_station(StationState::default(), short, 1000000, p);
    let checks = [
        start.study_command_feasible,
        replay.state.latched_fault == Some(StationFault::ClockOrReplay),
        stale.state.latched_fault == Some(StationFault::StalePhase),
        coast_out.study_command_feasible && coast_out.study_force_n == 0.,
        brake.study_command_feasible && brake.study_force_n < 0.,
        failed_receiver.independent_recovery_required,
        !denied.study_command_feasible,
        !limited.study_command_feasible,
        !start.physical_output_authorised && !failed_receiver.onboard_support_shutdown_requested,
    ];
    assert!(checks.iter().all(|v| *v));
    println!("{{\"schema\":\"osr-station-control-replay/1\",\"checks\":{{\"launch\":{},\"replay_rejected\":{},\"stale_phase_rejected\":{},\"zero_thrust_coast\":{},\"resistor_braking\":{},\"receiver_fault_requires_independent_recovery\":{},\"uncommitted_launch_rejected\":{},\"insufficient_overlap_rejected\":{},\"physical_outputs_disabled_and_support_preserved\":{}}},\"launch_current_a\":{},\"launch_phase_mdeg\":{},\"voltage_bound_v\":{},\"copper_loss_w\":{},\"all_passed\":{},\"physical_output_authorised\":false,\"measured_motor_map\":false,\"scope\":\"offline scalar force/current/phase and fault screens; no MCU timing, shared-field or six-car phase validation\"}}",
        checks[0],checks[1],checks[2],checks[3],checks[4],checks[5],checks[6],checks[7],checks[8],
        start.study_current_a,start.electrical_phase_mdeg.unwrap_or(0),start.study_voltage_bound_v,start.study_copper_loss_w,checks.iter().all(|v|*v));
}
