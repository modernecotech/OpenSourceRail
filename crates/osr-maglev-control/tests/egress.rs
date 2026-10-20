use osr_maglev_control::egress::{evaluate, Fault, Inputs, Params, Phase, State};
fn params() -> Params {
    Params {
        maximum_age_ns: 500_000,
        maximum_tick_ns: 2_000_000,
    }
}
fn frame(sequence: u64) -> Inputs {
    Inputs {
        issued_ns: sequence * 1_000_000,
        sequence,
        candidate_revision: 7,
        door_id: 1,
        emergency_requested: true,
        stopped: true,
        secured: true,
        traction_isolated: true,
        landing_clear: true,
        height_covered: true,
        adjacent_clear: true,
        device_ready: true,
        assistance_ready: true,
        deployment_requested: false,
        deployment_confirmed: false,
        exit_open_confirmed: false,
        flow_complete: false,
        stowed_locked: true,
        reset_requested: false,
    }
}
fn tick(state: State, i: Inputs) -> State {
    let r = evaluate(state, i, i.issued_ns, params());
    assert!(!r.physical_output_authorised);
    assert_eq!(
        r.traction_inhibit_required_in_study,
        r.state.phase != Phase::Idle
    );
    assert_eq!(
        r.support_must_be_maintained_in_study,
        r.state.phase != Phase::Idle
    );
    r.state
}
#[test]
fn complete_sequence_stays_held_until_a_new_secured_stowed_reset() {
    let a = tick(State::default(), frame(1));
    assert_eq!(a.phase, Phase::StopRequested);
    let b = tick(a, frame(2));
    assert_eq!(b.phase, Phase::Assessing);
    let c = tick(b, frame(3));
    assert_eq!(c.phase, Phase::Ready);
    let mut i = frame(4);
    i.deployment_requested = true;
    i.stowed_locked = false;
    let d = tick(c, i);
    assert_eq!(d.phase, Phase::DeploymentStudy);
    i = frame(5);
    i.stowed_locked = false;
    i.deployment_confirmed = true;
    i.exit_open_confirmed = true;
    let e = tick(d, i);
    assert_eq!(e.phase, Phase::FlowStudy);
    i = frame(6);
    i.stowed_locked = false;
    i.deployment_confirmed = true;
    i.exit_open_confirmed = true;
    i.flow_complete = true;
    let f = tick(e, i);
    assert_eq!(f.phase, Phase::CompleteHold);
    assert_eq!(tick(f, frame(7)).phase, Phase::CompleteHold);
    i = frame(8);
    i.emergency_requested = false;
    i.reset_requested = true;
    let done = tick(f, i);
    assert_eq!(done.phase, Phase::Idle);
    assert!(done.context.is_none());
}
#[test]
fn every_missing_gate_prevents_ready_and_deployment() {
    let a = tick(State::default(), frame(1));
    let assessing = tick(a, frame(2));
    for mask in 1_u16..256 {
        let mut i = frame(3);
        i.stopped = mask & 1 == 0;
        i.secured = mask & 2 == 0;
        i.traction_isolated = mask & 4 == 0;
        i.landing_clear = mask & 8 == 0;
        i.height_covered = mask & 16 == 0;
        i.adjacent_clear = mask & 32 == 0;
        i.device_ready = mask & 64 == 0;
        i.assistance_ready = mask & 128 == 0;
        i.deployment_requested = true;
        let r = evaluate(assessing, i, i.issued_ns, params());
        assert_eq!(r.missing_prerequisites, mask);
        assert_eq!(r.state.phase, Phase::Assessing);
        assert!(!r.physical_output_authorised);
    }
}
#[test]
fn stale_replay_context_change_and_contradictory_feedback_latch() {
    let a = tick(State::default(), frame(1));
    let mut changed = frame(2);
    changed.candidate_revision = 8;
    let mut other_door = frame(2);
    other_door.door_id = 2;
    let mut contradictory = frame(2);
    contradictory.exit_open_confirmed = true;
    for (i, now, expected) in [
        (frame(1), 2_000_000, Fault::ClockReplayOrDeadline),
        (frame(2), 2_500_001, Fault::ClockReplayOrDeadline),
        (changed, 2_000_000, Fault::ContextChanged),
        (other_door, 2_000_000, Fault::ContextChanged),
        (contradictory, 2_000_000, Fault::ContradictoryFeedback),
    ] {
        let r = evaluate(a, i, now, params());
        assert_eq!(r.state.phase, Phase::FaultHold);
        assert_eq!(r.state.fault, Some(expected));
        let later = evaluate(r.state, frame(4), 4_000_000, params());
        assert_eq!(later.state.phase, Phase::FaultHold);
        assert!(!later.physical_output_authorised);
    }
}
#[test]
fn losing_a_landing_during_deployment_does_not_command_retraction_or_release() {
    let a = tick(State::default(), frame(1));
    let b = tick(a, frame(2));
    let c = tick(b, frame(3));
    let mut i = frame(4);
    i.deployment_requested = true;
    i.stowed_locked = false;
    let d = tick(c, i);
    i = frame(5);
    i.stowed_locked = false;
    i.landing_clear = false;
    let r = evaluate(d, i, i.issued_ns, params());
    assert_eq!(r.state.phase, Phase::FaultHold);
    assert_eq!(r.state.fault, Some(Fault::LostDeploymentPrerequisite));
    assert!(r.support_must_be_maintained_in_study);
    assert!(r.traction_inhibit_required_in_study);
    assert!(!r.physical_output_authorised);
}
#[test]
fn egress_stop_can_inhibit_traction_without_removing_valid_support_control() {
    let e = evaluate(State::default(), frame(1), 1_000_000, params());
    let p = osr_maglev_control::Params {
        target_gap_um: 8000,
        minimum_gap_um: 3000,
        maximum_gap_um: 13000,
        sensor_disagreement_um: 200,
        maximum_age_ns: 500_000,
        maximum_tick_ns: 2_000_000,
        bias_current_ma: 1000,
        minimum_current_ma: -5000,
        maximum_current_ma: 5000,
        proportional_ma_per_um: 1,
        derivative_ma_per_um_s: 0,
    };
    let i = osr_maglev_control::Inputs {
        issued_ns: 1_000_000,
        sequence: 1,
        gap_a_um: 8000,
        gap_b_um: 8000,
        sensors_healthy: true,
        drive_healthy: true,
        support_power_available: true,
        traction_requested: true,
        stop_requested: e.traction_inhibit_required_in_study,
        secured: false,
        stopped: false,
        reset_requested: false,
    };
    let r = osr_maglev_control::evaluate(osr_maglev_control::State::default(), i, 1_000_000, p);
    assert_eq!(r.support, osr_maglev_control::Support::StudyCurrentMa(1000));
    assert!(!r.traction_permitted_in_study);
    assert!(!r.physical_output_authorised);
}

