//! Fare-gate state machine.

use std::collections::BTreeSet;

use serde::{Deserialize, Serialize};

use crate::token::FareToken;
use crate::validate::{validate_token, Decision};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum GateCommand {
    /// Barrier retracted; passenger may pass.
    Open,
    /// Barrier in place; reject passage.
    #[default]
    Closed,
}

/// Structured event the gate emits to the back-office on each tap.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AfcEvent {
    pub now_ns: u64,
    pub gate_station_id: u32,
    pub account_id: u32,
    pub decision: Decision,
}

/// Inputs to the gate evaluator.
#[derive(Clone, Debug)]
pub struct AfcInputs<'a> {
    pub now_ns: u64,
    pub gate_station_id: u32,
    /// Token scanned this tick, if any. `None` means "no passenger
    /// at the scanner"; the gate should default to Closed.
    pub scanned_token: Option<FareToken>,
    pub secret: &'a [u8],
    pub blacklist: &'a BTreeSet<u32>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AfcParams {
    /// How long the gate stays open after a valid tap, in ns.
    pub open_duration_ns: u64,
}

impl AfcParams {
    #[must_use]
    pub fn metro_default() -> Self {
        Self {
            open_duration_ns: 3_000_000_000, // 3 s
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct AfcState {
    /// `Some(ns)` = gate is open until that deadline.
    pub open_until_ns: Option<u64>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AfcOutput {
    pub state: AfcState,
    pub gate: GateCommand,
    /// `Some` when a token was scanned this tick (event is always
    /// emitted — granted or denied — for audit).
    pub event: Option<AfcEvent>,
    pub last_decision: Option<Decision>,
}

/// Evaluate one AFC tick. Pure.
#[must_use]
pub fn afc_evaluate(prev: &AfcState, inputs: &AfcInputs<'_>, params: &AfcParams) -> AfcOutput {
    // 1. Process scanned token if present.
    let (event, decision) = match &inputs.scanned_token {
        None => (None, None),
        Some(token) => {
            let decision = validate_token(
                token,
                inputs.secret,
                inputs.now_ns,
                inputs.gate_station_id,
                inputs.blacklist,
            );
            let ev = AfcEvent {
                now_ns: inputs.now_ns,
                gate_station_id: inputs.gate_station_id,
                account_id: token.account_id,
                decision,
            };
            (Some(ev), Some(decision))
        }
    };

    // 2. Update gate-open deadline on Grant.
    let mut open_until_ns = prev.open_until_ns;
    if matches!(decision, Some(Decision::Grant)) {
        open_until_ns = Some(inputs.now_ns.saturating_add(params.open_duration_ns));
    }

    // 3. Drive gate command from deadline.
    let gate = match open_until_ns {
        Some(until) if inputs.now_ns < until => GateCommand::Open,
        _ => {
            open_until_ns = None;
            GateCommand::Closed
        }
    };

    AfcOutput {
        state: AfcState { open_until_ns },
        gate,
        event,
        last_decision: decision,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use crate::validate::{sign_token, DenyReason};

    fn fresh_token(account_id: u32, now_ns: u64, secret: &[u8], station: Option<u32>) -> FareToken {
        let mut t = FareToken {
            account_id,
            issued_ns: now_ns - 1_000_000_000,
            expires_ns: now_ns + 3_600_000_000_000, // +1 hour
            station_restriction: station,
            signature: [0u8; osr_crypto::HMAC_SHA256_LEN],
        };
        t.signature = sign_token(&t, secret);
        t
    }

    #[test]
    fn nothing_scanned_gate_closed() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let out = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: 1_000_000_000,
                gate_station_id: 1,
                scanned_token: None,
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(out.gate, GateCommand::Closed);
        assert!(out.event.is_none());
    }

    #[test]
    fn valid_token_opens_gate() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let now = 1_000_000_000_000;
        let token = fresh_token(42, now, secret, None);
        let out = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: now,
                gate_station_id: 1,
                scanned_token: Some(token),
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(out.gate, GateCommand::Open);
        assert_eq!(out.last_decision, Some(Decision::Grant));
        assert!(out.state.open_until_ns.is_some());
    }

    #[test]
    fn expired_token_denied() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let mut token = fresh_token(42, 1_000_000_000_000, secret, None);
        token.expires_ns = 500_000_000_000; // in the past
        token.signature = sign_token(&token, secret);
        let out = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: 1_000_000_000_000,
                gate_station_id: 1,
                scanned_token: Some(token),
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(out.last_decision, Some(Decision::Deny(DenyReason::Expired)));
        assert_eq!(out.gate, GateCommand::Closed);
    }

    #[test]
    fn wrong_station_denied() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let now = 1_000_000_000_000;
        let token = fresh_token(42, now, secret, Some(7)); // valid only at station 7
        let out = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: now,
                gate_station_id: 3, // different station
                scanned_token: Some(token),
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(
            out.last_decision,
            Some(Decision::Deny(DenyReason::WrongStation))
        );
    }

    #[test]
    fn blacklisted_denied() {
        let secret = b"s3cret";
        let mut blacklist = BTreeSet::new();
        blacklist.insert(42);
        let now = 1_000_000_000_000;
        let token = fresh_token(42, now, secret, None);
        let out = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: now,
                gate_station_id: 1,
                scanned_token: Some(token),
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(
            out.last_decision,
            Some(Decision::Deny(DenyReason::Blacklisted))
        );
    }

    #[test]
    fn bad_signature_denied() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let now = 1_000_000_000_000;
        let mut token = fresh_token(42, now, secret, None);
        token.signature[0] ^= 1; // flip a bit
        let out = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: now,
                gate_station_id: 1,
                scanned_token: Some(token),
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(
            out.last_decision,
            Some(Decision::Deny(DenyReason::BadSignature))
        );
    }

    #[test]
    fn gate_auto_closes_after_duration() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let now = 1_000_000_000_000;
        let token = fresh_token(42, now, secret, None);
        // First tick: scan, gate opens, deadline = now + 3s.
        let first = afc_evaluate(
            &AfcState::default(),
            &AfcInputs {
                now_ns: now,
                gate_station_id: 1,
                scanned_token: Some(token),
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(first.gate, GateCommand::Open);

        // Second tick: no scan, still within 3 s window → Open.
        let second = afc_evaluate(
            &first.state,
            &AfcInputs {
                now_ns: now + 1_000_000_000,
                gate_station_id: 1,
                scanned_token: None,
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(second.gate, GateCommand::Open);

        // Third tick: past the 3 s window → Closed.
        let third = afc_evaluate(
            &second.state,
            &AfcInputs {
                now_ns: now + 4_000_000_000,
                gate_station_id: 1,
                scanned_token: None,
                secret,
                blacklist: &blacklist,
            },
            &AfcParams::metro_default(),
        );
        assert_eq!(third.gate, GateCommand::Closed);
    }

    #[test]
    fn determinism() {
        let secret = b"s3cret";
        let blacklist = BTreeSet::new();
        let now = 1_000_000_000_000;
        let token = fresh_token(42, now, secret, None);
        let inputs = AfcInputs {
            now_ns: now,
            gate_station_id: 1,
            scanned_token: Some(token),
            secret,
            blacklist: &blacklist,
        };
        let a = afc_evaluate(&AfcState::default(), &inputs, &AfcParams::metro_default());
        let b = afc_evaluate(&AfcState::default(), &inputs, &AfcParams::metro_default());
        assert_eq!(a, b);
    }
}
