//! Property tests C1–C4.

use osr_crypto::{ct_eq, hmac_sha256, hmac_sha256_verify, Hmac256Key, HMAC_SHA256_LEN};
use proptest::prelude::*;

fn arb_bytes(max: usize) -> impl Strategy<Value = Vec<u8>> {
    prop::collection::vec(any::<u8>(), 1..=max)
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn c1_determinism(key in arb_bytes(64), msg in arb_bytes(256)) {
        let k = Hmac256Key::from_bytes(key);
        let a = hmac_sha256(&k, &msg);
        let b = hmac_sha256(&k, &msg);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn c2_verify_accepts_honest_mac(key in arb_bytes(64), msg in arb_bytes(256)) {
        let k = Hmac256Key::from_bytes(key);
        let tag = hmac_sha256(&k, &msg);
        prop_assert!(hmac_sha256_verify(&k, &msg, &tag));
    }

    #[test]
    fn c3_verify_rejects_bit_flip(
        key in arb_bytes(64),
        msg in arb_bytes(256),
        flip_index in 0usize..HMAC_SHA256_LEN,
        flip_bit in 0u8..8,
    ) {
        let k = Hmac256Key::from_bytes(key);
        let mut tag = hmac_sha256(&k, &msg);
        tag[flip_index] ^= 1u8 << flip_bit;
        prop_assert!(!hmac_sha256_verify(&k, &msg, &tag));
    }

    #[test]
    fn c4_different_keys_different_macs(
        k1 in arb_bytes(64),
        k2 in arb_bytes(64),
        msg in arb_bytes(256),
    ) {
        prop_assume!(k1 != k2);
        let a = hmac_sha256(&Hmac256Key::from_bytes(k1), &msg);
        let b = hmac_sha256(&Hmac256Key::from_bytes(k2), &msg);
        prop_assert_ne!(a, b);
    }

    #[test]
    fn ct_eq_matches_plain_equality(a in arb_bytes(128), b in arb_bytes(128)) {
        prop_assert_eq!(ct_eq(&a, &b), a == b);
    }
}
