//! OpenSourceRail message-authentication bus (SIL-2).
//!
//! Per [RFC 0017](../../docs/rfcs/0017-cybersecurity-message-authentication.md)
//! every entry on the consensus log is signed by the originating
//! entity and verified by every consumer before it reaches derived
//! state.
//!
//! This crate provides the application-layer policy on top of the
//! `osr-crypto` ed25519 primitives:
//!
//! - [`KeyRegistry`] — per-deployment map `EntityId → Ed25519PublicKey`.
//! - [`SignedBytes`] — envelope carrying raw entry bytes + issuer +
//!   signature.
//! - [`sign_bytes`] / [`verify_signed`] — the public API.
//! - [`VerifyError`] — enumerated rejection reasons.
//!
//! # Three SIL-2 properties (S1–S3)
//!
//! - **S1 (determinism):** `verify_signed` is a pure function — same
//!   inputs → same output.
//! - **S2 (reject bad signature):** any single-bit mutation of the
//!   signature causes `verify_signed` to return
//!   `Err(VerifyError::BadSignature)`.
//! - **S3 (reject missing issuer):** an envelope whose `issuer` is
//!   not in the registry rejects with
//!   `Err(VerifyError::UnknownIssuer)`.
//!
//! Each property anchors a Kani harness + a proptest under `tests/`.
//!
//! # Coding-standard compliance
//!
//! - `#![forbid(unsafe_code)]`.
//! - No allocation on the hot `verify_signed` path: the function
//!   takes references and returns a `Result` by value.
//! - `Debug + Clone + PartialEq` on all public types (except the
//!   private-key types which deliberately redact in `Debug`).

#![forbid(unsafe_code)]

use osr_core::EntityId;
use osr_crypto::{
    ed25519_sign, ed25519_verify, Ed25519PublicKey, Ed25519Signature, Ed25519SigningKey,
    ED25519_PUBKEY_LEN, ED25519_SIGNATURE_LEN,
};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[cfg(kani)]
pub mod kani_proofs;

/// Per-deployment registry of public keys, one per authorised
/// entity (train, W-SBC, OCC console, …). Built at bootstrap from
/// the deployment's key-manifest file and queried by the consensus
/// verifier on every inbound entry.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct KeyRegistry {
    keys: BTreeMap<EntityId, Ed25519PublicKey>,
}

impl KeyRegistry {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Register `pk` as the authoritative public key for `entity`.
    /// The **latest** registration wins, overwriting any previous
    /// entry for the same `EntityId`. For v1 this is only called at
    /// bootstrap; v2 (per RFC 0017 §3.5) will drive it from
    /// `KeyRotation` consensus entries.
    pub fn insert(&mut self, entity: EntityId, pk: Ed25519PublicKey) {
        self.keys.insert(entity, pk);
    }

    /// Look up the public key for `entity`. Returns `None` if the
    /// registry has never seen this entity, which causes
    /// `verify_signed` to reject.
    #[must_use]
    pub fn get(&self, entity: EntityId) -> Option<&Ed25519PublicKey> {
        self.keys.get(&entity)
    }

    #[must_use]
    pub fn len(&self) -> usize {
        self.keys.len()
    }

    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.keys.is_empty()
    }
}

/// Signed envelope carrying raw entry bytes (pre-deserialisation)
/// plus issuer + signature. The wire format of a committed
/// consensus entry.
///
/// The payload is opaque bytes — verification happens **before**
/// parsing so a hostile payload cannot exploit a parser bug before
/// the signature check.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SignedBytes {
    pub issuer: EntityId,
    pub payload: Vec<u8>,
    /// 64-byte ed25519 signature. Held as a `Vec<u8>` (not
    /// `[u8; 64]`) only so `serde_derive` works without the
    /// `serde-big-array` dep; the crate always validates the length
    /// on the verify path.
    pub signature: Vec<u8>,
}

impl SignedBytes {
    /// Construct a signed envelope by producing a fresh signature.
    /// The caller owns the signing key; this crate never holds one.
    #[must_use]
    pub fn sign(issuer: EntityId, payload: Vec<u8>, key: &Ed25519SigningKey) -> Self {
        let sig = ed25519_sign(key, &payload);
        Self {
            issuer,
            payload,
            signature: sig.0.to_vec(),
        }
    }
}

/// Verification failures, each naming the specific rejection path.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VerifyError {
    /// The `issuer` is not registered in the deployment's
    /// [`KeyRegistry`]. Covers the "unknown sender" attack (S3).
    UnknownIssuer,
    /// The signature does not verify against the registered public
    /// key for the claimed issuer. Covers the "forged entry" and
    /// "tampered payload" attacks (S2).
    BadSignature,
}

/// Sign `payload` under `key` and wrap it into a [`SignedBytes`].
/// Convenience shortcut for callers that only want one envelope —
/// `SignedBytes::sign` is the primary API.
#[must_use]
pub fn sign_bytes(
    issuer: EntityId,
    payload: Vec<u8>,
    key: &Ed25519SigningKey,
) -> SignedBytes {
    SignedBytes::sign(issuer, payload, key)
}

