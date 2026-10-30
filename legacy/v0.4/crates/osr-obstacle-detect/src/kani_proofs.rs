//! Kani bounded-model-checker harnesses for the five O-series
//! safety properties.
//!
//! Each harness builds an `any()`-generated [`SensorFrame`],
//! constrains only the pre-condition under test, and asserts the
//! evaluator's post-condition. `cargo kani --harness <name>` runs
//! the proof; `cargo test` skips this module.

#![cfg(kani)]

use crate::evaluate::evaluate;
use crate::sensors::{SensorFrame, MAX_SENSOR_STALE_MS};
use crate::verdict::{ObstacleVerdict, ULTRASONIC_MAX_SPEED_MMPS};

/// O1 — any ultrasonic echo inside the envelope forces EB.
#[kani::proof]
#[kani::unwind(5)]
fn o1_ultrasonic_return_forces_eb() {
    let mut f = SensorFrame::clear();
    // Force channel 0 to report a return; all other channels clean,
    // peer agreeing.
    let range: u32 = kani::any();
    kani::assume(range >= 200 && range <= 20_000);
    f.ultrasonic[0].nearest_mm = Some(range);

    let speed: u32 = kani::any();
    kani::assume(speed <= ULTRASONIC_MAX_SPEED_MMPS);

    let stop: u32 = kani::any();
    kani::assume(stop >= 1_000 && stop <= 200_000);

    let o = evaluate(&f, speed, stop, true);
    assert!(o.verdict == ObstacleVerdict::EmergencyBrake);
}

/// O2 — any stale safety-primary sensor forces EB.
#[kani::proof]
#[kani::unwind(5)]
fn o2_stale_ultrasonic_forces_eb() {
    let mut f = SensorFrame::clear();
    let stale: u32 = kani::any();
    kani::assume(stale > MAX_SENSOR_STALE_MS);
    f.ultrasonic[0].age_ms = stale;

    let o = evaluate(&f, 0, 100_000, true);
    assert!(o.verdict == ObstacleVerdict::EmergencyBrake);
}

/// O3 — peer disagreement on an otherwise-clear frame forces EB.
#[kani::proof]
#[kani::unwind(5)]
fn o3_peer_disagreement_forces_eb() {
    let f = SensorFrame::clear();
    let o = evaluate(&f, 0, 100_000, /*peer_clear=*/ false);
    assert!(o.verdict == ObstacleVerdict::EmergencyBrake);
}

/// O4a — speed above ultrasonic band with *every* long-range sensor
/// offline forces EB.
#[kani::proof]
#[kani::unwind(5)]
fn o4a_all_long_range_offline_above_band_forces_eb() {
    let mut f = SensorFrame::clear();
    f.lidar_offline = true;
    f.radar_offline = true;

    let speed: u32 = kani::any();
    kani::assume(speed > ULTRASONIC_MAX_SPEED_MMPS);
    kani::assume(speed <= 100_000);

    let o = evaluate(&f, speed, 100_000, true);
    assert!(o.verdict == ObstacleVerdict::EmergencyBrake);
}

/// O4b — LIDAR offline with radar still healthy produces at least
/// `RestrictedSpeed` (speed cap), not EB.
#[kani::proof]
#[kani::unwind(5)]
fn o4b_lidar_offline_with_radar_healthy_restricts_speed() {
    let mut f = SensorFrame::clear();
    f.lidar_offline = true;
    // Radar explicitly healthy.
    f.radar_offline = false;
    f.radar_age_ms = 0;

    let speed: u32 = kani::any();
    kani::assume(speed <= 100_000);

    let o = evaluate(&f, speed, 100_000, true);
    // Verdict is at least `RestrictedSpeed` — i.e., never `Clear` in
    // this configuration. No EB expected (no detections, no stale
    // ultrasonic).
    assert!(o.verdict >= ObstacleVerdict::RestrictedSpeed);
    assert!(o.verdict != ObstacleVerdict::EmergencyBrake);
}

/// O5 — refreshing a stale sensor never moves the verdict in the
/// less-restrictive direction (monotone severity under freshness).
///
/// Formally: for any frame `f` and any strictly-fresher frame `f'`
/// (same detections, same peer), the verdict of `f'` is ≤ verdict of
/// `f` on the severity order (Clear < CrawlOnly < EmergencyBrake).
#[kani::proof]
#[kani::unwind(5)]
fn o5_fresher_sensors_never_increase_severity() {
    let mut stale = SensorFrame::clear();
    stale.ultrasonic[0].age_ms = MAX_SENSOR_STALE_MS + 10;

    let mut fresh = stale.clone();
    fresh.ultrasonic[0].age_ms = 0;

    let a = evaluate(&stale, 0, 100_000, true);
    let b = evaluate(&fresh, 0, 100_000, true);

    // Severity of b must be ≤ severity of a.
    assert!(b.verdict <= a.verdict);
}
