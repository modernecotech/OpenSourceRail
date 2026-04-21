//! Small value types for the BMS.

use serde::{Deserialize, Serialize};

/// Cell chemistry. Used only to select appropriate default
/// [`crate::BmsParams`]; the evaluator itself is chemistry-agnostic.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Chemistry {
    /// Sodium-ion — reference chemistry for OpenSourceRail. Voltage
    /// window 2.0–3.9 V/cell, usable −20…+60 °C.
    SodiumIon,
    /// Lithium iron phosphate — alternative where energy density
    /// binds. Voltage window 2.5–3.65 V/cell, charge-restricted < 0 °C.
    Lfp,
}

/// Commanded / reported state of the main pack contactor.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum ContactorState {
    /// Contactor open by command (nominal standby).
    Open,
    /// Contactor closed; pack electrically connected.
    Closed,
    /// Contactor force-opened by the BMS due to a hard fault.
    /// Latched; cleared only after `fault_until_ns` expires.
    #[default]
    OpenFault,
}

/// Reasons for tripping the contactor. Bit-indexed in [`crate::FaultMask`].
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum FaultReason {
    /// Any cell exceeded `v_trip_max_mv`.
    OverVoltage = 0,
    /// Any cell dropped below `v_trip_min_mv`.
    UnderVoltage = 1,
    /// Any cell exceeded `t_trip_max_dc` (tenths of °C).
    OverTemperature = 2,
    /// Any cell below `t_trip_min_dc` (tenths of °C).
    UnderTemperature = 3,
    /// Cell voltage spread exceeded `imbalance_trip_mv`.
    Imbalance = 4,
    /// Cell voltage / temperature slice length mismatch or zero cells.
    SensorMismatch = 5,
    /// Pack current exceeded the absolute safety limit.
    OverCurrent = 6,
}

impl FaultReason {
    #[must_use]
    pub const fn bit(self) -> u8 {
        self as u8
    }
}
