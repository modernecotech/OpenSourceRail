//! Proptests exercising I1–I5 across a wide random-input space.

use osr_intrusion_detect::{
    evaluate, CameraClass, CameraReturn, IntrusionParams, IntrusionVerdict, LidarReturn,
    RadarReturn, TriggerReason, WaysideSensorFrame, LATERAL_GATE_MM, MAX_SENSOR_STALE_MS,
};
use proptest::prelude::*;

proptest! {
    /// I1 — any LIDAR return inside the rail profile always forces Present.
    #[test]
    fn i1_lidar_in_profile_always_present(
        lateral in -LATERAL_GATE_MM..=LATERAL_GATE_MM,
        long in 0u32..=1_000_000u32,
    ) {
        let mut f = WaysideSensorFrame::clear();
        f.lidar[0] = Some(LidarReturn {
            longitudinal_mm: long,
            lateral_mm: lateral,
        });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        prop_assert_eq!(o.verdict, IntrusionVerdict::Present);
    }

    /// I1 — any radar return inside the rail profile always forces Present.
    #[test]
    fn i1_radar_in_profile_always_present(
        lateral in -LATERAL_GATE_MM..=LATERAL_GATE_MM,
        long in 0u32..=1_000_000u32,
        vel in -50_000i32..=50_000i32,
    ) {
        let mut f = WaysideSensorFrame::clear();
        f.radar[0] = Some(RadarReturn {
            longitudinal_mm: long,
            lateral_mm: lateral,
            radial_speed_mmps: vel,
        });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        prop_assert_eq!(o.verdict, IntrusionVerdict::Present);
    }

    /// I2 — any stale safety-primary sensor produces at least Unknown.
    #[test]
    fn i2_stale_is_never_clear(
        stale in (MAX_SENSOR_STALE_MS + 1)..=500u32,
    ) {
        let mut f = WaysideSensorFrame::clear();
        f.lidar_age_ms = stale;
        let o = evaluate(&f, 0, &IntrusionParams::default());
        prop_assert!(o.verdict != IntrusionVerdict::Clear);
    }

    /// I3 — fence breach always forces Present.
    #[test]
    fn i3_fence_breach_always_present(seed in 0u32..=1000u32) {
        let mut f = WaysideSensorFrame::clear();
        f.fence.breach_latched = true;
        // Additional noise in the frame must not change the verdict.
        if seed % 2 == 0 {
            f.lidar_age_ms = MAX_SENSOR_STALE_MS + 10;
        }
        let o = evaluate(&f, 0, &IntrusionParams::default());
        prop_assert_eq!(o.verdict, IntrusionVerdict::Present);
        prop_assert_eq!(o.reason, TriggerReason::FenceBreach);
    }

    /// I4 — confident hazard classifier alone never emits Clear.
    #[test]
    fn i4_camera_hazard_never_clear(
        class_idx in 0u8..=2u8,
        conf in 160u8..=255u8,
    ) {
        let class = match class_idx {
            0 => CameraClass::Human,
            1 => CameraClass::LargeAnimal,
            _ => CameraClass::Vehicle,
        };
        let mut f = WaysideSensorFrame::clear();
        f.camera = Some(CameraReturn { class, confidence: conf });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        prop_assert!(o.verdict != IntrusionVerdict::Clear);
    }

    /// I5 — fresher frame never more severe.
    #[test]
    fn i5_fresher_never_more_severe(
        stale_age in (MAX_SENSOR_STALE_MS + 1)..=500u32,
    ) {
        let mut stale = WaysideSensorFrame::clear();
        stale.lidar_age_ms = stale_age;
        let mut fresh = stale.clone();
        fresh.lidar_age_ms = 0;

        let a = evaluate(&stale, 0, &IntrusionParams::default());
        let b = evaluate(&fresh, 0, &IntrusionParams::default());

        prop_assert!(b.verdict <= a.verdict);
    }
}
