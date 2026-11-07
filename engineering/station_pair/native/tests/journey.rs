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
