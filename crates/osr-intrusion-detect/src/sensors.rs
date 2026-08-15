//! Wayside sensor frame — one snapshot the evaluator consumes.

use serde::{Deserialize, Serialize};

/// Maximum age of any safety-primary sensor frame before it is
/// treated as stale and triggers `IntrusionVerdict::Unknown` (I2).
///
/// 200 ms — the wayside cycle is slower than the onboard T-OBS
/// (100 ms) because wayside is proactive and has less time
/// pressure, and because pole-mounted sensors on long poles have
/// longer comms paths back to the W-SBC.
pub const MAX_SENSOR_STALE_MS: u32 = 200;

/// Rail-profile lateral half-width: detections further than this
/// from the track centreline are off-profile and do not trigger
/// `Present` (same envelope as RFC 0015).
pub const LATERAL_GATE_MM: i32 = 1500;

/// One fence-line contact sensor state.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct FenceLineState {
    /// Contact-sensor alarm latched `true` on a breach (cut wire,
    /// vibration above threshold, climb detected). Latched; cleared
    /// by the wayside maintainer after inspection (M7).
    pub breach_latched: bool,
    /// Monotonic age of this reading, ms.
    pub age_ms: u32,
    /// Sensor hardware self-test; `false` → treat the fence-line
    /// channel as failed (still not Clear).
    pub healthy: bool,
}

/// One LIDAR return inside the section.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct LidarReturn {
    /// Longitudinal distance from the section's start marker, mm.
    pub longitudinal_mm: u32,
    /// Lateral offset from rail centreline, signed mm. Positive = right.
    pub lateral_mm: i32,
}

/// One radar return inside the section.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct RadarReturn {
    pub longitudinal_mm: u32,
    pub lateral_mm: i32,
    /// Radial velocity in mm/s; positive = approaching the nearest
    /// pole. Doppler filter can reject stationary non-threats.
    pub radial_speed_mmps: i32,
}

/// Camera classifier output.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct CameraReturn {
    pub class: CameraClass,
    /// 0..=255 classifier confidence. Anything below the params' floor
    /// is treated as `Unknown`.
    pub confidence: u8,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum CameraClass {
    Human,
    LargeAnimal,
    Vehicle,
    StaticDebris,
    Unknown,
}

/// Full wayside sensor snapshot for one section at one tick.
///
/// Fixed-size: up to 8 LIDAR poles + 4 radar poles + 1 camera per
/// section. A section longer than that is over the RFC 0001 section-
/// length limit and should be subdivided.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct WaysideSensorFrame {
    pub fence: FenceLineState,

    /// LIDAR returns aggregated across all poles in the section.
    /// `None` in a slot means "no return from that pole this tick".
    pub lidar: [Option<LidarReturn>; 8],
    pub lidar_age_ms: u32,
    pub lidar_offline: bool,

    pub radar: [Option<RadarReturn>; 4],
    pub radar_age_ms: u32,
    pub radar_offline: bool,

    pub camera: Option<CameraReturn>,
    pub camera_age_ms: u32,
}

impl WaysideSensorFrame {
    /// Construct a neutral frame: fence clean + healthy, all sensor
    /// frames fresh, zero detections. The baseline for tests.
    pub fn clear() -> Self {
        WaysideSensorFrame {
            fence: FenceLineState {
                breach_latched: false,
                age_ms: 0,
                healthy: true,
            },
            lidar: [None; 8],
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
    fn clear_frame_is_actually_clear() {
        let f = WaysideSensorFrame::clear();
        assert!(!f.fence.breach_latched);
        assert!(f.fence.healthy);
        assert!(f.lidar.iter().all(|x| x.is_none()));
        assert!(f.radar.iter().all(|x| x.is_none()));
        assert!(f.camera.is_none());
    }
}
