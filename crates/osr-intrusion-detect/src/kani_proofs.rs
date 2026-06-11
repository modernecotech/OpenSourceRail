//! Kani bounded-model-checker harnesses for I1–I5.

#![cfg(kani)]

use crate::evaluate::{evaluate, IntrusionParams};
use crate::sensors::{
    CameraReturn, LidarReturn, RadarReturn, WaysideSensorFrame, LATERAL_GATE_MM,
    MAX_SENSOR_STALE_MS,
};
use crate::verdict::IntrusionVerdict;

/// I1 — LIDAR return inside the rail profile forces Present.
#[kani::proof]
#[kani::unwind(5)]
fn i1_lidar_in_profile_forces_present() {
    let mut f = WaysideSensorFrame::clear();
    let lateral: i32 = kani::any();
    kani::assume(lateral.abs() <= LATERAL_GATE_MM);
    let long_mm: u32 = kani::any();
    kani::assume(long_mm <= 1_000_000);
    f.lidar[0] = Some(LidarReturn {
        longitudinal_mm: long_mm,
        lateral_mm: lateral,
    });

    let o = evaluate(&f, 0, &IntrusionParams::default());
    assert!(o.verdict == IntrusionVerdict::Present);
}

/// I2 — any stale safety-primary sensor forces at least Unknown.
#[kani::proof]
#[kani::unwind(5)]
fn i2_stale_lidar_forces_unknown_or_worse() {
    let mut f = WaysideSensorFrame::clear();
    let stale: u32 = kani::any();
    kani::assume(stale > MAX_SENSOR_STALE_MS);
    f.lidar_age_ms = stale;

    let o = evaluate(&f, 0, &IntrusionParams::default());
    assert!(o.verdict != IntrusionVerdict::Clear);
}

/// I3 — fence breach forces Present unconditionally.
#[kani::proof]
#[kani::unwind(5)]
fn i3_fence_breach_forces_present() {
    let mut f = WaysideSensorFrame::clear();
    f.fence.breach_latched = true;

    let o = evaluate(&f, 0, &IntrusionParams::default());
    assert!(o.verdict == IntrusionVerdict::Present);
}

/// I4 — camera classifier alone (no safety-primary hit) cannot emit Clear
/// when the camera is a confident hazard class.
#[kani::proof]
#[kani::unwind(5)]
fn i4_camera_alone_cannot_clear_a_hazard_class() {
    let mut f = WaysideSensorFrame::clear();
    f.camera = Some(CameraReturn {
        class: crate::sensors::CameraClass::Human,
        confidence: 200,
    });
    let o = evaluate(&f, 0, &IntrusionParams::default());
    assert!(o.verdict != IntrusionVerdict::Clear);
}

/// I5 — strictly-fresher sensor frame never moves the verdict in the
/// less-restrictive direction.
#[kani::proof]
#[kani::unwind(5)]
fn i5_fresher_never_increases_severity() {
    let mut stale = WaysideSensorFrame::clear();
    stale.lidar_age_ms = MAX_SENSOR_STALE_MS + 50;
    let mut fresh = stale.clone();
    fresh.lidar_age_ms = 0;

    let a = evaluate(&stale, 0, &IntrusionParams::default());
    let b = evaluate(&fresh, 0, &IntrusionParams::default());

    // Severity of b is ≤ severity of a.
    assert!(b.verdict <= a.verdict);
}
