//! OpenSourceRail Ticket Vending Machine.
//!
//! Consumer side of the fare pipeline — issues signed
//! [`FareToken`](osr_afc::FareToken)s that [`osr_afc`]'s gates
//! validate. Accepts mobile-money QR confirmations or cash; both
//! are gated through the same evaluator so the bottom half of the
//! machine (token signing + inventory + revenue tracking) is
//! identical regardless of payment rail.
//!
//! Phase 2e crate 2 of [RFC 0005 §4.7](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0. The integrity of the token lives in [`osr_afc`]'s
//! signing; a TVM issuing over-budget tickets is a revenue bug,
//! not a safety one.
//!
//! # Product catalogue
//!
//! Three reference ticket types; adding product codes is
//! straightforward via a new enum variant and fare-table entry.
//!
//! | Product | Price (cents) | Duration | Station restriction |
//! |---|---|---|---|
//! | `SingleRide` | 100 | 1 h | Issuing station only |
//! | `DayPass` | 500 | 24 h | Network-wide |
//! | `WeekPass` | 2500 | 7 days | Network-wide |
//!
//! # Properties (proptest-verified)
//!
//! - **TVM1 determinism.**
//! - **TVM2 insufficient payment → no token:** if `paid_cents <
//!   price(product)`, no token is issued.
//! - **TVM3 sufficient payment → token:** if payment covers price,
//!   the output carries a [`FareToken`] whose signature validates
//!   against the same secret.
//! - **TVM4 token has correct TTL:** `expires_ns - issued_ns`
//!   equals the product's duration.
//! - **TVM5 single-ride is station-restricted:** product
//!   `SingleRide` produces `station_restriction = Some(issuing)`.
//! - **TVM6 change accounting:** `change_returned_cents = paid -
//!   price` on a successful sale; unchanged inventory on refusal.

#![forbid(unsafe_code)]

use osr_afc::{sign_token, FareToken};
use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Product {
    SingleRide,
    DayPass,
    WeekPass,
}

impl Product {
    /// Price in cents (local currency unit).
    #[must_use]
    pub const fn price_cents(self) -> u32 {
        match self {
            Product::SingleRide => 100,
            Product::DayPass => 500,
            Product::WeekPass => 2500,
        }
    }

    /// Duration in nanoseconds.
    #[must_use]
    pub const fn duration_ns(self) -> u64 {
        match self {
            Product::SingleRide => 3_600_000_000_000,        // 1 h
            Product::DayPass => 24 * 3_600_000_000_000,      // 24 h
            Product::WeekPass => 7 * 24 * 3_600_000_000_000, // 7 days
        }
    }

