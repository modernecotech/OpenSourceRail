//! Eight bounded research network calls; geometry/feed/terminal proof absent.
mod common;
use osr_journey::fleet::*;
use serde_json::Value;
use std::sync::atomic::{AtomicUsize, Ordering};
static CALLS: AtomicUsize = AtomicUsize::new(0);
fn run(c: &FleetCase) -> Result<FleetResult, String> {
    let n = CALLS.fetch_add(1, Ordering::SeqCst) + 1;
    assert!(n <= 8, "Network case budget exceeded before evaluation");
    eprintln!("NETWORK_CASE_LEDGER {}", serde_json::to_string(c).unwrap());
    let result = evaluate(c);
    match &result {
        Ok(r) => eprintln!(
            "NETWORK_RESULT_LEDGER {}",
            serde_json::to_string(r).unwrap()
        ),
        Err(e) => eprintln!("NETWORK_ERROR_LEDGER {}", serde_json::to_string(e).unwrap()),
    }
    result
}
fn train(id: &str, station: &str) -> Train {
    Train {
        id: id.into(),
        initial_station_id: station.into(),
        initial_position_m: 0.,
        ready_at_s: 0.,
        role: TrainRole::Active,
        initial_drive_temperature_c: Some(50.),
    }
}
fn departure(id: &str, route: &str, time: f64, requested: &str) -> Departure {
    let (from, to, distance) = match route {
        "AB" => ("A", "B", 1500.),
        "BA" => ("B", "A", 1500.),
        "BC" => ("B", "C", 900.),
        "CB" => ("C", "B", 900.),
        _ => unreachable!(),
    };
    let mut journey = common::fixture().legs.remove(0).journey;
    journey.id = id.into();
    journey.distance_m = distance;
    journey.brake_start_m = distance;
    journey.control.as_mut().unwrap().end_of_authority_m = distance;
    journey.drive.as_mut().unwrap().windows_m = vec![[0., distance]];
    Departure {
        id: id.into(),
        journey,
        departure_station_id: from.into(),
        arrival_station_id: to.into(),
        departure_time_s: time,
        departure_authorized: true,
        capture_failed: false,
        release_failed: false,
        reset_failed: false,
        requested_train_id: Some(requested.into()),
        route_id: Some(route.into()),
        frame_binding: None,
    }
}
fn fixture(id: &str, departures: Vec<Departure>) -> FleetCase {
    let base = common::fixture();
    let mut stations = vec![
        base.stations[0].clone(),
        base.stations[1].clone(),
        base.stations[0].clone(),
    ];
    for (s, name) in stations.iter_mut().zip(["A", "B", "C"]) {
        s.id = name.into();
        s.initial_energy_j = 0.;
        s.store.capacity_j = 0.;
        s.store.leakage_per_s = 0.;
        s.release.max_force_n = 0.;
        s.release.max_power_w = 0.;
        s.release.start_m = 0.;
        s.release.end_m = 1.;
        s.capture_stages.clear();
        s.reset.duration_s = 0.;
        s.reset.grid_energy_j = 0.;
        s.reset.grid_power_w = 0.;
    }
    // Nonstation order deliberately differs from route-state order.
    let routes = [
        ("CB", "C", "B", 900.),
        ("AB", "A", "B", 1500.),
        ("BC", "B", "C", 900.),
        ("BA", "B", "A", 1500.),
    ]
    .into_iter()
    .enumerate()
    .map(|(i, (id, a, b, distance))| DirectedRoute {
        id: id.into(),
        from_station_id: a.into(),
        to_station_id: b.into(),
        distance_m: distance,
        geometry_record_id: format!("{i:064x}"),
        entry_frame: None,
    })
    .collect();
    let candidate = base.candidate_id;
    FleetCase {
        id: id.into(),
        candidate_id: candidate.clone(),
        stations,
        release_control: base.release_control.unwrap(),
        trains: vec![
            train("A0", "A"),
            train("A1", "A"),
            train("B0", "B"),
            train("C0", "C"),
        ],
        departures,
        turnaround_s: 45.,
        clearance_s: 3.,
        network: Some(ResearchNetwork {
            schema: "osr-no-storage-adjacent-network/1".into(),
            position_reference: "signed-station-order-offset/1".into(),
            route_resource_model: "dedicated-directed-double-track-blocks/1".into(),
            geometry_binding: GeometryBinding {
                project_candidate_id: candidate,
                alignment_candidate_id: "b".repeat(64),
                alignment_evaluation_id: "c".repeat(64),
                route_manifest_id: "d".repeat(64),
            },
            station_order: vec!["A".into(), "B".into(), "C".into()],
            routes,
        }),
    }
}
fn checks(r: &FleetResult) {
    assert!(
        !r.physical_accepted
            && !r.engineering_accepted
            && !r.operating_release
            && !r.admitted_operating_map
    );
    assert!(!r.route_separation_qualified && !r.terminal_dynamics_supported);
    let n = r.network.as_ref().unwrap();
    assert!(n.storage_disabled && !n.geometry_verified && !n.shared_feed_capacity_verified);
    assert!(!n.signed_through_entry_supported);
    assert_eq!(r.ledger.initial_store_j, 0.);
    assert_eq!(r.ledger.final_store_j, 0.);
    assert_eq!(r.ledger.capture_work_j, 0.);
    assert_eq!(r.ledger.released_from_store_j, 0.);
    assert!(r.ledger.train_and_storage_balance_residual_j.abs() < 1e-3);
    assert!(r.events.windows(2).all(|w| w[0].time_s <= w[1].time_s));
    let ids: std::collections::HashSet<_> = r.train_states.iter().map(|t| &t.id).collect();
    assert_eq!(ids.len(), r.train_states.len());
}
#[test]
fn absent_network_keeps_two_recorded_legacy_controls_byte_exact() {
    let golden: Value =
        serde_json::from_str(include_str!("data/fleet_legacy_control.json")).unwrap();
    let q: Request = serde_json::from_str(golden["request_raw_json"].as_str().unwrap()).unwrap();
    assert!(
        q.cases
            .iter()
            .all(|c| c.network.is_none() && c.departures.iter().all(|d| d.route_id.is_none()))
    );
    let actual = serde_json::to_string(&execute(q).unwrap()).unwrap();
    assert_eq!(
        actual,
        golden["expected_raw_json"].as_str().unwrap().trim_end()
    );
    eprintln!("LEGACY_REPLAY_CASES 2");
}
#[test]
fn eight_frozen_network_cases_retain_causality_and_holds() {
    let c = fixture(
        "N1-unequal-and-stable-order",
        vec![
            departure("z-cb", "CB", 0., "C0"),
            departure("a-ab", "AB", 0., "A0"),
        ],
    );
    let r = run(&c).unwrap();
    checks(&r);
    assert_eq!(r.normal_arrivals, 2);
    let dispatched: Vec<_> = r
        .events
        .iter()
        .filter(|e| e.kind == "departure-dispatched")
        .map(|e| e.departure_id.as_deref().unwrap())
        .collect();
    assert_eq!(dispatched, ["a-ab", "z-cb"]);
    assert_ne!(
        r.departures[0].journey.as_ref().unwrap().final_position_m,
        r.departures[1].journey.as_ref().unwrap().final_position_m
    );

    let c = fixture(
        "N2-exact-reverse-reuse",
        vec![
            departure("go", "AB", 0., "A0"),
            departure("back", "BA", 500., "A0"),
        ],
    );
    let r = run(&c).unwrap();
    checks(&r);
    assert_eq!(r.normal_arrivals, 2);
    let first = r.departures[0].journey.as_ref().unwrap();
    assert_eq!(
        r.departures[1].initial_position_m,
        Some(1500. - first.final_position_m)
    );
    let t = r.train_states.iter().find(|t| t.id == "A0").unwrap();
    assert_eq!(t.station_id.as_deref(), Some("A"));
    assert!(
        t.network_position
            .as_ref()
            .unwrap()
            .station_offset_m
            .unwrap()
            >= 0.
    );
    assert!(t.ready_at_s > r.departures[1].arrival_time_s.unwrap());

    let c = fixture(
        "N3-no-duplicated-or-premature-train",
        vec![
            departure("a-go", "AB", 0., "A0"),
            departure("b-duplicate", "AB", 0., "A0"),
            departure("c-premature", "BA", 1., "A0"),
        ],
    );
    let r = run(&c).unwrap();
    checks(&r);
    assert_eq!(r.dispatched_departures, 1);
    assert_eq!(r.blocked_departures, 2);
    assert_eq!(r.train_states.iter().filter(|t| t.id == "A0").count(), 1);

    let mut c = fixture(
        "N4-directed-clearance-blocks",
        vec![
            departure("a-ab", "AB", 0., "A0"),
            departure("b-ba", "BA", 0., "B0"),
            departure("c-cb", "CB", 0., "C0"),
            departure("d-occupied", "AB", 500., "A1"),
        ],
    );
    c.clearance_s = 600.;
    let r = run(&c).unwrap();
    checks(&r);
    assert_eq!(r.normal_arrivals, 3);
    assert_eq!(r.departures[3].state, "departure-held");
    assert!(
        r.departures[3]
            .hold_reason
            .as_ref()
            .unwrap()
            .contains("clearance")
    );
    assert!(
        r.route_states
            .iter()
            .find(|s| s.route_id.as_deref() == Some("AB"))
            .unwrap()
            .occupied_until_s
            > 500.
    );

    let mut c = fixture(
        "N5-route-rescue-isolation",
        vec![
            departure("a-failed", "AB", 0., "A0"),
            departure("b-independent", "CB", 0., "C0"),
            departure("c-rescue-held", "AB", 500., "A1"),
        ],
    );
    c.departures[0].journey.fault.power_loss_at_s = Some(10.);
    let r = run(&c).unwrap();
    checks(&r);
    assert_eq!(r.normal_arrivals, 1);
    let route = r
        .route_states
        .iter()
        .find(|s| s.route_id.as_deref() == Some("AB"))
        .unwrap();
    assert!(route.pending_rescue);
    let t = r.train_states.iter().find(|t| t.id == "A0").unwrap();
    assert!(t.pending_rescue && t.station_id.is_none());
    assert_eq!(
        t.network_position.as_ref().unwrap().route_position_m,
        Some(r.departures[0].journey.as_ref().unwrap().final_position_m)
    );
    assert!(
        r.departures[2]
            .hold_reason
            .as_ref()
            .unwrap()
            .contains("rescue")
    );

    let c = fixture(
        "N6-negative-through-offset-held",
        vec![
            departure("go", "AB", 0., "A0"),
            departure("through", "BC", 500., "A0"),
        ],
    );
    let r = run(&c).unwrap();
    checks(&r);
    assert_eq!(r.normal_arrivals, 1);
    assert_eq!(r.departures[1].state, "departure-held");
    let offset = r.departures[0].journey.as_ref().unwrap().final_position_m - 1500.;
    assert!(offset < 0.);
    assert_eq!(r.departures[1].initial_position_m, Some(offset));
    let t = r.train_states.iter().find(|t| t.id == "A0").unwrap();
    assert_eq!(t.station_id.as_deref(), Some("B"));
    assert_eq!(
        t.network_position.as_ref().unwrap().station_offset_m,
        Some(offset)
    );
    assert!(
        r.departures[1]
            .hold_reason
            .as_ref()
            .unwrap()
            .contains("coordinate-rebase")
    );

    let mut c = fixture(
        "N7-active-storage-rejected",
        vec![departure("go", "AB", 0., "A0")],
    );
    c.stations[1].store.capacity_j = 1.;
    assert!(run(&c).unwrap_err().contains("active storage"));

    let mut c = fixture(
        "N8-exact-route-distance-rejected",
        vec![departure("go", "AB", 0., "A0")],
    );
    c.network
        .as_mut()
        .unwrap()
        .routes
        .iter_mut()
        .find(|r| r.id == "AB")
        .unwrap()
        .distance_m = 1499.;
    assert!(run(&c).unwrap_err().contains("unchanged journey distance"));
    assert_eq!(CALLS.load(Ordering::SeqCst), 8);
}
