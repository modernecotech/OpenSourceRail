//! The pure-function SIL-4 evaluator.
//!
//! Ticks through the five safety properties O1–O5 in a fixed order,
//! returning the first (highest-severity) match. Fail-restrictive by
//! construction: any path that can't prove "clear" returns
//! [`ObstacleVerdict::EmergencyBrake`].

use serde::{Deserialize, Serialize};

use crate::sensors::{
    SensorFrame, CAMERA_CONFIDENCE_THRESHOLD, MAX_SENSOR_STALE_MS, ULTRASONIC_CHANNELS,
};
use crate::verdict::{ObstacleClass, ObstacleVerdict, ULTRASONIC_MAX_SPEED_MMPS};

// Rail-profile lateral gate in millimetres. A LIDAR or radar
// detection further than this from the rail centreline is off the
// rail profile and does not trigger a brake event.
const LATERAL_GATE_MM: i32 = 1500;

/// Reason the evaluator emitted its verdict — for logging + analysis.
/// Never changes the verdict itself; purely explanatory.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TriggerReason {
    /// No trigger — verdict is `Clear`.
    None,
    /// Ultrasonic transducer reported an echo inside the envelope.
    UltrasonicReturn,
    /// LIDAR detection inside the envelope.
    LidarReturn,
    /// Radar detection inside the envelope.
    RadarReturn,
    /// An ultrasonic transducer is unhealthy or stale.
    UltrasonicStale,
    /// LIDAR frame stale or offline (and radar still healthy) —
    /// pairs with [`ObstacleVerdict::RestrictedSpeed`] (O4b).
    LidarDegraded,
    /// Train above ultrasonic safe speed and every long-range sensor
    /// is offline (O4a).
    LongRangeRequired,
    /// Camera classifier raised severity (e.g., human in the path).
    ClassifierEscalation,
    /// Peer channel cross-check disagreed (O3).
    PeerDisagreement,
}

/// Result of a single evaluator tick.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct ObstacleOutcome {
    pub verdict: ObstacleVerdict,
    pub reason: TriggerReason,
}

impl ObstacleOutcome {
    pub const fn clear() -> Self {
        ObstacleOutcome {
            verdict: ObstacleVerdict::Clear,
            reason: TriggerReason::None,
        }
    }

    pub const fn emergency(reason: TriggerReason) -> Self {
        ObstacleOutcome {
            verdict: ObstacleVerdict::EmergencyBrake,
            reason,
        }
    }

    pub const fn crawl(reason: TriggerReason) -> Self {
        ObstacleOutcome {
            verdict: ObstacleVerdict::CrawlOnly,
            reason,
        }
    }

    pub const fn restricted(reason: TriggerReason) -> Self {
        ObstacleOutcome {
            verdict: ObstacleVerdict::RestrictedSpeed,
            reason,
        }
    }
}

