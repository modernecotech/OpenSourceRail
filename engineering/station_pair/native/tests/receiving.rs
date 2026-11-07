//! Declared six-car method fixture, not a qualified vehicle or actuator map.
use osr_journey::{cycle::*, *};
fn fixture() -> CycleCase {
    let c: Case = serde_json::from_str(
        r#"{
  "acceleration_request_m_s2": 1.0,
  "air_density_kg_m3": 1.2,
  "auxiliary_power_w": 210000.0,
  "berth_tolerance_m": 2.0,
  "brake_adhesion_force_cap_n": 152583.55455357945,
  "brake_force_cap_n": 35556.214959365745,
  "brake_latency_s": 0.5,
  "brake_rise_s": 1.0,
  "brake_start_m": 1200.0,
  "candidate_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "cd_a_m2": 8.0,
  "comfort_jerk_m_s3": 0.5,
  "control": {
    "acceleration_bias_m_s2": 0.0,
    "acceleration_error_bound_m_s2": 0.02,
    "brake_force_lower_bound_n": 32000.59346342917,
    "brake_rise_time_bound_s": 1.3,
    "drive_fault_observed": false,
    "end_of_authority_m": 1500.0,
    "external_mass_upper_kg": 0.0,
    "external_resistance_upper_n": 0.0,
    "grade_error_bound": 0.001,
    "grade_estimate_fraction": 0.0,
    "initial_hold_applied": true,
    "mass_lower_kg": 113539.44497903739,
    "mass_upper_kg": 156050.44095811964,
    "policy_id": "a935951ba8225a3ed8c4e9942c4b4fbc6992f4767fc0670f8bc78b4f2c511cf9",
    "position_bias_m": 0.0,
    "position_error_bound_m": 0.25,
    "positive_acceleration_bound_m_s2": 2.0,
    "reaction_time_bound_s": 0.7,
    "rolling_resistance_upper_n": 6121.328227287776,
    "rotating_mass_upper_kg": 15605.044095811965,
    "speed_bias_m_s": 0.0,
    "speed_error_bound_m_s": 0.1,
    "start_traction_lower_bound_n": 22158.315984800058,
    "stopping_margin_m": 0.5
  },
  "distance_m": 1500.0,
  "drive": {
    "contact_force_cap_n": 76291.77727678973,
    "electrical_efficiency": 0.9,
    "external_mass_kg": 0.0,
    "external_resistance_n": 0.0,
    "grid_power_w": 2280000.0,
    "maximum_speed_m_s": 22.22222222222222,
    "mechanical_power_w": 1744200.0,
    "points": [
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 0.0
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 0.9259259259259259
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 1.8518518518518519
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 2.7777777777777772
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 3.7037037037037037
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 4.62962962962963
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 5.5555555555555545
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 6.481481481481481
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 7.407407407407407
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 8.333333333333334
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 9.25925925925926
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 10.185185185185185
      },
      {
        "force_n": 145643.13331097102,
        "speed_m_s": 11.111111111111109
      },
      {
        "force_n": 144902.76923076925,
        "speed_m_s": 12.037037037037036
      },
      {
        "force_n": 134552.57142857145,
        "speed_m_s": 12.962962962962962
      },
      {
        "force_n": 125582.40000000001,
        "speed_m_s": 13.888888888888888
      },
      {
        "force_n": 117733.5,
        "speed_m_s": 14.814814814814815
      },
      {
        "force_n": 110808.0,
        "speed_m_s": 15.74074074074074
      },
      {
        "force_n": 104651.99999999999,
        "speed_m_s": 16.666666666666668
      },
      {
        "force_n": 99144.0,
        "speed_m_s": 17.59259259259259
      },
      {
        "force_n": 94186.8,
        "speed_m_s": 18.51851851851852
      },
      {
        "force_n": 89701.71428571429,
        "speed_m_s": 19.444444444444443
      },
      {
        "force_n": 85624.36363636363,
        "speed_m_s": 20.37037037037037
      },
      {
        "force_n": 81901.56521739131,
        "speed_m_s": 21.296296296296294
      },
      {
        "force_n": 78489.0,
        "speed_m_s": 22.22222222222222
      }
    ],
    "windows_m": [
      [
        0.0,
        1500.0
      ]
    ]
  },
  "dt_s": 0.05,
  "dwell_s": 35.0,
  "fault": {
    "emergency_at_m": null,
    "failed_drive_fraction": 0.0,
    "power_loss_at_s": null
  },
  "grade_fraction": 0.0,
  "headway_s": 200.0,
  "headwind_m_s": 0.0,
  "id": "six-car-method-fixture",
  "mass_kg": 129659.93701007264,
  "max_time_s": 600.0,
  "rolling_coefficient": 0.003,
  "rotating_equivalent_mass_kg": 7779.596220604358,
  "speed_cap_m_s": 16.666666666666668,
  "thermal": {
    "ambient_c": 50.0,
    "capacity_j_k": 1200000.0,
    "heat_rejection_w_k": 2000.0,
    "initial_c": 50.0,
    "maximum_c": 120.0
  }
}"#,
    )
    .unwrap();
    let stations: Vec<Station> = serde_json::from_str(
        r#"[
  {
    "capture_stages": [
      {
        "end_m": 1300.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1250.0
      },
      {
        "end_m": 1350.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1300.0
      },
      {
        "end_m": 1400.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1350.0
      },
      {
        "end_m": 1450.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1400.0
      },
      {
        "end_m": 1500.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1450.0
      }
    ],
    "id": "A",
    "initial_energy_j": 0.0,
    "release": {
      "end_m": 200.0,
      "max_force_n": 100000.0,
      "max_power_w": 1000000.0,
      "start_m": 0.0
    },
    "reset": {
      "duration_s": 15.0,
      "grid_energy_j": 250000.0,
      "grid_power_w": 25000.0
    },
    "store": {
      "capacity_j": 4000000.0,
      "capture_efficiency": 0.9,
      "leakage_per_s": 1e-06,
      "release_efficiency": 0.9
    }
  },
  {
    "capture_stages": [
      {
        "end_m": 1300.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1250.0
      },
      {
        "end_m": 1350.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1300.0
      },
      {
        "end_m": 1400.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1350.0
      },
      {
        "end_m": 1450.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1400.0
      },
      {
        "end_m": 1500.0,
        "max_force_n": 30000.0,
        "max_power_w": 400000.0,
        "start_m": 1450.0
      }
    ],
    "id": "B",
    "initial_energy_j": 0.0,
    "release": {
      "end_m": 200.0,
      "max_force_n": 100000.0,
      "max_power_w": 1000000.0,
      "start_m": 0.0
    },
    "reset": {
      "duration_s": 15.0,
      "grid_energy_j": 250000.0,
      "grid_power_w": 25000.0
    },
    "store": {
      "capacity_j": 4000000.0,
      "capture_efficiency": 0.9,
      "leakage_per_s": 1e-06,
      "release_efficiency": 0.9
    }
  }
]"#,
    )
    .unwrap();
    CycleCase {
        id: "method-fixture".into(),
        candidate_id: c.candidate_id.clone(),
        stations,
        release_control: Some(ReleaseControl {
            mode: "grid-substitution-slew/1".into(),
            force_slew_n_s: 10000.,
            maximum_traction_share: 0.8,
            reserve_factor: 2.,
        }),
        legs: (0..8)
            .map(|i| {
                let mut journey = c.clone();
                journey.id = format!("fixture-leg-{i}");
                Leg {
                    train_id: "same-point-train".into(),
                    journey,
                    departure_station_id: if i % 2 == 0 { "A" } else { "B" }.into(),
                    arrival_station_id: if i % 2 == 0 { "B" } else { "A" }.into(),
                    departure_time_s: i as f64 * 260.,
                    departure_authorized: true,
                    capture_failed: false,
                    release_failed: false,
                    reset_failed: false,
                }
            })
            .collect(),
    }
}
#[test]
fn six_car_receiver_handles_same_hardware_on_off_and_body_mass_sensitivity_at_all_steps() {
    for dt in [0.05, 0.025, 0.0125] {
        for extra in [0., 1018., 1387.3443] {
            let mut on = fixture();
            for l in &mut on.legs {
                let old = l.journey.mass_kg;
                l.journey.mass_kg += extra;
                l.journey.rotating_equivalent_mass_kg += extra * 0.06;
                l.journey.brake_adhesion_force_cap_n *= l.journey.mass_kg / old;
                l.journey.dt_s = dt;
            }
            let mut off = on.clone();
            for l in &mut off.legs {
                l.capture_failed = true;
                l.release_failed = true;
            }
            let a = osr_journey::cycle::evaluate(&on).unwrap();
            let b = osr_journey::cycle::evaluate(&off).unwrap();
            assert_eq!(a.arrived_legs, 8, "dt{dt} extra{extra} state{}", a.state);
            assert_eq!(b.arrived_legs, 8);
            for (on, off) in a.legs.iter().zip(&b.legs) {
                let j = on.journey.as_ref().unwrap();
                let k = off.journey.as_ref().unwrap();
                assert!(
                    j.maximum_absolute_jerk_m_s3 <= 0.5,
                    "dt{dt} extra{extra} {:?}",
                    on.energy.release_control
                );
                assert!(
                    j.elapsed_s <= 210.,
                    "dt{dt} extra{extra} elapsed{}",
                    j.elapsed_s
                );
                assert!(j.final_position_m >= 1498. && j.final_position_m <= 1500.);
                assert!(
                    j.control.as_ref().unwrap().bounds_valid
                        && !j.control.as_ref().unwrap().end_of_authority_violated
                );
                assert_eq!(
                    serde_json::to_value(&j.trace).unwrap(),
                    serde_json::to_value(&k.trace).unwrap()
                );
                assert!(
                    !on.energy
                        .release_control
                        .as_ref()
                        .unwrap()
                        .slew_limit_exceeded
                );
                assert_eq!(
                    on.energy.release_control.as_ref().unwrap().forced_cutoffs,
                    0,
                    "dt{dt} extra{extra}"
                );
            }
            assert!(a.ledger.storage_balance_residual_j.abs() < 1e-5);
            assert!(a.ledger.train_and_storage_balance_residual_j.abs() < 1e-5);
        }
    }
}
