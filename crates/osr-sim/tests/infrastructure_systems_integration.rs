//! End-to-end station and wayside embedded-controller evidence.

use osr_interlocking::IntrusionState;
use osr_sim::fault::{Fault, FaultKind, FaultScope};
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
fn nominal_station_and_wayside_controllers_cover_every_asset_tick() {
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(180));
    let infrastructure = &result.infrastructure_systems;

    assert_eq!(
        infrastructure.stations.controller_ticks,
        scenario.network.stations.len() as u64 * 180
    );
    assert_eq!(
        infrastructure.stations.psd_panel_evaluations,
        infrastructure.stations.controller_ticks * 12
    );
    assert!(infrastructure.stations.psd_open_ticks > 0);
    assert!(infrastructure.stations.pis_board_entries > 0);
    assert_eq!(infrastructure.stations.psd_obstruction_ticks, 0);
    assert_eq!(infrastructure.stations.scada_degraded_ticks, 0);
    assert_eq!(
        infrastructure.wayside.detector_ticks,
        scenario.network.sections.len() as u64 * 180
    );
    assert_eq!(
        infrastructure.wayside.clear_ticks,
        infrastructure.wayside.detector_ticks
    );
    assert_eq!(infrastructure.wayside.verdict_transitions, 0);
}

#[test]
fn infrastructure_faults_reach_real_controllers_and_consensus() {
    let mut scenario = canonical_samawah_scenario();
    let station = *scenario.network.stations.keys().next().expect("station");
    let section = *scenario.network.sections.keys().next().expect("section");
    scenario.faults.extend([
        Fault {
            name: "platform-obstruction".into(),
            from_sim_s: 10,
            to_sim_s: 20,
            kind: FaultKind::PlatformDoorObstruction {
                scope: FaultScope::Station(station),
            },
        },
        Fault {
            name: "station-scada".into(),
            from_sim_s: 20,
            to_sim_s: 30,
            kind: FaultKind::StationScadaFailure {
                scope: FaultScope::Station(station),
            },
        },
        Fault {
            name: "wayside-present".into(),
            from_sim_s: 30,
            to_sim_s: 40,
            kind: FaultKind::WaysideIntrusion {
                section,
                state: IntrusionState::Present,
            },
        },
    ]);

    let first = run(&scenario, &runtime(70));
    let second = run(&scenario, &runtime(70));
    assert_eq!(
        first.infrastructure_systems, second.infrastructure_systems,
        "infrastructure controller evidence must replay exactly"
    );
    assert!(first.infrastructure_systems.stations.psd_obstruction_ticks >= 10);
    assert!(first.infrastructure_systems.stations.scada_degraded_ticks >= 10);
    assert_eq!(first.infrastructure_systems.wayside.present_ticks, 10);
    assert_eq!(first.infrastructure_systems.wayside.verdict_transitions, 2);
    assert_eq!(first.faults_fired.len(), 3);
    assert!(first.invariant_violations.is_empty());
}
