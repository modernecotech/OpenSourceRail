use osr_journey::*;
fn near(a: f64, b: f64, eps: f64) {
    assert!((a - b).abs() < eps, "{a} != {b}");
}
fn case() -> Case {
    Case {
        id: "test".into(),
        candidate_id: "a".repeat(64),
        mass_kg: 1000.,
        rotating_equivalent_mass_kg: 0.,
        distance_m: 1000.,
        grade_fraction: 0.,
        rolling_coefficient: 0.,
        air_density_kg_m3: 1.2,
        cd_a_m2: 0.,
        headwind_m_s: 0.,
        speed_cap_m_s: 100.,
        acceleration_request_m_s2: 2.,
        comfort_jerk_m_s3: 1e9,
        brake_start_m: 1000.,
        berth_tolerance_m: 1.,
        brake_force_cap_n: 2000.,
        brake_adhesion_force_cap_n: 2000.,
        brake_latency_s: 0.,
        brake_rise_s: 0.,
        dt_s: 0.01,
        max_time_s: 10.,
        dwell_s: 0.,
        headway_s: 100.,
        auxiliary_power_w: 0.,
        drive: Some(Drive {
            points: vec![
                ForcePoint {
                    speed_m_s: 0.,
                    force_n: 1000.,
                },
                ForcePoint {
                    speed_m_s: 100.,
                    force_n: 1000.,
                },
            ],
            windows_m: vec![[0., 1000.]],
            maximum_speed_m_s: 100.,
            mechanical_power_w: 1e9,
            electrical_efficiency: 0.8,
            grid_power_w: 1e9,
            contact_force_cap_n: 1e9,
            external_mass_kg: 0.,
            external_resistance_n: 0.,
        }),
        fault: Fault {
            power_loss_at_s: None,
            failed_drive_fraction: 0.,
            emergency_at_m: None,
        },
        thermal: None,
        control: None,
    }
}
#[test]
fn constant_force_closes_energy() {
    let c = case();
    let r = evaluate(&c).unwrap();
    near(r.final_speed_m_s, 10., 1e-7);
    near(r.final_position_m, 50., 1e-6);
    near(r.traction_work_j, 50000., 1e-5);
    near(r.grid_energy_j, 62500., 1e-5);
    near(r.energy_residual_j, 0., 1e-5);
    assert!(!r.physical_accepted && !r.admitted_operating_map);
}

fn feedback_case() -> Case {
    let mut c = case();
    c.max_time_s = 300.;
    c.speed_cap_m_s = 15.;
    c.comfort_jerk_m_s3 = 0.5;
    c.control = Some(FeedbackControl {
        policy_id: "fixture-policy".into(),
        mass_lower_kg: 900.,
        mass_upper_kg: 1200.,
        rotating_mass_upper_kg: 50.,
        external_mass_upper_kg: 0.,
        brake_force_lower_bound_n: 1500.,
        grade_estimate_fraction: 0.,
        grade_error_bound: 0.001,
        position_error_bound_m: 0.05,
        speed_error_bound_m_s: 0.02,
        acceleration_error_bound_m_s2: 0.01,
        position_bias_m: 0.,
        speed_bias_m_s: 0.,
        acceleration_bias_m_s2: 0.,
        reaction_time_bound_s: 0.2,
        brake_rise_time_bound_s: 0.2,
        stopping_margin_m: 0.3,
        end_of_authority_m: c.distance_m,
        initial_hold_applied: true,
        start_traction_lower_bound_n: 1000.,
        rolling_resistance_upper_n: 50.,
        external_resistance_upper_n: 0.,
        positive_acceleration_bound_m_s2: 3.,
        drive_fault_observed: false,
        research_v2: None,
    });
    c
}

#[test]
fn feedback_nominal_diagnostic() {
    let c = feedback_case();
    let r = evaluate(&c).unwrap();

    assert!(r.normal_numerical_arrival);
}

