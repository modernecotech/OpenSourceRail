//! Inputs and static parameters.

use serde::{Deserialize, Serialize};

/// Per-tick ATO inputs.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AtoInputs {
    pub now_ns: u64,
    /// Elapsed since previous evaluator call, nanoseconds.
    pub dt_ns: u64,

    /// Fused reference speed from `osr-odometry`, mm/s signed.
    pub current_speed_mmps: i32,
    /// Envelope speed from `osr-atp` — max safe instantaneous speed.
    /// mm/s, ≥ 0.
    pub envelope_mmps: i32,
    /// Schedule-derived cruise speed for the current section. mm/s.
    pub cruise_target_mmps: i32,

    /// Distance in millimetres to the next stop point (platform edge).
    /// `None` when no stop is in range of the ATO's station-approach
    /// profile (typically > ~500 m ahead).
    pub distance_to_stop_mm: Option<i64>,
    /// True when the train is at a platform and the vehicle
    /// controller wants a stopped state.
    pub at_station: bool,
    /// Remaining dwell time in milliseconds. Zero when not dwelling.
    /// Only consulted when `at_station && speed ≈ 0`.
    pub dwell_remaining_ms: u32,

    /// Driver's AUTO/MANUAL switch. When `false`, ATO commands zero.
    pub ato_engaged: bool,
}

/// Static ATO parameters, loaded at commissioning.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AtoParams {
    // --- PI controller -------------------------------------------------
    /// Proportional gain: mN·m per mm/s of speed error.
    pub kp_mnm_per_mmps: i32,
    /// Integral gain: mN·m per (mm/s · s) of accumulated error.
    /// Applied once per tick (scaled by `dt_ns`).
    pub ki_mnm_per_mmps_s: i32,
    /// Integrator anti-windup clamp (absolute value), mN·m.
    pub max_integral_mnm: i32,
    /// Deadband below which the integrator freezes, mm/s.
    pub cruise_deadband_mmps: i32,

    // --- Torque / brake mapping ---------------------------------------
    /// Maximum traction torque (mN·m).
    pub max_torque_mnm: i32,
    /// Maximum service-brake effort (ppt). Usually 1000.
    pub max_service_brake_ppt: u16,
    /// The "full brake" demand in the same units as PI output, i.e.
    /// the magnitude of negative PI output that maps to
    /// `max_service_brake_ppt`. Larger = softer brake response.
    pub full_brake_demand_mnm: i32,
    /// Coasting band: if |PI output| is below this and negative,
    /// apply neither torque nor brake. mN·m.
    pub coast_band_mnm: i32,

    // --- Station approach ---------------------------------------------
    /// Target deceleration for the station-approach profile.
    /// mm/s². A 1.0 m/s² value = 1000 mm/s².
    pub station_approach_decel_mmps2: i32,
    /// Distance at which we consider the train "stopped at platform"
    /// for mode-reporting purposes. mm.
    pub station_stop_distance_mm: i64,
    /// Speed below which the train is considered stopped at a
    /// platform (entering Stopped / Dwelling). mm/s.
    pub stop_tolerance_mmps: i32,
    /// Holding brake effort when stopped at a platform, ppt.
    pub holding_brake_ppt: u16,

    // --- Envelope guard -----------------------------------------------
    /// Stay this far under the ATP envelope. mm/s.
    pub envelope_margin_mmps: i32,
}

impl AtoParams {
    /// Sensible defaults for a light-metro trainset.
    ///
    /// At 22 m/s (≈80 km/h) a 1 m/s speed error → ~3000 mN·m command
    /// torque. Service accel ≈ 1 m/s² requires ≈ 2400 N of tractive
    /// force against ~200 t mass, or ≈ 480 N·m at the wheel — the
    /// gains below are pack-aggregate values tuned for the 3-car
    /// reference consist (RFC 0003 §4.3).
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            kp_mnm_per_mmps: 3_000,
            ki_mnm_per_mmps_s: 100,
            max_integral_mnm: 4_000_000,
            cruise_deadband_mmps: 200,
            max_torque_mnm: 10_000_000,
            max_service_brake_ppt: 1_000,
            full_brake_demand_mnm: 8_000_000,
            coast_band_mnm: 500_000,
            station_approach_decel_mmps2: 900, // 0.9 m/s² comfort decel
            station_stop_distance_mm: 300,      // 30 cm
            stop_tolerance_mmps: 100,            // 0.1 m/s
            holding_brake_ppt: 500,
            envelope_margin_mmps: 500,           // 0.5 m/s guard band
        }
    }
}
