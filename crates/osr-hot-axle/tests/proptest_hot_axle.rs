//! Property tests HA1–HA5.

use osr_hot_axle::{
    hot_axle_evaluate, AxleAlarm, AxleFault, AxleReading, AxleSensor, HotAxleInputs, HotAxleParams,
};
use proptest::prelude::*;

fn params() -> HotAxleParams {
    HotAxleParams::default_metro()
}

fn arb_sensor() -> impl Strategy<Value = AxleSensor> {
    (-200i16..1_500, any::<bool>()).prop_map(|(t, v)| AxleSensor {
        temp_dc: t,
        valid: v,
    })
}

fn arb_reading() -> impl Strategy<Value = AxleReading> {
    (arb_sensor(), arb_sensor()).prop_map(|(a, b)| AxleReading {
        sensor_a: a,
        sensor_b: b,
    })
}

fn arb_inputs() -> impl Strategy<Value = HotAxleInputs> {
    (
        0u64..60_000_000_000,
        0i16..500,
        prop::collection::vec(arb_reading(), 1..=8),
    )
        .prop_map(|(now, amb, axles)| HotAxleInputs {
            now_ns: now,
            ambient_dc: amb,
            axles,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ha1_determinism(i in arb_inputs()) {
        let p = params();
        let a = hot_axle_evaluate(&i, &p);
        let b = hot_axle_evaluate(&i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn ha2_trip_is_2oo2(i in arb_inputs()) {
        let p = params();
        let out = hot_axle_evaluate(&i, &p);
        for (k, alarm) in out.axle_alarms.iter().enumerate() {
            if *alarm == AxleAlarm::Trip {
                // 2oo2 invariant: both valid and some condition
                // satisfied on both channels.
                prop_assert!(i.axles[k].sensor_a.valid && i.axles[k].sensor_b.valid);
            }
        }
    }

    #[test]
    fn ha3_invalid_sensor_blocks_trip(mut i in arb_inputs()) {
        let p = params();
        // Force sensor_b invalid on every axle.
        for a in &mut i.axles {
            a.sensor_b.valid = false;
        }
        let out = hot_axle_evaluate(&i, &p);
        prop_assert!(out.axle_alarms.iter().all(|a| *a != AxleAlarm::Trip));
        prop_assert!(!out.emergency_advisory);
    }

    #[test]
    fn ha4_any_trip_sets_advisory(i in arb_inputs()) {
        let p = params();
        let out = hot_axle_evaluate(&i, &p);
        let any_trip = out.axle_alarms.iter().any(|a| *a == AxleAlarm::Trip);
        prop_assert_eq!(out.emergency_advisory, any_trip);
    }

    #[test]
    fn ha5_any_fault_raises_alarm(i in arb_inputs()) {
        let p = params();
        let out = hot_axle_evaluate(&i, &p);
        for (k, faults) in out.axle_faults.iter().enumerate() {
            if faults.any() {
                // At least one fault ⇒ alarm is Warning or Trip (not Nominal).
                // Exception: pure `SensorInvalid` is always at least Warning.
                prop_assert_ne!(out.axle_alarms[k], AxleAlarm::Nominal);
            }
            // Also: Trip ⇒ at least one fault bit.
            if out.axle_alarms[k] == AxleAlarm::Trip {
                prop_assert!(faults.contains(AxleFault::AbsoluteExceedance)
                    || faults.contains(AxleFault::DifferentialExceedance));
            }
        }
    }
}
