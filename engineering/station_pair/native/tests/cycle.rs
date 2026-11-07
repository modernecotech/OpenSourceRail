#![recursion_limit = "256"]
use osr_journey::{cycle::*, *};
fn near(a: f64, b: f64) {
    assert!((a - b).abs() < 1e-5, "{a} != {b}");
}
fn journey(id: &str) -> Case {
    serde_json::from_value(serde_json::json!({
        "id":id,"candidate_id":"a".repeat(64),"mass_kg":1000.,"rotating_equivalent_mass_kg":0.,
        "distance_m":1000.,"grade_fraction":0.,"rolling_coefficient":0.,"air_density_kg_m3":1.2,
        "cd_a_m2":0.,"headwind_m_s":0.,"speed_cap_m_s":15.,"acceleration_request_m_s2":2.,
        "comfort_jerk_m_s3":0.5,"brake_start_m":800.,"berth_tolerance_m":1.,
        "brake_force_cap_n":2000.,"brake_adhesion_force_cap_n":2000.,"brake_latency_s":0.,"brake_rise_s":0.,
        "dt_s":0.01,"max_time_s":300.,"dwell_s":20.,"headway_s":250.,"auxiliary_power_w":0.,
        "drive":{"points":[{"speed_m_s":0.,"force_n":1000.},{"speed_m_s":100.,"force_n":1000.}],
            "windows_m":[[0.,1000.]],"maximum_speed_m_s":100.,"mechanical_power_w":1e9,
            "electrical_efficiency":0.8,"grid_power_w":1e9,"contact_force_cap_n":1e9,
            "external_mass_kg":0.,"external_resistance_n":0.},
        "fault":{"power_loss_at_s":null,"failed_drive_fraction":0.,"emergency_at_m":null},"thermal":null,
        "control":{"policy_id":"fixture","mass_lower_kg":900.,"mass_upper_kg":1200.,"rotating_mass_upper_kg":50.,
            "external_mass_upper_kg":0.,"brake_force_lower_bound_n":1500.,"grade_estimate_fraction":0.,"grade_error_bound":0.001,
            "position_error_bound_m":0.05,"speed_error_bound_m_s":0.02,"acceleration_error_bound_m_s2":0.01,
            "position_bias_m":0.,"speed_bias_m_s":0.,"acceleration_bias_m_s2":0.,"reaction_time_bound_s":0.2,
            "brake_rise_time_bound_s":0.2,"stopping_margin_m":0.3,"end_of_authority_m":1000.,"initial_hold_applied":true,
            "start_traction_lower_bound_n":1000.,"rolling_resistance_upper_n":50.,"external_resistance_upper_n":0.,
            "positive_acceleration_bound_m_s2":3.,"drive_fault_observed":false}
    })).unwrap()
}
fn station(id: &str) -> Station {
    Station {
        id: id.into(),
        initial_energy_j: 0.,
        store: Store {
            capacity_j: 100000.,
            capture_efficiency: 0.8,
            release_efficiency: 0.7,
            leakage_per_s: 1e-5,
        },
        capture_stages: vec![
            Transfer {
                start_m: 700.,
                end_m: 850.,
                max_force_n: 500.,
                max_power_w: 5000.,
            },
            Transfer {
                start_m: 850.,
                end_m: 1000.,
                max_force_n: 500.,
                max_power_w: 5000.,
            },
        ],
        release: Transfer {
            start_m: 0.,
            end_m: 200.,
            max_force_n: 600.,
            max_power_w: 6000.,
        },
        reset: Reset {
            duration_s: 10.,
            grid_energy_j: 1000.,
            grid_power_w: 100.,
        },
    }
}
fn cycle() -> CycleCase {
    CycleCase {
        id: "cycle".into(),
        candidate_id: "a".repeat(64),
        stations: vec![station("A"), station("B")],
        release_control: None,
        legs: (0..4)
            .map(|i| Leg {
                train_id: "same-point-train".into(),
                journey: journey(&format!("leg{i}")),
                departure_station_id: if i % 2 == 0 { "A" } else { "B" }.into(),
                arrival_station_id: if i % 2 == 0 { "B" } else { "A" }.into(),
                departure_time_s: i as f64 * 250.,
                departure_authorized: true,
                capture_failed: false,
                release_failed: false,
                reset_failed: false,
            })
            .collect(),
    }
}
#[test]
fn empty_cold_start_captures_at_receiver_and_later_releases() {
    let c = cycle();
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.state, "sequence-complete");
    assert_eq!(r.arrived_legs, 4);
    near(r.legs[0].energy.delivered_launch_work_j, 0.);
    assert!(r.legs[0].energy.capture_work_j > 0.);
    assert!(r.legs[1].energy.delivered_launch_work_j > 0.);
    assert!(r.legs[0].station_states[1].energy_j > 0.);
    assert_eq!(r.legs[1].departure_station_id, "B");
    near(r.ledger.storage_balance_residual_j, 0.);
    near(r.ledger.train_and_storage_balance_residual_j, 0.);
    assert!(!r.physical_accepted && !r.same_train_circulation_verified);
}
#[test]
fn actual_stop_offset_carries_without_position_snap() {
    let r = osr_journey::cycle::evaluate(&cycle()).unwrap();
    for pair in r.legs.windows(2) {
        near(
            pair[1].initial_position_m,
            1000. - pair[0].journey.as_ref().unwrap().final_position_m,
        );
        assert!(pair[1].initial_position_m > 0.);
    }
}
#[test]
fn capture_bypass_does_not_change_motion_or_independent_braking() {
    let mut c = cycle();
    c.legs.truncate(1);
    c.legs[0].capture_failed = true;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let baseline = osr_journey::evaluate(&c.legs[0].journey).unwrap();
    let j = r.legs[0].journey.as_ref().unwrap();
    near(j.final_position_m, baseline.final_position_m);
    near(j.brake_heat_j, baseline.brake_heat_j);
    near(r.ledger.capture_work_j, 0.);
    assert!(r.ledger.bypassed_capture_work_j > 0.);
}
#[test]
fn full_receiver_bypasses_to_friction_without_double_counting() {
    let mut c = cycle();
    c.legs.truncate(1);
    c.stations[1].initial_energy_j = 100000.;
    c.stations[1].store.leakage_per_s = 0.;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    near(r.ledger.capture_work_j, 0.);
    assert!(r.ledger.bypassed_capture_work_j > 0.);
    assert!(r.legs[0].journey.as_ref().unwrap().normal_numerical_arrival);
    near(r.ledger.train_and_storage_balance_residual_j, 0.);
}
#[test]
fn capacity_efficiency_and_power_limits_apply_to_actual_steps() {
    let c = cycle();
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    for l in &r.legs {
        assert!(l.energy.maximum_capture_force_n <= 500. + 1e-7);
        assert!(l.energy.maximum_capture_power_w <= 5000. + 1e-7);
        assert!(l.energy.maximum_release_force_n <= 600. + 1e-7);
        assert!(l.energy.maximum_release_power_w <= 6000. + 1e-7);
        near(l.energy.stored_capture_j, l.energy.capture_work_j * 0.8);
        near(
            l.energy.delivered_launch_work_j,
            l.energy.released_from_store_j * 0.7,
        );
        assert!(
            l.station_states
                .iter()
                .all(|s| s.energy_j >= 0. && s.energy_j <= 100000.)
        );
        assert!(
            l.energy
                .trace
                .iter()
                .filter(|p| p.position_m > 200.01)
                .all(|p| p.store_traction_n == 0.)
        );
    }
}
#[test]
fn unauthorized_departure_preserves_locked_energy() {
    let mut c = cycle();
    c.stations[0].initial_energy_j = 50000.;
    c.legs[0].departure_authorized = false;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.state, "sequence-held");
    assert_eq!(r.executed_legs, 0);
    near(r.station_states[0].energy_j, 50000.);
    near(r.ledger.grid_traction_energy_j, 0.);
}
#[test]
fn release_failure_cannot_draw_store() {
    let mut c = cycle();
    c.legs.truncate(1);
    c.stations[0].initial_energy_j = 50000.;
    c.legs[0].release_failed = true;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    near(r.ledger.delivered_launch_work_j, 0.);
    near(r.ledger.released_from_store_j, 0.);
    assert!(r.legs[0].journey.as_ref().unwrap().normal_numerical_arrival);
}
#[test]
fn grid_power_loss_blocks_release_and_commands_independent_brake() {
    let mut c = cycle();
    c.legs.truncate(1);
    c.stations[0].initial_energy_j = 100000.;
    c.legs[0].journey.fault.power_loss_at_s = Some(10.);
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.state, "journey-held");
    let l = &r.legs[0];
    assert!(
        l.energy
            .trace
            .iter()
            .filter(|p| p.time_s > 10.05)
            .all(|p| p.store_traction_n == 0.)
    );
    assert!(!l.journey.as_ref().unwrap().normal_numerical_arrival);
    near(r.ledger.train_and_storage_balance_residual_j, 0.);
}
#[test]
fn reset_failure_holds_onward_departure() {
    let mut c = cycle();
    c.legs[0].reset_failed = true;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.executed_legs, 1);
    assert_eq!(r.legs[1].state, "departure-held");
    assert!(!r.station_states[1].ready);
    near(r.ledger.reset_grid_energy_j, 0.);
}
#[test]
fn reset_requires_energy_power_duration_budget() {
    let mut c = cycle();
    c.stations[1].reset.grid_power_w = 1.;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.executed_legs, 1);
    assert!(!r.station_states[1].ready);
}
#[test]
fn dwell_and_travel_leakage_ages_both_stations() {
    let mut c = cycle();
    c.legs.truncate(1);
    c.stations[0].initial_energy_j = 50000.;
    c.stations[1].initial_energy_j = 50000.;
    c.legs[0].release_failed = true;
    c.legs[0].capture_failed = true;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let t = r.legs[0].end_time_s;
    near(r.station_states[0].energy_j, 50000. * (-1e-5 * t).exp());
    near(r.station_states[1].energy_j, 50000. * (-1e-5 * t).exp());
    near(r.ledger.storage_balance_residual_j, 0.);
}
#[test]
fn schedule_cannot_spend_future_capture_before_arrival() {
    let mut c = cycle();
    c.legs[1].departure_time_s = 10.;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.executed_legs, 1);
    assert_eq!(r.legs[1].state, "departure-held");
}
#[test]
fn missing_arrival_never_teleports_to_next_leg() {
    let mut c = cycle();
    c.legs[0].journey.max_time_s = 10.;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.state, "journey-held");
    assert_eq!(r.legs.len(), 1);
    assert!(!r.station_states[1].ready);
}
#[test]
fn absent_module_is_explicit_zero_hardware_and_matches_old_first_leg() {
    let mut c = cycle();
    c.legs.truncate(1);
    for s in &mut c.stations {
        s.store.capacity_j = 0.;
        s.release.max_force_n = 0.;
        for q in &mut s.capture_stages {
            q.max_force_n = 0.;
        }
        s.reset.grid_energy_j = 0.;
        s.reset.duration_s = 0.;
    }
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let old = osr_journey::evaluate(&c.legs[0].journey).unwrap();
    assert_eq!(
        serde_json::to_value(&r.legs[0].journey).unwrap(),
        serde_json::to_value(Some(old)).unwrap()
    );
    near(r.ledger.final_store_j, 0.);
    near(r.ledger.delivered_launch_work_j, 0.);
}
#[test]
fn zero_capacity_cannot_hide_active_hardware_or_initial_energy() {
    let mut c = cycle();
    c.stations[0].store.capacity_j = 0.;
    assert!(osr_journey::cycle::evaluate(&c).is_err());
    c.stations[0].release.max_force_n = 0.;
    for q in &mut c.stations[0].capture_stages {
        q.max_force_n = 0.;
    }
    c.stations[0].initial_energy_j = 1.;
    assert!(osr_journey::cycle::evaluate(&c).is_err());
}
#[test]
fn no_recovery_request_is_unchanged_by_cycle_evaluation() {
    let c = cycle();
    let before = serde_json::to_value(osr_journey::evaluate(&c.legs[0].journey).unwrap()).unwrap();
    let _ = osr_journey::cycle::evaluate(&c).unwrap();
    let after = serde_json::to_value(osr_journey::evaluate(&c.legs[0].journey).unwrap()).unwrap();
    assert_eq!(before, after);
}
#[test]
fn arbitrarily_small_store_cannot_supply_more_energy_than_available() {
    let mut c = cycle();
    c.legs.truncate(1);
    for s in &mut c.stations {
        s.store.capacity_j = 0.01;
    }
    c.stations[0].initial_energy_j = 0.01;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert!(r.ledger.released_from_store_j <= 0.01 + 1e-9);
    near(r.ledger.storage_balance_residual_j, 0.);
    near(r.ledger.train_and_storage_balance_residual_j, 0.);
}
#[test]
fn long_launcher_reset_cannot_be_bypassed_by_next_departure() {
    let mut c = cycle();
    c.stations[0].initial_energy_j = 100000.;
    c.stations[0].reset.duration_s = 500.;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    assert_eq!(r.executed_legs, 1);
    assert_eq!(r.legs[1].state, "departure-held");
    assert!(
        r.legs[0]
            .events
            .iter()
            .any(|e| e.kind == "launcher-reset-complete-assumed")
    );
    near(r.ledger.reset_grid_energy_j, 2000.);
}
#[test]
fn emergency_blocks_store_release_and_preserves_independent_stop() {
    let mut c = cycle();
    c.legs.truncate(1);
    c.stations[0].initial_energy_j = 100000.;
    c.legs[0].journey.fault.emergency_at_m = Some(50.);
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let l = &r.legs[0];
    assert!(!l.journey.as_ref().unwrap().normal_numerical_arrival);
    assert!(
        l.energy
            .trace
            .iter()
            .filter(|p| p.position_m > 50.01)
            .all(|p| p.store_traction_n == 0.)
    );
    assert!(r.ledger.unperformed_reset_grid_energy_j > 0.);
}
#[test]
fn timestep_refinement_retains_controller_and_conserves_energy() {
    let c = cycle();
    let a = osr_journey::cycle::evaluate(&c).unwrap();
    let mut d = c.clone();
    for l in &mut d.legs {
        l.journey.dt_s *= 0.5;
    }
    let b = osr_journey::cycle::evaluate(&d).unwrap();
    assert_eq!(a.arrived_legs, b.arrived_legs);
    near(b.ledger.storage_balance_residual_j, 0.);
    near(b.ledger.train_and_storage_balance_residual_j, 0.);
    assert!(
        (a.ledger.delivered_launch_work_j - b.ledger.delivered_launch_work_j).abs()
            < 0.02 * a.ledger.delivered_launch_work_j
    );
    for l in &b.legs {
        near(l.energy.storage_balance_residual_j, 0.);
    }
}
#[test]
fn cold_capture_allocation_does_not_change_the_mechanical_stopping_trace() {
    let mut c = cycle();
    c.legs.truncate(1);
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let baseline = osr_journey::evaluate(&c.legs[0].journey).unwrap();
    let got = r.legs[0].journey.as_ref().unwrap();
    assert_eq!(
        serde_json::to_value(&got.trace).unwrap(),
        serde_json::to_value(&baseline.trace).unwrap()
    );
    assert_eq!(got.elapsed_s, baseline.elapsed_s);
    assert_eq!(got.final_position_m, baseline.final_position_m);
    near(
        got.brake_heat_j + r.ledger.capture_work_j,
        baseline.brake_heat_j,
    );
}
fn controlled_cycle() -> CycleCase {
    let mut c = cycle();
    c.release_control = Some(ReleaseControl {
        mode: "grid-substitution-slew/1".into(),
        force_slew_n_s: 100.,
        maximum_traction_share: 0.8,
        reserve_factor: 2.,
        cutoff_audit: false,
    });
    c.legs = (0..8)
        .map(|i| {
            let mut l = c.legs[i % 4].clone();
            l.journey.id = format!("controlled-leg-{i}");
            l.departure_time_s = i as f64 * 250.;
            l
        })
        .collect();
    c
}
#[test]
fn controlled_release_preserves_actual_motion_and_reduces_grid_work_without_boost() {
    let c = controlled_cycle();
    let mut disabled = c.clone();
    for l in &mut disabled.legs {
        l.capture_failed = true;
        l.release_failed = true;
    }
    let a = osr_journey::cycle::evaluate(&c).unwrap();
    let b = osr_journey::cycle::evaluate(&disabled).unwrap();
    assert_eq!(a.arrived_legs, 8);
    assert_eq!(b.arrived_legs, 8);
    for (on, off) in a.legs.iter().zip(&b.legs) {
        assert_eq!(
            serde_json::to_value(&on.journey.as_ref().unwrap().trace).unwrap(),
            serde_json::to_value(&off.journey.as_ref().unwrap().trace).unwrap()
        );
        near(
            on.journey.as_ref().unwrap().traction_work_j,
            off.journey.as_ref().unwrap().traction_work_j,
        );
        let d = on.energy.release_control.as_ref().unwrap();
        assert!(!d.slew_limit_exceeded, "{d:?}");
        assert_eq!(d.forced_cutoffs, 0);
        assert!(d.maximum_store_force_rate_n_s <= 100.000001);
    }
    assert!(a.ledger.grid_traction_energy_j < b.ledger.grid_traction_energy_j);
    assert!(a.ledger.delivered_launch_work_j > 0.);
    near(a.ledger.train_and_storage_balance_residual_j, 0.);
    near(a.ledger.storage_balance_residual_j, 0.);
}
#[test]
fn controlled_transfer_has_actual_component_ramps_and_finite_release_window() {
    let mut c = controlled_cycle();
    c.stations[0].initial_energy_j = 100000.;
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    for l in &r.legs {
        for p in &l.energy.trace {
            let q = p.release_control.as_ref().unwrap();
            assert!(q.store_start_force_n >= 0. && q.store_end_force_n >= 0.);
            assert!(q.grid_start_force_n >= 0. && q.grid_end_force_n >= 0.);
            assert!(q.store_force_rate_n_s <= 100.000001);
            if p.position_m > 200.1 {
                near(q.store_end_force_n, 0.);
            }
        }
        assert!(l.energy.maximum_release_power_w <= 6000. + 1e-6);
        assert!(l.energy.maximum_release_force_n <= 600. + 1e-6);
    }
}
#[test]
fn controlled_store_fault_cutoff_is_visible_and_never_provides_emergency_traction() {
    let mut c = controlled_cycle();
    c.legs.truncate(1);
    c.stations[0].initial_energy_j = 100000.;
    c.legs[0].journey.fault.power_loss_at_s = Some(10.);
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let l = &r.legs[0];
    assert!(
        l.energy
            .trace
            .iter()
            .filter(|p| p.time_s > 10.05)
            .all(|p| p.store_traction_n == 0.)
    );
    let d = l.energy.release_control.as_ref().unwrap();
    assert!(d.forced_cutoffs > 0);
    assert!(d.slew_limit_exceeded);
    assert!(!l.journey.as_ref().unwrap().normal_numerical_arrival);
    near(r.ledger.train_and_storage_balance_residual_j, 0.);
}
#[test]
fn controlled_grid_thermal_receives_only_grid_conversion_loss() {
    let mut c = controlled_cycle();
    c.legs.truncate(1);
    c.stations[0].initial_energy_j = 100000.;
    c.legs[0].journey.thermal = Some(Thermal {
        capacity_j_k: 10000.,
        heat_rejection_w_k: 0.,
        ambient_c: 10.,
        initial_c: 10.,
        maximum_c: 1000.,
    });
    let mut off = c.clone();
    off.legs[0].release_failed = true;
    let a = osr_journey::cycle::evaluate(&c).unwrap();
    let b = osr_journey::cycle::evaluate(&off).unwrap();
    let on = a.legs[0].journey.as_ref().unwrap();
    let off = b.legs[0].journey.as_ref().unwrap();
    near(
        on.final_temperature_c.unwrap() - 10.,
        on.drive_loss_j / 10000.,
    );
    assert!(on.final_temperature_c < off.final_temperature_c);
    assert!(a.ledger.release_loss_j > 0.);
}
#[test]
fn controlled_input_is_explicit_and_legacy_serialization_omits_new_fields() {
    let c = cycle();
    let json = serde_json::to_value(&c).unwrap();
    assert!(json.get("release_control").is_none());
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let json = serde_json::to_value(&r).unwrap();
    assert!(json["legs"][0]["energy"].get("release_control").is_none());
    assert!(
        json["legs"][0]["energy"]["trace"][0]
            .get("release_control")
            .is_none()
    );
    let mut c = controlled_cycle();
    c.release_control.as_mut().unwrap().reserve_factor = 0.5;
    assert!(osr_journey::cycle::evaluate(&c).is_err());
}

