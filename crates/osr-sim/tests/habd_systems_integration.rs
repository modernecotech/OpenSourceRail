//! End-to-end physical HABD passage, stop-order, and inspection-reset evidence.

use osr_core::TrainId;
use osr_sim::fault::{Fault, FaultKind, TrainFaultScope};
use osr_sim::habd_systems::{HabdDetectorConfig, HabdResetAction, HabdTrackPosition};
use osr_sim::scenario_file::load_scenario_from_str;
use osr_sim::sim::{run, EventKind, RuntimeConfig, SimResult};

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

fn scenario_with_detector() -> osr_sim::sim::ScenarioConfig {
    let mut scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    let forward = scenario.network.lines[0].forward_sections[0];
    let reverse = scenario.network.lines[0].reverse_sections[0];
    let length = scenario.network.section(forward).length_mm;
    scenario.habd_detectors.push(HabdDetectorConfig {
        id: "shuttle-west-approach".into(),
        track_positions: vec![
            HabdTrackPosition {
                section: forward,
                offset_mm: 500_000,
            },
            HabdTrackPosition {
                section: reverse,
                offset_mm: length - 500_000,
            },
        ],
    });
    scenario
}

fn first_arrival(result: &SimResult) -> u32 {
    result
        .events
        .iter()
        .find(|event| matches!(event.kind, EventKind::ArriveStation { .. }))
        .map(|event| event.sim_time_s)
        .expect("train should arrive during the run")
}

#[test]
fn nominal_physical_passage_runs_real_detector() {
    let scenario = scenario_with_detector();
    let first = run(&scenario, &runtime(90)).habd_systems;
    let second = run(&scenario, &runtime(90)).habd_systems;

    assert_eq!(first, second);
    assert_eq!(first.detector_count, 1);
    assert_eq!(first.track_position_count, 2);
    assert_eq!(first.passages_evaluated, 1);
    assert_eq!(first.nominal_passages, 1);
    assert_eq!(first.stop_orders_issued, 0);
    assert!(first.active_stop_orders.is_empty());
}

#[test]
fn trip_latches_until_qualified_clear_reset_then_motion_resumes() {
    let nominal_scenario = scenario_with_detector();
    let nominal = run(&nominal_scenario, &runtime(220));

    let mut scenario = nominal_scenario;
    scenario.faults.push(Fault {
        name: "wayside-bearing-overheat".into(),
        from_sim_s: 0,
        to_sim_s: 60,
        kind: FaultKind::HabdOverheat {
            scope: TrainFaultScope::Train(TrainId::new(1)),
        },
    });
    scenario.habd_resets.extend([
        HabdResetAction {
            at_sim_s: 50,
            train: TrainId::new(1),
            authorised_by: "rolling-stock-technician".into(),
            inspection_reference: "inspection-early".into(),
        },
        HabdResetAction {
            at_sim_s: 70,
            train: TrainId::new(1),
            authorised_by: "rolling-stock-technician".into(),
            inspection_reference: "inspection-clear".into(),
        },
    ]);

    let first = run(&scenario, &runtime(220));
    let second = run(&scenario, &runtime(220));
    let habd = &first.habd_systems;

    assert_eq!(habd, &second.habd_systems);
    assert_eq!(habd.trip_passages, 1);
    assert_eq!(habd.stop_orders_issued, 1);
    assert_eq!(habd.reset_actions_rejected, 1);
    assert_eq!(habd.reset_actions_accepted, 1);
    assert_eq!(habd.reset_records.len(), 2);
    assert_eq!(habd.reset_records[0].decision, "rejected-overheat-active");
    assert_eq!(habd.reset_records[1].decision, "released-after-inspection");
    assert_eq!(
        habd.reset_records[1].authorised_by,
        "rolling-stock-technician"
    );
    assert!(habd.stop_hold_ticks > 0);
    assert!(habd.active_stop_orders.is_empty());
    assert_eq!(first.embedded.tcms_trip_ticks, 0);
    assert_eq!(
        first_arrival(&first),
        first_arrival(&nominal) + habd.stop_hold_ticks as u32
    );
}

#[test]
fn trip_without_reset_remains_fail_safe_and_latched() {
    let mut scenario = scenario_with_detector();
    scenario.faults.push(Fault {
        name: "unreleased-wayside-bearing-overheat".into(),
        from_sim_s: 0,
        to_sim_s: 60,
        kind: FaultKind::HabdOverheat {
            scope: TrainFaultScope::All,
        },
    });

    let result = run(&scenario, &runtime(120));
    assert_eq!(result.habd_systems.stop_orders_issued, 1);
    assert_eq!(result.habd_systems.active_stop_orders.len(), 1);
    assert!(result.habd_systems.stop_hold_ticks > 0);
    assert!(!result
        .events
        .iter()
        .any(|event| matches!(event.kind, EventKind::ArriveStation { .. })));
}
