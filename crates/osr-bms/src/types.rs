//! Small value types for the BMS.

use serde::{Deserialize, Serialize};

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
    /// Battery off-gas detector crossed its qualified trip threshold.
    OffGasDetected = 7,
    /// The independent fire controller requested car-pack isolation.
    ExternalFireTrip = 8,
}

impl FaultReason {
    #[must_use]
    pub const fn bit(self) -> u8 {
        self as u8
    }
}
