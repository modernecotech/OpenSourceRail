//! State and output.

use serde::{Deserialize, Serialize};

use crate::types::{FaultMask, InverterState};

/// Persistent supervisor state. Caller carries across ticks.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct TractionState {
    pub inverter: InverterState,
    pub commanded_torque_mnm: i32,
    /// Estimated pack current this tick, milliamps. Signed: positive
    /// = discharge (motoring), negative = charge (regen).
    pub estimated_current_ma: i32,
    /// Anti-slip engaged this tick. Diagnostic.
    pub anti_slip_active: bool,
    /// Latched faults; cleared only via cooldown + fresh enable.
    pub faults: FaultMask,
    /// ns-since-epoch at which the fault latch may be cleared.
    pub fault_until_ns: Option<u64>,
}

/// Full output of one evaluator tick.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TractionOutput {
    pub state: TractionState,
    /// Commanded torque to forward to the FOC drive, mN·m, signed.
    /// Echo of `state.commanded_torque_mnm`.
    pub commanded_torque_mnm: i32,
    /// Gate enable for the inverter power stage. `true` only when
    /// the supervisor is commanding torque and no faults are latched.
    pub inverter_enable: bool,
    /// Estimated pack current. Fed back to `osr-bms` as
    /// pre-knowledge of the upcoming load.
    pub estimated_current_ma: i32,
    /// Diagnostic: anti-slip is reducing torque.
    pub anti_slip_active: bool,
}
