use osr_sim::fault::{Fault, FaultKind, TrainFaultScope};
use osr_sim::scenario_file::canonical_samawah_scenario;
use osr_sim::sim::{run, RuntimeConfig};

fn runtime() -> RuntimeConfig {
    RuntimeConfig {
        duration_s: 30,
        status_every_s: 0,
        ma_check_every_s: 0,
        ..RuntimeConfig::default()
    }
}

#[test]
fn generated_registry_feeds_deterministic_odometry_fixes() {
    let scenario = canonical_samawah_scenario();
    let first = run(&scenario, &runtime()).balise_systems;
    let second = run(&scenario, &runtime()).balise_systems;
    assert_eq!(first, second);
    assert_eq!(
        first.registry_count as usize,
        scenario.network.sections.len()
    );
    assert!(first.crossing_opportunities > 0);
    assert_eq!(first.fixes_applied, first.crossing_opportunities);
    assert_eq!(first.seen_sightings, first.fixes_applied);
    assert_eq!(first.missed_sightings, 0);
    assert_eq!(first.position_mismatches, 0);
}

#[test]
fn missed_and_mismatched_sightings_never_become_position_fixes() {
    for kind in [
        FaultKind::BaliseMissed {
            scope: TrainFaultScope::All,
        },
        FaultKind::BalisePositionMismatch {
            scope: TrainFaultScope::All,
        },
    ] {
        let mut scenario = canonical_samawah_scenario();
        scenario.faults.push(Fault {
            name: "balise integration fault".to_string(),
            from_sim_s: 0,
            to_sim_s: 30,
            kind,
        });
        let summary = run(&scenario, &runtime()).balise_systems;
        assert!(summary.crossing_opportunities > 0);
        assert_eq!(summary.fixes_applied, 0);
        assert_eq!(summary.seen_sightings, 0);
        assert_eq!(
            summary.missed_sightings + summary.position_mismatches,
            summary.crossing_opportunities
        );
    }
}
