//! OpenSourceRail Automatic Fare Collection (AFC).
//!
//! Per [ARCHITECTURE.md §D4](../../../docs/ARCHITECTURE.md#d4-passenger-services)
//! OpenSourceRail is account-based first: passengers present short-TTL
//! signed tokens (issued by [`osr_tvm`] or a mobile-money back-office)
//! to a fare gate, which validates them *offline* against a shared
//! secret. This crate ships:
//!
//! - [`FareToken`] — the token wire format.
//! - [`validate_token`] — pure validation against `(secret, now, station, blacklist)`.
//! - [`afc_evaluate`] — the gate state machine (scanner → validation →
//!   gate command → event).
//!
//! Phase 2e crate 1 of [RFC 0005 §4.7](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0 — fare evasion is a revenue issue, not a safety hazard. The
//! integrity story is cryptographic (HMAC) and operational
//! (blacklisting), not safety-rated.
//!
//! # Token signing
//!
//! Tokens are signed with HMAC-SHA256 from [`osr_crypto`] over
//! [`FareToken::signed_bytes`]. Signature comparison is constant-time
//! to keep a compromised gate from being turned into a MAC oracle
//! via timing. Key rotation and distribution live outside this
//! crate (in the back-office key-management service).
//!
//! # Properties (proptest-verified)
//!
//! - **AFC1 determinism.**
//! - **AFC2 expired token denied:** `expires_ns ≤ now_ns` ⇒ Deny.
//! - **AFC3 bad signature denied:** any bit flip in the signed
//!   region invalidates the token.
//! - **AFC4 wrong-station denied:** a token with
//!   `station_restriction = Some(S)` presented at a gate with a
//!   different station id is denied.
//! - **AFC5 blacklisted token denied** regardless of other fields.
//! - **AFC6 honest-token granted.**
//! - **AFC7 gate open iff decision == Grant.**

#![forbid(unsafe_code)]

pub mod evaluate;
pub mod token;
pub mod validate;

pub use evaluate::{afc_evaluate, AfcEvent, AfcInputs, AfcOutput, AfcParams, AfcState, GateCommand};
pub use osr_crypto::HMAC_SHA256_LEN;
pub use token::{FareToken, SIGNED_BYTE_LEN};
pub use validate::{sign_token, validate_token, Decision, DenyReason};
