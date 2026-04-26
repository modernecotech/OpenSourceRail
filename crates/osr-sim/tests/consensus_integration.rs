//! Integration test: run a Samawah scenario with the MA log backed
//! by a real 3-node `osr-consensus::Cluster` and verify the run is
//! invariant-clean with a healthy fleet-wide MA sweep summary.
//!
//! Post-M5 the MA computer is the authoritative source of occupancy,
//! so the "zero consistency violations" check is now the main
//! `invariant_violations` list — if any gate decision ever disagrees
//! with the derived state, a violation lands there.

use osr_sim::scenario_file::canonical_samawah_scenario;
use osr_sim::sim::{run, RuntimeConfig};

#[test]
fn consensus_backed_ma_check_produces_clean_run() {
    let scenario = canonical_samawah_scenario();
    let runtime = RuntimeConfig {
        duration_s: 900, // 15 minutes of service
        time_step_s: 1,
        status_every_s: 0,
        csv_out: None,
        csv_every_s: 60,
        ma_check_every_s: 60, // a handful of MA sweeps
        use_consensus: true,
    };
    let result = run(&scenario, &runtime);

    let ma = &result.ma_check;
    assert!(
        ma.checks_run > 0,
        "no MA sweeps ran — expected at least one within {} s",
        runtime.duration_s
    );
    assert!(
        ma.total_mas_computed > 0,
        "no MAs computed — consensus may not have delivered entries"
    );
    assert!(
        result.invariant_violations.is_empty(),
        "invariant violations under consensus: {:#?}",
        result.invariant_violations
    );
}

#[test]
fn consensus_and_simulated_produce_equivalent_ma_summaries() {
    // Same short scenario under both backends; both should report
    // zero invariant violations and roughly equal numbers of MA
    // evaluations. Not byte-equal (consensus timing adds small
    // differences in when entries commit), but structurally equivalent.
    let scenario = canonical_samawah_scenario();
    let short_runtime = |use_consensus: bool| RuntimeConfig {
        duration_s: 300,
        time_step_s: 1,
        status_every_s: 0,
        csv_out: None,
        csv_every_s: 60,
        ma_check_every_s: 30,
        use_consensus,
    };

    let sim = run(&scenario, &short_runtime(false));
    let con = run(&scenario, &short_runtime(true));

    assert_eq!(
        sim.ma_check.checks_run, con.ma_check.checks_run,
        "sweep count should match (both use the same cadence)"
    );
    assert!(sim.invariant_violations.is_empty());
    assert!(con.invariant_violations.is_empty());
    let s = sim.ma_check.total_mas_computed as f64;
    let c = con.ma_check.total_mas_computed as f64;
    assert!(
        (s - c).abs() / s.max(1.0) < 0.2,
        "MA count diverges too much: simulated={} consensus={}",
        sim.ma_check.total_mas_computed,
        con.ma_check.total_mas_computed
    );
}
