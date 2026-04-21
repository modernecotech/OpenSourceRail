//! Property tests F1–F5.

use osr_fire_safety::{
    fire_evaluate, AlarmLevel, Bay, BaySensors, FireInputs, FireParams, FireState,
};
use proptest::prelude::*;

fn params() -> FireParams {
    FireParams::default_metro()
}

fn arb_bay() -> impl Strategy<Value = BaySensors> {
    (0u32..200, -200i16..1_000, any::<bool>()).prop_map(
        |(smoke, temp, agent)| BaySensors {
            smoke_ppm: smoke,
            temp_dc: temp,
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
    )
        .prop_map(|(now, b, t, h, amb, reset)| FireInputs {
            now_ns: now,
            battery: b,
            traction: t,
            hvac: h,
            ambient_temp_dc: amb,
            reset_requested: reset,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn f1_determinism(i in arb_inputs()) {
        let p = params();
        let a = fire_evaluate(&FireState::default(), &i, &p);
        let b = fire_evaluate(&FireState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn f2_emergency_iff_any_latched(i in arb_inputs()) {
        let p = params();
        let out = fire_evaluate(&FireState::default(), &i, &p);
        prop_assert_eq!(out.emergency_requested, out.state.latched_tripped.any());
    }

    #[test]
    fn f4_suppression_only_for_current_trip(i in arb_inputs()) {
        let p = params();
        let out = fire_evaluate(&FireState::default(), &i, &p);
        if !out.current_tripped.contains(Bay::Battery) {
            prop_assert!(!out.activate_battery);
        }
        if !out.current_tripped.contains(Bay::Traction) {
            prop_assert!(!out.activate_traction);
        }
        if !out.current_tripped.contains(Bay::Hvac) {
            prop_assert!(!out.activate_hvac);
        }
    }

    #[test]
    fn f5_suppression_requires_agent(i in arb_inputs()) {
        let p = params();
        let out = fire_evaluate(&FireState::default(), &i, &p);
        if !i.battery.agent_available {
            prop_assert!(!out.activate_battery);
        }
        if !i.traction.agent_available {
            prop_assert!(!out.activate_traction);
        }
        if !i.hvac.agent_available {
            prop_assert!(!out.activate_hvac);
        }
    }
}

// F3: latch persists through cooldown. Dedicated test because it's
// a multi-tick property.
proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn f3_latch_persists(
        tick_ms in 100u64..2_000,
        resets in prop::collection::vec(any::<bool>(), 40),
    ) {
        let p = params();
        // Trip at t=0.
        let mut trigger = FireInputs {
            now_ns: 0,
            battery: BaySensors { smoke_ppm: 200, temp_dc: 250, agent_available: true },
            traction: BaySensors { smoke_ppm: 0, temp_dc: 250, agent_available: true },
            hvac: BaySensors { smoke_ppm: 0, temp_dc: 250, agent_available: true },
            ambient_temp_dc: 250,
            reset_requested: false,
        };
        let mut state = fire_evaluate(&FireState::default(), &trigger, &p).state;
        prop_assert!(state.cooldown_until_ns.is_some());
        let cd_end = state.cooldown_until_ns.unwrap();

        // Clear the sensors and tick forward, interleaving reset
        // requests. Until cooldown expires, emergency stays asserted.
        trigger.battery.smoke_ppm = 0;
        let mut now = 0_u64;
        for &reset in &resets {
            now = now.saturating_add(tick_ms * 1_000_000);
            let i = FireInputs {
                now_ns: now,
                battery: trigger.battery,
                traction: trigger.traction,
                hvac: trigger.hvac,
                ambient_temp_dc: trigger.ambient_temp_dc,
                reset_requested: reset,
            };
            let out = fire_evaluate(&state, &i, &p);
            if now < cd_end {
                prop_assert!(
                    out.emergency_requested,
                    "emergency cleared during cooldown at now={now}"
                );
            }
            state = out.state;
        }
    }
}

// Quick alarm-level sanity.
#[test]
fn alarm_level_rolls_up_correctly() {
    let p = params();
    // All clean → Nominal.
    let clean = FireInputs {
        now_ns: 0,
        battery: BaySensors { smoke_ppm: 0, temp_dc: 200, agent_available: true },
        traction: BaySensors { smoke_ppm: 0, temp_dc: 200, agent_available: true },
        hvac: BaySensors { smoke_ppm: 0, temp_dc: 200, agent_available: true },
        ambient_temp_dc: 200,
        reset_requested: false,
    };
    assert_eq!(
        fire_evaluate(&FireState::default(), &clean, &p).alarm,
        AlarmLevel::Nominal
    );
    // Warning-level smoke → Warning.
    let mut warn = clean;
    warn.traction.smoke_ppm = 30; // > 20 warn, < 50 trip
    assert_eq!(
        fire_evaluate(&FireState::default(), &warn, &p).alarm,
        AlarmLevel::Warning
    );
    // Trip-level smoke → Trip.
    let mut trip = clean;
    trip.hvac.smoke_ppm = 100;
    assert_eq!(
        fire_evaluate(&FireState::default(), &trip, &p).alarm,
        AlarmLevel::Trip
    );
}
