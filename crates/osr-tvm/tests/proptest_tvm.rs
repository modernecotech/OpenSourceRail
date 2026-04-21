//! Property tests TVM1–TVM6.

use std::collections::BTreeSet;

use osr_afc::{validate_token, Decision};
use osr_tvm::{
    tvm_evaluate, PaymentMethod, Product, TvmDenyReason, TvmInputs, TvmOutcome, TvmState,
};
use proptest::prelude::*;

fn arb_product() -> impl Strategy<Value = Product> {
    prop_oneof![
        Just(Product::SingleRide),
        Just(Product::DayPass),
        Just(Product::WeekPass),
    ]
}

fn arb_payment(quoted: u32, force_insufficient: bool) -> impl Strategy<Value = PaymentMethod> {
    if force_insufficient {
        (0u32..quoted).prop_map(|a| PaymentMethod::Cash { amount_cents: a }).boxed()
    } else {
        prop_oneof![
            Just(PaymentMethod::MobileMoney { confirmation_code: 1 }),
            (quoted..quoted + 10_000).prop_map(|a| PaymentMethod::Cash { amount_cents: a }),
        ]
        .boxed()
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    /// TVM1 determinism.
    #[test]
    fn tvm1_determinism(
        product in arb_product(),
        now in 1_000_000_000u64..10_000_000_000_000,
        station in 0u32..100,
        account in 0u32..10_000,
        amount in 0u32..10_000,
    ) {
        let i = TvmInputs {
            now_ns: now,
            issuing_station_id: station,
            product,
            payment: PaymentMethod::Cash { amount_cents: amount },
            account_id: account,
            secret: b"k",
        };
        let a = tvm_evaluate(&TvmState::default(), &i);
        let b = tvm_evaluate(&TvmState::default(), &i);
        prop_assert_eq!(a, b);
    }

    /// TVM2 insufficient payment → Denied.
    #[test]
    fn tvm2_insufficient_denied(product in arb_product(), station in 0u32..100) {
        let quoted = product.price_cents();
        prop_assume!(quoted > 0);
        let payment = PaymentMethod::Cash { amount_cents: quoted.saturating_sub(1) };
        let i = TvmInputs {
            now_ns: 1,
            issuing_station_id: station,
            product,
            payment,
            account_id: 42,
            secret: b"k",
        };
        let out = tvm_evaluate(&TvmState::default(), &i);
        let denied = matches!(out.outcome, TvmOutcome::Denied(TvmDenyReason::InsufficientPayment { .. }));
        prop_assert!(denied);
    }

    /// TVM3 + TVM4 + TVM5: sufficient payment produces a token with
    /// correct TTL, correct station restriction, and a signature
    /// that validates at a gate with the same secret.
    #[test]
    fn tvm3_4_5_sufficient_issues_validatable_token(
        product in arb_product(),
        now in 1_000_000_000u64..10_000_000_000_000,
        station in 0u32..100,
        account in 0u32..10_000,
    ) {
        let quoted = product.price_cents();
        let i = TvmInputs {
            now_ns: now,
            issuing_station_id: station,
            product,
            payment: PaymentMethod::Cash { amount_cents: quoted + 500 },
            account_id: account,
            secret: b"k",
        };
        let out = tvm_evaluate(&TvmState::default(), &i);
        if let TvmOutcome::Issued { token, .. } = out.outcome {
            // TVM4 TTL matches.
            prop_assert_eq!(token.expires_ns - token.issued_ns, product.duration_ns());
            // TVM5 station restriction iff product requires.
            prop_assert_eq!(
                token.station_restriction,
                if product.station_restricted() { Some(station) } else { None }
            );
            // TVM3 token validates at a gate with the same
            // secret and the issuing station.
            let blacklist = BTreeSet::new();
            let gate_station = token.station_restriction.unwrap_or(station);
            prop_assert_eq!(
                validate_token(&token, b"k", now, gate_station, &blacklist),
                Decision::Grant
            );
        } else {
            prop_assert!(false, "expected Issued");
        }
    }

    /// TVM6 change = paid - quoted on Issued; state unchanged on Deny.
    #[test]
    fn tvm6_change_accounting(
        product in arb_product(),
        extra in 0u32..5_000,
    ) {
        let quoted = product.price_cents();
        let i = TvmInputs {
            now_ns: 1,
            issuing_station_id: 1,
            product,
            payment: PaymentMethod::Cash { amount_cents: quoted + extra },
            account_id: 1,
            secret: b"k",
        };
        let out = tvm_evaluate(&TvmState::default(), &i);
        if let TvmOutcome::Issued { change_returned_cents, .. } = out.outcome {
            prop_assert_eq!(change_returned_cents, extra);
            prop_assert_eq!(out.state.revenue_cents, u64::from(quoted));
            prop_assert_eq!(out.state.tickets_sold, 1);
        } else {
            prop_assert!(false);
        }
    }

    /// Denied leaves state unchanged.
    #[test]
    fn denied_state_unchanged(product in arb_product(), shortfall in 1u32..50) {
        let quoted = product.price_cents();
        prop_assume!(quoted >= shortfall);
        let payment = PaymentMethod::Cash { amount_cents: quoted - shortfall };
        let i = TvmInputs {
            now_ns: 1,
            issuing_station_id: 1,
            product,
            payment,
            account_id: 1,
            secret: b"k",
        };
        let prior = TvmState { tickets_sold: 99, revenue_cents: 888, next_serial: 7 };
        let out = tvm_evaluate(&prior, &i);
        prop_assert_eq!(out.state, prior);
    }
}
