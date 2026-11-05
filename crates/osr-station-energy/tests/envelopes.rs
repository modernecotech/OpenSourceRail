use osr_station_energy::{evaluate, execute, CaptureProfile, Case, Request, REQUEST_SCHEMA};

fn fixture() -> Case {
    Case {
        id: "illustrative-160t".into(),
        effective_mass_kg: 160_000.0,
        physical_mass_kg: 160_000.0,
        capture_speed_m_s: 5.0,
        capture_deceleration_m_s2: 0.8,
        capture_stroke_m: 20.0,
        capture_profile: CaptureProfile::ControlledConstant,
        forward_transfer: true,
        efficiency_capture: 1.0,
        efficiency_store: 0.7,
        efficiency_release: 1.0,
        store_capacity_j: 64_000_000.0,
        store_initial_j: 0.0,
        store_reserve_j: 0.0,
        standing_loss_w: 0.0,
        dwell_s: 30.0,
        launch_request_j: 1_400_000.0,
        release_duration_s: 10.0,
        booster_offset_m: 0.0,
        booster_length_m: 200.0,
        target_speed_m_s: 20.0,
        resistance_n: 0.0,
        grade_fraction: 0.0,
        booster_efficiency: 0.8,
        reset_s: 10.0,
        headway_s: 200.0,
        capture_force_limit_n: None,
        max_booster_acceleration_m_s2: None,
        available_booster_force_n: None,
        source_power_limit_w: None,
        independent_brake_deceleration_m_s2: None,
    }
}

fn close(a: f64, b: f64) {
    assert!(
        (a - b).abs() <= 1e-10 * a.abs().max(b.abs()).max(1.0),
        "{a} != {b}"
    );
}

#[test]
fn independently_known_ideal_example() {
    let r = evaluate(&fixture()).unwrap();
    close(r.capture.kinetic_energy_j, 2_000_000.0);
    close(r.storage.delivered_j, 1_400_000.0);
    close(r.motion.ideal_launch_speed_m_s, 4.183300132670378);
    close(r.booster.net_acceleration_m_s2.unwrap(), 0.95625);
    close(r.booster.required_force_n.unwrap(), 153_000.0);
    close(r.booster.peak_mechanical_power_w.unwrap(), 3_060_000.0);
    close(r.booster.peak_source_power_w.unwrap(), 3_825_000.0);
    close(r.booster.time_s.unwrap(), 16.54033973054078);
    close(r.capture.required_stroke_m.unwrap(), 15.625);
    close(r.energy_residual_j, 0.0);
    assert_eq!(r.necessary_bounds, "unknown");
    assert!(!r.physical_accepted && !r.engineering_accepted && !r.operating_release);
    assert!(r.unknowns.iter().any(|s| s.contains("jerk")));
    assert!(r
        .unknowns
        .iter()
        .any(|s| s == "booster-available-force-unspecified"));
}

#[test]
fn zero_capture_is_no_recovery_comparator() {
    let mut c = fixture();
    c.capture_speed_m_s = 0.0;
    c.launch_request_j = 0.0;
    c.release_duration_s = 0.0;
    let r = evaluate(&c).unwrap();
    close(r.storage.delivered_j, 0.0);
    close(r.booster.net_acceleration_m_s2.unwrap(), 1.0);
    close(r.booster.peak_mechanical_power_w.unwrap(), 3_200_000.0);
    close(r.energy_residual_j, 0.0);
}

