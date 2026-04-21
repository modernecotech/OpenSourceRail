//! Property-based tests for the points controller.
//!
//! Exercises W1–W6 over randomised inputs and multi-tick sequences.

use osr_wayside_points::{
    switch_evaluate, CommandedPosition, DetectedPosition, FaultReason, MotorCommand, RawSensor,
    SwitchInputs, SwitchOutput, SwitchParams, SwitchState,
};
use proptest::prelude::*;

fn arb_sensor() -> impl Strategy<Value = RawSensor> {
    prop_oneof![
        Just(RawSensor::ReadNormal),
        Just(RawSensor::ReadReverse),
        Just(RawSensor::InTransit),
        Just(RawSensor::Dead),
    ]
}

fn arb_cmd() -> impl Strategy<Value = Option<CommandedPosition>> {
    prop_oneof![
        Just(None),
        Just(Some(CommandedPosition::Normal)),
        Just(Some(CommandedPosition::Reverse)),
    ]
}

fn arb_inputs() -> impl Strategy<Value = SwitchInputs> {
    (
        0u64..60_000_000_000,
        arb_sensor(),
        arb_sensor(),
        arb_cmd(),
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(
            |(now_ns, a, b, cmd, ot, df)| SwitchInputs {
                now_ns,
                sensor_a: a,
                sensor_b: b,
                commanded: cmd,
                motor_over_temp: ot,
                motor_drive_fault: df,
            },
        )
}

fn params() -> SwitchParams {
    SwitchParams::typical()
}

// ---------------------------------------------------------------------------
// W1: determinism.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn w1_determinism(i in arb_inputs()) {
        let prev = SwitchState::default();
        let p = params();
        let a = switch_evaluate(&prev, &i, &p);
        let b = switch_evaluate(&prev, &i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// W2: fail-restrictive detection.
//
// Any sensor that is not an end-of-travel read (Dead, InTransit), or
// any disagreement between the two, produces Unknown.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn w2_fail_restrictive_detection(i in arb_inputs()) {
        let prev = SwitchState::default();
        let p = params();
        let out = switch_evaluate(&prev, &i, &p);

        let agree_normal = matches!((i.sensor_a, i.sensor_b),
            (RawSensor::ReadNormal, RawSensor::ReadNormal));
        let agree_reverse = matches!((i.sensor_a, i.sensor_b),
            (RawSensor::ReadReverse, RawSensor::ReadReverse));

        match out.state.detected {
            DetectedPosition::Normal => prop_assert!(agree_normal),
            DetectedPosition::Reverse => prop_assert!(agree_reverse),
            DetectedPosition::Unknown => {
                prop_assert!(!agree_normal && !agree_reverse);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// W3: motor stops at target.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn w3_motor_stops_at_target(i in arb_inputs()) {
        let prev = SwitchState::default();
        let p = params();
        let out = switch_evaluate(&prev, &i, &p);
        if let Some(cmd) = i.commanded {
            if out.state.detected.matches(cmd) {
                prop_assert_eq!(out.motor, MotorCommand::Stop);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// W4: motor times out.
//
// After motor has been running for > motor_timeout_ms, next tick
// must command Stop with a fault recorded.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn w4_motor_times_out(
        direction in prop_oneof![
            Just(MotorCommand::DriveToNormal),
            Just(MotorCommand::DriveToReverse),
        ],
        cmd in prop_oneof![
            Just(CommandedPosition::Normal),
            Just(CommandedPosition::Reverse),
        ],
    ) {
        // Motor has been running 6 s — past default 5 s timeout.
        let prev = SwitchState {
            motor: direction,
            motor_started_ns: Some(0),
            commanded: Some(cmd),
            detected: DetectedPosition::Unknown,
            ..Default::default()
        };
        let p = params();
        let i = SwitchInputs {
            now_ns: 6_000_000_000,
            sensor_a: RawSensor::InTransit,
            sensor_b: RawSensor::InTransit,
            commanded: Some(cmd),
            motor_over_temp: false,
            motor_drive_fault: false,
        };
        let out = switch_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.motor, MotorCommand::Stop);
        prop_assert_eq!(out.state.fault_reason, Some(FaultReason::MotorTimeout));
        prop_assert!(out.state.fault_until_ns.is_some());
    }
}

// ---------------------------------------------------------------------------
// W5: motor never drives in the opposite direction of commanded.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn w5_motor_never_drives_away_from_commanded(i in arb_inputs()) {
        let prev = SwitchState::default();
        let p = params();
        let out = switch_evaluate(&prev, &i, &p);
        if let Some(cmd) = i.commanded {
            match (cmd, out.motor) {
                (CommandedPosition::Normal, MotorCommand::DriveToReverse) => {
                    prop_assert!(false, "driving Reverse while commanded Normal: {:?}", out);
                }
                (CommandedPosition::Reverse, MotorCommand::DriveToNormal) => {
                    prop_assert!(false, "driving Normal while commanded Reverse: {:?}", out);
                }
                _ => {}
            }
        }
    }
}

// ---------------------------------------------------------------------------
// W6: observation tracks detection.
//
// `publish_observation` is Some iff `detected != prev.last_emitted_detected`.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn w6_observation_publishes_on_change(
        prev_last in prop_oneof![
            Just(DetectedPosition::Normal),
            Just(DetectedPosition::Reverse),
            Just(DetectedPosition::Unknown),
        ],
        i in arb_inputs(),
    ) {
        let prev = SwitchState {
            last_emitted_detected: prev_last,
            ..Default::default()
        };
        let p = params();
        let out = switch_evaluate(&prev, &i, &p);
        if out.state.detected != prev_last {
            prop_assert_eq!(out.publish_observation, Some(out.state.detected));
        } else {
            prop_assert_eq!(out.publish_observation, None);
        }
    }
}

