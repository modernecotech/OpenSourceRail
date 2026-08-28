//! End-to-end evidence for the legacy application-tier embedded crates.

use osr_core::TrainId;
use osr_sim::fault::{Fault, FaultKind, TrainFaultScope};
use osr_sim::scenario_file::canonical_samawah_scenario;
use osr_sim::sim::{run, RuntimeConfig};

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
fn nominal_embedded_stack_runs_every_tick_and_is_deterministic() {
    let scenario = canonical_samawah_scenario();
    let expected_trains: u32 = scenario
        .fleets
        .iter()
        .map(|fleet| fleet.trainset_count)
        .sum();

    let first = run(&scenario, &runtime(120)).embedded;
    let second = run(&scenario, &runtime(120)).embedded;

    assert_eq!(first, second, "embedded results must replay exactly");
    assert_eq!(first.train_count, expected_trains);
    assert_eq!(
        first.controller_ticks,
        u64::from(expected_trains) * 120,
        "TCMS/application stack did not run for every train tick"
    );
    assert_eq!(first.cbm_samples, first.controller_ticks);
    assert_eq!(first.t2g_primary_ticks, first.controller_ticks);
    assert!(first.t2g_transmissions > 0);
    assert!(first.event_records_written >= first.controller_ticks);
    assert!(first.tcms_ready_to_move_ticks > 0);
    assert_eq!(first.cbm_service_flags, 0);
    assert_eq!(first.hot_axle_trip_ticks, 0);
    assert_eq!(first.t2g_offline_ticks, 0);
}

#[test]
fn embedded_faults_exercise_failover_store_forward_and_maintenance_alerts() {
    let mut scenario = canonical_samawah_scenario();
    let train = TrainFaultScope::Train(TrainId::new(1));
    scenario.faults.extend([
        Fault {
            name: "primary-radio-loss".into(),
            from_sim_s: 10,
            to_sim_s: 20,
            kind: FaultKind::T2gPrimaryOffline { scope: train },
        },
        Fault {
            name: "total-radio-loss".into(),
            from_sim_s: 20,
            to_sim_s: 30,
            kind: FaultKind::T2gAllOffline { scope: train },
        },
        Fault {
            name: "bearing-overheat".into(),
            from_sim_s: 30,
            to_sim_s: 40,
            kind: FaultKind::HotAxleOverheat { scope: train },
        },
        Fault {
            name: "service-degradation".into(),
            from_sim_s: 40,
            to_sim_s: 50,
            kind: FaultKind::CbmDegradation { scope: train },
        },
    ]);

    let result = run(&scenario, &runtime(90));
    let embedded = &result.embedded;
    let affected = embedded
        .per_train
        .iter()
        .find(|item| item.train == "T1")
        .expect("T1 embedded summary");

    assert!(affected.t2g_backup_ticks >= 10);
    assert!(affected.t2g_offline_ticks >= 10);
    assert!(affected.maximum_t2g_queue_depth > 0);
    assert_eq!(
        affected.final_t2g_queue_depth, 0,
        "queued telemetry should drain after radio recovery"
    );
    assert!(affected.hot_axle_trip_ticks >= 10);
    assert!(affected.cbm_service_flags > 0);
    assert!(affected.tcms_trip_ticks >= 10);
    assert_eq!(result.faults_fired.len(), 4);
}

#[test]
fn event_recorders_remain_bounded_on_long_runs() {
    let scenario = canonical_samawah_scenario();
    let embedded = run(&scenario, &runtime(4_200)).embedded;

    assert!(embedded.event_records_dropped > 0);
    assert_eq!(
        embedded.event_records_written,
        embedded.event_records_retained + embedded.event_records_dropped
    );
    assert!(embedded
        .per_train
        .iter()
        .all(|train| train.event_records_retained <= 4_096));
}
