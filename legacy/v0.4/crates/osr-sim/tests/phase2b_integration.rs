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
use osr_sim::sim::{run, EventKind, RuntimeConfig};

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
fn promoted_buildable_trainset_baseline_runs_on_samawah() {
    let scenario = canonical_samawah_scenario();

    assert_eq!(scenario.consist.car_count, 3);
    assert_eq!(scenario.consist.length_mm, 49_500);
    assert_eq!(scenario.consist.mass_kg, 78_750);
    assert_eq!(scenario.consist.battery_capacity_wh, 675_000);
    assert!((scenario.roof_pv.nameplate_kw - 15.12).abs() < 0.01);

    let result = run(&scenario, &runtime(900));
    assert!(
        result.invariant_violations.is_empty(),
        "running-test invariant violations: {:?}",
        result.invariant_violations
    );
    assert!(result.total_train_km > 0.1, "trainset did not move");
    assert!(
        result.total_energy_consumed_kwh > 0.0,
        "trainset did not consume traction/auxiliary energy"
    );
    assert_eq!(
        result.onboard.total_emergency_ticks, 0,
        "promoted trainset tripped emergency during nominal running test"
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
    // starting SoC (950 ppt from the sim fleet constructor).
    const INITIAL_SOC_PPT: f64 = 950.0;
    let avg_min_soc: f64 = if result.onboard.per_train.is_empty() {
        INITIAL_SOC_PPT
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
        avg_min_soc < INITIAL_SOC_PPT,
        "avg min SoC {avg_min_soc:.1} ≥ initial {INITIAL_SOC_PPT:.0} — Coulomb counting isn't tracking load"
    );
}

#[test]
fn peak_torque_within_traction_rating() {
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(600));

    // Peak torque across any train shouldn't exceed the crate's
    // default max_torque_mnm (12 kN·m aggregate from
    // TractionParams::light_metro_default).
    let max_rating = 12_000_000_i32;
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

#[test]
#[ignore = "long-horizon consensus soak; run explicitly before release"]
fn two_hour_samawah_run_preserves_battery_reserve_and_event_balance() {
    let scenario = canonical_samawah_scenario();
    let result = run(&scenario, &runtime(7_200));

    let minimum_soc = result
        .per_train_final_soc
        .iter()
        .map(|(_, _, _, minimum)| *minimum)
        .fold(1.0_f32, f32::min);
    assert!(
        minimum_soc >= 0.20,
        "nominal Samawah service breached the 20% operating reserve: {minimum_soc:.3}"
    );
    for event in &result.events {
        if let EventKind::SocWarning { soc } = event.kind {
            assert!(
                soc >= 0.20,
                "an SoC warning reported a reserve breach: {soc:.3}"
            );
        }
    }

    let arrivals = result
        .events
        .iter()
        .filter(|event| matches!(event.kind, EventKind::ArriveStation { .. }))
        .count();
    let departures = result
        .events
        .iter()
        .filter(|event| matches!(event.kind, EventKind::DepartStation))
        .count();
    let dispatches = result
        .events
        .iter()
        .filter(|event| matches!(event.kind, EventKind::Dispatched))
        .count();
    let movements_started = departures + dispatches;
    assert!(
        departures <= arrivals,
        "a station departure must follow an arrival: {departures} departures, {arrivals} arrivals"
    );
    assert!(
        arrivals <= movements_started && movements_started - arrivals <= 108,
        "started/finished movement balance is impossible: {movements_started} starts, {arrivals} arrivals"
    );
    assert!(
        result.invariant_violations.is_empty(),
        "two-hour invariant violations: {:?}",
        result.invariant_violations
    );
}
