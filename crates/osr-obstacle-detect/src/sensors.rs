//! Sensor-frame types — one snapshot in time across the full
//! suite, which [`crate::evaluate`] consumes.

use serde::{Deserialize, Serialize};

use crate::verdict::ObstacleClass;

/// Number of ultrasonic transducers on the nose sensor cowl.
///
/// Four transducers arranged in a quadrant (upper-left, upper-right,
/// lower-left, lower-right) with overlapping cones cover the
/// platform-gap + track envelope at close range.
pub const ULTRASONIC_CHANNELS: usize = 4;

/// Maximum age of any safety-primary sensor reading before its frame
/// is treated as stale.
///
/// At 20 Hz nominal update rate the inter-frame gap is 50 ms. Two
/// missed frames (100 ms) is the fail-restrictive threshold — past
/// this the evaluator assumes the sensor has failed and emits
/// `EmergencyBrake` (O2).
pub const MAX_SENSOR_STALE_MS: u32 = 100;

/// One ultrasonic transducer's most-recent echo.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct UltrasonicChannel {
    /// Distance to nearest echo, in millimetres. `None` means "no
    /// return at all this tick" (beyond range, or the transducer
    /// itself has faulted — the evaluator treats both the same).
    pub nearest_mm: Option<u32>,

    /// Monotonic age of this reading in milliseconds since acquisition.
    pub age_ms: u32,

    /// Hardware self-test status. `false` → treat the channel as
    /// failed, contributes to the O2 stale-data path.
    pub healthy: bool,
}

/// A single LIDAR return in the forward envelope.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct LidarDetection {
    /// Forward range to the detection, in millimetres.
    pub range_mm: u32,
    /// Lateral offset from the rail centreline, signed millimetres.
    /// Positive = right of centre, negative = left.
    pub lateral_mm: i32,
    /// Relative intensity of the return (0..=255). Used only by the
    /// classifier; the safety path relies on presence alone.
    pub intensity: u8,
}

/// A single mmWave-radar return in the forward envelope.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct RadarDetection {
    /// Forward range to the detection, in millimetres.
    pub range_mm: u32,
    /// Lateral offset from the rail centreline, signed millimetres.
    pub lateral_mm: i32,
    /// Radial velocity (positive = approaching), in mm/s. The radar
    /// channel can disambiguate a stationary fixed object from an
    /// approaching hazard via Doppler.
    pub radial_speed_mmps: i32,
}

/// A classifier output from the stereo camera pair.
///
/// The classifier is *not* in the safety-primary path. It informs
/// verdict severity: a `Human` classification escalates to
/// `EmergencyBrake` even if the LIDAR/radar return alone might
/// otherwise support `CrawlOnly`.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct CameraDetection {
    /// Forward range to the classifier's bounding box, in mm.
    pub range_mm: u32,
    /// What the classifier believes the obstacle is.
    pub class: ObstacleClass,
    /// Classifier confidence 0..=255. Values below
    /// [`CAMERA_CONFIDENCE_THRESHOLD`] are treated as `Unknown`.
    pub confidence: u8,
}

/// Minimum classifier confidence required before the camera class is
/// trusted by the severity-escalation logic.
pub const CAMERA_CONFIDENCE_THRESHOLD: u8 = 160;

/// Fixed-size sensor frame — one tick of data from every sensor on
/// the active nose. Kept fixed-size so the evaluator allocates
/// nothing.
///
/// Up to four detections per mid-range sensor is sufficient for the
/// forward envelope; more than four obstacles in a mainline rail
/// ROW is itself a stop-for-inspection case (covered by the
/// fail-restrictive disagreement path in O3).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct SensorFrame {
    /// Ultrasonic channels in fixed quadrant order: UL, UR, LL, LR.
    pub ultrasonic: [UltrasonicChannel; ULTRASONIC_CHANNELS],

    /// Up to four LIDAR detections in the forward envelope.
    /// `lidar_count` gates the used entries.
    pub lidar: [Option<LidarDetection>; 4],

    /// Age of the LIDAR frame itself. `lidar_offline == true` signals
    /// the sensor is known-bad (e.g., dust-storm degradation).
    pub lidar_age_ms: u32,
    pub lidar_offline: bool,

    /// Up to four radar detections.
    pub radar: [Option<RadarDetection>; 4],

    /// Age of the radar frame. `radar_offline` same semantics as
    /// LIDAR.
    pub radar_age_ms: u32,
    pub radar_offline: bool,

    /// Optional classifier output from the stereo camera.
    pub camera: Option<CameraDetection>,
    pub camera_age_ms: u32,
}

impl SensorFrame {
    /// Construct a frame with all channels healthy + reporting no
    /// detections. Used as the neutral starting point for tests.
    pub fn clear() -> Self {
        let chan = UltrasonicChannel {
            nearest_mm: None,
            age_ms: 0,
            healthy: true,
        };
        SensorFrame {
            ultrasonic: [chan; ULTRASONIC_CHANNELS],
            lidar: [None; 4],
            lidar_age_ms: 0,
            lidar_offline: false,
            radar: [None; 4],
            radar_age_ms: 0,
            radar_offline: false,
            camera: None,
            camera_age_ms: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn clear_frame_has_no_detections() {
        let f = SensorFrame::clear();
        for ch in &f.ultrasonic {
            assert!(ch.healthy);
            assert!(ch.nearest_mm.is_none());
        }
        assert!(f.lidar.iter().all(|x| x.is_none()));
        assert!(f.radar.iter().all(|x| x.is_none()));
        assert!(f.camera.is_none());
    }
}
