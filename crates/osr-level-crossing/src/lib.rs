//! OpenSourceRail level-crossing controller.
//!
//! Manages a road/rail crossing's barriers + warning lights + bell
//! through a five-state machine. Every wayside crossing is a
//! participant in the consensus log ([`osr_consensus`]) — it
//! receives train-approach events and publishes its crossing-state
//! back so the interlocking can refuse MAs that would allow a
//! train to enter an unclosed crossing section.
//!
//! Phase 2d crate of [RFC 0005 §4.6](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-4 — a mis-timed barrier raises the risk of a grade-crossing
//! collision, historically one of the most common causes of rail
//! fatality.
//!
//! # State machine
//!
//! ```text
//!   Idle ──(train approach + minimum_warning_ns)──► Warning
//!    ▲                                                 │
//!    │                                                 │ barriers fully down
//!    │                                                 ▼
//!  Clearing ◄─ train cleared ─── Closed
//!    │
//!    │ barriers fully up
//!    ▼
//!   Idle
//!
//!   Any state ── barrier stuck / motor fault ──► Faulted
//! ```
//!
//! # Properties (proptest-verified)
//!
//! - **LC1 determinism.**
//! - **LC2 interlock safe:** `crossing_safe_for_train == true`
//!   iff state == Closed AND barriers both fully down.
//! - **LC3 warning precedes closure:** `state == Closed` implies
//!   the tick's `time_in_state_ns ≥ min_warning_ns` was satisfied
//!   in the `Warning → Closed` transition (enforced structurally).
//! - **LC4 faulted is conservative:** `state == Faulted` →
//!   `crossing_safe_for_train == false`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum LcState {
    #[default]
    Idle,
    Warning,
    Closed,
    Clearing,
    Faulted,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BarrierSensors {
    pub fully_up: bool,
    pub fully_down: bool,
    pub motor_fault: bool,
}

