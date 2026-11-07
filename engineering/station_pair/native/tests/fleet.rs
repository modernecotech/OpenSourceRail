//! Event-order and resource tests use declared method fixtures, not qualified
//! terminal, drivetrain, storage or train-control hardware.
mod common;
use osr_journey::fleet::*;
fn near(a: f64, b: f64, tolerance: f64) {
    assert!((a - b).abs() < tolerance, "{a}!={b}");
}
fn fleet(headway: f64, phase: f64, active: usize) -> FleetCase {
    let base = common::fixture();
    let mut trains = vec![
        Train {
            id: "A0".into(),
            initial_station_id: "A".into(),
            initial_position_m: 0.,
            ready_at_s: 0.,
            role: TrainRole::Active,
            initial_drive_temperature_c: Some(50.),
        },
        Train {
            id: "A1".into(),
            initial_station_id: "A".into(),
            initial_position_m: 0.,
            ready_at_s: 0.,
            role: TrainRole::Active,
            initial_drive_temperature_c: Some(50.),
        },
        Train {
            id: "B0".into(),
            initial_station_id: "B".into(),
            initial_position_m: 0.,
            ready_at_s: 0.,
            role: TrainRole::Active,
            initial_drive_temperature_c: Some(50.),
        },
    ];
    if active == 4 {
        trains.push(Train {
            id: "B1".into(),
            initial_station_id: "B".into(),
            initial_position_m: 0.,
            ready_at_s: 0.,
            role: TrainRole::Active,
            initial_drive_temperature_c: Some(50.),
        });
    }
    trains.push(Train {
        id: "spare".into(),
        initial_station_id: "B".into(),
        initial_position_m: 0.,
        ready_at_s: 0.,
        role: TrainRole::Spare,
        initial_drive_temperature_c: Some(50.),
    });
    let departures = (0..8)
        .flat_map(|i| (0..2).map(move |dir| (i, dir)))
        .map(|(i, dir)| {
            let mut journey = base.legs[0].journey.clone();
            let id = format!("departure-{dir}-{i}");
            journey.id = id.clone();
            Departure {
                id,
                journey,
                departure_station_id: if dir == 0 { "A" } else { "B" }.into(),
                arrival_station_id: if dir == 0 { "B" } else { "A" }.into(),
                departure_time_s: i as f64 * headway + if dir == 0 { 0. } else { phase },
                departure_authorized: true,
                capture_failed: false,
                release_failed: false,
                reset_failed: false,
                requested_train_id: None,
            }
        })
        .collect();
    FleetCase {
        id: "fleet-method".into(),
        candidate_id: base.candidate_id,
        stations: base.stations,
        release_control: base.release_control.unwrap(),
        trains,
        departures,
        turnaround_s: 45.,
        clearance_s: 3.,
    }
}
#[test]
fn three_active_trains_and_spare_deliver_phased210s_without_future_energy() {
    let c = fleet(210., 60., 3);
    let r = evaluate(&c).unwrap();
    assert!(
        r.schedule_numerical_complete,
        "{} arrivals{} held{:?}",
        r.state,
        r.normal_arrivals,
        r.departures
            .iter()
            .filter(|d| d.state == "departure-held")
            .map(|d| &d.hold_reason)
            .collect::<Vec<_>>()
    );
    assert_eq!(r.normal_arrivals, 16);
    assert_eq!(r.active_trains, 3);
    assert_eq!(r.spare_trains, 1);
    assert!(
        r.departures
            .iter()
            .all(|d| d.train_id.as_deref() != Some("spare"))
    );
    for d in r.departures.iter().filter(|d| d.departure_time_s < 100.) {
        near(d.energy.delivered_launch_work_j, 0., 1e-8);
    }
    near(r.ledger.storage_balance_residual_j, 0., 1e-4);
    near(r.ledger.train_and_storage_balance_residual_j, 0., 1e-4);
    assert!(
        !r.physical_accepted
            && !r.terminal_dynamics_supported
            && !r.route_separation_qualified
            && !r.thermal_duty_verified
    );
}
#[test]
fn synchronized210s_requires_counted_fourth_active_not_the_spare() {
    let a = evaluate(&fleet(210., 0., 3)).unwrap();
    let b = evaluate(&fleet(210., 0., 4)).unwrap();
    assert!(!a.schedule_numerical_complete);
    assert!(a.blocked_departures > 0);
    assert!(
        b.schedule_numerical_complete,
        "{:?}",
        b.departures
            .iter()
            .map(|d| &d.hold_reason)
            .collect::<Vec<_>>()
    );
    assert!(
        a.departures
            .iter()
            .all(|d| d.train_id.as_deref() != Some("spare"))
    );
}
#[test]
fn bank_busy_bypasses_to_grid_and_friction_instead_of_holding_service() {
    let c = fleet(200., 90., 3);
    let r = evaluate(&c).unwrap();
    assert!(r.schedule_numerical_complete);
    assert!(r.departures.iter().any(|d| d.release_bypassed));
    assert!(r.departures.iter().any(|d| d.capture_bypassed));
    assert!(
        r.departures.iter().filter(|d| d.release_bypassed).all(|d| d
            .journey
            .as_ref()
            .unwrap()
            .normal_numerical_arrival)
    );
}
#[test]
fn actual_stop_offset_and_drive_temperature_follow_the_assigned_train() {
    let c = fleet(210., 60., 3);
    let r = evaluate(&c).unwrap();
    let mut previous = std::collections::HashMap::new();
    for d in &r.departures {
        let Some(id) = d.train_id.as_ref() else {
            continue;
        };
        if d.state != "arrived" {
            continue;
        }
        if let Some(old) = previous.get(id) {
            near(d.initial_position_m.unwrap(), *old, 1e-8);
        }
        previous.insert(
            id.clone(),
            1500. - d.journey.as_ref().unwrap().final_position_m,
        );
        assert_eq!(
            d.actual_applied_case
                .as_ref()
                .unwrap()
                .thermal
                .as_ref()
                .unwrap()
                .initial_c,
            d.initial_drive_temperature_c.unwrap()
        );
    }
    assert!(r.maximum_thermal_proxy_temperature_c.unwrap() > 50.);
    assert!(r.numerical_thermal_limits_met);
}
#[test]
fn initial_and_idle_thermal_states_are_explicit_not_reset_each_departure() {
    let mut c = fleet(210., 60., 3);
    for t in &mut c.trains {
        t.initial_drive_temperature_c = Some(80.);
    }
    let r = evaluate(&c).unwrap();
    let d = r
        .departures
        .iter()
        .find(|d| d.train_id.as_deref() == Some("A1") && d.state == "arrived")
        .unwrap();
    let m = c.departures[0].journey.thermal.as_ref().unwrap();
    let expected = m.ambient_c
        + (80. - m.ambient_c) * (-m.heat_rejection_w_k / m.capacity_j_k * d.departure_time_s).exp();
    near(d.initial_drive_temperature_c.unwrap(), expected, 1e-9);
}
#[test]
fn source_domain_and_missing_temperature_block_before_route_entry() {
    let mut c = fleet(210., 60., 3);
    for t in &mut c.trains {
        t.initial_drive_temperature_c = None;
    }
    let r = evaluate(&c).unwrap();
    assert_eq!(r.dispatched_departures, 0);
    near(r.ledger.grid_traction_energy_j, 0., 1e-8);
    assert!(r.route_states.iter().all(|q| !q.pending_rescue));
    let mut c = fleet(210., 60., 3);
    for d in &mut c.departures {
        d.journey.mass_kg = 1e6;
    }
    let r = evaluate(&c).unwrap();
    assert_eq!(r.dispatched_departures, 0);
    assert!(
        r.departures
            .iter()
            .all(|d| !d.source_domain.as_ref().unwrap().bounds_valid)
    );
}
#[test]
fn failed_train_keeps_route_occupied_pending_rescue() {
    let mut c = fleet(210., 60., 3);
    c.departures[0].journey.fault.power_loss_at_s = Some(10.);
    let r = evaluate(&c).unwrap();
    assert!(r.route_states[0].pending_rescue);
    assert!(r.train_states.iter().any(|t| t.pending_rescue));
    assert!(
        r.departures
            .iter()
            .filter(|d| d.departure_station_id == "A" && d.departure_time_s > 0.)
            .all(|d| d.state == "departure-held")
    );
}
#[test]
fn reset_fault_degrades_recovery_without_using_unavailable_bank() {
    let mut c = fleet(210., 60., 3);
    for d in &mut c.departures {
        d.reset_failed = true;
    }
    let r = evaluate(&c).unwrap();
    assert!(r.schedule_numerical_complete);
    assert!(r.station_states.iter().any(|s| !s.ready));
    assert!(r.ledger.unperformed_reset_grid_energy_j > 0.);
}
#[test]
fn deterministic_event_order_does_not_depend_on_unrelated_request_order() {
    let a = fleet(210., 60., 3);
    let mut b = a.clone();
    b.departures.reverse();
    let x = evaluate(&a).unwrap();
    let y = evaluate(&b).unwrap();
    assert_eq!(x.normal_arrivals, y.normal_arrivals);
    near(
        x.ledger.grid_traction_energy_j,
        y.ledger.grid_traction_energy_j,
        1e-7,
    );
    near(x.ledger.final_store_j, y.ledger.final_store_j, 1e-7);
    let by_id = |r: FleetResult| {
        r.departures
            .into_iter()
            .map(|d| (d.id, (d.train_id, d.state)))
            .collect::<std::collections::BTreeMap<_, _>>()
    };
    assert_eq!(by_id(x), by_id(y));
}