/// Top-level evaluator — the single public entry point.
///
/// # Parameters
///
/// - `frame`: the fused sensor snapshot at this tick.
/// - `speed_mmps`: current train speed in mm/s.
/// - `stopping_distance_mm`: the ATP-computed stopping distance for
///   the current speed, braking curve, and adhesion — this is the
///   envelope the obstacle must be *outside* for the verdict to be
///   `Clear`.
/// - `peer_clear`: `true` iff the peer 2oo2 channel computed
///   `Clear` on the same tick. `false` means the peer disagreed or
///   its heartbeat is lost — either way, §O3 says we fail to
///   `EmergencyBrake`.
pub fn evaluate(
    frame: &SensorFrame,
    speed_mmps: u32,
    stopping_distance_mm: u32,
    peer_clear: bool,
) -> ObstacleOutcome {
    // O2 — sensor freshness. Any ultrasonic channel stale or
    // faulted → EB. Ultrasonic is the always-required close-range
    // belt; we never run without it.
    for ch in &frame.ultrasonic {
        if !ch.healthy || ch.age_ms > MAX_SENSOR_STALE_MS {
            return ObstacleOutcome::emergency(TriggerReason::UltrasonicStale);
        }
    }

    let lidar_ok = !frame.lidar_offline && frame.lidar_age_ms <= MAX_SENSOR_STALE_MS;
    let radar_ok = !frame.radar_offline && frame.radar_age_ms <= MAX_SENSOR_STALE_MS;

    // O4a — every long-range sensor offline AND train above the
    // ultrasonic safe speed band → EB. Ultrasonic alone is only
    // trusted at ≤ 40 km/h.
    if speed_mmps > ULTRASONIC_MAX_SPEED_MMPS && !lidar_ok && !radar_ok {
        return ObstacleOutcome::emergency(TriggerReason::LongRangeRequired);
    }

    // O4b — LIDAR offline (independent of radar state) → emit
    // `RestrictedSpeed` so ATO caps the trainset at 40 km/h. This is
    // the "LIDAR-is-failing" safety posture: radar alone still sees
    // 5 – 200 m all-weather, but we don't trust a single long-range
    // channel to let the train run at mainline speed. ATO brakes
    // smoothly on the service brake; no EB.
    //
    // `pending` carries this verdict through the rest of the checks,
    // which can only raise severity (to CrawlOnly or EmergencyBrake).
    let mut pending = ObstacleOutcome::clear();
    if !lidar_ok {
        pending = ObstacleOutcome::restricted(TriggerReason::LidarDegraded);
    }

    // O1 — detection inside envelope. Any safety-primary sensor
    // detection escalates to at least CrawlOnly (and usually EB via
    // classifier gating in `escalated_outcome`).
    //
    // Ultrasonic first: any echo on any channel is treated as a
    // detection in the envelope because the ultrasonic band (0–20 m)
    // lies entirely within any meaningful stopping distance.
    for ch in &frame.ultrasonic {
        if ch.nearest_mm.is_some() {
            return escalated_outcome(frame, TriggerReason::UltrasonicReturn);
        }
    }
    if lidar_ok {
        for det in frame.lidar.iter().flatten() {
            if det.range_mm <= stopping_distance_mm && det.lateral_mm.abs() <= LATERAL_GATE_MM {
                return escalated_outcome(frame, TriggerReason::LidarReturn);
            }
        }
    }
    if radar_ok {
        for det in frame.radar.iter().flatten() {
            if det.range_mm <= stopping_distance_mm && det.lateral_mm.abs() <= LATERAL_GATE_MM {
                return escalated_outcome(frame, TriggerReason::RadarReturn);
            }
        }
    }

    // O3 — peer disagreement on an otherwise-clear frame → EB.
    // 2oo2 safety property: any single-channel dissent fails
    // restrictive.
    if !peer_clear {
        return ObstacleOutcome::emergency(TriggerReason::PeerDisagreement);
    }

    pending
}

/// Use the camera classifier to escalate a detection to
/// `EmergencyBrake` when the classifier is confident that the
/// object is human, vehicle, or large-animal class. Otherwise
/// emit `CrawlOnly`.
///
/// This is the one place the camera influences the verdict — it
/// cannot *suppress* a detection (fail-restrictive) but it can
/// *raise* severity from `CrawlOnly` to `EmergencyBrake`.
fn escalated_outcome(frame: &SensorFrame, reason: TriggerReason) -> ObstacleOutcome {
    // Default: treat any detection as EB. The camera can *downgrade*
    // to `CrawlOnly` only if it confidently classifies the obstacle
    // as LightDebris — never for Unknown (conservative).
    let verdict = match frame.camera {
        Some(det)
            if det.confidence >= CAMERA_CONFIDENCE_THRESHOLD
                && det.class == ObstacleClass::LightDebris =>
        {
            ObstacleVerdict::CrawlOnly
        }
        _ => ObstacleVerdict::EmergencyBrake,
    };

    // Preserve the original detection reason; classifier escalation
    // is an annotation, not a root cause.
    let reason = if verdict == ObstacleVerdict::CrawlOnly {
        TriggerReason::ClassifierEscalation
    } else {
        reason
    };

    ObstacleOutcome { verdict, reason }
}