/// Verify a [`SignedBytes`] against the registry. Returns the
/// opaque payload bytes on success so the caller can deserialise
/// only after authentication.
pub fn verify_signed<'a>(
    registry: &KeyRegistry,
    envelope: &'a SignedBytes,
) -> Result<&'a [u8], VerifyError> {
    let Some(pk) = registry.get(envelope.issuer) else {
        return Err(VerifyError::UnknownIssuer);
    };
    let sig_bytes: &[u8; ED25519_SIGNATURE_LEN] = envelope
        .signature
        .as_slice()
        .try_into()
        .map_err(|_| VerifyError::BadSignature)?;
    let sig = Ed25519Signature(*sig_bytes);
    if !ed25519_verify(pk, &envelope.payload, &sig) {
        return Err(VerifyError::BadSignature);
    }
    Ok(&envelope.payload)
}

// `ED25519_PUBKEY_LEN` is re-exported via the osr-crypto dep; no
// need to reference it from this crate's impl, but callers often
// want a compile-time constant, so we ensure the constant remains
// visible via a documentation anchor.
const _: usize = ED25519_PUBKEY_LEN;

#[cfg(test)]
mod tests {
    use super::*;
    use osr_crypto::ed25519_generate;

    fn entity(n: u64) -> EntityId {
        EntityId::new(n)
    }

    fn registry_with(entity_id: EntityId, key: &Ed25519SigningKey) -> KeyRegistry {
        let mut r = KeyRegistry::new();
        r.insert(entity_id, key.public());
        r
    }

    #[test]
    fn sign_and_verify_roundtrip() {
        let sk = ed25519_generate();
        let issuer = entity(7);
        let reg = registry_with(issuer, &sk);
        let env = sign_bytes(issuer, b"hello".to_vec(), &sk);
        let payload = verify_signed(&reg, &env).expect("must verify");
        assert_eq!(payload, b"hello");
    }

    #[test]
    fn s2_tampered_payload_rejects() {
        let sk = ed25519_generate();
        let issuer = entity(7);
        let reg = registry_with(issuer, &sk);
        let mut env = sign_bytes(issuer, b"original".to_vec(), &sk);
        env.payload[0] ^= 0xFF;
        assert_eq!(verify_signed(&reg, &env), Err(VerifyError::BadSignature));
    }

    #[test]
    fn s2_bit_flipped_signature_rejects() {
        let sk = ed25519_generate();
        let issuer = entity(7);
        let reg = registry_with(issuer, &sk);
        let mut env = sign_bytes(issuer, b"m".to_vec(), &sk);
        env.signature[3] ^= 0x01;
        assert_eq!(verify_signed(&reg, &env), Err(VerifyError::BadSignature));
    }

    #[test]
    fn s3_unknown_issuer_rejects() {
        let sk = ed25519_generate();
        let issuer = entity(7);
        let other = entity(99);
        let reg = registry_with(issuer, &sk);
        let env = sign_bytes(other, b"m".to_vec(), &sk);
        assert_eq!(verify_signed(&reg, &env), Err(VerifyError::UnknownIssuer));
    }

    #[test]
    fn s1_verify_is_deterministic() {
        let sk = ed25519_generate();
        let issuer = entity(7);
        let reg = registry_with(issuer, &sk);
        let env = sign_bytes(issuer, b"m".to_vec(), &sk);
        let r1 = verify_signed(&reg, &env);
        let r2 = verify_signed(&reg, &env);
        assert_eq!(r1, r2);
        assert!(r1.is_ok());
    }

    #[test]
    fn wrong_key_registered_rejects() {
        // Issuer signs with key A; registry publishes key B for that
        // same issuer — verification must fail with BadSignature
        // (not UnknownIssuer, because the issuer IS registered).
        let sk_a = ed25519_generate();
        let sk_b = ed25519_generate();
        let issuer = entity(7);
        let reg = registry_with(issuer, &sk_b); // wrong public key
        let env = sign_bytes(issuer, b"m".to_vec(), &sk_a);
        assert_eq!(verify_signed(&reg, &env), Err(VerifyError::BadSignature));
    }

    #[test]
    fn registry_latest_insert_wins() {
        let sk_a = ed25519_generate();
        let sk_b = ed25519_generate();
        let issuer = entity(7);
        let mut reg = KeyRegistry::new();
        reg.insert(issuer, sk_a.public());
        reg.insert(issuer, sk_b.public()); // rotation-style overwrite
        // Signatures from sk_a must now fail (old key).
        let env_a = sign_bytes(issuer, b"m".to_vec(), &sk_a);
        assert_eq!(verify_signed(&reg, &env_a), Err(VerifyError::BadSignature));
        // Signatures from sk_b must succeed (new key).
        let env_b = sign_bytes(issuer, b"m".to_vec(), &sk_b);
        assert!(verify_signed(&reg, &env_b).is_ok());
    }
}
