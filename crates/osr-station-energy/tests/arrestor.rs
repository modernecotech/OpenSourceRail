use osr_station_energy::arrestor::*;
fn near(a: f64, b: f64) {
    assert!((a - b).abs() <= 1e-8 * b.abs().max(1.0), "{a} != {b}");
}
fn case() -> Case {
    Case {
        id: "reference".into(),
        effective_mass_kg: 160000.0,
        capture_entry_speed_m_s: 10.0,
        grade_fraction: 0.0,
        resistance_n: 0.0,
        handover: Handover::ContinuousTotalForce,
        stages: [8.0, 6.0, 4.0, 2.0, 0.0]
            .into_iter()
            .map(|v| Stage {
                exit_speed_m_s: v,
                max_deceleration_m_s2: 0.8,
                max_jerk_m_s3: 0.5,
                available_stroke_m: 1000.0,
                force_limit_n: None,
                displacement_ratio: 10.0,
            })
            .collect(),
        storage: Store {
            capacity_j: 8000000.0,
            initial_j: 0.0,
            reserve_j: 0.0,
            efficiency_capture: 0.7,
            efficiency_store: 1.0,
            efficiency_release: 1.0,
            standing_loss_w: 0.0,
            dwell_s: 30.0,
            isolated_during_dwell: true,
            controlled_forward_transfer: true,
            departure_authorized: true,
            design: StorageDesign::DeclaredSpecificEnergy {
                specific_energy_j_kg: 140.0,
                density_kg_m3: 7850.0,
                packing_fraction: 0.2,
            },
        },
        launch: Launch {
            target_speed_m_s: 70.0_f64.sqrt(),
            max_acceleration_m_s2: 1.0,
            max_jerk_m_s3: 0.5,
            available_stroke_m: 1000.0,
            force_limit_n: None,
            mass_fractions: vec![1.0 / 6.0; 6],
            force_fractions: vec![0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        },
        booster: Booster {
            target_speed_m_s: 20.0,
            max_acceleration_m_s2: 1.0,
            max_jerk_m_s3: 0.5,
            efficiency: 0.9,
            available_stroke_m: 1000.0,
            force_limit_n: None,
            source_power_limit_w: None,
        },
        reset_s: 10.0,
        headway_s: 200.0,
    }
}
#[test]
fn independent_continuous_capture_and_energy_controls() {
    let c = case();
    let r = evaluate(&c).unwrap();
    near(r.capture.entry_kinetic_energy_j, 8000000.0);
    near(r.capture.total_time_s.unwrap(), 14.1);
    near(r.capture.total_distance_m.unwrap(), 70.5);
    near(r.capture.required_peak_force_n.unwrap(), 128000.0);
    near(r.storage.delivered_j, 5600000.0);
    near(r.launch.as_ref().unwrap().exit_speed_m_s, 70.0_f64.sqrt());
    near(r.storage.end_j, 0.0);
    near(r.energy_residual_j, 0.0);
    assert_eq!(r.necessary_bounds, "unknown");
    assert!(r.failures.is_empty());
}
#[test]
fn pulses_trade_extra_track_and_time_for_force_release_at_handover() {
    let mut c = case();
    c.handover = Handover::IndependentStagePulses;
    let r = evaluate(&c).unwrap();
    near(r.capture.total_time_s.unwrap(), 20.5);
    near(r.capture.total_distance_m.unwrap(), 102.5);
    near(r.storage.delivered_j, 5600000.0);
    let rows = r.capture.stages.unwrap();
    for pair in rows.windows(2) {
        near(pair[0].end_x_m, pair[1].start_x_m);
        near(pair[0].exit_speed_m_s, pair[1].entry_speed_m_s);
    }
}
#[test]
fn gearing_trades_force_for_stroke_without_inventing_work() {
    let r = evaluate(&case()).unwrap();
    for s in r.capture.stages.unwrap() {
        near(s.store_travel_m, s.distance_m / 10.0);
        near(s.store_force_upper_bound_n, s.required_peak_force_n * 10.0);
    }
}
#[test]
fn rear_front_and_distributed_force_paths_have_different_quasistatic_couplers() {
    let mut c = case();
    let rear = evaluate(&c).unwrap().launch.unwrap();
    near(*rear.coupler_tension_n.last().unwrap(), -133333.3333333333);
    c.launch.force_fractions = vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0];
    let front = evaluate(&c).unwrap().launch.unwrap();
    near(front.coupler_tension_n[0], 133333.3333333333);
    c.launch.force_fractions = c.launch.mass_fractions.clone();
    let distributed = evaluate(&c).unwrap().launch.unwrap();
    assert!(distributed.coupler_tension_n.iter().all(|x| x.abs() < 1e-8));
}
#[test]
fn jerk_limited_launcher_exceeds_the_constant_acceleration_35m_bound() {
    let r = evaluate(&case()).unwrap();
    let l = r.launch.unwrap();
    near(l.distance_m, 35.0 + 70.0_f64.sqrt());
    near(l.time_s, 70.0_f64.sqrt() + 2.0);
    near(l.required_peak_force_n, 160000.0);
    assert!(l.peak_mechanical_power_w > 0.0);
    assert!(l.peak_mechanical_power_w < 160000.0 * 70.0_f64.sqrt());
    near(l.phase_knots[0].acceleration_m_s2, 0.0);
    near(l.phase_knots.last().unwrap().acceleration_m_s2, 0.0);
}
#[test]
fn analytic_peak_power_bounds_dense_independent_sampling() {
    let r = evaluate(&case()).unwrap();
    let l = r.launch.unwrap();
    let a = 1.0;
    let j = 0.5;
    let tr = a / j;
    let hold = 70.0_f64.sqrt() / a - tr;
    let ttotal = 2.0 * tr + hold;
    let mut sampled = 0.0_f64;
    for i in 0..10001 {
        let t = ttotal * f64::from(i) / 10000.0;
        let (acc, v) = if t < tr {
            (j * t, j * t * t / 2.0)
        } else if t < tr + hold {
            (a, a * tr / 2.0 + a * (t - tr))
        } else {
            let u = t - tr - hold;
            (a - j * u, a * tr / 2.0 + a * hold + a * u - j * u * u / 2.0)
        };
        sampled = sampled.max(160000.0 * acc * v);
    }
    assert!(l.peak_mechanical_power_w >= sampled * (1.0 - 1e-10));
    near(
        l.peak_mechanical_power_w,
        160000.0 * (70.0_f64.sqrt() - 1.0),
    );
    assert!(l.peak_mechanical_power_w - sampled <= 160000.0 * a * a * ttotal / 10000.0);
}
#[test]
fn literature_specific_energy_is_a_sensitivity_not_installed_mass() {
    for (capacity, expected) in [
        (2000000.0, 14285.714285714286),
        (8000000.0, 57142.857142857145),
        (32000000.0, 228571.42857142858),
    ] {
        let s = size_store(capacity, &case().storage.design).unwrap();
        near(s.active_mass_kg, expected);
        assert!(!s.complete_installed_mass);
    }
}
#[test]
fn elastic_stress_model_has_quadratic_stress_and_inverse_modulus_scaling() {
    let d = StorageDesign::Elastic {
        stress_mode: StressMode::Torsional,
        density_kg_m3: 7850.0,
        modulus_pa: 80e9,
        allowable_stress_pa: 650e6,
        utilisation: 0.4,
        packing_fraction: 0.2,
    };
    let s = size_store(8e6, &d).unwrap();
    near(
        s.specific_energy_j_kg.unwrap(),
        650e6 * 650e6 / (2.0 * 80e9 * 7850.0) * 0.4,
    );
    assert!(s.active_mass_kg > 50000.0);
    near(
        s.active_material_volume_m3.unwrap() * 7850.0,
        s.active_mass_kg,
    );
}
#[test]
fn hydraulic_isothermal_limit_matches_analytic_log_and_nearby_exponents() {
    let hydraulic = |n| StorageDesign::Hydraulic {
        precharge_pressure_pa: 10e6,
        min_pressure_pa: 12e6,
        max_pressure_pa: 30e6,
        return_pressure_pa: 1e5,
        polytropic_exponent: n,
        vessel_mass_kg_per_m3: 3000.0,
        packing_fraction: 0.7,
    };
    let s = size_store(8e6, &hydraulic(1.0)).unwrap();
    let expected = 10e6 * (2.5_f64).ln() - 1e5 * (10.0 / 12.0 - 10.0 / 30.0);
    near(s.specific_work_j_m3.unwrap(), expected);
    near(s.active_mass_kg, 8e6 / expected * 3000.0);
    let close = size_store(8e6, &hydraulic(1.000000001)).unwrap();
    near(close.specific_work_j_m3.unwrap(), expected);
    assert!(s.active_material_volume_m3.is_none());
    assert!(s.internal_volume_m3.is_some());
}
#[test]
fn hydraulic_polytropic_capacity_accounts_return_pressure_work() {
    let d = StorageDesign::Hydraulic {
        precharge_pressure_pa: 10e6,
        min_pressure_pa: 12e6,
        max_pressure_pa: 30e6,
        return_pressure_pa: 1e5,
        polytropic_exponent: 1.4,
        vessel_mass_kg_per_m3: 3000.0,
        packing_fraction: 0.7,
    };
    let s = size_store(8e6, &d).unwrap();
    let v1 = (10.0_f64 / 12.0).powf(1.0 / 1.4);
    let v2 = (10.0_f64 / 30.0).powf(1.0 / 1.4);
    near(
        s.specific_work_j_m3.unwrap(),
        (30e6 * v2 - 12e6 * v1) / 0.4 - 1e5 * (v1 - v2),
    );
}
#[test]
fn flywheel_rim_is_not_a_complete_contained_assembly() {
    let d = StorageDesign::Flywheel {
        density_kg_m3: 7850.0,
        allowable_stress_pa: 600e6,
        utilisation: 0.6,
        min_max_speed_ratio: 0.5,
        radius_m: 0.5,
        packing_fraction: 0.05,
    };
    let s = size_store(8e6, &d).unwrap();
    near(
        s.specific_energy_j_kg.unwrap(),
        0.5 * 600e6 / 7850.0 * 0.6 * 0.75,
    );
    near(s.tip_speed_m_s.unwrap(), (600e6_f64 / 7850.0).sqrt());
    assert!(!s.complete_installed_mass);
}
#[test]
fn storage_losses_capacity_reserve_and_origins_balance_together() {
    let mut c = case();
    c.storage.capacity_j = 800000.0;
    c.storage.initial_j = 200000.0;
    c.storage.reserve_j = 50000.0;
    c.storage.efficiency_capture = 0.8;
    c.storage.efficiency_store = 0.9;
    c.storage.efficiency_release = 0.7;
    c.storage.standing_loss_w = 100.0;
    let r = evaluate(&c).unwrap();
    near(r.storage.accepted_j, 600000.0);
    near(r.storage.overflow_j, 5160000.0);
    near(r.storage.delivered_j, 522900.0);
    near(r.storage.end_j, 50000.0);
    near(r.storage.delivered_from_initial_j, 137900.0);
    near(r.storage.delivered_from_new_capture_j, 385000.0);
    near(r.energy_residual_j, 0.0);
    assert_eq!(r.necessary_bounds, "fail");
}
#[test]
fn held_energy_is_not_launched_without_departure_authority() {
    let mut c = case();
    c.storage.departure_authorized = false;
    let r = evaluate(&c).unwrap();
    near(r.storage.delivered_j, 0.0);
    near(r.storage.end_j, 5600000.0);
    assert!(r.launch.is_none());
    assert!(r.booster.is_none());
    assert!(r.resource.occupation_s.is_none());
    assert_eq!(r.storage.departure_state, "held-no-departure-authority");
    assert!(r.failures.is_empty());
}
#[test]
fn missing_isolation_or_forward_transfer_blocks_positive_launch_work() {
    let mut c = case();
    c.storage.isolated_during_dwell = false;
    let r = evaluate(&c).unwrap();
    near(r.storage.delivered_j, 0.0);
    assert_eq!(r.necessary_bounds, "fail");
    assert!(r.launch.is_none());
    c.storage.isolated_during_dwell = true;
    c.storage.controlled_forward_transfer = false;
    let r = evaluate(&c).unwrap();
    near(r.storage.delivered_j, 0.0);
    assert!(r.launch.is_none());
}
#[test]
fn stage_failure_never_credits_that_stages_energy() {
    let mut c = case();
    c.stages[0].available_stroke_m = 0.1;
    let r = evaluate(&c).unwrap();
    let first = &r.capture.stages.as_ref().unwrap()[0];
    near(first.credited_capture_j, 0.0);
    near(first.unrecovered_braking_j, 2880000.0);
    assert!(!first.bound_failures.is_empty());
    near(r.energy_residual_j, 0.0);
    assert_eq!(r.necessary_bounds, "fail");
}
#[test]
fn unsupported_grade_keeps_unresolved_energy_instead_of_fabricated_trajectory() {
    let mut c = case();
    c.grade_fraction = 0.02;
    let r = evaluate(&c).unwrap();
    assert_eq!(r.necessary_bounds, "unknown");
    assert!(r.capture.stages.is_none());
    assert!(r.launch.is_none());
    near(r.storage.unresolved_capture_j, 8000000.0);
    near(r.storage.accepted_j, 0.0);
    near(r.energy_residual_j, 0.0);
}
#[test]
fn longer_reset_and_source_power_limit_are_known_failures() {
    let mut c = case();
    c.reset_s = 300.0;
    c.booster.source_power_limit_w = Some(1000.0);
    let r = evaluate(&c).unwrap();
    assert!(r.resource.headway_margin_s.unwrap() < 0.0);
    assert!(r.failures.iter().any(|s| s.contains("power-limit")));
}
#[test]
fn next_event_cannot_reuse_the_predecessors_spent_energy() {
    let first = evaluate(&case()).unwrap();
    let mut c = case();
    c.id = "next".into();
    c.capture_entry_speed_m_s = 0.0;
    c.stages.clear();
    c.storage.initial_j = first.storage.end_j;
    let next = evaluate(&c).unwrap();
    near(next.storage.delivered_j, 0.0);
    near(next.storage.delivered_from_new_capture_j, 0.0);
    near(next.energy_residual_j, 0.0);
}
#[test]
fn speed_choices_and_car_counts_are_not_fixed_to_reference() {
    for speed in [40.0, 50.0, 60.0, 72.0] {
        let mut c = case();
        c.booster.target_speed_m_s = speed / 3.6;
        c.launch.mass_fractions = vec![0.25, 0.75];
        c.launch.force_fractions = vec![0.0, 1.0];
        let r = evaluate(&c).unwrap();
        near(r.booster.unwrap().motion.exit_speed_m_s, speed / 3.6);
        assert_eq!(r.launch.unwrap().coupler_tension_n.len(), 1);
    }
}
#[test]
fn malformed_domains_schema_and_duplicate_ids_are_rejected() {
    let mut c = case();
    c.storage.efficiency_capture = 1.1;
    assert!(evaluate(&c).is_err());
    c = case();
    c.stages[0].exit_speed_m_s = 10.0;
    assert!(evaluate(&c).is_err());
    c = case();
    c.launch.mass_fractions[0] = 0.5;
    assert!(evaluate(&c).is_err());
    c = case();
    c.storage.initial_j = 9e6;
    assert!(evaluate(&c).is_err());
    let v = serde_json::to_value(case()).unwrap();
    let mut altered = v.clone();
    altered["pretend_accepted"] = serde_json::json!(true);
    assert!(serde_json::from_value::<Case>(altered).is_err());
    let c = case();
    assert!(execute(Request {
        schema: REQUEST_SCHEMA.into(),
        cases: vec![c.clone(), c]
    })
    .is_err());
    assert!(execute(Request {
        schema: "wrong".into(),
        cases: vec![case()]
    })
    .is_err());
}
#[test]
fn all_acceptance_and_authority_flags_stay_false() {
    let r = evaluate(&case()).unwrap();
    assert!(
        !r.physical_accepted
            && !r.engineering_accepted
            && !r.manufacturing_release
            && !r.operating_release
            && !r.selected_reference_changed
            && !r.movement_authority
    );
}

#[test]
fn triangular_launch_peak_power_has_an_interior_analytic_maximum() {
    let mut c = case();
    c.launch.target_speed_m_s = 0.5;
    let l = evaluate(&c).unwrap().launch.unwrap();
    near(
        l.peak_mechanical_power_w,
        160000.0 * (2.0 * 0.5 / 3.0) * (2.0_f64 * 0.5 * 0.5 / 3.0).sqrt(),
    );
}
#[test]
fn representational_overflow_and_instantaneous_underflow_motion_are_rejected() {
    let mut c = case();
    c.effective_mass_kg = f64::MAX;
    assert!(evaluate(&c).is_err());
    c = case();
    c.launch.max_acceleration_m_s2 = f64::MIN_POSITIVE;
    c.launch.max_jerk_m_s3 = 1e300;
    assert!(evaluate(&c).is_err());
}
