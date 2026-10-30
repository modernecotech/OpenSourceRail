//! End-to-end evidence for the legacy application-tier embedded crates.

use osr_core::TrainId;
use osr_sim::fault::{Fault, FaultKind, TrainFaultScope};
use osr_sim::scenario_file::{canonical_samawah_scenario, load_scenario_from_str};
use osr_sim::sim::{run, EventKind, RuntimeConfig};

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
    assert_eq!(first.tcms_departure_inhibit_ticks, 0);
    assert_eq!(first.tcms_travel_hold_ticks, 0);
    assert_eq!(first.cbm_service_flags, 0);
    assert_eq!(first.hot_axle_trip_ticks, 0);
    assert_eq!(first.t2g_offline_ticks, 0);
}

#[test]
fn tcms_trip_feedback_holds_motion_and_delays_arrival_deterministically() {
    let scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    let nominal = run(&scenario, &runtime(180));

    let mut faulted_scenario = scenario;
    faulted_scenario.faults.push(Fault {
        name: "bearing-overheat-movement-feedback".into(),
        from_sim_s: 10,
        to_sim_s: 20,
        kind: FaultKind::HotAxleOverheat {
            scope: TrainFaultScope::All,
        },
    });
    let first = run(&faulted_scenario, &runtime(180));
    let second = run(&faulted_scenario, &runtime(180));

    let first_arrival = |result: &osr_sim::sim::SimResult| {
        result
            .events
            .iter()
            .find(|event| matches!(event.kind, EventKind::ArriveStation { .. }))
            .map(|event| event.sim_time_s)
            .expect("train should arrive within the test run")
    };

    assert_eq!(first.embedded, second.embedded);
    assert_eq!(first.events.len(), second.events.len());
    assert_eq!(first.embedded.tcms_travel_hold_ticks, 10);
    assert_eq!(first.embedded.tcms_departure_inhibit_ticks, 0);
    assert_eq!(first_arrival(&first), first_arrival(&nominal) + 10);
    assert!(first.total_train_km < nominal.total_train_km);
}

#[test]
fn tcms_trip_feedback_inhibits_scheduled_dispatch() {
    let mut scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    scenario.start_time_s_after_midnight = 5 * 3_600 + 59 * 60 + 50;
    let nominal = run(&scenario, &runtime(60));

    scenario.faults.push(Fault {
        name: "pre-service-bearing-overheat".into(),
        from_sim_s: 0,
        to_sim_s: 20,
        kind: FaultKind::HotAxleOverheat {
            scope: TrainFaultScope::All,
        },
    });
    let faulted = run(&scenario, &runtime(60));

    let dispatch_time = |result: &osr_sim::sim::SimResult| {
        result
            .events
            .iter()
            .find(|event| matches!(event.kind, EventKind::Dispatched))
            .map(|event| event.sim_time_s)
            .expect("train should dispatch within the test run")
    };

    assert_eq!(dispatch_time(&nominal), 10);
    assert_eq!(dispatch_time(&faulted), 21);
    assert_eq!(faulted.embedded.tcms_departure_inhibit_ticks, 11);
    assert_eq!(faulted.embedded.tcms_travel_hold_ticks, 0);
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

#[test]
fn prolonged_radio_outage_keeps_payload_memory_bounded() {
    let mut scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    scenario.faults.push(Fault {
        name: "prolonged-radio-blackout".into(),
        from_sim_s: 0,
        to_sim_s: 8_300,
        kind: FaultKind::T2gAllOffline {
            scope: TrainFaultScope::All,
        },
    });

    let embedded = run(&scenario, &runtime(8_300)).embedded;
    assert_eq!(embedded.maximum_t2g_queue_depth, 4_096);
    assert_eq!(embedded.final_t2g_queue_depth, 4_096);
    assert!(embedded.t2g_payloads_dropped > 0);
    assert_eq!(embedded.t2g_transmissions, 0);
}
