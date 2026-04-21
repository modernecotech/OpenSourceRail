//! Inputs and fixed parameters.

use serde::{Deserialize, Serialize};

/// Per-tick traction supervisor inputs.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TractionInputs {
    pub now_ns: u64,

    // --- Command ------------------------------------------------------
    /// Commanded torque in millinewton-metres, signed.
    /// Positive = motoring (traction), negative = regenerative braking.
    /// Sourced from `osr-ato` (tractive) or `osr-brake` (regen).
    pub torque_setpoint_mnm: i32,
    /// Explicit enable / disable request from the vehicle controller.
    pub enable_requested: bool,

    // --- BMS state ---------------------------------------------------
    pub bms_contactor_closed: bool,
    /// BMS-reported maximum discharge current, milliamps.
    /// Positive magnitude, i.e. the "current sink" side.
    pub bms_discharge_limit_ma: u32,
    /// BMS-reported maximum charge current for regen acceptance, mA.
    pub bms_charge_limit_ma: u32,
    /// Pack terminal voltage, mV. Used for efficiency → current
    /// back-computation.
    pub pack_voltage_mv: u32,

    // --- Wheel / body speed ------------------------------------------
    /// Train body reference speed (from `osr-odometry`), mm/s signed.
    pub reference_speed_mmps: i32,
    /// Driven wheel tangential speed, mm/s signed.
    pub wheel_speed_mmps: i32,

    // --- Drive health ------------------------------------------------
    pub inverter_over_temp: bool,
    pub inverter_drive_fault: bool,
}

/// Fixed traction-supervisor parameters, loaded at commissioning.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TractionParams {
    /// Maximum rated motor torque, mN·m (absolute value; applies to
    /// both motoring and braking directions).
    pub max_torque_mnm: u32,
    /// Motor torque constant, micro-newton-metres per milliamp.
    /// e.g., 2_000 µN·m/mA → a 1 A current produces 2 mN·m.
    /// (Using micro scaling to keep integer precision at realistic
    /// torque constants of ~1–3 N·m/A.)
    pub torque_constant_unmpma: u32,
    /// Drive + motor efficiency in parts-per-thousand. 950 = 95 %.
    pub efficiency_ppt: u16,

    // --- Slip / slide detection -------------------------------------
    /// Slip threshold in mm/s: if `wheel_speed - reference_speed`
    /// exceeds this while motoring, anti-slip engages.
    pub slip_threshold_mmps: i32,
    /// Fraction of torque retained under anti-slip, in ppt.
    /// 400 = retain 40 %. Must be ≤ 1000.
    pub anti_slip_retention_ppt: u16,
    /// Severe-slip threshold: if slip exceeds this,
    /// [`crate::FaultReason::SeverelySlipping`] is asserted.
    pub severe_slip_mmps: i32,

    /// Cooldown after any fault, milliseconds.
    pub fault_cooldown_ms: u32,
}

impl TractionParams {
    /// Sensible defaults for a light-metro 3-car traction set
    /// (per RFC 0003 reference consist).
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            max_torque_mnm: 12_000_000,       // 12 kN·m aggregate
            torque_constant_unmpma: 3_000,    // 3 N·m/A — light-metro-ish
            efficiency_ppt: 950,
            slip_threshold_mmps: 500,          // 0.5 m/s slip band
            anti_slip_retention_ppt: 400,
            severe_slip_mmps: 2_000,
            fault_cooldown_ms: 5_000,
        }
    }
}