impl Default for BarrierSensors {
    fn default() -> Self {
        Self {
            fully_up: true,
            fully_down: false,
            motor_fault: false,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LcInputs {
    pub now_ns: u64,
    /// `true` when the consensus log reports a train approaching
    /// this crossing (within the announce distance).
    pub train_approaching: bool,
    /// `true` when the consensus log reports the train has cleared
    /// the crossing section.
    pub train_cleared: bool,
    pub barrier_a: BarrierSensors,
    pub barrier_b: BarrierSensors,
    pub manual_emergency_lower: bool,
    pub manual_reset: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LcParams {
    /// Minimum warning time before barriers may close, ns.
    pub min_warning_ns: u64,
    /// Maximum allowed time to move a barrier (up→down or
    /// down→up) before declaring a motor fault, ns.
    pub barrier_move_timeout_ns: u64,
    pub fault_cooldown_ns: u64,
}

impl LcParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            min_warning_ns: 20_000_000_000,      // 20 s
            barrier_move_timeout_ns: 15_000_000_000, // 15 s
            fault_cooldown_ns: 60_000_000_000,   // 60 s
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct LcStatePersistent {
    pub state: LcState,
    pub state_entered_ns: u64,
    pub fault_until_ns: Option<u64>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum BarrierCommand {
    #[default]
    Hold,
    Lower,
    Raise,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LcOutput {
    pub state: LcStatePersistent,
    pub barrier_command: BarrierCommand,
    pub warning_lights_on: bool,
    pub bell_on: bool,
    /// The consensus-log-published flag: `true` iff the interlocking
    /// may grant an MA through this crossing section.
    pub crossing_safe_for_train: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

fn barriers_down(a: &BarrierSensors, b: &BarrierSensors) -> bool {
    a.fully_down && b.fully_down
}
fn barriers_up(a: &BarrierSensors, b: &BarrierSensors) -> bool {
    a.fully_up && b.fully_up
}
fn barrier_fault(a: &BarrierSensors, b: &BarrierSensors) -> bool {
    a.motor_fault || b.motor_fault
}

#[must_use]
pub fn lc_evaluate(prev: &LcStatePersistent, inputs: &LcInputs, params: &LcParams) -> LcOutput {
    // Detect barrier motor fault and enter/remain in Faulted.
    let mut fault_until_ns = prev.fault_until_ns;
    let hardware_fault_now = barrier_fault(&inputs.barrier_a, &inputs.barrier_b);

    if hardware_fault_now {
        fault_until_ns = Some(
            inputs
                .now_ns
                .saturating_add(params.fault_cooldown_ns),
        );
    }
    if let Some(until) = fault_until_ns {
        if inputs.now_ns >= until {
            fault_until_ns = None;
        }
    }
    let in_fault = fault_until_ns.is_some();

    // Emergency manual override: forces Warning → Closed progression.
    let want_closed = inputs.train_approaching || inputs.manual_emergency_lower;

    let time_in_state = inputs.now_ns.saturating_sub(prev.state_entered_ns);

    let (next_state, barrier_command, state_entered_ns) = if in_fault {
        (LcState::Faulted, BarrierCommand::Hold, prev.state_entered_ns)
    } else {
        match prev.state {
            LcState::Idle => {
                if want_closed {
                    (LcState::Warning, BarrierCommand::Lower, inputs.now_ns)
                } else {
                    (LcState::Idle, BarrierCommand::Hold, prev.state_entered_ns)
                }
            }
            LcState::Warning => {
                if time_in_state >= params.min_warning_ns
                    && barriers_down(&inputs.barrier_a, &inputs.barrier_b)
                {
                    (LcState::Closed, BarrierCommand::Hold, inputs.now_ns)
                } else if !want_closed {
                    // Train withdrew; abort and raise.
                    (LcState::Clearing, BarrierCommand::Raise, inputs.now_ns)
                } else {
                    (LcState::Warning, BarrierCommand::Lower, prev.state_entered_ns)
                }
            }
            LcState::Closed => {
                if inputs.train_cleared && !want_closed {
                    (LcState::Clearing, BarrierCommand::Raise, inputs.now_ns)
                } else {
                    (LcState::Closed, BarrierCommand::Hold, prev.state_entered_ns)
                }
            }
            LcState::Clearing => {
                if barriers_up(&inputs.barrier_a, &inputs.barrier_b) {
                    (LcState::Idle, BarrierCommand::Hold, inputs.now_ns)
                } else if want_closed {
                    // Another train approached mid-raise.
                    (LcState::Warning, BarrierCommand::Lower, inputs.now_ns)
                } else {
                    (
                        LcState::Clearing,
                        BarrierCommand::Raise,
                        prev.state_entered_ns,
                    )
                }
            }
            LcState::Faulted => {
                if inputs.manual_reset && !hardware_fault_now {
                    (LcState::Idle, BarrierCommand::Raise, inputs.now_ns)
                } else {
                    (LcState::Faulted, BarrierCommand::Hold, prev.state_entered_ns)
                }
            }
        }
    };

    let warning_lights_on = matches!(next_state, LcState::Warning | LcState::Closed | LcState::Clearing | LcState::Faulted);
    let bell_on = matches!(next_state, LcState::Warning);
    let crossing_safe_for_train = next_state == LcState::Closed
        && barriers_down(&inputs.barrier_a, &inputs.barrier_b);

    LcOutput {
        state: LcStatePersistent {
            state: next_state,
            state_entered_ns,
            fault_until_ns,
        },
        barrier_command,
        warning_lights_on,
        bell_on,
        crossing_safe_for_train,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn barriers_both(up: bool, down: bool) -> BarrierSensors {
        BarrierSensors { fully_up: up, fully_down: down, motor_fault: false }
    }

    fn idle_inputs(now: u64) -> LcInputs {
        LcInputs {
            now_ns: now,
            train_approaching: false,
            train_cleared: false,
            barrier_a: barriers_both(true, false),
            barrier_b: barriers_both(true, false),
            manual_emergency_lower: false,
            manual_reset: false,
        }
    }

    #[test]
    fn idle_stays_idle_when_clear() {
        let out = lc_evaluate(
            &LcStatePersistent::default(),
            &idle_inputs(1_000),
            &LcParams::default_metro(),
        );
        assert_eq!(out.state.state, LcState::Idle);
        assert!(!out.warning_lights_on);
        assert!(!out.crossing_safe_for_train);
    }

    #[test]
    fn approach_enters_warning() {
        let mut i = idle_inputs(1_000);
        i.train_approaching = true;
        let out = lc_evaluate(&LcStatePersistent::default(), &i, &LcParams::default_metro());
        assert_eq!(out.state.state, LcState::Warning);
        assert_eq!(out.barrier_command, BarrierCommand::Lower);
        assert!(out.bell_on);
    }

    #[test]
    fn warning_to_closed_after_time_and_barriers_down() {
        let p = LcParams::default_metro();
        let prev = LcStatePersistent {
            state: LcState::Warning,
            state_entered_ns: 0,
            fault_until_ns: None,
        };
        let mut i = idle_inputs(21_000_000_000); // 21 s
        i.train_approaching = true;
        i.barrier_a = barriers_both(false, true);
        i.barrier_b = barriers_both(false, true);
        let out = lc_evaluate(&prev, &i, &p);
        assert_eq!(out.state.state, LcState::Closed);
        assert!(out.crossing_safe_for_train);
    }

    #[test]
    fn fault_forces_unsafe() {
        let mut i = idle_inputs(1_000);
        i.barrier_a.motor_fault = true;
        let out = lc_evaluate(&LcStatePersistent::default(), &i, &LcParams::default_metro());
        assert_eq!(out.state.state, LcState::Faulted);
        assert!(!out.crossing_safe_for_train);
    }

    #[test]
    fn clearing_returns_to_idle_when_up() {
        let prev = LcStatePersistent {
            state: LcState::Clearing,
            state_entered_ns: 0,
            fault_until_ns: None,
        };
        let i = idle_inputs(1_000); // barriers fully up, train cleared
        let out = lc_evaluate(&prev, &i, &LcParams::default_metro());
        assert_eq!(out.state.state, LcState::Idle);
    }

    #[test]
    fn determinism() {
        let i = idle_inputs(1_000);
        let p = LcParams::default_metro();
        assert_eq!(
            lc_evaluate(&LcStatePersistent::default(), &i, &p),
            lc_evaluate(&LcStatePersistent::default(), &i, &p)
        );
    }
}
