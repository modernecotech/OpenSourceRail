//! BMS state and output.

use serde::{Deserialize, Serialize};

use crate::types::{ContactorState, FaultReason};

/// Severity rollup for driver-facing display.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AlarmLevel {
    #[default]
    Nominal,
    /// At least one cell is in its warning band.
    Warning,
    /// A fault is latched. Contactor is (or has just become) open.
    Trip,
}

/// Bitmask of currently-asserted fault reasons. Up to one bit per
/// variant of [`FaultReason`]. Stored as `u16` — there are fewer than
/// 16 reasons.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub struct FaultMask(pub u16);

impl FaultMask {
    #[must_use]
    pub fn empty() -> Self {
        Self(0)
    }

    #[must_use]
    pub fn contains(self, reason: FaultReason) -> bool {
        (self.0 >> reason.bit()) & 1 == 1
    }

    pub fn insert(&mut self, reason: FaultReason) {
        self.0 |= 1u16 << reason.bit();
    }

    pub fn clear(&mut self) {
        self.0 = 0;
    }

    #[must_use]
    pub fn any(self) -> bool {
        self.0 != 0
    }
}

/// Persistent per-BMS state. Caller carries across ticks.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BmsState {
    /// State-of-charge, parts-per-thousand (0..=1000). Updated each
    /// tick via Coulomb counting on `pack_current_ma × dt_ns`.
    pub soc_ppt: u16,
    /// State-of-health, parts-per-thousand. Stubbed at 1000 in v1;
    /// a real estimator would track capacity fade and internal
    /// resistance growth.
    pub soh_ppt: u16,
    pub contactor: ContactorState,
    pub faults: FaultMask,
    /// Nanoseconds-since-epoch at which the fault latch may be cleared.
    pub fault_until_ns: Option<u64>,
    /// Accumulated charge in milliamp-seconds since construction
    /// (positive). Used internally by Coulomb counting; exposed for
    /// diagnostics.
    pub charge_accum_mas: i64,
    pub alarm: AlarmLevel,
}

impl BmsState {
    /// Initialise at a given SoC (e.g. 800 ppt = 80 %) with no
    /// faults, contactor open.
    #[must_use]
    pub fn initial(soc_ppt: u16) -> Self {
        Self {
            soc_ppt: soc_ppt.min(1000),
            soh_ppt: 1000,
            contactor: ContactorState::Open,
            faults: FaultMask::empty(),
            fault_until_ns: None,
            charge_accum_mas: 0,
            alarm: AlarmLevel::Nominal,
        }
    }
}

/// Full per-tick output of the BMS.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BmsOutput {
    pub state: BmsState,
    /// Contactor command applied this tick (echo of `state.contactor`).
    pub contactor: ContactorState,
    /// Maximum charge current the pack will accept, milliamps.
    /// Zero when `contactor != Closed`.
    pub charge_limit_ma: u32,
    /// Maximum discharge current magnitude, milliamps.
    /// Zero when `contactor != Closed`.
    pub discharge_limit_ma: u32,
}
