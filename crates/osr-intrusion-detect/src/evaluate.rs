//! The pure-function SIL-4 intrusion evaluator.
//!
//! Ticks through I1..I5 in priority order and returns the highest-
//! severity verdict. Fail-restrictive: any path that cannot prove
//! `Clear` returns at least `Unknown`.

use serde::{Deserialize, Serialize};

use crate::sensors::{
    CameraClass, WaysideSensorFrame, LATERAL_GATE_MM, MAX_SENSOR_STALE_MS,
};
use crate::verdict::IntrusionVerdict;

/// Per-deployment tuning.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct IntrusionParams {
    /// Minimum camera confidence (0..=255) before the classifier
    /// opinion is trusted for severity escalation. Default 160
    /// matches RFC 0015's onboard threshold.
    pub camera_confidence_floor: u8,
}

impl Default for IntrusionParams {
    fn default() -> Self {
        IntrusionParams {
            camera_confidence_floor: 160,
        }
    }
}

/// Logging reason for the verdict — never changes the verdict itself.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TriggerReason {
    None,
    /// Fence-line alarm latched — I3.
    FenceBreach,
    /// LIDAR return inside the rail profile — I1.
    LidarReturn,
    /// Radar return inside the rail profile — I1.
    RadarReturn,
    /// Camera classifier — severity escalation with safety-primary
    /// corroboration.
    ClassifierEscalation,
    /// Fence-line sensor faulted or stale — I2.
    FenceStale,
    /// LIDAR offline / stale — I2.
    LidarStale,
    /// Radar offline / stale — I2.
    RadarStale,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct IntrusionOutcome {
    pub verdict: IntrusionVerdict,
    pub reason: TriggerReason,
}

impl IntrusionOutcome {
    pub const fn clear() -> Self {
        IntrusionOutcome {
            verdict: IntrusionVerdict::Clear,
            reason: TriggerReason::None,
        }
    }
    pub const fn unknown(reason: TriggerReason) -> Self {
        IntrusionOutcome {
            verdict: IntrusionVerdict::Unknown,
            reason,
        }
    }
    pub const fn present(reason: TriggerReason) -> Self {
        IntrusionOutcome {
            verdict: IntrusionVerdict::Present,
            reason,
        }
    }
}

