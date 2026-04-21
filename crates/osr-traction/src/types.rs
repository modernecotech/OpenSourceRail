//! Value types.

use serde::{Deserialize, Serialize};

/// State of the inverter's power stage.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum InverterState {
    /// Power stage off. No gate pulses, zero output.
    #[default]
    Disabled,
    /// Inverter active and tracking the torque command.
    Running,
    /// Latched fault. Clears only after cooldown and a fresh enable.
    Faulted,
}

/// Reasons the inverter can latch into `Faulted`. Stored in a
/// bit-mask (see `FaultMask` below).
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum FaultReason {
    /// Drive electronics reported over-temperature.
    OverTemperature = 0,
    /// Drive electronics reported over-current, under-voltage, or
    /// another uncleared fault.
    DriveFault = 1,
    /// BMS contactor opened while the inverter was running — a
    /// ride-through fault (different from a clean nominal shutdown).
    ContactorOpen = 2,
    /// Persistent wheel slip above the emergency threshold.
    /// In v1 this is advisory; the brake crate's WSP is authoritative.
    SeverelySlipping = 3,
}

impl FaultReason {
    #[must_use]
    pub const fn bit(self) -> u8 {
        self as u8
    }
}

/// Compact fault bitmask.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub struct FaultMask(pub u8);

impl FaultMask {
    #[must_use]
    pub fn empty() -> Self {
        Self(0)
    }
    #[must_use]
    pub fn contains(self, r: FaultReason) -> bool {
        (self.0 >> r.bit()) & 1 == 1
    }
    pub fn insert(&mut self, r: FaultReason) {
        self.0 |= 1u8 << r.bit();
    }
    pub fn clear(&mut self) {
        self.0 = 0;
    }
    #[must_use]
    pub fn any(self) -> bool {
        self.0 != 0
    }
}
