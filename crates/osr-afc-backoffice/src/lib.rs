//! OpenSourceRail AFC back-office: fare settlement, revenue
//! reconciliation, and fraud flagging.
//!
//! Consumes the [`AfcEvent`](osr_afc::AfcEvent) stream produced by
//! every fare-gate and keeps three running views:
//!
//! 1. **Account ledger deltas** — one entry per Grant, charged at
//!    `fare_cents` to the account.
//! 2. **Per-station revenue totals** — sum of charged fares and
//!    paid-tap count, keyed by `gate_station_id`.
//! 3. **Fraud flags** — accounts that exceeded a rolling
//!    `max_denies_per_window` rate, which is a cheap proxy for a
//!    stolen token being probed against multiple gates.
//!
//! Phase 2e crate of [RFC 0005 §4.8](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0 — a wrong settlement is a revenue/billing issue; no safety
//! impact. The MaaS API surface mentioned in RFC 0005 is out of
//! scope for this crate (that's a web-server concern, built on top
//! of this evaluator).
//!
//! # Properties (proptest-verified)
//!
//! - **BO1 determinism.**
//! - **BO2 revenue accounting:** `Σ revenue_cents = grants · fare_cents`.
//! - **BO3 granted events never appear in the fraud set** (purely
//!   driven by denies).

#![forbid(unsafe_code)]

use std::collections::BTreeMap;

use osr_afc::{AfcEvent, Decision};
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AfcBackofficeParams {
    pub fare_cents: u32,
    /// Rolling window width for fraud detection, nanoseconds.
    pub fraud_window_ns: u64,
    /// Denies-within-window threshold; exceeding flags the account.
    pub max_denies_per_window: u16,
}

impl AfcBackofficeParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            fare_cents: 50,                   // 50¢ flat fare
            fraud_window_ns: 300_000_000_000, // 5 min
            max_denies_per_window: 5,
        }
    }
}

/// One debit against an account.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LedgerEntry {
    pub posted_ns: u64,
    pub account_id: u32,
    pub station_id: u32,
    pub amount_cents: u32,
}

#[derive(Copy, Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct StationRevenue {
    pub taps_granted: u32,
    pub revenue_cents: u64,
}

/// Persistent state threaded between batches.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct AfcBackofficeState {
    pub station_revenue: BTreeMap<u32, StationRevenue>,
    /// Per-account recent deny timestamps (oldest first).
    pub deny_history: BTreeMap<u32, Vec<u64>>,
    /// Accounts currently flagged as suspected fraud.
    pub flagged_accounts: BTreeMap<u32, u64>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AfcBackofficeOutput {
    pub state: AfcBackofficeState,
    /// New ledger entries produced by this batch, in input order.
    pub ledger: Vec<LedgerEntry>,
    /// Accounts newly flagged during this batch.
    pub new_flags: Vec<u32>,
}

