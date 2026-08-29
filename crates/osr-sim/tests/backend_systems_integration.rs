//! End-to-end CBM → T2G → depot backend/historian/analytics evidence.

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
fn nominal_radio_payloads_reach_bounded_backend_services_deterministically() {
    let scenario = canonical_samawah_scenario();
    let expected_trains: u32 = scenario
        .fleets
        .iter()
        .map(|fleet| fleet.trainset_count)
        .sum();
    let first = run(&scenario, &runtime(120));
    let second = run(&scenario, &runtime(120));
    let backend = &first.backend_systems;

    assert_eq!(first.backend_systems, second.backend_systems);
    assert_eq!(
        backend.cbm_samples_received, first.embedded.t2g_transmissions,
        "every successful telemetry transmission must reach the backend"
    );
    assert_eq!(
        backend.historian_samples_ingested,
        backend.cbm_samples_received * 5
    );
    assert_eq!(backend.historian_metrics_retained, expected_trains * 5);
    assert_eq!(
        backend.analytics_metrics_evaluated,
        backend.historian_metrics_retained
    );
    assert_eq!(
        backend.analytics_samples_evaluated,
        backend.historian_samples_ingested
    );
    assert_eq!(backend.routine_work_orders, 0);
    assert_eq!(backend.urgent_work_orders, 0);
    assert!(backend.work_orders.is_empty());
}

#[test]
fn offline_degraded_payloads_replay_in_order_and_raise_backend_orders() {
    let mut scenario = canonical_samawah_scenario();
    let train = TrainFaultScope::Train(TrainId::new(1));
    scenario.faults.extend([
        Fault {
            name: "radio-blackout".into(),
            from_sim_s: 10,
            to_sim_s: 30,
            kind: FaultKind::T2gAllOffline { scope: train },
        },
        Fault {
            name: "degradation-during-blackout".into(),
            from_sim_s: 12,
            to_sim_s: 22,
            kind: FaultKind::CbmDegradation { scope: train },
        },
    ]);

    let first = run(&scenario, &runtime(90));
    let second = run(&scenario, &runtime(90));
    assert_eq!(first.backend_systems, second.backend_systems);
    assert!(first.embedded.maximum_t2g_queue_depth > 0);
    assert_eq!(first.embedded.final_t2g_queue_depth, 0);
    assert!(first.backend_systems.urgent_work_orders > 0);
    assert!(first
        .backend_systems
        .work_orders
        .iter()
        .all(|order| order.train_id == 1 && order.priority == "Urgent"));
    assert_eq!(first.faults_fired.len(), 2);
    assert!(first.invariant_violations.is_empty());
}