#[test]
fn feedback_curve_matches_zero_response_analytic_limit() {
    let c = feedback_case();
    let mut p = c.control.unwrap();
    p.grade_error_bound = 0.;
    p.rotating_mass_upper_kg = 0.;
    p.reaction_time_bound_s = 0.;
    p.brake_rise_time_bound_s = 0.;
    p.stopping_margin_m = 0.;
    near(
        stopping_distance_bound(&p, 10., f64::INFINITY, 0., 0.).unwrap(),
        40.,
        1e-10,
    );
}
#[test]
fn feedback_curve_grows_with_delay_mass_grade_and_observation_speed() {
    let c = feedback_case();
    let p = c.control.unwrap();
    let distance = stopping_distance_bound(&p, 10., 0.5, 0.05, 0.).unwrap();
    let mut q = p.clone();
    q.reaction_time_bound_s += 1.;
    assert!(stopping_distance_bound(&q, 10., 0.5, 0.05, 0.).unwrap() > distance);
    q = p.clone();
    q.mass_upper_kg *= 1.2;
    assert!(stopping_distance_bound(&q, 10., 0.5, 0.05, 0.).unwrap() > distance);
    q = p.clone();
    q.grade_estimate_fraction = -0.02;
    assert!(stopping_distance_bound(&q, 10., 0.5, 0.05, 0.).unwrap() > distance);
    assert!(stopping_distance_bound(&p, 11., 0.5, 0.05, 0.).unwrap() > distance);
}
#[test]
fn feedback_same_policy_handles_independent_actual_masses_without_refitting() {
    let c = feedback_case();
    for mass in [900., 1000., 1200.] {
        let mut q = c.clone();
        q.mass_kg = mass;
        q.brake_start_m = 0.;
        let r = evaluate(&q).unwrap();
        assert!(
            r.normal_numerical_arrival,
            "mass {mass}, x{}, state{}",
            r.final_position_m, r.state
        );
        near(r.energy_residual_j, 0., 1e-4);
    }
}
#[test]
fn feedback_does_not_use_fixed_brake_start() {
    let a = feedback_case();
    let mut b = a.clone();
    b.brake_start_m = 1.;
    let x = evaluate(&a).unwrap();
    let y = evaluate(&b).unwrap();
    near(x.final_position_m, y.final_position_m, 1e-10);
    near(x.elapsed_s, y.elapsed_s, 1e-10);
}
#[test]
fn feedback_actual_weak_brake_is_reported_outside_policy_not_repaired() {
    let mut c = feedback_case();
    c.brake_force_cap_n = 500.;
    let r = evaluate(&c).unwrap();
    assert!(!r.control.unwrap().bounds_valid);
    assert!(!r.normal_numerical_arrival);
    assert!(r.maximum_brake_n <= 500.);
}
#[test]
fn feedback_outside_sensor_domain_cannot_claim_arrival() {
    let mut c = feedback_case();
    c.control.as_mut().unwrap().position_bias_m = 5.;
    let r = evaluate(&c).unwrap();
    assert!(!r.control.unwrap().bounds_valid);
    assert!(!r.normal_numerical_arrival);
}
#[test]
fn feedback_tailwind_domain_is_explicit() {
    let mut c = feedback_case();
    c.headwind_m_s = -5.;
    let r = evaluate(&c).unwrap();
    assert!(!r.control.unwrap().bounds_valid);
    assert!(!r.normal_numerical_arrival);
}
#[test]
fn feedback_insufficient_declared_brake_rejects_departure_with_actual_hold_report() {
    let mut c = feedback_case();
    let p = c.control.as_mut().unwrap();
    p.grade_estimate_fraction = -0.08;
    p.brake_force_lower_bound_n = 500.;
    let r = evaluate(&c).unwrap();
    assert!(r.control.unwrap().departure_held);
    assert_eq!(r.final_position_m, 0.);
    assert!(!r.normal_numerical_arrival);
}
#[test]
fn feedback_initial_hill_hold_has_no_reverse_energy() {
    let mut c = feedback_case();
    c.grade_fraction = 0.01;
    c.control.as_mut().unwrap().grade_estimate_fraction = 0.01;
    let r = evaluate(&c).unwrap();
    assert!(!r.rollback_detected);
    assert!(r.final_position_m > 0.);
    near(r.energy_residual_j, 0., 1e-4);
}
#[test]
fn feedback_power_loss_stops_without_propulsive_energy_after_failure() {
    let mut c = feedback_case();
    c.fault.power_loss_at_s = Some(10.);
    let r = evaluate(&c).unwrap();
    assert!(r.fault_stop_in_route);
    assert!(!r.normal_numerical_arrival);
    assert!(
        r.trace
            .iter()
            .filter(|p| p.time_s > 10.1)
            .all(|p| p.traction_n == 0.)
    );
    near(r.energy_residual_j, 0., 1e-4);
}
#[test]
fn feedback_finite_cable_window_never_creeps_after_detachment() {
    let mut c = feedback_case();
    c.drive.as_mut().unwrap().windows_m = vec![[0., 100.]];
    let r = evaluate(&c).unwrap();
    assert!(
        r.trace
            .iter()
            .filter(|p| p.position_m > 100.001)
            .all(|p| p.traction_n == 0.)
    );
    near(r.energy_residual_j, 0., 1e-4);
}
#[test]
fn feedback_timestep_refinement_retains_unmodified_policy() {
    let a = feedback_case();
    let mut b = a.clone();
    b.dt_s = 0.005;
    let x = evaluate(&a).unwrap();
    let y = evaluate(&b).unwrap();
    assert!(x.normal_numerical_arrival && y.normal_numerical_arrival);
    near(x.final_position_m, y.final_position_m, 0.2);
}