    /// Whether the product is restricted to the issuing station.
    #[must_use]
    pub const fn station_restricted(self) -> bool {
        matches!(self, Product::SingleRide)
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum PaymentMethod {
    /// Mobile-money confirmation — upstream wallet already
    /// debited the account; the TVM just needs the confirmation
    /// code.
    MobileMoney { confirmation_code: u64 },
    /// Cash: inserted-amount in cents.
    Cash { amount_cents: u32 },
}

impl PaymentMethod {
    #[must_use]
    pub const fn paid_cents(&self, quoted: u32) -> u32 {
        match self {
            // Mobile money always settles at the quoted price.
            PaymentMethod::MobileMoney { .. } => quoted,
            PaymentMethod::Cash { amount_cents } => *amount_cents,
        }
    }
}

#[derive(Clone, Debug)]
pub struct TvmInputs<'a> {
    pub now_ns: u64,
    pub issuing_station_id: u32,
    pub product: Product,
    pub payment: PaymentMethod,
    pub account_id: u32,
    /// Signing secret (same as the station's AFC gates).
    pub secret: &'a [u8],
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum TvmDenyReason {
    InsufficientPayment { quoted_cents: u32, paid_cents: u32 },
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum TvmOutcome {
    Issued {
        token: FareToken,
        change_returned_cents: u32,
    },
    Denied(TvmDenyReason),
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct TvmState {
    pub tickets_sold: u64,
    pub revenue_cents: u64,
    /// Running next-serial for issued tokens, useful for
    /// reconciliation at the back office.
    pub next_serial: u64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TvmOutput {
    pub state: TvmState,
    pub outcome: TvmOutcome,
}

/// Evaluate one TVM sale. Pure.
#[must_use]
pub fn tvm_evaluate(prev: &TvmState, inputs: &TvmInputs<'_>) -> TvmOutput {
    let quoted = inputs.product.price_cents();
    let paid = inputs.payment.paid_cents(quoted);

    if paid < quoted {
        return TvmOutput {
            state: *prev,
            outcome: TvmOutcome::Denied(TvmDenyReason::InsufficientPayment {
                quoted_cents: quoted,
                paid_cents: paid,
            }),
        };
    }

    let station_restriction = if inputs.product.station_restricted() {
        Some(inputs.issuing_station_id)
    } else {
        None
    };
    let mut token = FareToken {
        account_id: inputs.account_id,
        issued_ns: inputs.now_ns,
        expires_ns: inputs.now_ns.saturating_add(inputs.product.duration_ns()),
        station_restriction,
        signature: [0u8; osr_afc::HMAC_SHA256_LEN],
    };
    token.signature = sign_token(&token, inputs.secret);

    let change = paid - quoted;
    let state = TvmState {
        tickets_sold: prev.tickets_sold.saturating_add(1),
        revenue_cents: prev.revenue_cents.saturating_add(u64::from(quoted)),
        next_serial: prev.next_serial.saturating_add(1),
    };

    TvmOutput {
        state,
        outcome: TvmOutcome::Issued {
            token,
            change_returned_cents: change,
        },
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use osr_afc::{validate_token, Decision};
    use std::collections::BTreeSet;

    fn inputs(product: Product, payment: PaymentMethod, station: u32) -> TvmInputs<'static> {
        TvmInputs {
            now_ns: 1_000_000_000_000,
            issuing_station_id: station,
            product,
            payment,
            account_id: 42,
            secret: b"k",
        }
    }

    #[test]
    fn single_ride_cash_exact_issues_token() {
        let out = tvm_evaluate(
            &TvmState::default(),
            &inputs(
                Product::SingleRide,
                PaymentMethod::Cash { amount_cents: 100 },
                7,
            ),
        );
        match out.outcome {
            TvmOutcome::Issued {
                token,
                change_returned_cents,
            } => {
                assert_eq!(change_returned_cents, 0);
                assert_eq!(token.station_restriction, Some(7));
                let blacklist = BTreeSet::new();
                assert_eq!(
                    validate_token(&token, b"k", 1_000_000_000_000, 7, &blacklist),
                    Decision::Grant
                );
            }
            _ => panic!("expected issue"),
        }
        assert_eq!(out.state.tickets_sold, 1);
        assert_eq!(out.state.revenue_cents, 100);
    }

    #[test]
    fn insufficient_cash_denied() {
        let out = tvm_evaluate(
            &TvmState::default(),
            &inputs(
                Product::DayPass,
                PaymentMethod::Cash { amount_cents: 200 },
                1,
            ),
        );
        assert!(matches!(
            out.outcome,
            TvmOutcome::Denied(TvmDenyReason::InsufficientPayment { .. })
        ));
        assert_eq!(out.state.tickets_sold, 0);
        assert_eq!(out.state.revenue_cents, 0);
    }

    #[test]
    fn change_returned() {
        let out = tvm_evaluate(
            &TvmState::default(),
            &inputs(
                Product::SingleRide,
                PaymentMethod::Cash { amount_cents: 250 },
                1,
            ),
        );
        match out.outcome {
            TvmOutcome::Issued {
                change_returned_cents,
                ..
            } => assert_eq!(change_returned_cents, 150),
            _ => panic!("expected issue"),
        }
    }

    #[test]
    fn mobile_money_settles_at_quoted() {
        let out = tvm_evaluate(
            &TvmState::default(),
            &inputs(
                Product::WeekPass,
                PaymentMethod::MobileMoney {
                    confirmation_code: 9,
                },
                1,
            ),
        );
        match out.outcome {
            TvmOutcome::Issued {
                change_returned_cents,
                ..
            } => assert_eq!(change_returned_cents, 0),
            _ => panic!("expected issue"),
        }
        assert_eq!(out.state.revenue_cents, 2500);
    }

    #[test]
    fn day_pass_is_network_wide() {
        let out = tvm_evaluate(
            &TvmState::default(),
            &inputs(
                Product::DayPass,
                PaymentMethod::Cash { amount_cents: 500 },
                3,
            ),
        );
        if let TvmOutcome::Issued { token, .. } = out.outcome {
            assert_eq!(token.station_restriction, None);
        } else {
            panic!("expected issue");
        }
    }

    #[test]
    fn ttl_matches_product_duration() {
        let out = tvm_evaluate(
            &TvmState::default(),
            &inputs(
                Product::DayPass,
                PaymentMethod::Cash { amount_cents: 500 },
                3,
            ),
        );
        if let TvmOutcome::Issued { token, .. } = out.outcome {
            assert_eq!(
                token.expires_ns - token.issued_ns,
                Product::DayPass.duration_ns()
            );
        }
    }

    #[test]
    fn determinism() {
        let i = inputs(
            Product::SingleRide,
            PaymentMethod::Cash { amount_cents: 100 },
            7,
        );
        let a = tvm_evaluate(&TvmState::default(), &i);
        let b = tvm_evaluate(&TvmState::default(), &i);
        assert_eq!(a, b);
    }
}
