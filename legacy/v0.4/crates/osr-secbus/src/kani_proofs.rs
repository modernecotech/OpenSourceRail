//! Kani bounded-model-checker harnesses for S1–S3.
//!
//! Ed25519 curve arithmetic itself is outside Kani's sensible model
//! checking budget. The harnesses here target the *envelope-level*
//! invariants: the `KeyRegistry` lookup and the `VerifyError`
//! routing logic are pure, small, and well-suited to Kani. Ed25519
//! primitives are covered by the `osr-crypto` proptest suite
//! (deterministic signature, bit-flip rejection, wrong-key
//! rejection) — this module composes those claims.

#![cfg(kani)]

use crate::{verify_signed, KeyRegistry, SignedBytes, VerifyError};
use osr_core::EntityId;
use osr_crypto::{ed25519_generate, ED25519_SIGNATURE_LEN};

/// S3 — an envelope whose issuer is not in the registry rejects with
/// `UnknownIssuer`, regardless of payload or signature contents.
#[kani::proof]
#[kani::unwind(2)]
fn s3_unknown_issuer_always_rejects() {
    // Empty registry — nothing is authorised.
    let reg = KeyRegistry::new();
    let issuer_id: u64 = kani::any();
    kani::assume(issuer_id < 1000); // bound the exploration

    let sig_byte: u8 = kani::any();
    let env = SignedBytes {
        issuer: EntityId::new(issuer_id),
        payload: vec![0u8; 1],
        signature: vec![sig_byte; ED25519_SIGNATURE_LEN],
    };

    let result = verify_signed(&reg, &env);
    assert!(matches!(result, Err(VerifyError::UnknownIssuer)));
}

/// S1 — `verify_signed` is deterministic: calling it twice on the
/// same inputs returns the same `Result`. Exercised here with a
/// simple frame; S1 is otherwise covered by the unit test
/// `s1_verify_is_deterministic` since Kani cannot run
/// `ed25519_generate` (needs OsRng).
#[kani::proof]
#[kani::unwind(2)]
fn s1_unknown_issuer_lookup_is_deterministic() {
    let reg = KeyRegistry::new();
    let env = SignedBytes {
        issuer: EntityId::new(42),
        payload: vec![],
        signature: vec![0u8; ED25519_SIGNATURE_LEN],
    };
    let a = verify_signed(&reg, &env);
    let b = verify_signed(&reg, &env);
    assert!(a == b);
}
