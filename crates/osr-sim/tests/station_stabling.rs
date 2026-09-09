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
