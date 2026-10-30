//! Property tests for osr-t2g.

use osr_t2g::{t2g_evaluate, ActiveChannel, T2gInputs, T2gParams, T2gState};
use proptest::prelude::*;

fn params() -> T2gParams {
    T2gParams::default_metro()
}

fn arb_inputs() -> impl Strategy<Value = T2gInputs> {
    (
        0u64..60_000_000_000,
        0u8..=100,
        0u8..=100,
        0u32..100,
        any::<bool>(),
    )
        .prop_map(|(now, pri, bak, q, em)| T2gInputs {
            now_ns: now,
            primary_signal: pri,
            backup_signal: bak,
            queued_payloads: q,
            emergency_priority: em,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn t2g1_determinism(i in arb_inputs()) {
        let p = params();
        let a = t2g_evaluate(&T2gState::default(), &i, &p);
        let b = t2g_evaluate(&T2gState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn t2g2_emergency_transmits_when_channel_available(i in arb_inputs()) {
        let p = params();
        let out = t2g_evaluate(&T2gState::default(), &i, &p);
        if i.emergency_priority && i.queued_payloads > 0 && out.active != ActiveChannel::Offline {
            prop_assert!(out.transmit_now);
        }
    }

    #[test]
    fn t2g3_failover(i in arb_inputs()) {
        let p = params();
        let out = t2g_evaluate(&T2gState::default(), &i, &p);
        let primary_ok = i.primary_signal >= p.primary_dropout_threshold;
        let backup_ok = i.backup_signal >= p.backup_dropout_threshold;
        if !primary_ok && backup_ok {
            prop_assert_eq!(out.active, ActiveChannel::Backup);
        }
        if primary_ok {
            prop_assert_eq!(out.active, ActiveChannel::Primary);
        }
    }

    #[test]
    fn t2g4_both_weak_is_offline(i in arb_inputs()) {
        let p = params();
        let out = t2g_evaluate(&T2gState::default(), &i, &p);
        let primary_ok = i.primary_signal >= p.primary_dropout_threshold;
        let backup_ok = i.backup_signal >= p.backup_dropout_threshold;
        if !primary_ok && !backup_ok {
            prop_assert_eq!(out.active, ActiveChannel::Offline);
            prop_assert!(!out.transmit_now);
        }
    }

    #[test]
    fn queue_decrement_on_transmit(i in arb_inputs()) {
        let p = params();
        let out = t2g_evaluate(&T2gState::default(), &i, &p);
        if out.transmit_now {
            prop_assert_eq!(out.queue_remaining, i.queued_payloads - 1);
        } else {
            prop_assert_eq!(out.queue_remaining, i.queued_payloads);
        }
    }
}
