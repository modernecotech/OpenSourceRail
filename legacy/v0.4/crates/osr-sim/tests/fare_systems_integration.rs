use osr_sim::fault::{Fault, FaultKind, FaultScope};
use osr_sim::scenario_file::canonical_samawah_scenario;
use osr_sim::sim::{run, RuntimeConfig};

fn runtime() -> RuntimeConfig {
    RuntimeConfig {
        duration_s: 360,
        status_every_s: 0,
        ma_check_every_s: 0,
        ..RuntimeConfig::default()
    }
}

#[test]
fn signed_station_fares_reconcile_deterministically() {
    let scenario = canonical_samawah_scenario();
    let first = run(&scenario, &runtime()).fare_systems;
    let second = run(&scenario, &runtime()).fare_systems;
    assert_eq!(first, second);
    assert_eq!(
        first.station_count as usize,
        scenario.network.stations.len()
    );
    assert!(first.gate_controller_ticks > 0);
    assert!(first.tickets_issued > 0);
    assert_eq!(first.gate_grants, first.tickets_issued);
    assert_eq!(first.ledger_entries, first.gate_grants);
    assert_eq!(first.tvm_sales_cents, first.settled_fare_cents);
    assert_eq!(first.gate_denials, 0);
    assert_eq!(first.flagged_accounts, 0);
}

#[test]
fn tampered_tokens_are_denied_and_repeated_probes_raise_fraud_flags() {
    let mut scenario = canonical_samawah_scenario();
    scenario.faults.push(Fault {
        name: "tampered fare token".to_string(),
        from_sim_s: 0,
        to_sim_s: 360,
        kind: FaultKind::FareTokenTamper {
            scope: FaultScope::All,
        },
    });
    let summary = run(&scenario, &runtime()).fare_systems;
    assert!(summary.tickets_issued > 0);
    assert_eq!(summary.gate_denials, summary.tickets_issued);
    assert_eq!(summary.gate_grants, 0);
    assert_eq!(summary.ledger_entries, 0);
    assert_eq!(summary.settled_fare_cents, 0);
    assert_eq!(summary.flagged_accounts, summary.station_count);
    assert_eq!(summary.fraud_flags_raised, u64::from(summary.station_count));
}
