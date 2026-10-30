//! `OpenSourceRail` cryptographic primitives.
//!
//! Thin, audited-dependency-only wrappers around `RustCrypto`. Every
//! TLS-configuring or MAC-signing crate in the workspace links this
//! crate rather than rolling its own primitives, so there is a
//! single place to change (and a single place to review).
//!
//! Phase 2f infrastructure crate per
//! [RFC 0005 §4.9](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 — a MAC forgery enables fare fraud and (once ed25519 lands)
//! entry spoofing. Not SIL-4: none of these primitives is on the
//! safety-critical brake path.
//!
//! # What this crate provides today
//!
//! - [`Hmac256Key`] — zero-on-drop wrapper around a symmetric key.
//! - [`hmac_sha256`] — compute a 32-byte MAC over a message.
//! - [`hmac_sha256_verify`] — constant-time MAC verification.
//! - [`ct_eq`] — constant-time byte-slice comparison.
//!
//! - [`Ed25519SigningKey`] / [`Ed25519PublicKey`] — ed25519 keypair
//!   wrappers used for signing and verifying consensus log entries
//!   (RFC 0017).
//! - [`ed25519_sign`] — produce a 64-byte signature over a message.
//! - [`ed25519_verify`] — verify a signature against a public key.
//!
//! # Roadmap
//!
//! - X25519 key agreement for session establishment on TRG.
//! - A `rustls` `ServerConfig`/`ClientConfig` builder configured for
//!   IEC 62443-4-2 conformance.
//!
//! # Properties (proptest-verified)
//!
//! - **C1 determinism:** same (key, msg) → same MAC.
//! - **C2 verify accepts honest MAC.**
//! - **C3 verify rejects every bit-flipped MAC.**
//! - **C4 key-sensitivity:** different keys → different MACs
//!   (with overwhelming probability).

#![forbid(unsafe_code)]

use hmac::{Hmac, Mac};
use sha2::Sha256;
use subtle::ConstantTimeEq;

type HmacSha256 = Hmac<Sha256>;

pub const HMAC_SHA256_LEN: usize = 32;

/// Symmetric key for HMAC-SHA256. Held by value, not by reference,
/// so callers explicitly choose where to store it.
#[derive(Clone)]
pub struct Hmac256Key(Vec<u8>);

impl Hmac256Key {
    #[must_use]
    pub fn from_bytes(bytes: impl Into<Vec<u8>>) -> Self {
        Self(bytes.into())
    }

    #[must_use]
    pub fn as_bytes(&self) -> &[u8] {
        &self.0
    }
}

impl core::fmt::Debug for Hmac256Key {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        // Don't print key bytes, even in Debug.
        write!(f, "Hmac256Key(<{} bytes>)", self.0.len())
    }
}

impl Drop for Hmac256Key {
    fn drop(&mut self) {
        // Best-effort zeroisation without pulling in the `zeroize`
        // crate. Compiler may still elide this in release; a follow
        // up will swap to `zeroize` once we're ready to audit the
        // extra `unsafe` hop through its macro.
        for b in &mut self.0 {
            *b = 0;
        }
    }
}

/// Compute HMAC-SHA256 over `msg` with `key`.
///
/// # Panics
///
/// This function does not panic for an HMAC key: HMAC accepts keys of any
/// length. The internal assertion documents that invariant.
#[must_use]
pub fn hmac_sha256(key: &Hmac256Key, msg: &[u8]) -> [u8; HMAC_SHA256_LEN] {
    let mut mac =
        <HmacSha256 as Mac>::new_from_slice(key.as_bytes()).expect("HMAC accepts any key length");
    mac.update(msg);
    let bytes = mac.finalize().into_bytes();
    let mut out = [0u8; HMAC_SHA256_LEN];
    out.copy_from_slice(&bytes);
    out
}

/// Verify a candidate MAC against `msg`. Constant-time.
#[must_use]
pub fn hmac_sha256_verify(key: &Hmac256Key, msg: &[u8], tag: &[u8]) -> bool {
    if tag.len() != HMAC_SHA256_LEN {
        return false;
    }
    let expected = hmac_sha256(key, msg);
    ct_eq(&expected, tag)
}

