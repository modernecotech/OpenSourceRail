use osr_maglev_control::{evaluate, Fault, Inputs, Params, State, Support};

fn params() -> Params {
    Params {
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
    }
}
fn input(sequence: u64) -> Inputs {
    Inputs {
        issued_ns: sequence * 1_000_000,
        sequence,
        gap_a_um: 8000,
        gap_b_um: 8000,
        sensors_healthy: true,
        drive_healthy: true,
        support_power_available: true,
        traction_requested: true,
        stop_requested: false,
        secured: false,
        stopped: false,
        reset_requested: false,
    }
}
#[test]
fn upward_attraction_sign_and_bias_are_explicit() {
    for (gap, expected) in [(7500, 500), (8000, 1000), (8500, 1500)] {
        let mut i = input(1);
        i.gap_a_um = gap;
        i.gap_b_um = gap;
        let r = evaluate(State::default(), i, i.issued_ns, params());
        assert_eq!(r.support, Support::StudyCurrentMa(expected));
        assert!(r.traction_permitted_in_study);
        assert!(!r.physical_output_authorised);
    }
}
#[test]
fn saturation_stops_traction_and_latches_until_secure_reset() {
    let mut i = input(1);
    i.gap_a_um = 13000;
    i.gap_b_um = 13000;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    assert_eq!(r.support, Support::StudyCurrentMa(5000));
    assert!(r.current_saturated);
    assert!(!r.traction_permitted_in_study);
    assert!(r.controlled_stop_required);
    let next = input(2);
    let s = evaluate(r.state, next, next.issued_ns, params());
    assert!(!s.traction_permitted_in_study);
}
#[test]
fn traction_stop_preserves_fresh_support_control() {
    let mut i = input(1);
    i.stop_requested = true;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    assert!(!r.traction_permitted_in_study);
    assert!(r.controlled_stop_required);
    assert_eq!(r.support, Support::StudyCurrentMa(1000));
}
#[test]
fn lost_or_disagreeing_sensing_requires_local_fallback_not_frozen_current() {
    let mut i = input(1);
    i.gap_b_um = 8500;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    assert_eq!(r.state.latched_fault, Some(Fault::Sensor));
    assert_eq!(r.support, Support::LocalFallbackRequired);
    assert!(r.controlled_stop_required);
}
#[test]
fn averaging_cannot_conceal_out_of_envelope_gap() {
    let mut p = params();
    p.sensor_disagreement_um = 1000;
    let mut i = input(1);
    i.gap_a_um = 2900;
    i.gap_b_um = 3100;
    let r = evaluate(State::default(), i, i.issued_ns, p);
    assert_eq!(r.state.latched_fault, Some(Fault::GapEnvelope));
}
#[test]
fn stale_future_replayed_and_clock_regression_inputs_fail() {
    let p = params();
    let i = input(1);
    let good = evaluate(State::default(), i, i.issued_ns, p);
    for (old, frame, now, fault) in [
        (State::default(), i, i.issued_ns + 500_001, Fault::Deadline),
        (State::default(), i, i.issued_ns - 1, Fault::ClockOrReplay),
        (good.state, i, i.issued_ns + 1_000_000, Fault::ClockOrReplay),
        (good.state, input(2), i.issued_ns - 1, Fault::ClockOrReplay),
        (good.state, input(4), 4_000_000, Fault::Deadline),
    ] {
        let r = evaluate(old, frame, now, p);
        assert_eq!(r.state.latched_fault, Some(fault));
        assert_eq!(r.support, Support::LocalFallbackRequired);
        assert!(!r.traction_permitted_in_study);
    }
}
#[test]
fn valid_support_can_resume_after_transient_fault_but_traction_stays_latched() {
    let mut i = input(1);
    i.drive_healthy = false;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    let j = input(2);
    let recovered = evaluate(r.state, j, j.issued_ns, params());
    assert_eq!(recovered.support, Support::StudyCurrentMa(1000));
    assert!(!recovered.traction_permitted_in_study);
    assert_eq!(recovered.state.latched_fault, Some(Fault::Drive));
}
#[test]
fn reset_requires_fresh_healthy_stopped_and_secured_state() {
    let mut i = input(1);
    i.stop_requested = true;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    for (stopped, secured, allowed) in [
        (false, false, false),
        (true, false, false),
        (false, true, false),
        (true, true, true),
    ] {
        let mut j = input(2);
        j.reset_requested = true;
        j.stopped = stopped;
        j.secured = secured;
        let s = evaluate(r.state, j, j.issued_ns, params());
        assert_eq!(!s.state.stop_latched, allowed);
        assert!(!s.physical_output_authorised);
        if allowed {
            assert_eq!(s.support, Support::Secured);
            assert!(!s.traction_permitted_in_study);
        }
    }
}
#[test]
fn derivative_uses_measurement_time_and_correct_damping_sign() {
    let mut p = params();
    p.proportional_ma_per_um = 0;
    p.derivative_ma_per_um_s = 1;
    let i = input(1);
    let initial = evaluate(State::default(), i, i.issued_ns, p);
    let mut j = input(2);
    j.gap_a_um = 8001;
    j.gap_b_um = 8001;
    let r = evaluate(initial.state, j, j.issued_ns + 100_000, p);
    assert_eq!(r.support, Support::StudyCurrentMa(2000));
}
#[test]
fn invalid_configuration_cannot_divide_by_zero_or_permit_traction() {
    let mut p = params();
    p.maximum_tick_ns = 0;
    let i = input(1);
    let r = evaluate(State::default(), i, i.issued_ns, p);
    assert_eq!(r.state.latched_fault, Some(Fault::InvalidParameters));
    assert!(!r.traction_permitted_in_study);
}
#[test]
fn extreme_integer_inputs_remain_bounded() {
    let mut p = params();
    p.proportional_ma_per_um = u32::MAX;
    p.derivative_ma_per_um_s = u32::MAX;
    let mut i = input(1);
    let first = evaluate(State::default(), i, i.issued_ns, p);
    i.sequence = 2;
    i.issued_ns += 1;
    i.gap_a_um = 13000;
    i.gap_b_um = 13000;
    let r = evaluate(first.state, i, i.issued_ns, p);
    assert_eq!(r.support, Support::StudyCurrentMa(5000));
    assert!(!r.physical_output_authorised);
}
#[test]
fn missing_support_power_is_explicit_even_when_magnets_remain() {
    let mut i = input(1);
    i.support_power_available = false;
    let r = evaluate(State::default(), i, i.issued_ns, params());
    assert_eq!(r.state.latched_fault, Some(Fault::SupportPower));
    assert_eq!(r.support, Support::LocalFallbackRequired);
}
