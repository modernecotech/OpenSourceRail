//! Property tests for osr-door-control — D1 through D8.

use osr_door_control::{
    door_evaluate, DoorAction, DoorInputs, DoorParams, DoorSensors, DoorSide, DoorState,
    DoorStatus, MotorCommand,
};
use proptest::prelude::*;

fn params() -> DoorParams {
    DoorParams::research_default()
}

fn arb_action() -> impl Strategy<Value = DoorAction> {
    prop_oneof![
        Just(DoorAction::Hold),
        Just(DoorAction::Open),
        Just(DoorAction::Close),
    ]
}

fn arb_side() -> impl Strategy<Value = DoorSide> {
    prop_oneof![Just(DoorSide::Left), Just(DoorSide::Right)]
}

fn arb_sensors() -> impl Strategy<Value = DoorSensors> {
    (
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        0u32..10_000,
        any::<bool>(),
    )
        .prop_map(|(cl, lk, ol, mc, obs)| DoorSensors {
            closed_limit: cl,
            lock_sensor: lk,
            open_limit: ol,
            motor_current_ma: mc,
            obstruction_detected: obs,
        })
}

fn arb_inputs() -> impl Strategy<Value = DoorInputs> {
    (
        0u64..60_000_000_000,
        -1_000i32..30_000,
        any::<bool>(),
        any::<bool>(),
        arb_side(),
        prop::option::of(arb_side()),
        arb_action(),
        any::<bool>(),
        any::<bool>(),
        arb_sensors(),
    )
        .prop_map(
            |(now, speed, at_s, identity, side, platform, cmd, eunlock, egress, sensors)| {
                DoorInputs {
                    now_ns: now,
                    speed_mmps: speed,
                    at_station: at_s,
                    station_identity_verified: identity,
                    door_side: side,
                    verified_platform_side: platform,
                    commanded: cmd,
                    emergency_unlock: eunlock,
                    emergency_egress_authorized: egress,
                    sensors,
                }
            },
        )
}

// ---------------------------------------------------------------------------
// D1: determinism.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn d1_determinism(i in arb_inputs()) {
        let p = params();
        let a = door_evaluate(&DoorState::default(), &i, &p);
        let b = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// D2: no-open-above-threshold.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn d2_no_open_above_threshold(mut i in arb_inputs()) {
        let p = params();
        // Force motion AND disable emergency unlock.
        i.speed_mmps = 5_000;
        i.emergency_unlock = false;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_ne!(out.motor, MotorCommand::DriveOpen);
    }
}

// ---------------------------------------------------------------------------
// D3: at-station-gates-open.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn d3_at_station_gates_open(mut i in arb_inputs()) {
        let p = params();
        i.at_station = false;
        i.emergency_unlock = false;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_ne!(out.motor, MotorCommand::DriveOpen);
    }

    #[test]
    fn d3a_wrong_or_unknown_platform_side_never_opens(mut i in arb_inputs()) {
        i.at_station = true;
        i.station_identity_verified = true;
        i.speed_mmps = 0;
        i.commanded = DoorAction::Open;
        i.emergency_unlock = false;
        i.verified_platform_side = Some(match i.door_side {
            DoorSide::Left => DoorSide::Right,
            DoorSide::Right => DoorSide::Left,
        });
        prop_assert_ne!(door_evaluate(&DoorState::default(), &i, &params()).motor, MotorCommand::DriveOpen);
        i.verified_platform_side = None;
        prop_assert_ne!(door_evaluate(&DoorState::default(), &i, &params()).motor, MotorCommand::DriveOpen);
        i.verified_platform_side = Some(i.door_side);
        i.station_identity_verified = false;
        prop_assert_ne!(door_evaluate(&DoorState::default(), &i, &params()).motor, MotorCommand::DriveOpen);
    }
}

// ---------------------------------------------------------------------------
// D4: obstruction-stops-close.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn d4_obstruction_stops_close(mut i in arb_inputs()) {
        let p = params();
        // Force an obstruction (sensor or current).
        i.sensors.obstruction_detected = true;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_ne!(out.motor, MotorCommand::DriveClose);
    }

    #[test]
    fn d4_current_spike_stops_close(mut i in arb_inputs()) {
        let p = params();
        i.sensors.motor_current_ma = p.obstruction_current_trip_ma + 100;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_ne!(out.motor, MotorCommand::DriveClose);
    }
}

// ---------------------------------------------------------------------------
// D5: emergency-unlock never drives close.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn d5_emergency_unlock_never_closes(mut i in arb_inputs()) {
        let p = params();
        i.emergency_unlock = true;
        let out = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_ne!(out.motor, MotorCommand::DriveClose);
        if out.motor == MotorCommand::DriveOpen {
            prop_assert!(i.emergency_egress_authorized);
            prop_assert_eq!(i.speed_mmps, 0);
        }
    }
}

// ---------------------------------------------------------------------------
// D6: interlock is 2oo2 of closed_limit && lock_sensor.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn d6_interlock_is_2oo2(i in arb_inputs()) {
        let p = params();
        let out = door_evaluate(&DoorState::default(), &i, &p);
        prop_assert_eq!(
            out.interlock_ok,
            i.sensors.closed_limit && i.sensors.lock_sensor
        );
    }
}

// ---------------------------------------------------------------------------
// D7: motor timeout latches Faulted. Multi-tick property.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn d7_motor_timeout_latches(cmd in prop_oneof![Just(DoorAction::Open), Just(DoorAction::Close)]) {
        let p = params();
        // Seed: motor has been running 9 s (past 8 s timeout).
        let motor = if cmd == DoorAction::Open {
            MotorCommand::DriveOpen
        } else {
            MotorCommand::DriveClose
        };
        let prev = DoorState {
            motor,
            status: if cmd == DoorAction::Open {
                DoorStatus::Opening
            } else {
                DoorStatus::Closing
            },
            motor_started_ns: Some(0),
            fault_until_ns: None,
            obstruction_latched: false,
        };
        let sensors = DoorSensors {
            closed_limit: false,
            lock_sensor: false,
            open_limit: false,
            motor_current_ma: 1_000,
            obstruction_detected: false,
        };
        let i = DoorInputs {
            now_ns: 9_000_000_000,
            speed_mmps: 0,
            at_station: true,
            station_identity_verified: true,
            door_side: DoorSide::Left,
            verified_platform_side: Some(DoorSide::Left),
            commanded: cmd,
            emergency_unlock: false,
            emergency_egress_authorized: false,
            sensors,
        };
        let out = door_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.motor, MotorCommand::Stop);
        prop_assert_eq!(out.status, DoorStatus::Faulted);
        prop_assert!(out.state.fault_until_ns.is_some());
    }
}

// ---------------------------------------------------------------------------
// D8: fault blocks motor.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn d8_fault_blocks_motor(i in arb_inputs()) {
        let p = params();
        let prev = DoorState {
            motor: MotorCommand::Stop,
            status: DoorStatus::Faulted,
            motor_started_ns: None,
            // Cooldown in the future.
            fault_until_ns: Some(i.now_ns + 1_000_000_000),
            obstruction_latched: false,
        };
        let out = door_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.motor, MotorCommand::Stop);
        prop_assert_eq!(out.status, DoorStatus::Faulted);
    }
}