#[test]
fn capacity_spill_and_all_losses_are_accounted() {
    let mut c = fixture();
    c.store_capacity_j = 800_000.0;
    c.store_initial_j = 200_000.0;
    c.efficiency_capture = 0.8;
    c.efficiency_store = 0.9;
    c.efficiency_release = 0.7;
    c.standing_loss_w = 100.0;
    let r = evaluate(&c).unwrap();
    close(r.storage.accepted_j, 600_000.0);
    close(r.storage.overflow_j, 840_000.0);
    close(r.storage.standing_loss_j, 3000.0);
    close(r.storage.delivered_j, 557_900.0);
    close(r.storage.end_j, 0.0);
    close(r.storage.balance_residual_j, 0.0);
    close(r.energy_residual_j, 0.0);
    close(
        r.storage.delivered_from_initial_j + r.storage.delivered_from_new_capture_j,
        r.storage.delivered_j,
    );
    assert_eq!(r.necessary_bounds, "fail");
}

#[test]
fn full_store_has_explicit_overflow_not_free_capacity() {
    let mut c = fixture();
    c.store_initial_j = c.store_capacity_j;
    let r = evaluate(&c).unwrap();
    close(r.storage.accepted_j, 0.0);
    close(r.storage.overflow_j, 1_400_000.0);
    close(r.storage.delivered_from_new_capture_j, 0.0);
    close(r.storage.delivered_from_initial_j, 1_400_000.0);
    close(r.energy_residual_j, 0.0);
}

#[test]
fn reserve_and_standing_loss_prevent_unfunded_departure() {
    let mut c = fixture();
    c.store_reserve_j = 500_000.0;
    let r = evaluate(&c).unwrap();
    close(r.storage.end_j, 500_000.0);
    close(r.storage.delivered_j, 900_000.0);
    close(r.energy_residual_j, 0.0);
    c.standing_loss_w = 1_000_000.0;
    let loss = evaluate(&c).unwrap();
    close(loss.storage.delivered_j, 0.0);
    assert!(loss
        .failures
        .iter()
        .any(|s| s == "store-below-declared-reserve"));
}

#[test]
fn malformed_domain_is_rejected_before_work() {
    for eta in [-0.01, 1.01, f64::NAN, f64::INFINITY] {
        let mut c = fixture();
        c.efficiency_store = eta;
        assert!(evaluate(&c).is_err());
    }
    let mut c = fixture();
    c.store_initial_j = c.store_capacity_j + 1.0;
    assert!(evaluate(&c).is_err());
    c = fixture();
    c.resistance_n = -1.0;
    assert!(evaluate(&c).is_err());
    c = fixture();
    c.effective_mass_kg = c.physical_mass_kg - 1.0;
    assert!(evaluate(&c).is_err());
    c = fixture();
    c.effective_mass_kg = f64::MAX;
    c.capture_speed_m_s = f64::MAX;
    assert!(evaluate(&c).is_err());
    c = fixture();
    c.independent_brake_deceleration_m_s2 = Some(0.0);
    assert!(evaluate(&c).is_err());
}

#[test]
fn strict_json_rejects_unknown_fields_and_duplicate_ids() {
    let mut value = serde_json::to_value(fixture()).unwrap();
    value["mystery_capacity"] = serde_json::json!(1000);
    assert!(serde_json::from_value::<Case>(value).is_err());
    let c = fixture();
    assert!(execute(Request {
        schema: REQUEST_SCHEMA.into(),
        cases: vec![c.clone(), c]
    })
    .is_err());
    assert!(execute(Request {
        schema: "unknown".into(),
        cases: vec![fixture()]
    })
    .is_err());
}

#[test]
fn directly_compressed_spring_does_not_launch_forward() {
    let mut c = fixture();
    c.capture_profile = CaptureProfile::UnpreloadedSpring;
    c.capture_stroke_m = 32.0;
    c.forward_transfer = false;
    let r = evaluate(&c).unwrap();
    close(r.capture.required_stroke_m.unwrap(), 31.25);
    close(r.storage.delivered_j, 0.0);
    close(r.storage.end_j, 1_400_000.0);
    assert!(r
        .failures
        .iter()
        .any(|s| s == "forward-energy-transfer-missing"));
    close(r.energy_residual_j, 0.0);
}