/// Evaluate one tick of wayside sensor data.
///
/// The order of checks matches priority:
/// 1. Fence-line breach (I3) → `Present`.
/// 2. LIDAR in-profile (I1) → `Present`.
/// 3. Radar in-profile (I1) → `Present`.
/// 4. Any safety-primary sensor stale (I2) → `Unknown`.
/// 5. Otherwise → `Clear`.
///
/// Camera classifier (I4) can never produce `Clear` on its own;
/// it only modulates logging severity.
#[must_use]
pub fn evaluate(
    frame: &WaysideSensorFrame,
    _now_ns: u64,
    _params: &IntrusionParams,
) -> IntrusionOutcome {
    // I3 — fence-line breach is unconditional Present.
    if frame.fence.breach_latched {
        return IntrusionOutcome::present(TriggerReason::FenceBreach);
    }

    let lidar_ok = !frame.lidar_offline && frame.lidar_age_ms <= MAX_SENSOR_STALE_MS;
    let radar_ok = !frame.radar_offline && frame.radar_age_ms <= MAX_SENSOR_STALE_MS;

    // I1 — any LIDAR detection inside the rail profile → Present.
    if lidar_ok {
        for det in frame.lidar.iter().flatten() {
            if det.lateral_mm.abs() <= LATERAL_GATE_MM {
                return IntrusionOutcome::present(TriggerReason::LidarReturn);
            }
        }
    }
    // I1 — same check for radar.
    if radar_ok {
        for det in frame.radar.iter().flatten() {
            if det.lateral_mm.abs() <= LATERAL_GATE_MM {
                return IntrusionOutcome::present(TriggerReason::RadarReturn);
            }
        }
    }

    // I2 — freshness checks. Order matters: report the first stale
    // sensor for the log; the verdict is the same Unknown either way.
    if !frame.fence.healthy || frame.fence.age_ms > MAX_SENSOR_STALE_MS {
        return IntrusionOutcome::unknown(TriggerReason::FenceStale);
    }
    if !lidar_ok {
        return IntrusionOutcome::unknown(TriggerReason::LidarStale);
    }
    if !radar_ok {
        return IntrusionOutcome::unknown(TriggerReason::RadarStale);
    }

    // I4 — camera alone cannot emit Clear. If a camera reports a
    // high-confidence hazard class but no safety-primary hit has
    // fired above, we still demote to Unknown — camera classification
    // drives response but not the Clear verdict.
    //
    // This only matters when the classifier confidence is above the
    // floor *and* the class is a hazard (Human / LargeAnimal /
    // Vehicle). StaticDebris and Unknown don't escalate.
    if let Some(cam) = frame.camera {
        let hazard = matches!(
            cam.class,
            CameraClass::Human | CameraClass::LargeAnimal | CameraClass::Vehicle
        );
        let confident = cam.confidence >= _params.camera_confidence_floor;
        if hazard && confident {
            return IntrusionOutcome::unknown(TriggerReason::ClassifierEscalation);
        }
    }

    IntrusionOutcome::clear()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sensors::{CameraReturn, LidarReturn, RadarReturn};

    fn baseline() -> WaysideSensorFrame {
        WaysideSensorFrame::clear()
    }

    #[test]
    fn clean_frame_is_clear() {
        let f = baseline();
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Clear);
    }

    #[test]
    fn fence_breach_forces_present_i3() {
        let mut f = baseline();
        f.fence.breach_latched = true;
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Present);
        assert_eq!(o.reason, TriggerReason::FenceBreach);
    }

    #[test]
    fn lidar_in_profile_forces_present_i1() {
        let mut f = baseline();
        f.lidar[0] = Some(LidarReturn { longitudinal_mm: 12_000, lateral_mm: 500 });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Present);
        assert_eq!(o.reason, TriggerReason::LidarReturn);
    }

    #[test]
    fn lidar_off_profile_stays_clear() {
        let mut f = baseline();
        // Lateral 3000 mm > LATERAL_GATE_MM (1500).
        f.lidar[0] = Some(LidarReturn { longitudinal_mm: 12_000, lateral_mm: 3_000 });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Clear);
    }

    #[test]
    fn radar_in_profile_forces_present_i1() {
        let mut f = baseline();
        f.radar[0] = Some(RadarReturn {
            longitudinal_mm: 20_000,
            lateral_mm: -200,
            radial_speed_mmps: 0,
        });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Present);
        assert_eq!(o.reason, TriggerReason::RadarReturn);
    }

    #[test]
    fn stale_lidar_forces_unknown_i2() {
        let mut f = baseline();
        f.lidar_age_ms = MAX_SENSOR_STALE_MS + 10;
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Unknown);
        assert_eq!(o.reason, TriggerReason::LidarStale);
    }

    #[test]
    fn fence_offline_forces_unknown_i2() {
        let mut f = baseline();
        f.fence.healthy = false;
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Unknown);
        assert_eq!(o.reason, TriggerReason::FenceStale);
    }

    #[test]
    fn camera_alone_cannot_produce_clear_i4() {
        // All safety-primary sensors fresh + clean; camera reports a
        // confident human — we should demote to Unknown (I4), not Clear.
        let mut f = baseline();
        f.camera = Some(CameraReturn {
            class: CameraClass::Human,
            confidence: 230,
        });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Unknown);
    }

    #[test]
    fn camera_low_confidence_does_not_demote() {
        let mut f = baseline();
        f.camera = Some(CameraReturn {
            class: CameraClass::Human,
            confidence: 100, // below default floor of 160
        });
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Clear);
    }

    #[test]
    fn present_beats_unknown() {
        // Fence breached AND lidar stale — verdict is Present, not
        // Unknown: I3 takes priority.
        let mut f = baseline();
        f.fence.breach_latched = true;
        f.lidar_age_ms = MAX_SENSOR_STALE_MS + 50;
        let o = evaluate(&f, 0, &IntrusionParams::default());
        assert_eq!(o.verdict, IntrusionVerdict::Present);
    }
}
