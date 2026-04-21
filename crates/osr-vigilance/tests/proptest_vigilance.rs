//! Property-based tests for `osr-vigilance`.
//!
//! Exercises the state-machine safety properties V1–V6 over random
//! inputs.

use osr_vigilance::{
    vigilance_evaluate, VigilanceInputs, VigilanceOutput, VigilanceParams, VigilanceState,
};
use proptest::prelude::*;

fn params() -> VigilanceParams {
    VigilanceParams::light_metro_default()
}

fn arb_inputs() -> impl Strategy<Value = VigilanceInputs> {
    (0u64..120_000_000_000, -30_000i32..30_000, any::<bool>()).prop_map(
        |(now_ns, speed_mmps, ack)| VigilanceInputs {
            now_ns,
            speed_mmps,
            ack_received_this_tick: ack,
        },
    )
}

// ---------------------------------------------------------------------------
// V1: determinism.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn v1_determinism(prev_state in 0u8..4, now_ns in 0u64..60_000_000_000,
                       speed in -30_000i32..30_000, ack in any::<bool>()) {
        let p = params();
        let prev = VigilanceOutput {
            state: match prev_state {
                0 => VigilanceState::Suppressed,
                1 => VigilanceState::Nominal,
                2 => VigilanceState::Warning,
                _ => VigilanceState::Tripped,
            },
            emergency_requested: prev_state == 3,
            last_ack_ns: 0,
            time_since_ack_ms: 0,
            time_to_warning_ms: None,
            time_to_trip_ms: None,
        };
        let i = VigilanceInputs { now_ns, speed_mmps: speed, ack_received_this_tick: ack };
        let a = vigilance_evaluate(&prev, &i, &p);
        let b = vigilance_evaluate(&prev, &i, &p);
        prop_assert_eq!(a, b);
    }
}

// ---------------------------------------------------------------------------
// V2: suppression under threshold.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn v2_suppressed_below_threshold(
        prev_state in 0u8..4,
        now_ns in 0u64..60_000_000_000,
        speed in -500i32..500, // well under the 1000 mm/s threshold
        ack in any::<bool>(),
    ) {
        let p = params();
        let prev = VigilanceOutput {
            state: match prev_state {
                0 => VigilanceState::Suppressed,
                1 => VigilanceState::Nominal,
                2 => VigilanceState::Warning,
                _ => VigilanceState::Tripped,
            },
            emergency_requested: prev_state == 3,
            last_ack_ns: 0,
            time_since_ack_ms: 0,
            time_to_warning_ms: None,
            time_to_trip_ms: None,
        };
        let i = VigilanceInputs { now_ns, speed_mmps: speed, ack_received_this_tick: ack };
        let out = vigilance_evaluate(&prev, &i, &p);
        prop_assert_eq!(out.state, VigilanceState::Suppressed);
        prop_assert!(!out.emergency_requested);
    }
}

// ---------------------------------------------------------------------------
// V3: warning always precedes trip.
//
// Simulate a sequence of ticks at speed, starting from Nominal. Track
// state transitions and assert that no direct Nominal → Tripped
// transition ever occurs.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn v3_warning_precedes_trip(
        tick_ms in 100u64..2_000,
        ticks in 1u32..100,
    ) {
        let p = params();
        let mut prev = VigilanceOutput::default();
        // Seed at speed → Nominal.
        prev = vigilance_evaluate(&prev, &VigilanceInputs {
            now_ns: 0, speed_mmps: 10_000, ack_received_this_tick: false,
        }, &p);
        prop_assert_eq!(prev.state, VigilanceState::Nominal);

        let mut now_ns = 0_u64;
        for _ in 0..ticks {
            now_ns = now_ns.saturating_add(tick_ms * 1_000_000);
            let next = vigilance_evaluate(&prev, &VigilanceInputs {
                now_ns, speed_mmps: 10_000, ack_received_this_tick: false,
            }, &p);
            // Illegal transition: Nominal → Tripped
            if prev.state == VigilanceState::Nominal && next.state == VigilanceState::Tripped {
                prop_assert!(false, "direct Nominal→Tripped at ack_elapsed_ms={}", next.time_since_ack_ms);
            }
            prev = next;
        }
    }
}

// ---------------------------------------------------------------------------
// V4: tripped iff emergency_requested.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn v4_tripped_iff_emergency(i in arb_inputs()) {
        let p = params();
        let prev = VigilanceOutput::default();
        let out = vigilance_evaluate(&prev, &i, &p);
        prop_assert_eq!(
            out.emergency_requested,
            out.state == VigilanceState::Tripped
        );
    }
}

// ---------------------------------------------------------------------------
// V5: in-window ack clears Warning → Nominal. (Unit test covers the
// happy path; this proptest varies timing.)
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn v5_warning_ack_clears(extra_ms in 100u32..4_000) {
        let p = params();
        let mut prev = VigilanceOutput::default();
        prev = vigilance_evaluate(&prev, &VigilanceInputs {
            now_ns: 0, speed_mmps: 10_000, ack_received_this_tick: false,
        }, &p);
        // Jump past ack interval into warning window.
        let into_warning_ns = (u64::from(p.ack_interval_ms) + u64::from(extra_ms)) * 1_000_000;
        prev = vigilance_evaluate(&prev, &VigilanceInputs {
            now_ns: into_warning_ns, speed_mmps: 10_000, ack_received_this_tick: false,
        }, &p);
        prop_assert_eq!(prev.state, VigilanceState::Warning);

        // Ack in the warning window.
        let ack_ns = into_warning_ns + 100_000_000;
        let out = vigilance_evaluate(&prev, &VigilanceInputs {
            now_ns: ack_ns, speed_mmps: 10_000, ack_received_this_tick: true,
        }, &p);
        prop_assert_eq!(out.state, VigilanceState::Nominal);
    }
}

// ---------------------------------------------------------------------------
// V6: trip latches.
//
// Once in Tripped, remaining at speed keeps the state Tripped
// regardless of subsequent ack behaviour.
// ---------------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn v6_trip_latches(
        ticks in 1u32..50,
        acks in prop::collection::vec(any::<bool>(), 50),
    ) {
        let p = params();
        let mut prev = VigilanceOutput::default();
        // Drive into Tripped.
        prev = vigilance_evaluate(&prev, &VigilanceInputs {
            now_ns: 0, speed_mmps: 10_000, ack_received_this_tick: false,
        }, &p);
        let trip_at_ns = (u64::from(p.ack_interval_ms) + u64::from(p.warning_ms) + 1) * 1_000_000;
        prev = vigilance_evaluate(&prev, &VigilanceInputs {
            now_ns: trip_at_ns, speed_mmps: 10_000, ack_received_this_tick: false,
        }, &p);
        prop_assert_eq!(prev.state, VigilanceState::Tripped);

        let mut now_ns = trip_at_ns;
        for i in 0..ticks {
            now_ns += 500_000_000;
            let ack = acks.get(i as usize).copied().unwrap_or(false);
            let out = vigilance_evaluate(&prev, &VigilanceInputs {
                now_ns, speed_mmps: 10_000, ack_received_this_tick: ack,
            }, &p);
            prop_assert_eq!(out.state, VigilanceState::Tripped);
            prop_assert!(out.emergency_requested);
            prev = out;
        }
    }
}
