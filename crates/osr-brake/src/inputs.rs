//! Brake controller inputs: the union of signals arriving on the
//! [O4 brake-apply topic](../../../docs/rfcs/0005-sbc-software-architecture.md#6-interface-contracts),
//! the measured train state, regen availability, and the fixed
//! calibration parameters.

use osr_atp::BrakeCommand;
use serde::{Deserialize, Serialize};

/// One snapshot of everything the brake controller needs to decide.
///
/// Every field except `atp_command`, `measured_speed_mmps`,
/// `wheel_speed_mmps`, and `now_ns` is an event-driven flag that the
/// caller (the brake ECU task) latches from the TCN-E bus.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BrakeInputs {
    /// The ATP's most recent brake command. Under nominal operation
    /// this carries `Release` or `Service(_)`; `Emergency` from ATP
    /// is one of several sources that can trigger a full brake.
    pub atp_command: BrakeCommand,

    /// Emergency triggers from the other SIL-4 monitors. Each bool is
    /// latched `true` by the owning crate when its trip condition is
    /// active; the brake takes the union.
    pub vigilance_emergency: bool,
    pub fire_emergency: bool,
    pub derailment_emergency: bool,
    /// Driver's cab emergency-brake plunger (GoA 2 legacy) OR the
    /// passenger-intercom-triggered emergency via OCC remote-assist
    /// (GoA 4, RFC 0015 §5.3). Hardwired path; safety-rated.
    pub driver_emergency: bool,
    /// Obstacle-detection emergency from `osr-obstacle-detect` —
    /// `ObstacleVerdict::EmergencyBrake` from the T-OBS 2oo2 stage.
    /// In GoA 4 operation this is the primary new emergency source
    /// that replaces the driver's-eye detection (RFC 0015 §5.1).
    pub obstacle_emergency: bool,

    /// Parking-brake request from the driver's console or the depot
    /// dispatch system.
    pub park_requested: bool,

    /// Fused reference speed from [`osr_odometry`], mm/s.
    pub measured_speed_mmps: i32,
    /// Raw wheel-tachometer speed, mm/s. Under nominal wheel-rail
    /// contact this equals `measured_speed_mmps` within sensor noise.
    /// A persistent deficit is a wheel-slide condition; a persistent
    /// surplus is a wheel-slip.
    pub wheel_speed_mmps: i32,

    /// Current regen-torque budget the traction converter is willing
    /// to accept, 0..=1000 ppt of the train's total brake capability.
    /// Typically falls to 0 when the battery is at high SoC or when
    /// no regen-capable receiver (onboard pack / trackside storage)
    /// is available.
    pub regen_available_ppt: u16,

    pub now_ns: u64,
}

impl BrakeInputs {
    /// Are any of the emergency sources asserted?
    #[must_use]
    pub fn any_emergency(&self) -> bool {
        matches!(self.atp_command, BrakeCommand::Emergency)
            || self.vigilance_emergency
            || self.fire_emergency
            || self.derailment_emergency
            || self.driver_emergency
            || self.obstacle_emergency
    }
}

/// Fixed calibration of the brake controller.
///
/// Held constant across ticks; loaded at boot from a depot-provisioned
/// configuration blob.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BrakeParams {
    /// Enable wheel-slide-protection modulation. Disabled only in
    /// special maintenance modes; always on in revenue service.
    pub wsp_enabled: bool,
    /// Slide detection threshold: if
    /// `measured_speed - wheel_speed >= wsp_slide_threshold_mmps`
    /// WSP is active.
    pub wsp_slide_threshold_mmps: i32,
    /// Friction-effort reduction applied when WSP is active,
    /// expressed as ppt of the commanded effort to *remove*. E.g.,
    /// `400` removes 40 % of the commanded friction, letting the
    /// wheel spin up before re-applying.
    pub wsp_reduction_ppt: u16,

    /// Maximum speed at which the parking brake may be engaged, mm/s.
    /// Typical 200 mm/s (0.2 m/s, effectively rest).
    pub park_brake_max_speed_mmps: i32,

    /// If `true`, the service brake blends regen first and falls back
    /// to friction for the shortfall. Disable to route service brake
    /// through friction only (used during regen-forbidden modes).
    pub regen_priority: bool,

    /// Minimum friction effort commanded during emergency, ppt.
    /// Must be ≥ 1000 under revenue operation (full emergency
    /// application). Lowered only for bench testing with explicit
    /// risk acceptance.
    pub min_friction_emergency_ppt: u16,
}

impl BrakeParams {
    /// Reasonable defaults for a light-metro trainset.
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            wsp_enabled: true,
            wsp_slide_threshold_mmps: 500, // 0.5 m/s wheel deficit
            wsp_reduction_ppt: 400,        // reduce commanded friction by 40 %
            park_brake_max_speed_mmps: 200,
            regen_priority: true,
            min_friction_emergency_ppt: 1_000,
        }
    }
}
