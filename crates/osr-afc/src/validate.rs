//! Token signing and validation.
//!
//! v1 uses the standard-library SipHash-13 hasher (via
//! `std::collections::hash_map::DefaultHasher`) as a placeholder
//! HMAC. SipHash is designed for hash-table integrity, not
//! cryptographic authentication; a production deployment must
//! replace this with HMAC-SHA256 from `osr-crypto` once that
//! crate lands. The algorithm seam is isolated to a single
//! function ([`sign_token`]) so the swap is straightforward.

use std::collections::hash_map::DefaultHasher;
use std::collections::BTreeSet;
use std::hash::{Hash, Hasher};

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

/// Compute the signature for a token. Pure; deterministic over
/// `(token.signed_bytes(), secret)`.
#[must_use]
pub fn sign_token(token_fields: &FareToken, secret: &[u8]) -> u64 {
    let mut h = DefaultHasher::new();
    secret.hash(&mut h);
    token_fields.signed_bytes().hash(&mut h);
    // Fold the secret a second time with the bytes to approximate
    // HMAC's inner-outer composition. Not cryptographically sound;
    // see module docs.
    let round1 = h.finish();
    let mut h2 = DefaultHasher::new();
    secret.hash(&mut h2);
    round1.hash(&mut h2);
    h2.finish()
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
    // Recompute signature and compare in constant-ish time via
    // equality (SipHash is not a cryptographic MAC but the equality
    // check is still the right shape for a real MAC later).
    let expected = sign_token(token, secret);
    if expected != token.signature {
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
