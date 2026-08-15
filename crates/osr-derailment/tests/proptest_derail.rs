//! Property tests D1–D5.

use osr_derailment::{
    derailment_evaluate, AlarmLevel, DerailmentInputs, DerailmentParams, DerailmentState,
    FaultReason, SensorChannel,
};
use proptest::prelude::*;

fn params() -> DerailmentParams {
    DerailmentParams::default_metro()
}

fn arb_channel() -> impl Strategy<Value = SensorChannel> {
    (
        -1_000i32..1_000,
        -500i32..500,
        0i32..3_000,
        -30_000i32..30_000,
        any::<bool>(),
    )
        .prop_map(|(lat, lon, vert, tilt, valid)| SensorChannel {
            lateral_mg: lat,
            longitudinal_mg: lon,
            vertical_mg: vert,
            tilt_mdeg: tilt,
            valid,
        })
}

fn arb_inputs() -> impl Strategy<Value = DerailmentInputs> {
    (
        0u64..60_000_000_000,
        arb_channel(),
        arb_channel(),
        any::<bool>(),
    )
        .prop_map(|(now, a, b, reset)| DerailmentInputs {
            now_ns: now,
            sensor_a: a,
            sensor_b: b,
            reset_requested: reset,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn d1_determinism(i in arb_inputs()) {
        let p = params();
        let a = derailment_evaluate(&DerailmentState::default(), &i, &p);
        let b = derailment_evaluate(&DerailmentState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn d2_2oo2_safety(i in arb_inputs()) {
        let p = params();
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        // An emergency from this tick alone (i.e., prev wasn't latched)
        // requires both channels valid.
        if out.emergency_requested {
            // State was fresh; trip had to come from this tick.
            prop_assert!(i.sensor_a.valid && i.sensor_b.valid);
        }
    }

    #[test]
    fn d4_invalid_sensor_blocks_trip(mut i in arb_inputs()) {
        let p = params();
        // Force either channel invalid.
        i.sensor_b.valid = false;
        // Fresh-state evaluation: no prior latch to carry over.
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        prop_assert!(!out.emergency_requested);
        prop_assert!(out.faults.contains(FaultReason::SensorInvalid));
    }

    #[test]
    fn d5_any_anomaly_raises_alarm(i in arb_inputs()) {
        let p = params();
        let out = derailment_evaluate(&DerailmentState::default(), &i, &p);
        // If any fault is present the alarm is ≥ Warning (Warning or Trip).
        if out.faults.any() {
            prop_assert_ne!(out.alarm, AlarmLevel::Nominal);
        }
    }
}

// D3: latch persists through cooldown.
proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn d3_latch_persists(tick_ms in 100u64..2_000, resets in prop::collection::vec(any::<bool>(), 30)) {
        let p = params();
        let mut trigger = DerailmentInputs {
            now_ns: 0,
            sensor_a: SensorChannel { lateral_mg: 500, ..Default::default() },
            sensor_b: SensorChannel { lateral_mg: 500, ..Default::default() },
            reset_requested: false,
        };
        let mut state = derailment_evaluate(&DerailmentState::default(), &trigger, &p).state;
        prop_assert!(state.cooldown_until_ns.is_some());
        let cd_end = state.cooldown_until_ns.unwrap();

        // Clear the sensor, tick forward.
        trigger.sensor_a = SensorChannel::default();
        trigger.sensor_b = SensorChannel::default();
        let mut now = 0_u64;
        for &reset in &resets {
            now = now.saturating_add(tick_ms * 1_000_000);
            let i = DerailmentInputs {
                now_ns: now,
                sensor_a: trigger.sensor_a,
                sensor_b: trigger.sensor_b,
                reset_requested: reset,
            };
            let out = derailment_evaluate(&state, &i, &p);
            if now < cd_end {
                prop_assert!(out.emergency_requested, "cleared during cooldown at {now}");
            }
            state = out.state;
        }
    }
}