#[test]
fn spring_grade_does_not_inherit_constant_deceleration_model() {
    let mut c = fixture();
    c.capture_profile = CaptureProfile::UnpreloadedSpring;
    c.grade_fraction = 0.02;
    c.launch_request_j = 0.0;
    let r = evaluate(&c).unwrap();
    assert_eq!(r.necessary_bounds, "unknown");
    assert!(r.capture.required_stroke_m.is_none());
    close(r.capture.unresolved_work_j, 2_000_000.0);
    close(r.storage.delivered_from_new_capture_j, 0.0);
    close(r.energy_residual_j, 0.0);
}

#[test]
fn failed_capture_stroke_or_force_does_not_credit_energy() {
    for force_limit in [None, Some(100_000.0)] {
        let mut c = fixture();
        c.independent_brake_deceleration_m_s2 = Some(0.5);
        c.capture_force_limit_n = force_limit;
        if force_limit.is_none() {
            c.capture_stroke_m = 1.0;
        }
        let r = evaluate(&c).unwrap();
        close(r.capture.credited_mechanical_capture_j, 0.0);
        close(r.capture.unrecovered_braking_j, 2_000_000.0);
        close(r.braking.capture_failure_stopping_distance_m.unwrap(), 25.0);
        assert!(!r.braking.physical_capability_verified);
        close(r.energy_residual_j, 0.0);
    }
}

#[test]
fn offset_and_active_length_are_distinct() {
    let mut c = fixture();
    c.booster_offset_m = 200.0;
    let r = evaluate(&c).unwrap();
    close(r.motion.coast_time_s.unwrap(), 47.809144373375744);
    close(r.booster.net_acceleration_m_s2.unwrap(), 0.95625);
    c.capture_speed_m_s = 0.0;
    c.launch_request_j = 0.0;
    let empty = evaluate(&c).unwrap();
    assert!(!empty.motion.booster_reached);
    assert!(empty.booster.required_force_n.is_none());
}

#[test]
fn two_percent_uphill_stalls_before_offset_booster() {
    let mut c = fixture();
    c.capture_speed_m_s = 0.0;
    c.store_initial_j = 1_400_000.0;
    c.efficiency_release = 1.0;
    c.grade_fraction = 0.02;
    c.booster_offset_m = 200.0;
    let r = evaluate(&c).unwrap();
    assert!(!r.motion.booster_reached);
    let force = 160_000.0 * 9.80665 * 0.02_f64.atan().sin();
    close(r.motion.coast_distance_travelled_m, 1_400_000.0 / force);
    assert!(r.booster.required_force_n.is_none());
    close(r.energy_residual_j, 0.0);
}

#[test]
fn gravity_uses_physical_mass_and_capture_work_balances() {
    let mut c = fixture();
    c.effective_mass_kg = 170_000.0;
    c.grade_fraction = 0.02;
    c.resistance_n = 3000.0;
    let r = evaluate(&c).unwrap();
    let force = 160_000.0 * 9.80665 * 0.02_f64.atan().sin() + 3000.0;
    close(r.capture.opposing_work_j, force * 15.625);
    close(
        r.capture.available_braking_work_j,
        2_125_000.0 - force * 15.625,
    );
    close(r.energy_residual_j, 0.0);
}

#[test]
fn requested_power_and_force_are_not_available_capacity() {
    let mut c = fixture();
    c.source_power_limit_w = Some(3_100_000.0);
    c.available_booster_force_n = Some(100_000.0);
    c.max_booster_acceleration_m_s2 = Some(0.9);
    let r = evaluate(&c).unwrap();
    assert!(r
        .failures
        .iter()
        .any(|s| s == "booster-source-power-limit-exceeded"));
    assert!(r
        .failures
        .iter()
        .any(|s| s == "booster-force-limit-exceeded"));
    assert!(r
        .failures
        .iter()
        .any(|s| s == "booster-net-acceleration-limit-exceeded"));
    assert!(!r.engineering_accepted);
}