/// Constant-time equality of two byte slices. Returns `false` for
/// slices of different lengths (length is allowed to be public).
#[must_use]
pub fn ct_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    a.ct_eq(b).into()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hmac_is_stable() {
        let k = Hmac256Key::from_bytes(b"key".to_vec());
        let a = hmac_sha256(&k, b"message");
        let b = hmac_sha256(&k, b"message");
        assert_eq!(a, b);
    }

    #[test]
    fn hmac_differs_across_keys() {
        let m = b"same-message";
        let a = hmac_sha256(&Hmac256Key::from_bytes(b"k1".to_vec()), m);
        let b = hmac_sha256(&Hmac256Key::from_bytes(b"k2".to_vec()), m);
        assert_ne!(a, b);
    }

    #[test]
    fn verify_accepts_honest_tag() {
        let k = Hmac256Key::from_bytes(b"key".to_vec());
        let tag = hmac_sha256(&k, b"msg");
        assert!(hmac_sha256_verify(&k, b"msg", &tag));
    }

    #[test]
    fn verify_rejects_bit_flip() {
        let k = Hmac256Key::from_bytes(b"key".to_vec());
        let mut tag = hmac_sha256(&k, b"msg");
        tag[0] ^= 1;
        assert!(!hmac_sha256_verify(&k, b"msg", &tag));
    }

    #[test]
    fn verify_rejects_wrong_length() {
        let k = Hmac256Key::from_bytes(b"key".to_vec());
        assert!(!hmac_sha256_verify(&k, b"msg", &[0u8; 16]));
    }

    #[test]
    fn ct_eq_matches() {
        assert!(ct_eq(b"abc", b"abc"));
        assert!(!ct_eq(b"abc", b"abd"));
        assert!(!ct_eq(b"abc", b"abcd"));
    }

    #[test]
    fn debug_hides_key_bytes() {
        let k = Hmac256Key::from_bytes(b"very-secret".to_vec());
        let rendered = format!("{:?}", k);
        assert!(!rendered.contains("very-secret"));
        assert!(rendered.contains("11 bytes"));
    }
}

// ---------------------------------------------------------------------------
// Ed25519 (RFC 0017 message authentication)
// ---------------------------------------------------------------------------

use ed25519_dalek::{
    Signature as DalekSignature, Signer, SigningKey as DalekSigningKey, Verifier,
    VerifyingKey as DalekVerifyingKey,
};

pub const ED25519_SIGNATURE_LEN: usize = 64;
pub const ED25519_PUBKEY_LEN: usize = 32;
pub const ED25519_SECRET_LEN: usize = 32;

/// Ed25519 signing key — owns the secret half of a keypair. Produce
/// via [`ed25519_generate`] or restore from persisted 32-byte seed
/// via [`Ed25519SigningKey::from_seed_bytes`].
///
/// Never log or serialise the raw secret. [`Debug`] implementation
/// hides it.
pub struct Ed25519SigningKey(DalekSigningKey);

impl Ed25519SigningKey {
    /// Restore a signing key from a persisted 32-byte seed. The seed
    /// is the secret half of the keypair; it must be stored in the
    /// ATECC608B secure element on production hardware.
    #[must_use]
    pub fn from_seed_bytes(seed: &[u8; ED25519_SECRET_LEN]) -> Self {
        Self(DalekSigningKey::from_bytes(seed))
    }

    /// Public half of this keypair; safe to publish.
    #[must_use]
    pub fn public(&self) -> Ed25519PublicKey {
        Ed25519PublicKey(self.0.verifying_key())
    }
}

impl core::fmt::Debug for Ed25519SigningKey {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "Ed25519SigningKey(<redacted>)")
    }
}

/// Ed25519 public key — 32 bytes; safe to publish.
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct Ed25519PublicKey(DalekVerifyingKey);

impl Ed25519PublicKey {
    /// Bytes form (32 bytes) suitable for serialisation into the key
    /// registry file.
    #[must_use]
    pub fn to_bytes(&self) -> [u8; ED25519_PUBKEY_LEN] {
        self.0.to_bytes()
    }

    /// Restore a public key from its 32-byte form. Returns `None` if
    /// the bytes are not a valid point on the curve.
    #[must_use]
    pub fn from_bytes(bytes: &[u8; ED25519_PUBKEY_LEN]) -> Option<Self> {
        DalekVerifyingKey::from_bytes(bytes).ok().map(Self)
    }
}

