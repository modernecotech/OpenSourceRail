//! Fare-token wire format.

use serde::{Deserialize, Serialize};

/// Size of the signed portion of [`FareToken`] in bytes.
/// `account_id` (4) + `issued_ns` (8) + `expires_ns` (8) +
/// `station_restriction_tag` (1) + `station_restriction_value` (4) = 25.
pub const SIGNED_BYTE_LEN: usize = 25;

/// Account-based fare token. Issued by [`crate::sign_token`] (by
/// `osr-tvm` or a mobile-money back-office), validated by
/// [`crate::validate_token`] at the gate.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct FareToken {
    pub account_id: u32,
    pub issued_ns: u64,
    pub expires_ns: u64,
    /// `None` means "valid at any station in the network";
    /// `Some(s)` restricts to station `s` only (single-ride ticket
    /// into that station).
    pub station_restriction: Option<u32>,
    /// SipHash-13 of the signed portion XOR-mixed with the shared
    /// secret. See `crate::validate::sign_token`.
    pub signature: u64,
}

impl FareToken {
    /// Serialise the signed portion (everything except `signature`)
    /// into a fixed-size byte buffer, exactly [`SIGNED_BYTE_LEN`]
    /// bytes. Deterministic and endian-normalised (little-endian).
    #[must_use]
    pub fn signed_bytes(&self) -> [u8; SIGNED_BYTE_LEN] {
        let mut out = [0_u8; SIGNED_BYTE_LEN];
        out[0..4].copy_from_slice(&self.account_id.to_le_bytes());
        out[4..12].copy_from_slice(&self.issued_ns.to_le_bytes());
        out[12..20].copy_from_slice(&self.expires_ns.to_le_bytes());
        let (tag, val) = match self.station_restriction {
            None => (0, 0_u32),
            Some(s) => (1, s),
        };
        out[20] = tag;
        out[21..25].copy_from_slice(&val.to_le_bytes());
        out
    }
}
