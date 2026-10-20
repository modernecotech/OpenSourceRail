//! Portable SBC-hosted offline replay. No GPIO, PWM, fieldbus or hardware enable.
use osr_maglev_control::{evaluate, Inputs, Params, State};

fn main() {
    let params = Params {
        target_gap_um: 8000,
        minimum_gap_um: 3000,
        maximum_gap_um: 13000,
        sensor_disagreement_um: 200,
        maximum_age_ns: 500_000,
        maximum_tick_ns: 2_000_000,
        bias_current_ma: 1000,
        minimum_current_ma: -5000,
        maximum_current_ma: 5000,
        proportional_ma_per_um: 1,
        derivative_ma_per_um_s: 0,
    };
    let mut state = State::default();
    println!("offline maglev replay; synthetic gains/inputs; physical output disabled");
    for tick in 1..=8 {
        let now = tick * 1_000_000;
        let input = Inputs {
            issued_ns: now,
            sequence: tick,
            gap_a_um: 8000,
            gap_b_um: 8010,
            sensors_healthy: true,
            drive_healthy: true,
            support_power_available: true,
            traction_requested: true,
            stop_requested: tick >= 5,
            secured: tick == 8,
            stopped: tick == 8,
            reset_requested: false,
        };
        let result = evaluate(state, input, now, params);
        println!(
            "tick={tick} support={:?} traction={} stop={} physical_output={}",
            result.support,
            result.traction_permitted_in_study,
            result.controlled_stop_required,
            result.physical_output_authorised
        );
        state = result.state;
    }
}