#[test]
fn invalid_parameters_never_enter_a_deployment_phase() {
    for p in [
        Params {
            maximum_age_ns: 0,
            maximum_tick_ns: 1,
        },
        Params {
            maximum_age_ns: 1,
            maximum_tick_ns: 0,
        },
    ] {
        let r = evaluate(State::default(), frame(1), 1_000_000, p);
        assert_eq!(r.state.fault, Some(Fault::InvalidParameters));
        assert_eq!(r.state.phase, Phase::FaultHold);
        assert!(!r.physical_output_authorised);
    }
}
#[test]
fn cancelling_before_deployment_requires_secured_stowed_fresh_reset() {
    let a = tick(State::default(), frame(1));
    let b = tick(a, frame(2));
    for mask in 0..16 {
        let mut i = frame(3);
        i.emergency_requested = false;
        i.reset_requested = true;
        i.stopped = mask & 1 != 0;
        i.secured = mask & 2 != 0;
        i.traction_isolated = mask & 4 != 0;
        i.stowed_locked = mask & 8 != 0;
        let r = evaluate(b, i, i.issued_ns, params());
        assert_eq!(r.state.phase == Phase::Idle, mask == 15);
        assert!(!r.physical_output_authorised);
    }
    let mut i = frame(3);
    i.emergency_requested = false;
    assert_ne!(tick(b, i).phase, Phase::Idle);
}

#[test]
fn corrupt_active_history_and_unlatched_idle_cassette_inhibit_traction() {
    let forged = State {
        phase: Phase::FlowStudy,
        ..State::default()
    };
    let r = evaluate(forged, frame(1), 1_000_000, params());
    assert_eq!(r.state.phase, Phase::FaultHold);
    assert_eq!(r.state.fault, Some(Fault::ContextChanged));
    let mut i = frame(1);
    i.emergency_requested = false;
    i.stowed_locked = false;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    assert_eq!(r.state.phase, Phase::FaultHold);
    assert!(r.traction_inhibit_required_in_study);
    assert!(!r.physical_output_authorised);
}
