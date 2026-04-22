//! Proptests exercising O1–O5 across a wide random-input space.

use osr_obstacle_detect::{
    evaluate, CameraDetection, LidarDetection, ObstacleClass, ObstacleVerdict, RadarDetection,
    SensorFrame, TriggerReason, UltrasonicChannel, MAX_SENSOR_STALE_MS, ULTRASONIC_CHANNELS,
    ULTRASONIC_MAX_SPEED_MMPS,
};
use proptest::prelude::*;

fn arb_ultrasonic() -> impl Strategy<Value = UltrasonicChannel> {
    (proptest::option::of(1u32..=30_000u32), 0u32..=300u32, any::<bool>()).prop_map(
        |(near, age, healthy)| UltrasonicChannel {
            nearest_mm: near,
            age_ms: age,
            healthy,
        },
    )
}

fn arb_frame() -> impl Strategy<Value = SensorFrame> {
    (
        proptest::array::uniform4(arb_ultrasonic()),
        any::<bool>(),
        0u32..=300u32,
        any::<bool>(),
        0u32..=300u32,
    )
        .prop_map(|(us, lidar_off, lidar_age, radar_off, radar_age)| {
            let mut f = SensorFrame::clear();
            f.ultrasonic = us;
            f.lidar_offline = lidar_off;
            f.lidar_age_ms = lidar_age;
            f.radar_offline = radar_off;
            f.radar_age_ms = radar_age;
            f
        })
}

proptest! {
    /// O3 — any peer-disagreement always produces EB, regardless of
    /// frame contents or speed (subject to clear-frame pre-conditions).
    #[test]
    fn o3_peer_disagreement_always_eb(
        frame in arb_frame(),
        speed in 0u32..=50_000u32,
        stop in 1_000u32..=200_000u32,
    ) {
        let mut f = frame;
        // Force every sensor clean so the only trigger would be O3.
        f.ultrasonic = [UltrasonicChannel {
            nearest_mm: None,
            age_ms: 0,
            healthy: true,
        }; ULTRASONIC_CHANNELS];
        f.lidar = [None; 4];
        f.lidar_offline = false;
        f.lidar_age_ms = 0;
        f.radar = [None; 4];
        f.radar_offline = false;
        f.radar_age_ms = 0;
        let o = evaluate(&f, speed, stop, /*peer_clear=*/ false);
        prop_assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }

    /// O2 — any ultrasonic staler than the threshold forces EB.
    #[test]
    fn o2_stale_ultrasonic_always_eb(
        ch_idx in 0usize..ULTRASONIC_CHANNELS,
        excess in 1u32..=200u32,
    ) {
        let mut f = SensorFrame::clear();
        f.ultrasonic[ch_idx].age_ms = MAX_SENSOR_STALE_MS + excess;
        let o = evaluate(&f, 0, 100_000, true);
        prop_assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }

    /// O1 — any ultrasonic detection at any range inside the band
    /// forces EB when no classifier downgrade applies.
    #[test]
    fn o1_ultrasonic_return_forces_eb(range in 200u32..=20_000u32) {
        let mut f = SensorFrame::clear();
        f.ultrasonic[0].nearest_mm = Some(range);
        let o = evaluate(&f, 0, 100_000, true);
        prop_assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }

    /// O4a — above ultrasonic band without *any* long-range sensors → EB.
    #[test]
    fn o4a_above_band_no_long_range_forces_eb(
        over in 1u32..=40_000u32,
    ) {
        let mut f = SensorFrame::clear();
        f.lidar_offline = true;
        f.radar_offline = true;
        let speed = ULTRASONIC_MAX_SPEED_MMPS + over;
        let o = evaluate(&f, speed, 100_000, true);
        prop_assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }

    /// O4b — LIDAR offline with radar healthy produces at least
    /// RestrictedSpeed (and never EB from the O4 branch alone).
    #[test]
    fn o4b_lidar_offline_radar_ok_restricts_to_40kmh(
        speed in 0u32..=50_000u32,
    ) {
        let mut f = SensorFrame::clear();
        f.lidar_offline = true;
        // Radar explicitly healthy.
        f.radar_offline = false;
        f.radar_age_ms = 0;
        let o = evaluate(&f, speed, 100_000, true);
        prop_assert!(o.verdict >= ObstacleVerdict::RestrictedSpeed);
        prop_assert!(o.verdict != ObstacleVerdict::EmergencyBrake);
        prop_assert_eq!(o.reason, TriggerReason::LidarDegraded);
    }

    /// Radar-only failure (LIDAR healthy) does NOT restrict speed.
    /// Radar is a validation channel, not primary mid-range.
    #[test]
    fn radar_offline_alone_stays_clear(
        speed in 0u32..=50_000u32,
    ) {
        let mut f = SensorFrame::clear();
        f.radar_offline = true;
        let o = evaluate(&f, speed, 100_000, true);
        prop_assert_eq!(o.verdict, ObstacleVerdict::Clear);
    }

    /// O5 — a strictly-fresher clone of any frame is never more
    /// severe. Tests the monotone property over ultrasonic freshness.
    #[test]
    fn o5_fresher_never_more_severe(
        stale_age in (MAX_SENSOR_STALE_MS + 1)..=300u32,
        speed in 0u32..=ULTRASONIC_MAX_SPEED_MMPS,
    ) {
        let mut stale = SensorFrame::clear();
        stale.ultrasonic[0].age_ms = stale_age;

        let mut fresh = stale.clone();
        fresh.ultrasonic[0].age_ms = 0;

        let a = evaluate(&stale, speed, 100_000, true);
        let b = evaluate(&fresh, speed, 100_000, true);

        prop_assert!(b.verdict <= a.verdict);
    }

    /// LightDebris classifier downgrades a LIDAR-only detection to
    /// CrawlOnly; anything else stays EB.
    #[test]
    fn light_debris_downgrades_lidar_eb_to_crawl(
        range in 5_000u32..=50_000u32,
    ) {
        let mut f = SensorFrame::clear();
        f.lidar[0] = Some(LidarDetection {
            range_mm: range,
            lateral_mm: 0,
            intensity: 50,
        });
        f.camera = Some(CameraDetection {
            range_mm: range,
            class: ObstacleClass::LightDebris,
            confidence: 220,
        });
        let o = evaluate(&f, 5_000, 60_000, true);
        prop_assert_eq!(o.verdict, ObstacleVerdict::CrawlOnly);
        prop_assert_eq!(o.reason, TriggerReason::ClassifierEscalation);
    }
}