// ---------------------------------------------------------------------------
// Fault inputs always stop the motor.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn any_active_fault_stops_motor(i in arb_inputs()) {
        let prev = SwitchState::default();
        let p = params();
        let out = switch_evaluate(&prev, &i, &p);
        if i.motor_over_temp || i.motor_drive_fault {
            prop_assert_eq!(out.motor, MotorCommand::Stop);
        }
    }
}

// ---------------------------------------------------------------------------
// Multi-tick monotonicity: once faulted, motor stays stopped until
// cooldown elapses, regardless of commands.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, .. ProptestConfig::default() })]

    #[test]
    fn fault_persists_through_cooldown(
        cmd in prop_oneof![
            Just(CommandedPosition::Normal),
            Just(CommandedPosition::Reverse),
        ],
        sensor_seq_hint in prop::collection::vec(arb_sensor(), 5..20),
    ) {
        let mut sensor_seq = sensor_seq_hint.into_iter().cycle();
        // Seed a timeout fault.
        let prev = SwitchState {
            motor: MotorCommand::DriveToNormal,
            motor_started_ns: Some(0),
            commanded: Some(cmd),
            detected: DetectedPosition::Unknown,
            ..Default::default()
        };
        let p = params();
        let trigger = SwitchInputs {
            now_ns: 6_000_000_000,
            sensor_a: RawSensor::InTransit,
            sensor_b: RawSensor::InTransit,
            commanded: Some(cmd),
            motor_over_temp: false,
            motor_drive_fault: false,
        };
        let mut state = switch_evaluate(&prev, &trigger, &p).state;
        prop_assert_eq!(state.fault_reason, Some(FaultReason::MotorTimeout));
        let fault_end = state.fault_until_ns.unwrap();

        // Tick for 20 s in 500 ms steps. Motor must stay stopped
        // until now_ns >= fault_end.
        for step in 1..=40u64 {
            let now_ns = 6_000_000_000 + step * 500_000_000;
            let i = SwitchInputs {
                now_ns,
                sensor_a: sensor_seq.next().unwrap(),
                sensor_b: sensor_seq.next().unwrap(),
                commanded: Some(cmd),
                motor_over_temp: false,
                motor_drive_fault: false,
            };
            let out = switch_evaluate(&state, &i, &p);
            if now_ns < fault_end {
                prop_assert_eq!(
                    out.motor, MotorCommand::Stop,
                    "motor ran during cooldown at t={}",
                    now_ns
                );
            }
            state = out.state;
        }
    }
}

// Smoke: types compile & are used.
#[test]
fn types_smoke() {
    let _ = SwitchState::default();
    let _ = SwitchParams::typical();
    let _: SwitchOutput = switch_evaluate(
        &SwitchState::default(),
        &SwitchInputs {
            now_ns: 0,
            sensor_a: RawSensor::InTransit,
            sensor_b: RawSensor::InTransit,
            commanded: None,
            motor_over_temp: false,
            motor_drive_fault: false,
        },
        &SwitchParams::typical(),
    );
}
