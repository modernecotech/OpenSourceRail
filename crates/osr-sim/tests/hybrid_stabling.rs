use osr_sim::{
    scenario_file::load_scenario_from_str,
    sim::{self, EventKind, RuntimeConfig},
};

const SCENARIO: &str = include_str!("../../../lib/examples/hybrid-stabling.toml");

#[test]
fn invalid_inventory_capacity_roles_and_disconnected_depot_are_rejected() {
    for invalid in [
        SCENARIO.replace("trainset_count = 8", "trainset_count = 9"),
        SCENARIO.replace("depot_stabling_positions = 2", "depot_stabling_positions = 1"),
        SCENARIO.replace("location_type = \"depot\"", "location_type = \"station\""),
        SCENARIO.replace("spare_count = 1", "spare_count = 0"),
        SCENARIO.replace("station_stabling = true", "station_stabling = false"),
        SCENARIO.replace("location_type = \"depot\"", "location_type = \"workshop\""),
        SCENARIO.replace("{ station = \"a\", heading = \"forward\", location_type = \"depot\"",
            "{ station = \"disconnected\", heading = \"forward\", location_type = \"depot\"")
            + "\n[[stations]]\nid = \"disconnected\"\nname = \"disconnected\"\nis_depot = true\ndepot_stabling_positions = 2\ndwell_seconds = 30\n",
    ] {
        assert!(load_scenario_from_str(&invalid).is_err(), "accepted invalid overnight plan");
    }
}

#[test]
fn two_continuous_days_return_to_station_and_depot_homes_and_restart() {
    let config = load_scenario_from_str(SCENARIO).unwrap();
    let directory = tempfile::tempdir().unwrap();
    let csv = directory.path().join("hybrid.csv");
    let runtime = RuntimeConfig {
        duration_s: 2 * 86400 + 901,
        time_step_s: 5,
        status_every_s: 0,
        csv_out: Some(csv.clone()),
        csv_every_s: 60,
        ma_check_every_s: 0,
    };
    let result = sim::run(&config, &runtime);
    assert!(
        result.invariant_violations.is_empty(),
        "{:?}",
        result.invariant_violations
    );
    let text = std::fs::read_to_string(csv).unwrap();
    let mut lines = text.lines();
    let header: Vec<_> = lines.next().unwrap().split(',').collect();
    let column = |name: &str| header.iter().position(|h| *h == name).unwrap();
    let rows: Vec<Vec<_>> = lines.map(|r| r.split(',').collect()).collect();
    for night in [86400 - 60, 2 * 86400 - 60] {
        let snapshot: Vec<_> = rows.iter().filter(|r| r[0] == night.to_string()).collect();
        assert_eq!(snapshot.len(), 8);
        for station in ["\"a\"", "\"b\"", "\"c\""] {
            assert_eq!(
                snapshot
                    .iter()
                    .filter(|r| r[column("station")] == station
                        && r[column("stabling_location")] == "station")
                    .count(),
                2
            );
        }
        let depot: Vec<_> = snapshot
            .iter()
            .filter(|r| r[column("stabling_location")] == "depot")
            .collect();
        assert_eq!(depot.len(), 2);
        assert!(depot.iter().all(|r| r[column("station")] == "\"a\""));
        assert!(snapshot.iter().all(|r| r[column("phase")] == "awaiting"));
        assert!(snapshot
            .iter()
            .all(|r| r[column("soc")].parse::<f32>().unwrap() >= 0.20));
    }
    assert!(result
        .events
        .iter()
        .any(|e| matches!(e.kind, EventKind::ReturnToStabling)));
    assert!(result.events.iter().all(|e| {
        let tod = (e.sim_time_s + 5 * 3600 + 30 * 60) % 86400;
        if matches!(e.kind, EventKind::DepartStation | EventKind::Dispatched) {
            (19800..20700).contains(&tod)
        } else if matches!(e.kind, EventKind::ReturnToStabling) {
            !(19800..20700).contains(&tod)
        } else {
            true
        }
    }));
    // Train 7 is the depot revenue set. It must really leave and return;
    // train 8 is the spare and remains in depot storage throughout.
    for day in [0, 86400, 2 * 86400] {
        for station_launch_train in [1, 3, 4, 5] {
            assert!(result
                .events
                .iter()
                .any(|e| e.train.0 == station_launch_train
                    && matches!(e.kind, EventKind::Dispatched)
                    && (day..=day + 60).contains(&e.sim_time_s)));
        }
        assert!(result.events.iter().any(|e| e.train.0 == 7
            && matches!(e.kind, EventKind::Dispatched)
            && (day..day + 900).contains(&e.sim_time_s)));
    }
    assert!(rows
        .iter()
        .filter(|r| r[column("train_id")] == "T8")
        .all(|r| r[column("stabling_location")] == "depot" && r[column("odometer_km")] == "0.000"));
    assert!(rows
        .iter()
        .any(|r| r[column("train_id")] == "T7"
            && r[column("odometer_km")].parse::<f64>().unwrap() > 0.0));
}

#[test]
fn identical_hybrid_inputs_produce_identical_traces_and_events() {
    let source = SCENARIO.to_owned()
        + r#"
[[faults]]
name = "depot pad outage during return"
kind = "charging_pad_outage"
station = "a"
from = "05:45"
to = "06:00"
"#;
    let config = load_scenario_from_str(&source).unwrap();
    let directory = tempfile::tempdir().unwrap();
    let run = |name: &str| {
        let csv = directory.path().join(name);
        let runtime = RuntimeConfig {
            duration_s: 3600,
            time_step_s: 5,
            status_every_s: 0,
            csv_out: Some(csv.clone()),
            csv_every_s: 5,
            ma_check_every_s: 0,
        };
        let result = sim::run(&config, &runtime);
        assert!(result.invariant_violations.is_empty());
        assert_eq!(result.faults_fired.len(), 1);
        assert!(result
            .events
            .iter()
            .any(|e| e.train.0 == 7 && matches!(e.kind, EventKind::Dispatched)));
        (
            std::fs::read(csv).unwrap(),
            serde_json::to_value(&result.events).unwrap(),
            serde_json::to_value(&result.faults_fired).unwrap(),
            result.total_train_km,
            result.total_energy_consumed_kwh,
            result.total_energy_charged_kwh,
        )
    };
    assert_eq!(run("first.csv"), run("second.csv"));
}
