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
