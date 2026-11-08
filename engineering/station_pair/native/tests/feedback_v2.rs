//! Synthetic controller-method controls, never a railway equipment admission.
use osr_journey::*;
use serde_json::{Value, json};

fn fixture(grade: f64) -> Case {
    let mut c: Case = serde_json::from_value(json!({
        "id":"synthetic-v2-method-control","candidate_id":"a".repeat(64),
        "mass_kg":1000.,"rotating_equivalent_mass_kg":0.,"distance_m":1005.,
        "grade_fraction":grade,"rolling_coefficient":0.003,"air_density_kg_m3":1.2,
        "cd_a_m2":0.,"headwind_m_s":0.,"speed_cap_m_s":10.,
        "acceleration_request_m_s2":0.8,"comfort_jerk_m_s3":0.5,"brake_start_m":1000.,
        "berth_tolerance_m":1.,"brake_force_cap_n":2000.,"brake_adhesion_force_cap_n":2000.,
        "brake_latency_s":0.1,"brake_rise_s":0.2,"dt_s":0.05,"max_time_s":600.,
        "dwell_s":35.,"headway_s":200.,"auxiliary_power_w":100.,
        "drive":{"points":[{"speed_m_s":0.,"force_n":1000.},{"speed_m_s":30.,"force_n":1000.}],
            "windows_m":[[0.,1005.]],"maximum_speed_m_s":30.,"mechanical_power_w":50000.,
            "electrical_efficiency":0.8,"grid_power_w":62500.,"contact_force_cap_n":2000.,
            "external_mass_kg":0.,"external_resistance_n":0.},
        "fault":{"power_loss_at_s":null,"failed_drive_fraction":0.,"emergency_at_m":null},
        "thermal":null,"control":null
    }))
    .unwrap();
    c.control = Some(FeedbackControl {
        policy_id: "synthetic-v2-policy".into(),
        mass_lower_kg: 900.,
        mass_upper_kg: 1200.,
        rotating_mass_upper_kg: 50.,
        external_mass_upper_kg: 0.,
        brake_force_lower_bound_n: 1500.,
        grade_estimate_fraction: grade,
        grade_error_bound: 0.001,
        position_error_bound_m: 0.05,
        speed_error_bound_m_s: 0.02,
        acceleration_error_bound_m_s2: 0.01,
        position_bias_m: 0.,
        speed_bias_m_s: 0.,
        acceleration_bias_m_s2: 0.,
        reaction_time_bound_s: 0.2,
        brake_rise_time_bound_s: 0.3,
        stopping_margin_m: 0.3,
        end_of_authority_m: 1005.,
        initial_hold_applied: true,
        start_traction_lower_bound_n: 1000.,
        rolling_resistance_upper_n: 50.,
        external_resistance_upper_n: 0.,
        positive_acceleration_bound_m_s2: 3.,
        drive_fault_observed: false,
        research_v2: Some(ResearchFeedbackV2 {
            strategy: "held-docking-speed-governor/2".into(),
            berth_target_m: 1000.,
            brake_floor_n: 300.,
            creep_speed_m_s: 0.2,
        }),
    });
    c
}

fn check_physics(c: &Case, r: &ResultRow) {
    assert!(
        !r.physical_accepted
            && !r.admitted_operating_map
            && !r.engineering_accepted
            && !r.operating_release
    );
    assert!(!r.control.as_ref().unwrap().protected_service_qualified);
    assert!(r.maximum_traction_n <= c.drive.as_ref().unwrap().contact_force_cap_n + 1e-7);
    assert!(r.maximum_brake_n <= c.brake_force_cap_n.min(c.brake_adhesion_force_cap_n) + 1e-7);
    assert!(
        r.energy_residual_j.abs()
            <= 1e-6 * r.traction_work_j.abs().max(r.grade_work_j.abs()).max(1.)
    );
}

#[test]
fn missing_strategy_reproduces_two_exact_legacy_results() {
    let golden: Value =
        serde_json::from_str(include_str!("data/legacy_corridor_control.json")).unwrap();
    let request: Request = serde_json::from_value(golden["request"].clone()).unwrap();
    let actual = serde_json::to_value(execute(request).unwrap()).unwrap();
    assert_eq!(actual, golden["expected"]);
}

#[test]
fn original_one_metre_authority_and_uncertainties_are_not_repaired_by_a_v2_tag() {
    let golden: Value =
        serde_json::from_str(include_str!("data/legacy_corridor_control.json")).unwrap();
    let request: Request = serde_json::from_value(golden["request"].clone()).unwrap();
    for mut c in request.cases {
        let target = c.distance_m;
        c.control.as_mut().unwrap().research_v2 = Some(ResearchFeedbackV2 {
            strategy: "held-docking-speed-governor/2".into(),
            berth_target_m: target,
            brake_floor_n: 40000.,
            creep_speed_m_s: 0.2,
        });
        let r = evaluate(&c).unwrap();
        assert_eq!(r.state, "controller-v2-domain-held");
        assert!(!r.normal_numerical_arrival);
        let d = r.control.unwrap().research_v2.unwrap();
        assert!(!d.static_domain_supported);
        assert!(
            d.domain_holds
                .iter()
                .any(|x| x.contains("zero-speed bound"))
        );
    }
}

