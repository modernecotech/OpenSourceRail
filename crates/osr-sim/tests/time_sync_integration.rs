//! End-to-end evidence that the shared IEEE 1588 state machine participates.

use osr_sim::scenario_file::load_scenario_from_str;
use osr_sim::sim::{run, RuntimeConfig};

#[test]
fn shared_clock_acquires_lock_and_replays_exactly() {
    let scenario =
        load_scenario_from_str(include_str!("../../../lib/examples/example-simple.toml"))
            .expect("simple scenario");
    let runtime = RuntimeConfig {
        duration_s: 10,
        time_step_s: 1,
        status_every_s: 0,
        csv_out: None,
        csv_every_s: 60,
        ma_check_every_s: 0,
    };

    let first = run(&scenario, &runtime).time_sync;
    let second = run(&scenario, &runtime).time_sync;

    assert_eq!(first, second);
    assert_eq!(first.controller_ticks, 10);
    assert_eq!(first.acquiring_ticks, 3);
    assert_eq!(first.locked_ticks, 7);
    assert_eq!(first.lock_transitions, 2);
    assert_eq!(first.maximum_absolute_offset_ns, 0);
    assert_eq!(first.maximum_path_delay_ns, 500);
    assert_eq!(first.final_lock_state, "Locked");
}
