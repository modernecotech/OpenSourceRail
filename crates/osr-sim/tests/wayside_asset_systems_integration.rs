//! End-to-end applicability and movement-gate evidence for explicit assets.

use osr_sim::scenario_file::load_scenario_from_str;
use osr_sim::sim::{run, EventKind, RuntimeConfig};
use osr_sim::wayside_asset_systems::{LevelCrossingAssetConfig, SwitchAssetConfig};

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
fn explicit_switch_and_crossing_execute_and_gate_entry() {
    let mut scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    let line = &scenario.network.lines[0];
    let station = line.stations[0];
    scenario.switches.push(SwitchAssetConfig {
        id: "test-turnout".into(),
        station,
    });
    scenario.level_crossings.push(LevelCrossingAssetConfig {
        id: "test-crossing".into(),
        sections: vec![line.forward_sections[0], line.reverse_sections[0]],
    });

    let first = run(&scenario, &runtime(90));
    let second = run(&scenario, &runtime(90));
    assert_eq!(first.wayside_asset_systems, second.wayside_asset_systems);
    let summary = &first.wayside_asset_systems;
    assert_eq!(summary.switch_count, 1);
    assert_eq!(summary.switch_controller_ticks, 90);
    assert!(summary.switch_observations > 0);
    assert_eq!(summary.switch_fault_ticks, 0);
    assert_eq!(summary.crossing_count, 1);
    assert_eq!(summary.crossing_controller_ticks, 90);
    assert!(summary.crossing_warning_ticks >= 20);
    assert!(summary.crossing_closed_ticks > 0);
    assert_eq!(summary.crossing_fault_ticks, 0);

    let first_dispatch = first
        .events
        .iter()
        .find(|event| matches!(event.kind, EventKind::Dispatched))
        .expect("crossing should eventually permit dispatch");
    assert!(first_dispatch.sim_time_s >= 20);
}

#[test]
fn absent_level_crossings_remain_not_applicable() {
    let scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    let summary = run(&scenario, &runtime(30)).wayside_asset_systems;
    assert_eq!(summary.switch_count, 0);
    assert_eq!(summary.switch_controller_ticks, 0);
    assert_eq!(summary.crossing_count, 0);
    assert_eq!(summary.crossing_controller_ticks, 0);
}
