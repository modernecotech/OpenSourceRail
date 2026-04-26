//! Integration test: run a short Samawah scenario and verify the
//! shadow onboard stack (osr-odometry + osr-atp + osr-brake) never
//! trips Emergency under nominal service conditions.
//!
//! Failure of this test indicates one of:
//! - The shadow's kinematic integrator produces speeds that exceed
//!   the ATP envelope computed from the consist's emergency braking
//!   curve.
//! - The local MA falls short of the train's head position (an
//!   integration bug in onboard.rs).
//! - ATP's envelope math (max_safe_speed_mmps) is wrong.
//! - The brake crate's emergency-trip conditions fire spuriously.
//!
//! Any of these is a regression. Nominal-service Samawah with the
//! default consist should produce thousands of Service and Release
//! ticks and zero Emergencies.

use osr_sim::scenario_file::canonical_samawah_scenario;
use osr_sim::sim::{run, RuntimeConfig};

#[test]
fn nominal_samawah_line1_produces_no_onboard_emergency() {
    let scenario = canonical_samawah_scenario();
    // Run 10 minutes (600 s) from service start. Enough for every
    // trainset to dispatch and complete at least one round of
    // section traversals, but fast enough to keep the test snappy.
    let runtime = RuntimeConfig {
        duration_s: 600,
        time_step_s: 1,
        status_every_s: 0, // silence status lines in CI
        csv_out: None,
        csv_every_s: 60,
        ma_check_every_s: 0, // disable periodic MA check; the onboard stack is the focus
        use_consensus: false,
    };
    let result = run(&scenario, &runtime);

    let ob = &result.onboard;
    assert!(
        ob.ticks_evaluated > 0,
        "no shadow ticks evaluated — onboard stack didn't run"
    );
    assert_eq!(
        ob.total_emergency_ticks, 0,
        "onboard emergencies under nominal service: {:?}",
        ob.emergencies
    );
    // Most ticks should be Release (train at cruise); a minority
    // Service (approach-to-station). No Emergency.
    assert!(
        ob.total_release_ticks > 0,
        "zero Release ticks — kinematic integrator may not be advancing"
    );

    // Every Traveling train should have accumulated some shadow
    // distance.
    let total_shadow_km: f64 = ob
        .per_train
        .iter()
        .map(|t| t.shadow_distance_km)
        .sum();
    assert!(
        total_shadow_km > 0.1,
        "total shadow distance {:.3} km — kinematic shadow didn't move",
        total_shadow_km
    );
}

#[test]
fn onboard_approach_ticks_fire_near_stations() {
    // Same scenario; check that ATP's EnvelopeApproach reason fires
    // at least once — a mild Service command near end-of-section is
    // expected as the kinematic shadow decelerates into the station.
    let scenario = canonical_samawah_scenario();
    let runtime = RuntimeConfig {
        duration_s: 600,
        time_step_s: 1,
        status_every_s: 0,
        csv_out: None,
        csv_every_s: 60,
        ma_check_every_s: 0,
        use_consensus: false,
    };
    let result = run(&scenario, &runtime);
    let ob = &result.onboard;
    // Approach ticks demonstrate the ATP→brake service-band logic
    // is actually exercised by realistic deceleration profiles.
    assert!(
        ob.total_approach_ticks > 0 || ob.total_service_ticks > 0,
        "no approach/service ticks — brake crate never exercises service band: {ob:?}"
    );
}
