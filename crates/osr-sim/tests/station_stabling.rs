//! Operating policy tests. Station berths are still outside the MA graph.
use osr_sim::{
    scenario_file::load_scenario_from_str,
    sim::{self, EventKind, RuntimeConfig},
};

fn scenario() -> String {
    let mut text = String::from(
        r#"
[scenario]
name = "distributed station overnight"
start_time = "01:59"
[climate]
ambient_c = 25.0
peak_sun_hours = 6.0
[consist]
car_count = 3
length_m = 49.5
mass_kg = 78750
max_speed_kmh = 80.0
battery_capacity_kwh = 540
service_accel_mps2 = 1.0
[[lines]]
id = "l1"
name = "L1"
stations = [
  { id = "a", distance_from_prev_m = 0 },
  { id = "b", distance_from_prev_m = 2000 },
  { id = "c", distance_from_prev_m = 2000 },
]
[[fleets]]
line = "l1"
trainset_count = 4
station_stabling = true
dispatch_points = [
  { station = "a", heading = "forward" },
  { station = "b", heading = "forward" },
  { station = "b", heading = "reverse" },
  { station = "c", heading = "reverse" },
]
service_start = "05:30"
service_end = "02:00"
schedule = [{ from = "05:30", to = "02:00", headway_min = 6 }]
"#,
    );
    for (id, terminal) in [("a", true), ("b", false), ("c", true)] {
        text.push_str(&format!(
            r#"
[[stations]]
id = "{id}"
name = "{id}"
charging_power_kw = 500
dwell_seconds = 30
is_terminal = {terminal}
is_depot = false
[[sites]]
station = "{id}"
pv_nameplate_kw = 0.0
storage_capacity_kwh = 500.0
storage_max_charge_kw = 500.0
storage_max_discharge_kw = 500.0
storage_initial_soc = 0.5
grid_import_kw = 500.0
grid_export_kw = 500.0
"#
        ));
    }
    text
}

fn runtime(duration_s: u32) -> RuntimeConfig {
    RuntimeConfig {
        duration_s,
        time_step_s: 1,
        status_every_s: 0,
        csv_out: None,
        csv_every_s: 60,
        ma_check_every_s: 0,
    }
}

#[test]
fn stations_hold_and_charge_overnight_then_resume_together() {
    let config = load_scenario_from_str(&scenario()).unwrap();
    assert!(config
        .network
        .stations
        .values()
        .all(|station| !station.is_depot));
    // 01:59 -> 05:30; trains finish their first section after closing at 02:00.
    let morning = 3 * 3600 + 31 * 60;
    let result = sim::run(&config, &runtime(morning + 1));
    assert!(
        result.invariant_violations.is_empty(),
        "{:?}",
        result.invariant_violations
    );
    assert_eq!(
        result
            .events
            .iter()
            .filter(|event| matches!(event.kind, EventKind::Dispatched))
            .count(),
        4
    );
    let departures: Vec<_> = result
        .events
        .iter()
        .filter(|event| matches!(event.kind, EventKind::DepartStation))
        .collect();
    assert_eq!(departures.len(), 4);
    assert!(departures.iter().all(|event| event.sim_time_s == morning));
    assert!(
        result.total_energy_charged_kwh > 0.0,
        "non-depot overnight top-up must deliver energy"
    );
    assert!(result.out_of_service_held_s > 4 * 3 * 3600);
    assert!(result
        .per_train_final_soc
        .iter()
        .all(|(_, _, soc, _)| *soc <= 0.95001));
    let stations: std::collections::HashSet<_> =
        departures.iter().map(|event| event.station).collect();
    assert_eq!(
        stations.len(),
        3,
        "morning departures must include the intermediate station"
    );
}

#[test]
fn pre_service_trains_do_not_move_or_charge_above_the_holding_target() {
    let config = load_scenario_from_str(&scenario().replace("01:59", "03:00")).unwrap();
    let result = sim::run(&config, &runtime(60));
    assert_eq!(result.total_train_km, 0.0);
    assert_eq!(result.total_energy_charged_kwh, 0.0);
    assert_eq!(result.out_of_service_held_s, 4 * 60);
}

#[test]
fn station_stabling_rejects_unpowered_duplicate_or_outward_points() {
    for invalid in [
        scenario().replace("charging_power_kw = 500", "charging_power_kw = 0"),
        scenario().replace("grid_import_kw = 500.0", "grid_import_kw = 0.0"),
        scenario().replace(
            "station = \"c\", heading = \"reverse\"",
            "station = \"a\", heading = \"forward\"",
        ),
        scenario().replace(
            "station = \"a\", heading = \"forward\"",
            "station = \"a\", heading = \"reverse\"",
        ),
    ] {
        assert!(load_scenario_from_str(&invalid)
            .unwrap_err()
            .to_string()
            .contains("station stabling"));
    }
}

#[test]
fn failed_station_pad_does_not_deliver_overnight_energy() {
    let text = scenario()
        + r#"
[[faults]]
name = "B pad unavailable"
kind = "charging_pad_outage"
station = "b"
from = "02:00"
to = "05:30"
"#;
    let config = load_scenario_from_str(&text).unwrap();
    let result = sim::run(&config, &runtime(720));
    let failed = result
        .energy_sites
        .iter()
        .find(|site| site.station_name == "b")
        .unwrap();
    assert_eq!(failed.delivered_to_trains_kwh, 0.0);
    assert!(result
        .energy_sites
        .iter()
        .filter(|site| site.station_name != "b")
        .all(|site| site.delivered_to_trains_kwh > 0.0));
    assert!(result.invariant_violations.is_empty());
}