#[test]
fn feedback_explicit_authority_is_not_the_berth_accuracy_window() {
    let mut c = feedback_case();
    c.control.as_mut().unwrap().end_of_authority_m = 500.;
    let r = evaluate(&c).unwrap();
    assert!(!r.normal_numerical_arrival);
    assert!(r.final_position_m <= 500.);
    assert!(!r.control.unwrap().end_of_authority_violated);
}
#[test]
fn feedback_initial_fault_reports_unattained_traction_bound() {
    let mut c = feedback_case();
    c.fault.power_loss_at_s = Some(0.);
    let r = evaluate(&c).unwrap();
    assert!(!r.control.unwrap().bounds_valid);
    assert!(r.standstill_holding);
    near(r.traction_work_j, 0., 1e-10);
}

fn docking_case() -> Case {
    let mut c = feedback_case();
    c.mass_kg = 125875.937;
    c.rotating_equivalent_mass_kg = 7552.556;
    c.distance_m = 1500.;
    c.speed_cap_m_s = 50. / 3.6;
    c.max_time_s = 600.;
    c.dt_s = 0.05;
    c.rolling_coefficient = 0.003;
    c.cd_a_m2 = 8.;
    c.brake_force_cap_n = 35556.215;
    c.brake_adhesion_force_cap_n = 100000.;
    c.brake_latency_s = 0.5;
    c.brake_rise_s = 1.;
    c.berth_tolerance_m = 2.;
    let d = c.drive.as_mut().unwrap();
    d.points[0].force_n = 60000.;
    d.points[1].force_n = 60000.;
    d.mechanical_power_w = 1200000.;
    d.windows_m = vec![[0., 1500.]];
    let p = c.control.as_mut().unwrap();
    p.mass_lower_kg = 110055.445;
    p.mass_upper_kg = 151666.441;
    p.rotating_mass_upper_kg = 15166.644;
    p.brake_force_lower_bound_n = 32000.;
    p.position_error_bound_m = 0.25;
    p.speed_error_bound_m_s = 0.1;
    p.acceleration_error_bound_m_s2 = 0.02;
    p.reaction_time_bound_s = 0.7;
    p.brake_rise_time_bound_s = 1.3;
    p.end_of_authority_m = 1500.;
    p.stopping_margin_m = 0.5;
    p.start_traction_lower_bound_n = 14494.;
    p.rolling_resistance_upper_n = 5950.;
    p.positive_acceleration_bound_m_s2 = 2.;
    c
}
#[test]
fn continuous_power_docks_but_finite_cable_window_cannot_creep() {
    let c = docking_case();
    let mut finite = c.clone();
    finite.drive.as_mut().unwrap().windows_m = vec![[0., 1450.]];
    let a = evaluate(&c).unwrap();
    let b = evaluate(&finite).unwrap();
    assert!(
        a.normal_numerical_arrival,
        "continuous state{} x{}",
        a.state, a.final_position_m
    );
    assert!(a.control.as_ref().unwrap().docking_attempts > 0);
    assert!(!b.normal_numerical_arrival);
    assert_eq!(b.control.unwrap().docking_attempts, 0);
    let began = a
        .events
        .iter()
        .find(|e| e.kind == "bounded-continuous-drive-docking")
        .unwrap()
        .time_s;
    assert!(
        a.trace
            .iter()
            .filter(|p| p.time_s > began)
            .all(|p| p.speed_m_s <= 0.5)
    );
    assert!(
        a.trace
            .iter()
            .any(|p| p.time_s > began && p.traction_n > 0.)
    );
    near(a.energy_residual_j, 0., 1e-4);
}
#[test]
fn observed_fault_or_emergency_never_restarts_for_docking() {
    let c = docking_case();
    for mode in 0..3 {
        let mut q = c.clone();
        if mode == 0 {
            q.fault.power_loss_at_s = Some(10.);
        }
        if mode == 1 {
            q.fault.emergency_at_m = Some(750.);
        }
        if mode == 2 {
            q.control.as_mut().unwrap().drive_fault_observed = true;
        }
        let r = evaluate(&q).unwrap();
        assert_eq!(r.control.unwrap().docking_attempts, 0);
        assert!(!r.normal_numerical_arrival);
    }
}
#[test]
fn insufficient_docking_observation_resolution_is_not_ignored() {
    let mut c = docking_case();
    c.control.as_mut().unwrap().speed_error_bound_m_s = 0.3;
    let r = evaluate(&c).unwrap();
    assert_eq!(r.control.unwrap().docking_attempts, 0);
}
#[test]
fn bounded_position_biases_never_authorize_power_past_physical_window() {
    let c = docking_case();
    for bias in [-0.25, 0.25] {
        let mut q = c.clone();
        q.control.as_mut().unwrap().position_bias_m = bias;
        let r = evaluate(&q).unwrap();
        assert!(
            r.trace
                .iter()
                .filter(|p| p.position_m >= 1500.)
                .all(|p| p.traction_n == 0.)
        );
        assert!(!r.control.unwrap().end_of_authority_violated);
    }
}
#[test]
fn docking_refinement_retains_policy_and_energy() {
    let a = docking_case();
    let mut b = a.clone();
    b.dt_s = 0.025;
    let x = evaluate(&a).unwrap();
    let y = evaluate(&b).unwrap();
    assert!(x.normal_numerical_arrival && y.normal_numerical_arrival);
    near(x.final_position_m, y.final_position_m, 0.2);
    near(y.energy_residual_j, 0., 1e-4);
}
#[test]
fn shortened_initial_hill_step_does_not_release_on_unaccepted_torque() {
    let mut c = feedback_case();
    c.grade_fraction = 0.01;
    c.control.as_mut().unwrap().grade_estimate_fraction = 0.01;
    c.dt_s = 0.05;
    c.fault.power_loss_at_s = Some(0.075);
    let r = evaluate(&c).unwrap();
    assert!(!r.rollback_detected);
    near(r.final_position_m, 0., 1e-10);
    assert!(
        !r.events
            .iter()
            .any(|e| e.kind == "bounded-hill-start-release")
    );
}

