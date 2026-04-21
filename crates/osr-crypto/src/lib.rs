//! OpenSourceRail cryptographic primitives.
//!
//! Thin, audited-dependency-only wrappers around RustCrypto. Every
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
//! # Roadmap
//!
//! - ed25519 sign/verify for [`Entry.leader_signature`](osr_proto) —
//!   lands with the first real consensus wire layer.
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
        for b in self.0.iter_mut() {
            *b = 0;
        }
    }
}

/// Compute HMAC-SHA256 over `msg` with `key`.
#[must_use]
pub fn hmac_sha256(key: &Hmac256Key, msg: &[u8]) -> [u8; HMAC_SHA256_LEN] {
    let mut mac = <HmacSha256 as Mac>::new_from_slice(key.as_bytes())
        .expect("HMAC accepts any key length");
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
