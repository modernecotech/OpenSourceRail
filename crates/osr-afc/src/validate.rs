//! Token signing and validation.
//!
//! Signatures are HMAC-SHA256 tags over [`FareToken::signed_bytes`]
//! under the shared back-office secret, produced and verified via
//! [`osr_crypto`]. Comparison uses [`osr_crypto::ct_eq`] for
//! constant-time MAC verification — a timing side-channel on the
//! gate would let an attacker iterate tags without tripping the
//! blacklist path.

use std::collections::BTreeSet;

use osr_crypto::{ct_eq, hmac_sha256, Hmac256Key, HMAC_SHA256_LEN};
use serde::{Deserialize, Serialize};

use crate::token::FareToken;

/// Why a token was refused.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum DenyReason {
    /// `expires_ns` already passed at `now_ns`.
    Expired,
    /// Signature did not match the computed value for the shared secret.
    BadSignature,
    /// Token restricted to a different station than the gate.
    WrongStation,
    /// Token ID is on the blacklist (lost / stolen / cloned).
    Blacklisted,
    /// `issued_ns` is in the future (clock skew or forgery).
    NotYetValid,
}

/// Grant/Deny decision, with reason on denial.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Decision {
    Grant,
    Deny(DenyReason),
}

/// Compute the HMAC-SHA256 tag for `token_fields` under `secret`.
/// Pure; deterministic over `(token.signed_bytes(), secret)`.
#[must_use]
pub fn sign_token(token_fields: &FareToken, secret: &[u8]) -> [u8; HMAC_SHA256_LEN] {
    let key = Hmac256Key::from_bytes(secret.to_vec());
    hmac_sha256(&key, &token_fields.signed_bytes())
}

/// Validate a token for a given gate / now / blacklist.
///
/// Pure. See the crate-level safety properties AFC2–AFC5.
#[must_use]
pub fn validate_token(
    token: &FareToken,
    secret: &[u8],
    now_ns: u64,
    gate_station_id: u32,
    blacklist: &BTreeSet<u32>,
) -> Decision {
    if blacklist.contains(&token.account_id) {
        return Decision::Deny(DenyReason::Blacklisted);
    }
    let expected = sign_token(token, secret);
    if !ct_eq(&expected, &token.signature) {
        return Decision::Deny(DenyReason::BadSignature);
    }
    if token.issued_ns > now_ns {
        return Decision::Deny(DenyReason::NotYetValid);
    }
    if token.expires_ns <= now_ns {
        return Decision::Deny(DenyReason::Expired);
    }
    if let Some(s) = token.station_restriction {
        if s != gate_station_id {
            return Decision::Deny(DenyReason::WrongStation);
        }
    }
    Decision::Grant
}