#[test]
fn declared_reserves_remain_parked_while_revenue_trains_dispatch() {
    let text = scenario().replace("01:59", "05:30").replace(
        "trainset_count = 4",
        "trainset_count = 4\nspare_count = 1\ncold_reserve_count = 1",
    );
    let config = load_scenario_from_str(&text).unwrap();
    let directory = tempfile::tempdir().unwrap();
    let csv = directory.path().join("roles.csv");
    let mut run = runtime(60);
    run.csv_out = Some(csv.clone());
    let result = sim::run(&config, &run);
    let dispatched: Vec<_> = result
        .events
        .iter()
        .filter(|event| matches!(event.kind, EventKind::Dispatched))
        .map(|event| event.train.0)
        .collect();
    assert_eq!(dispatched, vec![1, 2]);
    assert_eq!(result.reserve_held_s, 120);
    let data = std::fs::read_to_string(csv).unwrap();
    let mut lines = data.lines();
    let header: Vec<_> = lines.next().unwrap().split(',').collect();
    let role = header
        .iter()
        .position(|value| *value == "service_role")
        .unwrap();
    let heading = header
        .iter()
        .position(|value| *value == "departure_heading")
        .unwrap();
    let station = header
        .iter()
        .position(|value| *value == "station_id")
        .unwrap();
    let rows: Vec<_> = lines
        .map(|line| line.split(',').collect::<Vec<_>>())
        .collect();
    assert_eq!(rows[2][role], "spare");
    assert_eq!(rows[3][role], "cold_reserve");
    assert_eq!(rows[2][heading], "reverse");
    assert_eq!(rows[3][heading], "reverse");
    assert_eq!(rows[2][station], "2");
    assert_eq!(rows[3][station], "3");
}

#[test]
fn invalid_and_overflowing_reserve_counts_are_rejected() {
    for roles in [
        "spare_count = 3\ncold_reserve_count = 2",
        "spare_count = 4294967295\ncold_reserve_count = 1",
    ] {
        let text = scenario().replace(
            "trainset_count = 4",
            &format!("trainset_count = 4\n{roles}"),
        );
        assert!(load_scenario_from_str(&text)
            .unwrap_err()
            .to_string()
            .contains("reserve counts"));
    }
}

fn charging_gap_scenario(distance_m: u32, start_at_c: bool) -> String {
    let mut text = scenario()
        .replace("01:59", "05:30")
        .replace("trainset_count = 4", "trainset_count = 1")
        .replace(
            "distance_from_prev_m = 2000",
            &format!("distance_from_prev_m = {distance_m}"),
        )
        .replace("  { station = \"b\", heading = \"forward\" },\n", "")
        .replace("  { station = \"b\", heading = \"reverse\" },\n", "")
        .replace(
            "name = \"b\"\ncharging_power_kw = 500",
            "name = \"b\"\ncharging_power_kw = 0",
        );
    // Keep both destinations configured; reverse their order for the reverse test.
    if start_at_c {
        text = text.replace(
            "  { station = \"a\", heading = \"forward\" },\n  { station = \"c\", heading = \"reverse\" },",
            "  { station = \"c\", heading = \"reverse\" },\n  { station = \"a\", heading = \"forward\" },",
        );
    }
    text
}

#[test]
fn charging_gap_holds_both_directions_before_an_unpowered_station() {
    // Each 30 km section fits above the reserve; the 60 km charging gap does not.
    for reverse in [false, true] {
        let text = charging_gap_scenario(30000, reverse);
        let config = load_scenario_from_str(&text).unwrap();
        let result = sim::run(&config, &runtime(60));
        assert_eq!(result.total_train_km, 0.0);
        assert!(
            result.events.is_empty(),
            "a held train must not consume a dispatch slot"
        );
        let legacy = load_scenario_from_str(
            &text.replace("station_stabling = true", "station_stabling = false"),
        )
        .unwrap();
        assert!(sim::run(&legacy, &runtime(60)).total_train_km > 0.0);
    }
}

#[test]
fn sufficient_energy_crosses_the_gap_and_preserves_the_reserve() {
    let config = load_scenario_from_str(&charging_gap_scenario(15000, false)).unwrap();
    let result = sim::run(&config, &runtime(11000));
    assert!(result.total_train_km >= 30.0);
    assert!(result.per_train_final_soc[0].3 >= 0.2);
    assert!(result.total_energy_charged_kwh > 0.0);
    assert!(result.invariant_violations.is_empty());
}

#[test]
fn unavailable_destination_requires_energy_for_the_return_to_a_working_charger() {
    for kind in ["charging_pad_outage", "grid_outage"] {
        let text = charging_gap_scenario(15000, false)
            + &format!(
                r#"
[[faults]]
name = "C charger unavailable"
kind = "{kind}"
station = "c"
from = "05:30"
to = "06:30"
"#
            );
        let config = load_scenario_from_str(&text).unwrap();
        assert_eq!(sim::run(&config, &runtime(60)).total_train_km, 0.0);
    }
}

#[test]
fn ring_with_all_chargers_unavailable_holds_without_unbounded_route_search() {
    let text = charging_gap_scenario(2000, false)
        .replace(
            "name = \"L1\"",
            "name = \"L1\"\nis_ring = true\nring_wrap_length_m = 2000",
        )
        .replace("is_terminal = true", "is_terminal = false")
        + r#"
[[faults]]
name = "A pad unavailable"
kind = "charging_pad_outage"
station = "a"
from = "05:30"
to = "06:30"
[[faults]]
name = "C pad unavailable"
kind = "charging_pad_outage"
station = "c"
from = "05:30"
to = "06:30"
"#;
    let config = load_scenario_from_str(&text).unwrap();
    assert_eq!(sim::run(&config, &runtime(60)).total_train_km, 0.0);
}