impl core::fmt::Debug for Ed25519PublicKey {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        let b = self.0.to_bytes();
        // Shortened hex — public keys are not secret but brevity helps.
        write!(
            f,
            "Ed25519PublicKey({:02x}{:02x}…{:02x}{:02x})",
            b[0], b[1], b[30], b[31]
        )
    }
}

/// Ed25519 signature — 64 bytes.
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub struct Ed25519Signature(pub [u8; ED25519_SIGNATURE_LEN]);

impl core::fmt::Debug for Ed25519Signature {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(
            f,
            "Ed25519Signature({:02x}{:02x}…{:02x}{:02x})",
            self.0[0], self.0[1], self.0[62], self.0[63]
        )
    }
}

/// Generate a fresh ed25519 keypair from the operating-system CSPRNG.
///
/// **Only use in bootstrap tools** (factory provisioning, dev tests).
/// Production deployments mint keys inside the ATECC608B secure
/// element; this helper is intentionally scoped to dev + test paths.
#[must_use]
pub fn ed25519_generate() -> Ed25519SigningKey {
    use rand_core::{OsRng, RngCore};
    let mut seed = [0u8; ED25519_SECRET_LEN];
    OsRng.fill_bytes(&mut seed);
    Ed25519SigningKey(DalekSigningKey::from_bytes(&seed))
}

/// Sign `msg` under `key` and return a 64-byte signature.
#[must_use]
pub fn ed25519_sign(key: &Ed25519SigningKey, msg: &[u8]) -> Ed25519Signature {
    Ed25519Signature(key.0.sign(msg).to_bytes())
}

/// Verify `sig` against `msg` under `key`. Returns `false` for any
/// tampered signature, tampered message, or wrong key.
#[must_use]
pub fn ed25519_verify(key: &Ed25519PublicKey, msg: &[u8], sig: &Ed25519Signature) -> bool {
    let dalek_sig = DalekSignature::from_bytes(&sig.0);
    key.0.verify(msg, &dalek_sig).is_ok()
}

#[cfg(test)]
mod ed25519_tests {
    use super::*;

    #[test]
    fn sign_and_verify_roundtrip() {
        let sk = ed25519_generate();
        let pk = sk.public();
        let sig = ed25519_sign(&sk, b"track state entry");
        assert!(ed25519_verify(&pk, b"track state entry", &sig));
    }

    #[test]
    fn verify_rejects_tampered_message() {
        let sk = ed25519_generate();
        let pk = sk.public();
        let sig = ed25519_sign(&sk, b"original");
        assert!(!ed25519_verify(&pk, b"tampered", &sig));
    }

    #[test]
    fn verify_rejects_bit_flipped_signature() {
        let sk = ed25519_generate();
        let pk = sk.public();
        let mut sig = ed25519_sign(&sk, b"message");
        sig.0[5] ^= 0x01;
        assert!(!ed25519_verify(&pk, b"message", &sig));
    }

    #[test]
    fn verify_rejects_wrong_key() {
        let sk_a = ed25519_generate();
        let sk_b = ed25519_generate();
        let sig = ed25519_sign(&sk_a, b"message");
        assert!(!ed25519_verify(&sk_b.public(), b"message", &sig));
    }

    #[test]
    fn sign_is_deterministic() {
        // Ed25519 signatures are deterministic in the secret key + msg.
        let seed = [7u8; ED25519_SECRET_LEN];
        let sk = Ed25519SigningKey::from_seed_bytes(&seed);
        let a = ed25519_sign(&sk, b"hello");
        let b = ed25519_sign(&sk, b"hello");
        assert_eq!(a.0, b.0);
    }

    #[test]
    fn public_key_roundtrip_through_bytes() {
        let sk = ed25519_generate();
        let pk = sk.public();
        let bytes = pk.to_bytes();
        let restored = Ed25519PublicKey::from_bytes(&bytes).expect("valid point");
        let sig = ed25519_sign(&sk, b"m");
        assert!(ed25519_verify(&restored, b"m", &sig));
    }

    #[test]
    fn debug_hides_signing_key_bytes() {
        let sk = ed25519_generate();
        let rendered = format!("{:?}", sk);
        assert!(rendered.contains("redacted"));
    }
}