#[test]
fn continuous_reserve_handles_low_energy_and_engagement_exit_without_literal_force_jumps() {
    for dt in [0.05, 0.025, 0.0125] {
        for energy in [1e-8, 29.869729359567003, 100000.] {
            let mut c = controlled_cycle();
            c.release_control.as_mut().unwrap().mode = "grid-substitution-slew/2".into();
            c.release_control.as_mut().unwrap().cutoff_audit = true;
            c.stations[0].initial_energy_j = energy;
            for l in &mut c.legs {
                l.journey.dt_s = dt;
            }
            let r = osr_journey::cycle::evaluate(&c).unwrap();
            assert_eq!(r.arrived_legs, 8, "dt{dt},E{energy}");
            for l in &r.legs {
                let d = l.energy.release_control.as_ref().unwrap();
                assert_eq!(d.forced_cutoffs, 0, "dt{dt},E{energy}: {d:?}");
                assert!(!d.slew_limit_exceeded, "{d:?}");
                let v = d.continuous_reserve.as_ref().unwrap();
                assert_eq!(
                    v.maximum_store_boundary_jump_n, 0.,
                    "dt{dt},E{energy}: {d:?}"
                );
                assert_eq!(v.force_boundary_discontinuities, 0);
                assert!(
                    v.minimum_current_and_future_energy_margin_j >= -1e-10,
                    "{v:?}"
                );
                assert!(l.energy.maximum_release_force_n <= 600.);
                assert!(l.energy.maximum_release_power_w <= 6000.);
                for a in d.cutoff_details.as_ref().unwrap() {
                    assert_eq!(a.start_force_n, a.previous_force_n);
                    assert!(!a.forced_cutoff);
                    assert!(a.delivered_work_j <= a.usable_j);
                    assert!(a.position_m < 200.);
                }
            }
            near(r.ledger.storage_balance_residual_j, 0.);
            near(r.ledger.train_and_storage_balance_residual_j, 0.);
        }
    }
}
#[test]
fn continuous_reserve_failure_cutoffs_remain_visible() {
    let mut c = controlled_cycle();
    c.release_control.as_mut().unwrap().mode = "grid-substitution-slew/2".into();
    c.release_control.as_mut().unwrap().cutoff_audit = true;
    c.stations[0].initial_energy_j = 100000.;
    c.legs.truncate(1);
    c.legs[0].journey.fault.power_loss_at_s = Some(3.);
    let r = osr_journey::cycle::evaluate(&c).unwrap();
    let d = r.legs[0].energy.release_control.as_ref().unwrap();
    assert!(d.forced_cutoffs > 0);
    assert!(
        d.continuous_reserve
            .as_ref()
            .unwrap()
            .force_boundary_discontinuities
            > 0
    );
    assert!(
        d.cutoff_details
            .as_ref()
            .unwrap()
            .iter()
            .any(|a| a.reasons.iter().any(|v| v.contains("fault")))
    );
    near(r.ledger.storage_balance_residual_j, 0.);
}
