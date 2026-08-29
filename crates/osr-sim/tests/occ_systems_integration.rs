use osr_core::TrainId;
use osr_sim::fault::{Fault, FaultKind, TrainFaultScope};
use osr_sim::scenario_file::canonical_samawah_scenario;
use osr_sim::sim::{run, EventKind, RuntimeConfig};

fn runtime(duration_s: u32) -> RuntimeConfig {
    RuntimeConfig {
        duration_s,
        status_every_s: 0,
        ma_check_every_s: 0,
        ..RuntimeConfig::default()
    }
}

#[test]
fn nominal_tcms_telemetry_populates_occ_roster_deterministically() {
    let scenario = canonical_samawah_scenario();
    let first = run(&scenario, &runtime(30)).occ_systems;
    let second = run(&scenario, &runtime(30)).occ_systems;
    assert_eq!(first, second);
    let fleet = scenario
        .fleets
        .iter()
        .map(|line| line.trainset_count)
        .sum::<u32>();
    assert_eq!(first.controller_ticks, 30);
    assert_eq!(first.final_roster_count, fleet);
    assert_eq!(first.telemetry_reports_processed, u64::from(fleet) * 30);
    assert_eq!(first.incidents_opened, 0);
    assert_eq!(first.final_active_dispatch_holds, 0);
}

#[test]
fn critical_incident_holds_line_dispatch_then_clears() {
    let mut scenario = canonical_samawah_scenario();
    scenario.faults.push(Fault {
        name: "line one emergency".to_string(),
        from_sim_s: 1,
        to_sim_s: 380,
        kind: FaultKind::ObstaclePeerDisagreement {
            scope: TrainFaultScope::Train(TrainId::new(1)),
        },
    });
    let result = run(&scenario, &runtime(420));
    assert_eq!(result.occ_systems.incidents_opened, 1);
    assert_eq!(result.occ_systems.incidents_closed, 1);
    assert!(result.occ_systems.dispatch_hold_ticks >= 378);
    assert_eq!(result.occ_systems.final_active_incidents, 0);
    assert_eq!(result.occ_systems.final_active_dispatch_holds, 0);

    let resumed_dispatch = result.events.iter().any(|event| {
        event.line == "line-1"
            && event.sim_time_s >= 380
            && matches!(event.kind, EventKind::Dispatched)
    });
    assert!(
        resumed_dispatch,
        "line dispatch should resume after incident clear"
    );
}