#[test]
fn explicit_feasible_preload_domain_completes_inclines_and_stops_on_creep_faults() {
    for grade in [0.02, -0.02] {
        let c = fixture(grade);
        let r = evaluate(&c).unwrap();
        check_physics(&c, &r);
        println!(
            "nominal grade{grade}: state{}, x{}, maxv{}, jerk{}, attempts{}",
            r.state,
            r.final_position_m,
            r.maximum_speed_m_s,
            r.maximum_absolute_jerk_m_s3,
            r.control.as_ref().unwrap().docking_attempts
        );
        assert!(
            r.normal_numerical_arrival,
            "grade{grade}: state{},x{},reason{:?}",
            r.state, r.final_position_m, r.hold_reason
        );
        assert!(r.maximum_speed_m_s <= c.speed_cap_m_s + 1e-7);
        assert!(!r.rollback_detected && r.standstill_holding);
        let d = r.control.as_ref().unwrap().research_v2.as_ref().unwrap();
        assert_eq!(d.final_state, "FinalHold");
        assert!(d.command_history_guaranteed_brake_n >= 1500. - 1e-7);
        assert!(!d.brake_force_observed);
        if grade < 0. {
            assert!(d.speed_governor_steps > 0 && r.brake_heat_j > 0.);
        }
        let creep = r
            .events
            .iter()
            .filter(|e| e.kind == "v2-bounded-forward-motion-observed")
            .nth(1)
            .expect("actual redocking movement");
        let mut lost = c.clone();
        lost.fault.power_loss_at_s = Some(creep.time_s + 0.075);
        let stopped = evaluate(&lost).unwrap();
        check_physics(&lost, &stopped);
        assert!(stopped.fault_stop_in_route && !stopped.rollback_detected);
        assert!(!stopped.normal_numerical_arrival);
        assert!(
            stopped
                .trace
                .iter()
                .filter(|z| z.time_s > creep.time_s + 0.075 + 1e-8)
                .all(|z| z.traction_n == 0.)
        );
        let mut emergency = c.clone();
        emergency.fault.emergency_at_m = Some(creep.position_m + 0.1);
        let stopped = evaluate(&emergency).unwrap();
        check_physics(&emergency, &stopped);
        assert!(stopped.fault_stop_in_route && !stopped.rollback_detected);
    }
}

#[test]
fn uncertainty_extremes_never_turn_domain_violations_into_success() {
    for (mass, sign) in [(900., -1.), (1200., 1.)] {
        let mut c = fixture(-0.02);
        c.mass_kg = mass;
        c.grade_fraction += sign * 0.001;
        let p = c.control.as_mut().unwrap();
        p.position_bias_m = sign * p.position_error_bound_m;
        p.speed_bias_m = sign * p.speed_error_bound_m_s;
        p.acceleration_bias_m_s2 = sign * p.acceleration_error_bound_m_s2;
        let r = evaluate(&c).unwrap();
        check_physics(&c, &r);
        assert!(r.maximum_speed_m_s <= c.speed_cap_m_s + 1e-7);
        assert!(!r.control.as_ref().unwrap().end_of_authority_violated);
        assert!(!r.rollback_detected);
        if r.normal_numerical_arrival {
            assert!(r.berth_error_m.abs() <= c.berth_tolerance_m && r.standstill_holding);
        }
    }
}

#[test]
fn timestep_refinement_retains_force_energy_and_stop_interface() {
    let mut results = vec![];
    for dt in [0.05, 0.025, 0.0125] {
        let mut c = fixture(-0.02);
        c.dt_s = dt;
        let r = evaluate(&c).unwrap();
        check_physics(&c, &r);
        assert!(
            r.normal_numerical_arrival,
            "dt{dt} state{} x{}",
            r.state, r.final_position_m
        );
        assert!(r.maximum_speed_m_s <= c.speed_cap_m_s + 1e-7);
        results.push(r);
    }
    // Case-specific method regression limits, not hardware or convergence proof.
    assert!((results[0].final_position_m - results[2].final_position_m).abs() < 0.25);
    assert!((results[0].elapsed_s - results[2].elapsed_s).abs() < 2.);
}

#[test]
fn detached_station_launch_cannot_invent_powered_docking() {
    let mut c = fixture(0.02);
    c.drive.as_mut().unwrap().windows_m = vec![[0., 200.]];
    let r = evaluate(&c).unwrap();
    check_physics(&c, &r);
    assert!(!r.normal_numerical_arrival);
    assert!(
        r.trace
            .iter()
            .filter(|q| q.position_m > 200. + 1e-7)
            .all(|q| q.traction_n == 0.)
    );
}

#[test]
fn invalid_explicit_strategy_geometry_and_preload_inputs_fail_closed() {
    for fault in 0..3 {
        let mut c = fixture(0.02);
        let p = c.control.as_mut().unwrap();
        let v = p.research_v2.as_mut().unwrap();
        match fault {
            0 => v.brake_floor_n = 1501.,
            1 => v.berth_target_m = 1006.,
            _ => v.strategy = "guess".into(),
        }
        assert!(evaluate(&c).is_err());
    }
}

#[test]
fn observed_fault_and_subsample_power_loss_do_not_authorize_departure() {
    let mut observed = fixture(0.02);
    observed.control.as_mut().unwrap().drive_fault_observed = true;
    let r = evaluate(&observed).unwrap();
    assert!(!r.normal_numerical_arrival && r.final_position_m == 0.);
    let mut lost = fixture(0.02);
    lost.fault.power_loss_at_s = Some(0.075);
    let r = evaluate(&lost).unwrap();
    check_physics(&lost, &r);
    assert!(r.fault_stop_in_route && r.grid_energy_j == 0. && !r.rollback_detected);
    assert!(r.events.iter().any(
        |e| e.kind == "traction-power-loss-independent-brake-command"
            && (e.time_s - 0.075).abs() < 1e-10
    ));
}
