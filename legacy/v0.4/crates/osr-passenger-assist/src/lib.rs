//! Passenger emergency intercom and OCC remote-assist control path.
//!
//! A button press immediately requests a 50% controlled service brake,
//! opens the authenticated media-channel request, and emits an event-recorder
//! record. The stop request remains latched through a communications outage;
//! only an authenticated OCC command can release it or escalate to emergency
//! brake. This is the software state machine required by RFC 0015 §5.3.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

pub const CONTROLLED_STOP_EFFORT_PPT: u16 = 500;
pub const STOP_DELIVERY_LIMIT_NS: u64 = 3_000_000_000;

#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub enum CallPhase {
    #[default]
    Idle,
    Calling,
    Connected,
    Closed,
}

#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub enum OperatorCommand {
    #[default]
    None,
    Accept,
    Release,
    EmergencyBrake,
}

#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct AssistState {
    pub phase: CallPhase,
    pub call_id: u64,
    pub pressed_at_ns: u64,
    pub car_id: u16,
    pub intercom_id: u16,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AssistInputs {
    pub now_ns: u64,
    pub car_id: u16,
    pub intercom_id: u16,
    pub button_pressed: bool,
    /// True only after the OCC peer identity and session have been verified.
    pub occ_link_authenticated: bool,
    pub operator_command: OperatorCommand,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AssistOutput {
    pub state: AssistState,
    pub alarm_to_occ: bool,
    pub request_media_channel: bool,
    pub event_record_requested: bool,
    pub service_brake_ppt: u16,
    pub emergency_brake: bool,
}

/// Evaluate one intercom/remote-assist tick.
#[must_use]
pub fn assist_evaluate(prev: &AssistState, inputs: &AssistInputs) -> AssistOutput {
    let mut state = *prev;
    let mut event_record_requested = false;

    if matches!(state.phase, CallPhase::Idle) && inputs.button_pressed {
        state = AssistState {
            phase: CallPhase::Calling,
            call_id: call_id(inputs.now_ns, inputs.car_id, inputs.intercom_id),
            pressed_at_ns: inputs.now_ns,
            car_id: inputs.car_id,
            intercom_id: inputs.intercom_id,
        };
        event_record_requested = true;
    }

    if inputs.occ_link_authenticated {
        state.phase = match (state.phase, inputs.operator_command) {
            (CallPhase::Calling, OperatorCommand::Accept) => CallPhase::Connected,
            (CallPhase::Calling | CallPhase::Connected, OperatorCommand::Release) => {
                CallPhase::Closed
            }
            (phase, _) => phase,
        };
    }

    // Require button release before a closed call returns to idle. This
    // prevents a held or failed switch from creating a stream of call IDs.
    if matches!(state.phase, CallPhase::Closed) && !inputs.button_pressed {
        state = AssistState::default();
    }

    let active = matches!(state.phase, CallPhase::Calling | CallPhase::Connected);
    let emergency_brake = active
        && inputs.occ_link_authenticated
        && matches!(inputs.operator_command, OperatorCommand::EmergencyBrake);

    AssistOutput {
        state,
        alarm_to_occ: active,
        request_media_channel: active,
        event_record_requested,
        service_brake_ppt: if active {
            CONTROLLED_STOP_EFFORT_PPT
        } else {
            0
        },
        emergency_brake,
    }
}

fn call_id(now_ns: u64, car_id: u16, intercom_id: u16) -> u64 {
    now_ns ^ (u64::from(car_id) << 16) ^ u64::from(intercom_id)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn press(now_ns: u64) -> AssistInputs {
        AssistInputs {
            now_ns,
            car_id: 2,
            intercom_id: 7,
            button_pressed: true,
            occ_link_authenticated: false,
            operator_command: OperatorCommand::None,
        }
    }

    #[test]
    fn press_immediately_requests_controlled_stop_and_media() {
        let input = press(10_000_000_000);
        let out = assist_evaluate(&AssistState::default(), &input);
        assert_eq!(out.service_brake_ppt, CONTROLLED_STOP_EFFORT_PPT);
        assert!(out.alarm_to_occ);
        assert!(out.request_media_channel);
        assert!(out.event_record_requested);
        assert!(input.now_ns - out.state.pressed_at_ns <= STOP_DELIVERY_LIMIT_NS);
    }

    #[test]
    fn link_loss_cannot_release_latched_stop() {
        let active = assist_evaluate(&AssistState::default(), &press(100)).state;
        let unauthenticated_release = AssistInputs {
            now_ns: 200,
            button_pressed: false,
            occ_link_authenticated: false,
            operator_command: OperatorCommand::Release,
            ..press(100)
        };
        let out = assist_evaluate(&active, &unauthenticated_release);
        assert_eq!(out.service_brake_ppt, CONTROLLED_STOP_EFFORT_PPT);
        assert_eq!(out.state.phase, CallPhase::Calling);
    }

    #[test]
    fn authenticated_operator_can_accept_release_or_escalate() {
        let active = assist_evaluate(&AssistState::default(), &press(100)).state;
        let accepted = assist_evaluate(
            &active,
            &AssistInputs {
                now_ns: 200,
                occ_link_authenticated: true,
                operator_command: OperatorCommand::Accept,
                ..press(100)
            },
        );
        assert_eq!(accepted.state.phase, CallPhase::Connected);

        let escalated = assist_evaluate(
            &accepted.state,
            &AssistInputs {
                now_ns: 300,
                occ_link_authenticated: true,
                operator_command: OperatorCommand::EmergencyBrake,
                ..press(100)
            },
        );
        assert!(escalated.emergency_brake);

        let released = assist_evaluate(
            &accepted.state,
            &AssistInputs {
                now_ns: 400,
                button_pressed: false,
                occ_link_authenticated: true,
                operator_command: OperatorCommand::Release,
                ..press(100)
            },
        );
        assert_eq!(released.service_brake_ppt, 0);
        assert_eq!(released.state.phase, CallPhase::Idle);
    }
}
