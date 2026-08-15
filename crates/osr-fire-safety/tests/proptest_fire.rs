//! Property tests for the staged RFC 0021 fire response.

use osr_fire_safety::{
    fire_evaluate, AlarmLevel, Bay, BaySensors, FireInputs, FireParams, FireState, MistSystemHealth,
};
use proptest::prelude::*;

fn params() -> FireParams {
    FireParams::default_metro()
}

fn healthy_mist() -> MistSystemHealth {
    MistSystemHealth {
        reservoir_level_ppt: 1_000,
        pump_ready: true,
        line_pressure_ok: true,
        flow_confirmed: true,
    }
}

fn arb_bay() -> impl Strategy<Value = BaySensors> {
    (0u32..200, -200i16..1_000, 0u32..100, any::<bool>()).prop_map(
        |(smoke, temp, off_gas, agent)| BaySensors {
            smoke_ppm: smoke,
            temp_dc: temp,
            off_gas_ppm: off_gas,
            agent_available: agent,
        },
    )
}

fn arb_inputs() -> impl Strategy<Value = FireInputs> {
    (
        0u64..120_000_000_000,
        arb_bay(),
        arb_bay(),
        arb_bay(),
        0i16..500,
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(|(now, b, t, h, amb, reset, danger, can_move)| FireInputs {
            now_ns: now,
            battery: b,
            traction: t,
            hvac: h,
            ambient_temp_dc: amb,
            battery_mist: healthy_mist(),
            immediate_danger: danger,
            train_can_move_safely: can_move,
            reset_requested: reset,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn f1_determinism(i in arb_inputs()) {
        let p = params();
        prop_assert_eq!(
            fire_evaluate(&FireState::default(), &i, &p),
            fire_evaluate(&FireState::default(), &i, &p)
        );
    }

    #[test]
    fn f2_latched_trip_requests_controlled_stop(i in arb_inputs()) {
        let out = fire_evaluate(&FireState::default(), &i, &params());
        prop_assert_eq!(out.controlled_stop_requested, out.state.latched_tripped.any());
        prop_assert_eq!(out.charge_inhibited, out.controlled_stop_requested);
        prop_assert_eq!(out.isolate_car_hv, out.controlled_stop_requested);
    }

    #[test]
    fn f3_emergency_requires_escalation(i in arb_inputs()) {
        let out = fire_evaluate(&FireState::default(), &i, &params());
        if out.emergency_requested {
            prop_assert!(out.current_tripped.any());
            prop_assert!(i.immediate_danger || !i.train_can_move_safely);
        }
    }

    #[test]
    fn f4_only_battery_has_automatic_suppression(i in arb_inputs()) {
        let out = fire_evaluate(&FireState::default(), &i, &params());
        prop_assert!(!out.activate_traction);
        prop_assert!(!out.activate_hvac);
        if out.activate_battery {
            prop_assert!(out.current_tripped.contains(Bay::Battery));
            prop_assert!(i.battery.agent_available);
        }
    }
}

#[test]
fn alarm_level_rolls_up_correctly() {
    let clean_bay = BaySensors {
        smoke_ppm: 0,
        temp_dc: 200,
        off_gas_ppm: 0,
        agent_available: true,
    };
    let clean = FireInputs {
        now_ns: 0,
        battery: clean_bay,
        traction: clean_bay,
        hvac: clean_bay,
        ambient_temp_dc: 200,
        battery_mist: healthy_mist(),
        immediate_danger: false,
        train_can_move_safely: true,
        reset_requested: false,
    };
    assert_eq!(
        fire_evaluate(&FireState::default(), &clean, &params()).alarm,
        AlarmLevel::Nominal
    );

    let mut trip = clean;
    trip.battery.off_gas_ppm = 100;
    let out = fire_evaluate(&FireState::default(), &trip, &params());
    assert_eq!(out.alarm, AlarmLevel::Trip);
    assert!(out.controlled_stop_requested);
    assert!(!out.emergency_requested);
}
