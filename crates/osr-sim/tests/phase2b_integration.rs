//! End-to-end integration test of the Phase 2b crates
//! (`osr-ato` + `osr-bms` + `osr-traction`) running alongside the
//! existing Phase 2a shadow stack, on a real Samawah scenario.
//!
//! Verifies that the full onboard software chain —
//! odometry → ATP → ATO → BMS → Traction → Brake — produces clean
//! telemetry under nominal service:
//!
//! - zero spurious safety trips (emergency, BMS fault, traction fault)
//! - realistic torque / current / SoC trajectories
//! - ATO actually drives the train through meaningful modes
//! - SoC decreases over time under a net-discharge duty cycle

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
        use_consensus: false,
    }
}

#[test]
fn full_phase2b_stack_runs_clean_on_samawah() {
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(900)); // 15 minutes

    let ob = &result.onboard;
    assert!(ob.ticks_evaluated > 0, "no shadow ticks");
    assert_eq!(
        ob.total_emergency_ticks, 0,
        "emergencies: {:?}",
        ob.emergencies
    );
    assert_eq!(
        ob.total_bms_fault_ticks, 0,
        "BMS faults observed — pack state drove out of range under nominal load"
    );
    assert_eq!(
        ob.total_traction_fault_ticks, 0,
        "traction faults observed — inverter tripped under nominal conditions"
    );
}

#[test]
fn ato_drives_trains_through_meaningful_modes() {
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(600));

    // Across the fleet we should see a healthy mix of ATO modes.
    // A train that never accelerates or never decelerates indicates
    // the control law isn't engaging properly.
    let total_accel: u64 = result
        .onboard
        .per_train
        .iter()
        .map(|t| u64::from(t.ato_ticks_accelerating))
        .sum();
    let total_brake: u64 = result
        .onboard
        .per_train
        .iter()
        .map(|t| u64::from(t.ato_ticks_braking))
        .sum();
    let total_approach: u64 = result
        .onboard
        .per_train
        .iter()
        .map(|t| u64::from(t.ato_ticks_station_approach))
        .sum();

    assert!(total_accel > 0, "no ATO acceleration ticks");
    // Decel must engage somehow — direct braking or station approach.
    assert!(
        total_brake + total_approach > 0,
        "no ATO decel ticks (brake + approach both zero)"
    );
}

#[test]
fn bms_soc_drops_over_run_under_net_discharge() {
    // Over a long run with a fleet actively moving, average SoC
    // should decrease (trains discharge more than they regen).
    // This is a sanity check that Coulomb counting + the traction
    // current feedback loop are actually connected.
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(1_800));

    // Average min SoC across the fleet should be strictly below the
    // starting SoC (800 ppt from the sim default).
    let avg_min_soc: f64 = if result.onboard.per_train.is_empty() {
        800.0
    } else {
        let total: u64 = result
            .onboard
            .per_train
            .iter()
            .map(|t| u64::from(t.min_soc_ppt))
            .sum();
        total as f64 / result.onboard.per_train.len() as f64
    };
    assert!(
        avg_min_soc < 800.0,
        "avg min SoC {avg_min_soc:.1} ≥ initial 800 — Coulomb counting isn't tracking load"
    );
}

#[test]
fn peak_torque_within_traction_rating() {
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(600));

    // Peak torque across any train shouldn't exceed the crate's
    // default max_torque_mnm (10 kN·m aggregate from
    // TractionParams::light_metro_default).
    let max_rating = 10_000_000_i32;
    for t in &result.onboard.per_train {
        assert!(
            t.peak_torque_mnm.abs() <= max_rating && t.min_torque_mnm.abs() <= max_rating,
            "train {} torque out of rating: peak={} min={}",
            t.train,
            t.peak_torque_mnm,
            t.min_torque_mnm
        );
    }
}
