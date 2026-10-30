//! Property tests BO1–BO3.

use osr_afc::validate::DenyReason;
use osr_afc::{AfcEvent, Decision};
use osr_afc_backoffice::{ingest_events, AfcBackofficeParams, AfcBackofficeState};
use proptest::prelude::*;

fn arb_deny() -> impl Strategy<Value = DenyReason> {
    prop_oneof![
        Just(DenyReason::Expired),
        Just(DenyReason::BadSignature),
        Just(DenyReason::WrongStation),
        Just(DenyReason::Blacklisted),
    ]
}

fn arb_decision() -> impl Strategy<Value = Decision> {
    prop_oneof![Just(Decision::Grant), arb_deny().prop_map(Decision::Deny),]
}

fn arb_event() -> impl Strategy<Value = AfcEvent> {
    (0u64..1_000_000_000_000, 0u32..20, 0u32..200, arb_decision()).prop_map(
        |(now, station, account, d)| AfcEvent {
            now_ns: now,
            gate_station_id: station,
            account_id: account,
            decision: d,
        },
    )
}

fn arb_batch() -> impl Strategy<Value = Vec<AfcEvent>> {
    prop::collection::vec(arb_event(), 0..=32)
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn bo1_determinism(events in arb_batch()) {
        let p = AfcBackofficeParams::default_metro();
        let a = ingest_events(&AfcBackofficeState::default(), &events, &p);
        let b = ingest_events(&AfcBackofficeState::default(), &events, &p);
        prop_assert_eq!(a, b);
    }

    /// BO2: total ledger amount equals grants * fare, and equals
    /// Σ station_revenue.revenue_cents.
    #[test]
    fn bo2_revenue_accounting(events in arb_batch()) {
        let p = AfcBackofficeParams::default_metro();
        let out = ingest_events(&AfcBackofficeState::default(), &events, &p);

        let grants = events.iter().filter(|e| e.decision == Decision::Grant).count() as u64;
        let expected_total = grants * u64::from(p.fare_cents);

        let ledger_total: u64 = out.ledger.iter().map(|l| u64::from(l.amount_cents)).sum();
        let revenue_total: u64 = out.state.station_revenue.values().map(|r| r.revenue_cents).sum();

        prop_assert_eq!(ledger_total, expected_total);
        prop_assert_eq!(revenue_total, expected_total);
    }

    /// BO3: an account that was only ever granted cannot end up flagged.
    #[test]
    fn bo3_grant_only_never_flagged(events in arb_batch()) {
        let p = AfcBackofficeParams::default_metro();
        let out = ingest_events(&AfcBackofficeState::default(), &events, &p);
        for flagged in out.new_flags.iter() {
            let ever_denied = events
                .iter()
                .any(|e| e.account_id == *flagged && matches!(e.decision, Decision::Deny(_)));
            prop_assert!(ever_denied);
        }
    }
}
