//! Offline doorway evacuation sequencing. Inputs are unauthenticated study facts.
//! This module supplies no door, restraint, support or inflation actuator adapter.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Phase {
    #[default]
    Idle,
    StopRequested,
    Assessing,
    Ready,
    DeploymentStudy,
    FlowStudy,
    CompleteHold,
    FaultHold,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Fault {
    InvalidParameters,
    ClockReplayOrDeadline,
    ContextChanged,
    ContradictoryFeedback,
    LostDeploymentPrerequisite,
    LostFlowConfirmation,
}
#[derive(Debug, Clone, Copy)]
pub struct Params {
    pub maximum_age_ns: u64,
    pub maximum_tick_ns: u64,
}
#[derive(Debug, Clone, Copy)]
pub struct Inputs {
    pub issued_ns: u64,
    pub sequence: u64,
    pub candidate_revision: u64,
    pub door_id: u16,
    pub emergency_requested: bool,
    pub stopped: bool,
    pub secured: bool,
    pub traction_isolated: bool,
    pub landing_clear: bool,
    pub height_covered: bool,
    pub adjacent_clear: bool,
    pub device_ready: bool,
    pub assistance_ready: bool,
    pub deployment_requested: bool,
    pub deployment_confirmed: bool,
    pub exit_open_confirmed: bool,
    pub flow_complete: bool,
    pub stowed_locked: bool,
    pub reset_requested: bool,
}
#[derive(Debug, Clone, Copy, Default)]
pub struct State {
    pub phase: Phase,
    pub last_now_ns: Option<u64>,
    pub last_issued_ns: Option<u64>,
    pub last_sequence: Option<u64>,
    pub context: Option<(u64, u16)>,
    pub fault: Option<Fault>,
}
#[derive(Debug, Clone, Copy)]
pub struct Output {
    pub state: State,
    /// Bits: stop, secured, traction isolation, landing, height, adjacent clearance,
    /// device readiness, assistance. These are study assertions, not certificates.
    pub missing_prerequisites: u16,
    pub traction_inhibit_required_in_study: bool,
    pub support_must_be_maintained_in_study: bool,
    pub further_entry_permitted_in_study: bool,
    pub physical_output_authorised: bool,
}
pub fn evaluate(previous: State, input: Inputs, now_ns: u64, params: Params) -> Output {
    let checks = [
        input.stopped,
        input.secured,
        input.traction_isolated,
        input.landing_clear,
        input.height_covered,
        input.adjacent_clear,
        input.device_ready,
        input.assistance_ready,
    ];
    let missing = checks.iter().enumerate().fold(0_u16, |bits, (i, good)| {
        bits | if *good { 0 } else { 1 << i }
    });
    let fresh = previous.last_now_ns.is_none_or(|v| now_ns > v)
        && previous.last_issued_ns.is_none_or(|v| input.issued_ns > v)
        && previous.last_sequence.is_none_or(|v| input.sequence > v)
        && input.issued_ns <= now_ns
        && input.sequence != 0
        && now_ns
            .checked_sub(input.issued_ns)
            .is_some_and(|v| v <= params.maximum_age_ns);
    let within_deadline = previous.last_now_ns.is_none_or(|v| {
        now_ns
            .checked_sub(v)
            .is_some_and(|d| d <= params.maximum_tick_ns)
    });
    let inconsistent_history = (previous.phase == Phase::Idle && previous.context.is_some())
        || (!matches!(previous.phase, Phase::Idle | Phase::FaultHold)
            && previous.context.is_none());
    let context_changed = previous
        .context
        .is_some_and(|v| v != (input.candidate_revision, input.door_id));
    let contradictory = (input.stowed_locked && input.deployment_confirmed)
        || (input.exit_open_confirmed && !input.deployment_confirmed)
        || (input.flow_complete && !input.exit_open_confirmed)
        || (previous.phase == Phase::Idle && !input.stowed_locked);
    let started = matches!(
        previous.phase,
        Phase::DeploymentStudy | Phase::FlowStudy | Phase::CompleteHold
    );
    let new_fault = if params.maximum_age_ns == 0 || params.maximum_tick_ns == 0 {
        Some(Fault::InvalidParameters)
    } else if !fresh || !within_deadline {
        Some(Fault::ClockReplayOrDeadline)
    } else if context_changed || inconsistent_history {
        Some(Fault::ContextChanged)
    } else if contradictory || (input.deployment_confirmed && !started) {
        Some(Fault::ContradictoryFeedback)
    } else if previous.phase == Phase::FlowStudy
        && (!input.deployment_confirmed || !input.exit_open_confirmed)
    {
        Some(Fault::LostFlowConfirmation)
    } else if started && missing != 0 {
        Some(Fault::LostDeploymentPrerequisite)
    } else {
        None
    };
    let mut state = previous;
    state.fault = previous.fault.or(new_fault);
    // A fresh monotonic frame advances timing history even after a missed tick.
    // The fault remains latched; reset needs a subsequent in-deadline frame.
    // Stale/replayed/regressed frames never establish new history.
    if fresh {
        state.last_now_ns = Some(now_ns);
        state.last_issued_ns = Some(input.issued_ns);
        state.last_sequence = Some(input.sequence);
    }
    if state.fault.is_some() {
        state.phase = Phase::FaultHold;
    } else {
        state.phase = match previous.phase {
            Phase::Idle if input.emergency_requested => {
                state.context = Some((input.candidate_revision, input.door_id));
                Phase::StopRequested
            }
            Phase::Idle => Phase::Idle,
            Phase::StopRequested if checks[..3].iter().all(|v| *v) => Phase::Assessing,
            Phase::StopRequested => Phase::StopRequested,
            Phase::Assessing if missing == 0 => Phase::Ready,
            Phase::Assessing => Phase::Assessing,
            Phase::Ready if missing != 0 => Phase::Assessing,
            Phase::Ready if input.deployment_requested => Phase::DeploymentStudy,
            Phase::Ready => Phase::Ready,
            Phase::DeploymentStudy if input.deployment_confirmed && input.exit_open_confirmed => {
                Phase::FlowStudy
            }
            Phase::DeploymentStudy => Phase::DeploymentStudy,
            Phase::FlowStudy if input.flow_complete => Phase::CompleteHold,
            Phase::FlowStudy => Phase::FlowStudy,
            Phase::CompleteHold => Phase::CompleteHold,
            Phase::FaultHold => Phase::FaultHold,
        };
    }
    // Completion never automatically releases traction. Reset is a new, fresh,
    // same-context, secured/stopped/isolated, positively stowed study operation.
    if matches!(
        previous.phase,
        Phase::StopRequested
            | Phase::Assessing
            | Phase::Ready
            | Phase::CompleteHold
            | Phase::FaultHold
    ) && input.reset_requested
        && !input.emergency_requested
        && input.stowed_locked
        && checks[..3].iter().all(|v| *v)
        && new_fault.is_none()
    {
        state.phase = Phase::Idle;
        state.fault = None;
        state.context = None;
    }
    let active = state.phase != Phase::Idle;
    Output {
        state,
        missing_prerequisites: missing,
        traction_inhibit_required_in_study: active,
        support_must_be_maintained_in_study: active,
        further_entry_permitted_in_study: state.phase == Phase::FlowStudy
            && input.deployment_confirmed
            && input.exit_open_confirmed,
        physical_output_authorised: false,
    }
}

/// Train-wide hold composition; no hardware actuation or automatic rescue.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TrainSupport {
    MaintainAvailableSupport,
    CaptureRequired,
    CapturedHold,
    NoEgressDemand,
}
#[derive(Debug, Clone, Copy)]
pub struct TrainHold {
    pub traction_inhibit_required_in_study: bool,
    pub support: TrainSupport,
    pub physical_output_authorised: bool,
}
pub fn train_hold(
    doors: &[Output],
    expected_doors: usize,
    support_available: bool,
    captured_confirmed: bool,
) -> TrainHold {
    // An incomplete configured door inventory cannot establish a release.
    let active = expected_doors == 0
        || doors.len() != expected_doors
        || doors.iter().any(|d| d.traction_inhibit_required_in_study);
    TrainHold {
        traction_inhibit_required_in_study: active,
        support: if !active {
            TrainSupport::NoEgressDemand
        } else if captured_confirmed {
            TrainSupport::CapturedHold
        } else if support_available {
            TrainSupport::MaintainAvailableSupport
        } else {
            TrainSupport::CaptureRequired
        },
        physical_output_authorised: false,
    }
}
