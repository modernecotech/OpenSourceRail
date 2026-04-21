//! Persistent state + output.

use serde::{Deserialize, Serialize};

use crate::types::AtoMode;

/// Persistent ATO state. Caller carries across ticks.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct AtoState {
    /// Accumulated integral term in the PI controller, mN·m · s.
    /// Clamped by `max_integral_mnm`.
    pub integral_mnm: i64,
    /// Mode of the previous tick — carried for reporting and
    /// hysteresis if needed. Current tick's mode is in the output.
    pub last_mode: AtoMode,
    /// Last tick's timestamp (ns). Currently only for diagnostics;
    /// `dt_ns` is supplied explicitly in the inputs.
    pub last_tick_ns: u64,
}

/// Per-tick output.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AtoOutput {
    pub state: AtoState,
    /// Torque setpoint for `osr-traction` (mN·m, signed).
    pub torque_setpoint_mnm: i32,
    /// Service-brake effort for `osr-brake` (ppt). Zero when torque
    /// is non-zero (AO2).
    pub service_brake_ppt: u16,
    /// Mode for diagnostics / DMI display.
    pub mode: AtoMode,
    /// Effective target speed tracked this tick, mm/s. Useful for
    /// understanding which constraint (cruise / station / envelope)
    /// is currently binding.
    pub effective_target_mmps: i32,
}
