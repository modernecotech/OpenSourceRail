//! Proptests exercising S1–S3 across a wide random-input space.

use osr_core::EntityId;
use osr_crypto::{ed25519_generate, ED25519_SIGNATURE_LEN};
use osr_secbus::{sign_bytes, verify_signed, KeyRegistry, VerifyError};
use proptest::prelude::*;

fn reg_with_issuer(issuer: EntityId, sk: &osr_crypto::Ed25519SigningKey) -> KeyRegistry {
    let mut r = KeyRegistry::new();
    r.insert(issuer, sk.public());
    r
}

proptest! {
    /// S1 — verify_signed is deterministic: same inputs → same output.
    #[test]
    fn s1_verify_deterministic(
        issuer_n in 1u64..=100u64,
        payload in proptest::collection::vec(any::<u8>(), 0..256),
    ) {
        let sk = ed25519_generate();
        let issuer = EntityId::new(issuer_n);
        let reg = reg_with_issuer(issuer, &sk);
        let env = sign_bytes(issuer, payload, &sk);
        let a = verify_signed(&reg, &env);
        let b = verify_signed(&reg, &env);
        prop_assert_eq!(a, b);
        prop_assert!(a.is_ok());
    }

    /// S2 — any single-bit mutation of the signature causes rejection.
    #[test]
    fn s2_bit_flip_in_signature_rejects(
        issuer_n in 1u64..=100u64,
        payload in proptest::collection::vec(any::<u8>(), 1..64),
        byte_idx in 0usize..ED25519_SIGNATURE_LEN,
        bit_idx in 0u8..8u8,
    ) {
        let sk = ed25519_generate();
        let issuer = EntityId::new(issuer_n);
        let reg = reg_with_issuer(issuer, &sk);
        let mut env = sign_bytes(issuer, payload, &sk);
        env.signature[byte_idx] ^= 1 << bit_idx;
        prop_assert_eq!(verify_signed(&reg, &env), Err(VerifyError::BadSignature));
    }

    /// S2 — any single-bit mutation of the payload causes rejection.
    #[test]
    fn s2_bit_flip_in_payload_rejects(
        issuer_n in 1u64..=100u64,
        payload in proptest::collection::vec(any::<u8>(), 1..64),
        byte_idx in 0usize..64usize,
        bit_idx in 0u8..8u8,
    ) {
        let sk = ed25519_generate();
        let issuer = EntityId::new(issuer_n);
        let reg = reg_with_issuer(issuer, &sk);
        let mut env = sign_bytes(issuer, payload, &sk);
        let idx = byte_idx % env.payload.len();
        env.payload[idx] ^= 1 << bit_idx;
        prop_assert_eq!(verify_signed(&reg, &env), Err(VerifyError::BadSignature));
    }

    /// S3 — an envelope whose issuer is absent from the registry
    /// always rejects with UnknownIssuer.
    #[test]
    fn s3_unknown_issuer_always_rejects(
        registered in 1u64..=50u64,
        claimed in 100u64..=200u64,
        payload in proptest::collection::vec(any::<u8>(), 0..64),
    ) {
        let sk = ed25519_generate();
        let reg = reg_with_issuer(EntityId::new(registered), &sk);
        let env = sign_bytes(EntityId::new(claimed), payload, &sk);
        prop_assert_eq!(
            verify_signed(&reg, &env),
            Err(VerifyError::UnknownIssuer)
        );
    }

    /// Honest roundtrip: any valid envelope with the registered issuer
    /// key verifies successfully.
    #[test]
    fn honest_signature_always_verifies(
        issuer_n in 1u64..=100u64,
        payload in proptest::collection::vec(any::<u8>(), 0..512),
    ) {
        let sk = ed25519_generate();
        let issuer = EntityId::new(issuer_n);
        let reg = reg_with_issuer(issuer, &sk);
        let payload_clone = payload.clone();
        let env = sign_bytes(issuer, payload, &sk);
        let out = verify_signed(&reg, &env).expect("honest envelope must verify");
        prop_assert_eq!(out, &payload_clone[..]);
    }
}