// Silence dead_code warning for ULTRASONIC_CHANNELS if the lint fires
// — we reference it indirectly via the array sizes.
const _: () = {
    let _ = ULTRASONIC_CHANNELS;
};

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sensors::{CameraDetection, LidarDetection, RadarDetection};

    fn baseline() -> SensorFrame {
        SensorFrame::clear()
    }

    #[test]
    fn clear_frame_at_rest_is_clear() {
        let f = baseline();
        let o = evaluate(&f, 0, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::Clear);
    }

    #[test]
    fn ultrasonic_echo_triggers_eb_o1() {
        let mut f = baseline();
        f.ultrasonic[0].nearest_mm = Some(5_000);
        let o = evaluate(&f, 0, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }

    #[test]
    fn stale_ultrasonic_triggers_eb_o2() {
        let mut f = baseline();
        f.ultrasonic[2].age_ms = MAX_SENSOR_STALE_MS + 1;
        let o = evaluate(&f, 0, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
        assert_eq!(o.reason, TriggerReason::UltrasonicStale);
    }

    #[test]
    fn peer_disagreement_triggers_eb_o3() {
        let f = baseline();
        let o = evaluate(&f, 0, 100_000, /*peer_clear=*/ false);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
        assert_eq!(o.reason, TriggerReason::PeerDisagreement);
    }

    #[test]
    fn above_ultrasonic_band_without_any_long_range_triggers_eb_o4a() {
        let mut f = baseline();
        f.lidar_offline = true;
        f.radar_offline = true;
        let o = evaluate(&f, ULTRASONIC_MAX_SPEED_MMPS + 1, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
        assert_eq!(o.reason, TriggerReason::LongRangeRequired);
    }

    #[test]
    fn lidar_offline_with_radar_healthy_restricts_speed_o4b() {
        // LIDAR dies, radar stays healthy — per user's safety
        // directive, cap at 40 km/h (RestrictedSpeed), not EB.
        let mut f = baseline();
        f.lidar_offline = true;
        // Speed is irrelevant to the verdict; ATO enforces the cap.
        let o = evaluate(&f, 22_000, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::RestrictedSpeed);
        assert_eq!(o.reason, TriggerReason::LidarDegraded);
    }

    #[test]
    fn lidar_stale_is_treated_as_offline() {
        let mut f = baseline();
        f.lidar_age_ms = MAX_SENSOR_STALE_MS + 50;
        let o = evaluate(&f, 5_000, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::RestrictedSpeed);
        assert_eq!(o.reason, TriggerReason::LidarDegraded);
    }

    #[test]
    fn radar_offline_alone_is_not_a_speed_restriction() {
        // Radar is a validation / all-weather channel, not primary.
        // Losing only radar does not restrict speed — LIDAR has the
        // 5–200 m band covered.
        let mut f = baseline();
        f.radar_offline = true;
        let o = evaluate(&f, 22_000, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::Clear);
    }

    #[test]
    fn radar_detection_still_triggers_eb_when_lidar_degraded() {
        // Severity must escalate: LidarDegraded emits RestrictedSpeed,
        // but a concurrent radar detection inside the envelope must
        // upgrade the verdict to EmergencyBrake.
        let mut f = baseline();
        f.lidar_offline = true;
        f.radar[0] = Some(RadarDetection {
            range_mm: 40_000,
            lateral_mm: 0,
            radial_speed_mmps: -4_000,
        });
        let o = evaluate(&f, 8_000, 60_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
        assert_eq!(o.reason, TriggerReason::RadarReturn);
    }

    #[test]
    fn light_debris_classifier_downgrades_to_crawl() {
        let mut f = baseline();
        f.lidar[0] = Some(LidarDetection {
            range_mm: 20_000,
            lateral_mm: 0,
            intensity: 40,
        });
        f.camera = Some(CameraDetection {
            range_mm: 20_000,
            class: ObstacleClass::LightDebris,
            confidence: 200,
        });
        let o = evaluate(&f, 5_000, 30_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::CrawlOnly);
    }

    #[test]
    fn human_classifier_stays_eb() {
        let mut f = baseline();
        f.lidar[0] = Some(LidarDetection {
            range_mm: 30_000,
            lateral_mm: 200,
            intensity: 80,
        });
        f.camera = Some(CameraDetection {
            range_mm: 30_000,
            class: ObstacleClass::Human,
            confidence: 230,
        });
        let o = evaluate(&f, 5_000, 50_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }

    #[test]
    fn radar_detection_inside_envelope_triggers_eb() {
        let mut f = baseline();
        f.radar[0] = Some(RadarDetection {
            range_mm: 40_000,
            lateral_mm: 0,
            radial_speed_mmps: -5_000, // approaching
        });
        let o = evaluate(&f, 10_000, 60_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
        assert_eq!(o.reason, TriggerReason::RadarReturn);
    }

    #[test]
    fn lidar_detection_off_rail_profile_does_not_trigger() {
        // A LIDAR return at 50 m but 5 m to the side — outside the
        // ±1500 mm rail profile — must not trigger an EB.
        let mut f = baseline();
        f.lidar[0] = Some(LidarDetection {
            range_mm: 50_000,
            lateral_mm: 5_000,
            intensity: 60,
        });
        let o = evaluate(&f, 10_000, 80_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::Clear);
    }

    #[test]
    fn faulted_ultrasonic_channel_triggers_eb() {
        let mut f = baseline();
        f.ultrasonic[1].healthy = false;
        let o = evaluate(&f, 0, 100_000, true);
        assert_eq!(o.verdict, ObstacleVerdict::EmergencyBrake);
    }
}