#[test]
fn dwell_warming_is_in_reported_temperature_maximum() {
    let mut c = case();
    c.drive.as_mut().unwrap().electrical_efficiency = 1.;
    c.max_time_s = 0.1;
    c.dwell_s = 1000.;
    c.thermal = Some(Thermal {
        capacity_j_k: 100.,
        heat_rejection_w_k: 1.,
        ambient_c: 20.,
        initial_c: -10.,
        maximum_c: 50.,
    });
    let r = evaluate(&c).unwrap();
    assert!(r.final_temperature_c.unwrap() > 19.);
    assert!(r.maximum_temperature_c.unwrap() >= r.final_temperature_c.unwrap());
}
#[test]
fn finite_window_has_exact_exit_and_coast() {
    let mut c = case();
    c.drive.as_mut().unwrap().windows_m = vec![[0., 20.]];
    let r = evaluate(&c).unwrap();
    near(r.traction_work_j, 20000., 1e-4);
    near(r.final_speed_m_s, 40f64.sqrt(), 1e-6);
    let exit = r
        .events
        .iter()
        .find(|e| e.kind == "drive-window-exit")
        .unwrap();
    near(exit.position_m, 20., 1e-6);
    near(r.energy_residual_j, 0., 1e-4);
}
#[test]
fn external_mass_exports_reset_energy_once() {
    let mut c = case();
    let d = c.drive.as_mut().unwrap();
    d.windows_m = vec![[0., 20.]];
    d.external_mass_kg = 500.;
    d.external_resistance_n = 100.;
    let r = evaluate(&c).unwrap();
    near(r.external_resistance_work_j, 2000., 1e-4);
    near(r.detached_reset_kinetic_energy_j, 6000., 1e-3);
    near(r.final_kinetic_energy_j, 12000., 1e-3);
    near(r.energy_residual_j, 0., 1e-3);
    assert_eq!(
        r.events
            .iter()
            .filter(|e| e.kind == "external-mass-detached-energy-export")
            .count(),
        1
    );
}
#[test]
fn later_external_engagement_is_held() {
    let mut c = case();
    let d = c.drive.as_mut().unwrap();
    d.external_mass_kg = 10.;
    d.windows_m = vec![[5., 20.]];
    assert!(evaluate(&c).unwrap().hold_reason.is_some());
}
#[test]
fn absent_curve_is_held_and_zero_start_does_not_invent_force() {
    let mut c = case();
    c.drive = None;
    assert!(evaluate(&c).unwrap().hold_reason.is_some());
    c = case();
    for p in &mut c.drive.as_mut().unwrap().points {
        p.force_n = 0.;
    }
    let r = evaluate(&c).unwrap();
    assert_eq!(r.state, "stalled-no-starting-force");
    near(r.final_position_m, 0., 1e-10);
}
#[test]
fn zero_force_before_future_window() {
    let mut c = case();
    c.drive.as_mut().unwrap().windows_m = vec![[20., 40.]];
    c.max_time_s = 1.;
    let r = evaluate(&c).unwrap();
    near(r.final_position_m, 0., 1e-10);
    near(r.traction_work_j, 0., 1e-10);
}
#[test]
fn independent_emergency_brake_stops_and_does_not_snap_position() {
    let mut c = case();
    c.fault.emergency_at_m = Some(20.);
    c.max_time_s = 30.;
    let r = evaluate(&c).unwrap();
    assert_eq!(r.state, "stopped");
    assert!(r.fault_stop_in_route);
    assert!(r.final_position_m > 20. && r.final_position_m < 40.);
    assert_ne!(r.final_position_m, c.distance_m);
    near(r.energy_residual_j, 0., 1e-3);
}
#[test]
fn low_adhesion_extends_stop() {
    let mut c = case();
    c.fault.emergency_at_m = Some(20.);
    c.max_time_s = 100.;
    let a = evaluate(&c).unwrap();
    c.brake_adhesion_force_cap_n = 500.;
    let b = evaluate(&c).unwrap();
    assert!(b.final_position_m > a.final_position_m + 10.);
    assert!(b.maximum_brake_n <= 500.);
}
#[test]
fn rollback_is_reported() {
    let mut c = case();
    c.grade_fraction = 0.05;
    c.fault.failed_drive_fraction = 1.;
    let r = evaluate(&c).unwrap();
    assert!(r.rollback_detected);
    near(r.final_speed_m_s, 0., 1e-12);
    assert_eq!(r.state, "incipient-rollback-held");
    assert!(!r.fault_stop_in_route);
}
#[test]
fn power_loss_jerk_is_not_smoothed_away() {
    let mut c = case();
    c.comfort_jerk_m_s3 = 0.2;
    c.fault.power_loss_at_s = Some(0.7);
    let r = evaluate(&c).unwrap();
    assert!(r.maximum_absolute_jerk_m_s3 > c.comfort_jerk_m_s3);
    assert!(r.events.iter().any(|e| e.kind == "traction-power-loss"));
}
#[test]
fn timestep_refinement_preserves_unsnapped_stopping() {
    let mut c = case();
    c.fault.emergency_at_m = Some(20.);
    c.brake_latency_s = 0.2;
    c.brake_rise_s = 0.5;
    c.max_time_s = 50.;
    c.dt_s = 0.05;
    let a = evaluate(&c).unwrap();
    c.dt_s = 0.025;
    let b = evaluate(&c).unwrap();
    assert!((a.final_position_m - b.final_position_m).abs() < 0.3);
    assert_ne!(a.final_position_m, c.distance_m);
    assert_ne!(b.final_position_m, c.distance_m);
}
#[test]
fn power_and_thermal_are_explicit_limits() {
    let mut c = case();
    c.drive.as_mut().unwrap().mechanical_power_w = 800.;
    c.thermal = Some(Thermal {
        capacity_j_k: 1000.,
        heat_rejection_w_k: 0.,
        ambient_c: 20.,
        initial_c: 20.,
        maximum_c: 100.,
    });
    let r = evaluate(&c).unwrap();
    assert!(r.maximum_mechanical_power_w <= 800.001);
    near(
        r.final_temperature_c.unwrap(),
        20. + r.drive_loss_j / 1000.,
        1e-6,
    );
}
#[test]
fn bad_si_and_unknown_fields_reject() {
    let mut c = case();
    c.mass_kg = 0.;
    assert!(evaluate(&c).is_err());
    c = case();
    c.dt_s = f64::NAN;
    assert!(evaluate(&c).is_err());
    c = case();
    c.drive.as_mut().unwrap().points[1].speed_m_s = 0.;
    assert!(evaluate(&c).is_err());
    let mut v = serde_json::to_value(case()).unwrap();
    v["hidden_default"] = 1.into();
    assert!(serde_json::from_value::<Case>(v).is_err());
}
#[test]
fn batch_identity_and_order() {
    let mut b = case();
    b.id = "second".into();
    let r = execute(Request {
        schema: REQUEST_SCHEMA.into(),
        cases: vec![case(), b],
    })
    .unwrap();
    assert_eq!(r.cases[1].id, "second");
    assert!(
        execute(Request {
            schema: REQUEST_SCHEMA.into(),
            cases: vec![case(), case()]
        })
        .is_err()
    );
}
#[test]
fn normal_launch_coast_brake_arrives_without_position_reset() {
    let mut c = case();
    c.distance_m = 100.;
    c.drive.as_mut().unwrap().windows_m = vec![[0., 50.]];
    c.brake_start_m = 75.;
    c.max_time_s = 40.;
    c.berth_tolerance_m = 0.001;
    c.fault.power_loss_at_s = Some(100.);
    let a = evaluate(&c).unwrap();
    assert!(a.normal_numerical_arrival, "{:?}", a);
    assert_eq!(a.state, "stopped");
    near(a.final_position_m, 100., 0.001);
    c.brake_start_m = 70.;
    let b = evaluate(&c).unwrap();
    near(b.final_position_m, 95., 0.001);
    assert!(!b.normal_numerical_arrival);
}
#[test]
fn drive_failure_does_not_double_derate_power() {
    let mut c = case();
    c.max_time_s = 20.;
    c.drive.as_mut().unwrap().mechanical_power_w = 1000.;
    c.fault.failed_drive_fraction = 0.5;
    let r = evaluate(&c).unwrap();
    assert!(r.maximum_mechanical_power_w > 499. && r.maximum_mechanical_power_w <= 500.001);
}
#[test]
fn power_loss_commands_independent_brake() {
    let mut c = case();
    c.fault.power_loss_at_s = Some(2.);
    c.brake_latency_s = 0.2;
    c.brake_rise_s = 0.3;
    c.max_time_s = 20.;
    let r = evaluate(&c).unwrap();
    assert_eq!(r.state, "stopped");
    assert!(r.fault_stop_in_route);
    assert!(
        r.events
            .iter()
            .any(|e| e.kind == "power-loss-independent-brake-command")
    );
    near(r.energy_residual_j, 0., 1e-3);
}
#[test]
fn insufficient_static_brake_never_claims_held_arrival() {
    let mut c = case();
    c.grade_fraction = 0.05;
    c.brake_force_cap_n = 10.;
    c.brake_adhesion_force_cap_n = 10.;
    c.drive
        .as_mut()
        .unwrap()
        .points
        .iter_mut()
        .for_each(|p| p.force_n = 2000.);
    c.drive.as_mut().unwrap().windows_m = vec![[0., 5.]];
    c.brake_start_m = 5.;
    c.max_time_s = 50.;
    let r = evaluate(&c).unwrap();
    assert!(!r.normal_numerical_arrival && !r.standstill_holding);
    assert!(r.standstill_brake_margin_n < 0.);
    near(r.energy_residual_j, 0., 1e-3);
}
#[test]
fn steep_characteristic_has_explicit_numerical_hold() {
    let mut c = case();
    c.mass_kg = 1.;
    c.dt_s = 0.2;
    let d = c.drive.as_mut().unwrap();
    d.maximum_speed_m_s = 0.001;
    d.points = vec![
        ForcePoint {
            speed_m_s: 0.,
            force_n: 1000.,
        },
        ForcePoint {
            speed_m_s: 0.001,
            force_n: 0.,
        },
    ];
    let r = evaluate(&c).unwrap();
    assert!(r.hold_reason.is_some());
    assert!(!r.normal_numerical_arrival);
    assert!(r.maximum_mechanical_power_w <= c.drive.as_ref().unwrap().mechanical_power_w);
}
#[test]
fn speed_control_only_reduces_available_force() {
    let mut c = case();
    c.speed_cap_m_s = 5.;
    c.max_time_s = 20.;
    c.comfort_jerk_m_s3 = 0.5;
    let r = evaluate(&c).unwrap();
    assert!(r.maximum_speed_m_s <= 5.0000001, "{:?}", r);
    assert!(r.maximum_traction_n <= 1000.);
    near(r.energy_residual_j, 0., 1e-4);
}
#[test]
fn nominal_speed_taper_meets_moving_jerk_request() {
    let mut c = case();
    c.speed_cap_m_s = 5.;
    c.comfort_jerk_m_s3 = 0.5;
    c.max_time_s = 30.;
    let r = evaluate(&c).unwrap();
    assert!(r.maximum_speed_m_s <= 5.000001);
    assert!(
        r.maximum_absolute_jerk_m_s3 <= 0.501,
        "{}",
        r.maximum_absolute_jerk_m_s3
    );
}
#[test]
fn planned_window_release_tapers_before_contact_ends() {
    let mut c = case();
    c.comfort_jerk_m_s3 = 0.5;
    c.max_time_s = 30.;
    c.drive.as_mut().unwrap().windows_m = vec![[0., 50.]];
    let r = evaluate(&c).unwrap();
    assert!(r.events.iter().any(|e| e.kind == "drive-window-exit"));
    assert!(
        r.maximum_absolute_jerk_m_s3 <= 0.501,
        "{}",
        r.maximum_absolute_jerk_m_s3
    );
    near(r.energy_residual_j, 0., 1e-4);
}
#[test]
fn terminal_acceleration_step_is_explicit() {
    let mut c = case();
    c.fault.emergency_at_m = Some(20.);
    c.max_time_s = 30.;
    let r = evaluate(&c).unwrap();
    assert!(!r.terminal_jerk_resolved);
    assert!(r.terminal_acceleration_step_m_s2 > 1.);
    assert!(
        r.events
            .iter()
            .any(|e| e.kind == "terminal-standstill-acceleration-step-unresolved")
    );
}
