//! Property tests AFC1–AFC7.

use std::collections::BTreeSet;

use osr_afc::{
    afc_evaluate, sign_token, validate_token, AfcInputs, AfcParams, AfcState, Decision,
    DenyReason, FareToken, GateCommand,
};
use proptest::prelude::*;

fn arb_token(now_ns: u64, secret: &[u8]) -> FareToken {
    let mut t = FareToken {
        account_id: 42,
        issued_ns: now_ns.saturating_sub(1_000_000_000),
        expires_ns: now_ns.saturating_add(3_600_000_000_000),
        station_restriction: None,
        signature: [0u8; 32],
    };
    t.signature = sign_token(&t, secret);
    t
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    /// AFC1 determinism.
    #[test]
    fn afc1_determinism(now in 1_000_000_000u64..10_000_000_000_000,
                        station in 0u32..100,
                        account in 0u32..1000)
    {
        let secret = b"k";
        let blacklist = BTreeSet::new();
        let mut token = arb_token(now, secret);
        token.account_id = account;
        token.signature = sign_token(&token, secret);
        let inputs = AfcInputs {
            now_ns: now,
            gate_station_id: station,
            scanned_token: Some(token),
            secret,
            blacklist: &blacklist,
        };
        let a = afc_evaluate(&AfcState::default(), &inputs, &AfcParams::metro_default());
        let b = afc_evaluate(&AfcState::default(), &inputs, &AfcParams::metro_default());
        prop_assert_eq!(a, b);
    }

    /// AFC2 expired tokens denied.
    #[test]
    fn afc2_expired_denied(now in 1_000_000_000u64..10_000_000_000_000,
                            past_delta in 1_000_000u64..1_000_000_000_000)
    {
        let secret = b"k";
        let blacklist = BTreeSet::new();
        let mut token = arb_token(now, secret);
        token.expires_ns = now.saturating_sub(past_delta);
        token.signature = sign_token(&token, secret);
        let d = validate_token(&token, secret, now, 0, &blacklist);
        prop_assert_eq!(d, Decision::Deny(DenyReason::Expired));
    }

    /// AFC3 bad-signature denied.
    #[test]
    fn afc3_bad_signature_denied(now in 1_000_000_000u64..10_000_000_000_000, bit in 0usize..256) {
        let secret = b"k";
        let blacklist = BTreeSet::new();
        let mut token = arb_token(now, secret);
        token.signature[bit / 8] ^= 1_u8 << (bit % 8);
        let d = validate_token(&token, secret, now, 0, &blacklist);
        prop_assert_eq!(d, Decision::Deny(DenyReason::BadSignature));
    }

    /// AFC4 wrong-station denied.
    #[test]
    fn afc4_wrong_station_denied(now in 1_000_000_000u64..10_000_000_000_000,
                                  s1 in 0u32..100, s2 in 100u32..200)
    {
        let secret = b"k";
        let blacklist = BTreeSet::new();
        let mut token = arb_token(now, secret);
        token.station_restriction = Some(s1);
        token.signature = sign_token(&token, secret);
        let d = validate_token(&token, secret, now, s2, &blacklist);
        prop_assert_eq!(d, Decision::Deny(DenyReason::WrongStation));
    }

    /// AFC5 blacklisted denied.
    #[test]
    fn afc5_blacklisted_denied(now in 1_000_000_000u64..10_000_000_000_000,
                                account in 0u32..1000)
    {
        let secret = b"k";
        let mut blacklist = BTreeSet::new();
        blacklist.insert(account);
        let mut token = arb_token(now, secret);
        token.account_id = account;
        token.signature = sign_token(&token, secret);
        let d = validate_token(&token, secret, now, 0, &blacklist);
        prop_assert_eq!(d, Decision::Deny(DenyReason::Blacklisted));
    }

    /// AFC6 honest-token granted.
    #[test]
    fn afc6_honest_token_granted(now in 1_000_000_000u64..10_000_000_000_000,
                                  station in 0u32..100)
    {
        let secret = b"k";
        let blacklist = BTreeSet::new();
        let token = arb_token(now, secret);
        let d = validate_token(&token, secret, now, station, &blacklist);
        prop_assert_eq!(d, Decision::Grant);
    }

    /// AFC7 gate open iff decision == Grant and within hold window.
    #[test]
    fn afc7_gate_iff_grant(now in 1_000_000_000u64..10_000_000_000_000,
                            grant in any::<bool>())
    {
        let secret = b"k";
        let blacklist = BTreeSet::new();
        let mut token = arb_token(now, secret);
        if !grant {
            token.signature[0] ^= 1;
        }
        let inputs = AfcInputs {
            now_ns: now,
            gate_station_id: 0,
            scanned_token: Some(token),
            secret,
            blacklist: &blacklist,
        };
        let out = afc_evaluate(&AfcState::default(), &inputs, &AfcParams::metro_default());
        if grant {
            prop_assert_eq!(out.gate, GateCommand::Open);
        } else {
            prop_assert_eq!(out.gate, GateCommand::Closed);
        }
    }
}