#[test]
fn exclusive_resource_includes_capture_dwell_release_and_reset() {
    let mut c = fixture();
    c.headway_s = 50.0;
    let r = evaluate(&c).unwrap();
    close(r.resource.occupation_s.unwrap(), 56.25);
    close(r.resource.headway_margin_s.unwrap(), -6.25);
    assert!(r
        .failures
        .iter()
        .any(|s| s == "exclusive-capture-release-resource-exceeds-headway"));
}

#[test]
fn sequential_departures_cannot_spend_the_same_store_twice() {
    let mut c = fixture();
    c.capture_speed_m_s = 0.0;
    c.store_initial_j = 1_400_000.0;
    let first = evaluate(&c).unwrap();
    close(first.storage.delivered_j, 1_400_000.0);
    c.store_initial_j = first.storage.end_j;
    let second = evaluate(&c).unwrap();
    close(second.storage.delivered_j, 0.0);
    close(
        first.storage.delivered_j + second.storage.delivered_j,
        1_400_000.0,
    );
    assert!(second
        .failures
        .iter()
        .any(|s| s == "launch-energy-request-not-met"));
}

#[test]
fn speed_is_a_variable_not_72_kmh_requirement() {
    let mut powers = Vec::new();
    for kmh in [40.0, 50.0, 60.0, 72.0] {
        let mut c = fixture();
        c.target_speed_m_s = kmh / 3.6;
        powers.push(
            evaluate(&c)
                .unwrap()
                .booster
                .peak_mechanical_power_w
                .unwrap(),
        );
    }
    assert!(powers.windows(2).all(|pair| pair[0] < pair[1]));
}

#[test]
fn release_duration_cannot_be_zero_for_positive_work() {
    let mut c = fixture();
    c.release_duration_s = 0.0;
    let r = evaluate(&c).unwrap();
    close(r.storage.delivered_j, 0.0);
    close(r.storage.end_j, 1_400_000.0);
    assert!(r
        .failures
        .iter()
        .any(|s| s == "positive-launch-work-needs-release-duration"));
}

#[test]
fn unit_efficiency_conserves_work_and_zero_efficiency_gives_no_launch() {
    let mut c = fixture();
    c.efficiency_store = 1.0;
    c.launch_request_j = 2_000_000.0;
    let r = evaluate(&c).unwrap();
    close(r.storage.delivered_j, 2_000_000.0);
    close(r.energy_residual_j, 0.0);
    c.efficiency_release = 0.0;
    let zero = evaluate(&c).unwrap();
    close(zero.storage.delivered_j, 0.0);
    close(zero.storage.end_j, 2_000_000.0);
    close(zero.energy_residual_j, 0.0);
}

#[test]
fn unconstrained_mass_scaling_preserves_launch_speed_not_force() {
    let base = evaluate(&fixture()).unwrap();
    let mut c = fixture();
    c.physical_mass_kg *= 2.0;
    c.effective_mass_kg *= 2.0;
    c.launch_request_j *= 2.0;
    let double = evaluate(&c).unwrap();
    close(
        double.motion.ideal_launch_speed_m_s,
        base.motion.ideal_launch_speed_m_s,
    );
    close(
        double.booster.required_force_n.unwrap(),
        2.0 * base.booster.required_force_n.unwrap(),
    );
    close(
        double.booster.peak_mechanical_power_w.unwrap(),
        2.0 * base.booster.peak_mechanical_power_w.unwrap(),
    );
    close(double.energy_residual_j, 0.0);
}

#[test]
fn request_count_bound_is_independent_of_reader_byte_bound() {
    assert!(execute(Request {
        schema: REQUEST_SCHEMA.into(),
        cases: Vec::new()
    })
    .is_err());
    assert!(execute(Request {
        schema: REQUEST_SCHEMA.into(),
        cases: vec![fixture(); 10_001]
    })
    .is_err());
}