#[must_use]
pub fn ingest_events(
    prev: &AfcBackofficeState,
    events: &[AfcEvent],
    params: &AfcBackofficeParams,
) -> AfcBackofficeOutput {
    let mut state = prev.clone();
    let mut ledger = Vec::new();
    let mut new_flags = Vec::new();

    for ev in events {
        match ev.decision {
            Decision::Grant => {
                ledger.push(LedgerEntry {
                    posted_ns: ev.now_ns,
                    account_id: ev.account_id,
                    station_id: ev.gate_station_id,
                    amount_cents: params.fare_cents,
                });
                let slot = state.station_revenue.entry(ev.gate_station_id).or_default();
                slot.taps_granted = slot.taps_granted.saturating_add(1);
                slot.revenue_cents = slot
                    .revenue_cents
                    .saturating_add(u64::from(params.fare_cents));
            }
            Decision::Deny(_) => {
                let hist = state.deny_history.entry(ev.account_id).or_default();
                let cutoff = ev.now_ns.saturating_sub(params.fraud_window_ns);
                hist.retain(|&t| t >= cutoff);
                hist.push(ev.now_ns);

                if hist.len() as u16 > params.max_denies_per_window
                    && !state.flagged_accounts.contains_key(&ev.account_id)
                {
                    state.flagged_accounts.insert(ev.account_id, ev.now_ns);
                    new_flags.push(ev.account_id);
                }
            }
        }
    }

    AfcBackofficeOutput {
        state,
        ledger,
        new_flags,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_afc::validate::DenyReason;

    fn ev(now_ns: u64, station: u32, account: u32, d: Decision) -> AfcEvent {
        AfcEvent {
            now_ns,
            gate_station_id: station,
            account_id: account,
            decision: d,
        }
    }

    #[test]
    fn single_grant_ledger_and_revenue() {
        let p = AfcBackofficeParams::default_metro();
        let out = ingest_events(
            &AfcBackofficeState::default(),
            &[ev(1_000_000_000, 7, 42, Decision::Grant)],
            &p,
        );
        assert_eq!(out.ledger.len(), 1);
        assert_eq!(out.ledger[0].amount_cents, 50);
        assert_eq!(out.state.station_revenue[&7].taps_granted, 1);
        assert_eq!(out.state.station_revenue[&7].revenue_cents, 50);
    }

    #[test]
    fn deny_does_not_charge() {
        let p = AfcBackofficeParams::default_metro();
        let out = ingest_events(
            &AfcBackofficeState::default(),
            &[ev(0, 1, 42, Decision::Deny(DenyReason::Expired))],
            &p,
        );
        assert!(out.ledger.is_empty());
    }

    #[test]
    fn rapid_denies_flag_account() {
        let p = AfcBackofficeParams {
            max_denies_per_window: 3,
            ..AfcBackofficeParams::default_metro()
        };
        let events: Vec<_> = (0..6u64)
            .map(|k| {
                ev(
                    k * 1_000_000_000,
                    1,
                    99,
                    Decision::Deny(DenyReason::BadSignature),
                )
            })
            .collect();
        let out = ingest_events(&AfcBackofficeState::default(), &events, &p);
        assert!(out.new_flags.contains(&99));
        assert!(out.state.flagged_accounts.contains_key(&99));
    }

    #[test]
    fn denies_outside_window_do_not_flag() {
        let p = AfcBackofficeParams {
            max_denies_per_window: 3,
            fraud_window_ns: 1_000_000_000,
            ..AfcBackofficeParams::default_metro()
        };
        // 10 s apart, window is 1 s → no accumulation.
        let events: Vec<_> = (0..10u64)
            .map(|k| {
                ev(
                    k * 10_000_000_000,
                    1,
                    5,
                    Decision::Deny(DenyReason::BadSignature),
                )
            })
            .collect();
        let out = ingest_events(&AfcBackofficeState::default(), &events, &p);
        assert!(out.new_flags.is_empty());
    }

    #[test]
    fn flag_not_re_emitted_once_set() {
        let p = AfcBackofficeParams {
            max_denies_per_window: 2,
            ..AfcBackofficeParams::default_metro()
        };
        let first_batch: Vec<_> = (0..5u64)
            .map(|k| ev(k * 1_000_000_000, 1, 7, Decision::Deny(DenyReason::Expired)))
            .collect();
        let a = ingest_events(&AfcBackofficeState::default(), &first_batch, &p);
        assert_eq!(a.new_flags, vec![7]);
        let b = ingest_events(&a.state, &first_batch, &p);
        assert!(b.new_flags.is_empty());
    }

    #[test]
    fn determinism() {
        let p = AfcBackofficeParams::default_metro();
        let events = vec![
            ev(1, 1, 1, Decision::Grant),
            ev(2, 1, 2, Decision::Deny(DenyReason::WrongStation)),
            ev(3, 2, 3, Decision::Grant),
        ];
        let a = ingest_events(&AfcBackofficeState::default(), &events, &p);
        let b = ingest_events(&AfcBackofficeState::default(), &events, &p);
        assert_eq!(a, b);
    }
}
