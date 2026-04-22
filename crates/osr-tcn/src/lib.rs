//! OpenSourceRail Train Communication Network (TCN).
//!
//! v1 per [RFC 0006](../../../docs/rfcs/0006-osr-tcn-design.md):
//! topic-addressed publish/subscribe with traffic-class-aware
//! back-pressure, an in-memory mock transport, and a compact
//! payload trait. Real TSN hardware transport is deferred
//! (RFC 0006 §11 v3).
//!
//! Phase 2c final crate of [RFC 0005](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # The three traffic classes
//!
//! - **`Safety`** — never drops. Queue sized to absorb worst-case
//!   bursts. Used for MA envelope, brake-apply, position reports,
//!   emergency monitor outputs.
//! - **`Control`** — bounded queue; drops under sustained overflow.
//!   Used for torque setpoints, BMS limits, door status.
//! - **`App`** — smaller bounded queue; drops readily. Used for
//!   HVAC / lighting / PIS / DMI / event records.
//!
//! The per-class capacity is configurable; defaults are sized for
//! the reference 3-car light metro (RFC 0003 §4.3).
//!
//! # API shape
//!
//! - [`TopicRegistry`] — static string ↔ `u16` interning.
//! - [`TcnPayload`] trait — any type implementing
//!   `Serialize + DeserializeOwned` can be a payload. Each payload
//!   declares its `TrafficClass`.
//! - [`MockTcn`] — in-memory transport for unit tests and the
//!   simulator shadow.
//!
//! # Properties (proptest-verified)
//!
//! - **T1 round-trip identity:** `recv(publish(p)) == p` for any
//!   `TcnPayload` p.
//! - **T2 FIFO per topic:** `recv` in publish order.
//! - **T3 Safety never drops:** stress-publishing a Safety payload
//!   never exceeds the reserved capacity such that later `recv` is
//!   missing; the queue must be sized generously.
//! - **T4 App drops under back-pressure:** when app-class capacity
//!   is N and N+k messages are published, k are counted as drops
//!   and the first N (or last N, per policy) survive.
//! - **T5 topic isolation:** `publish(A, p)` never appears on
//!   `recv(B)` for A ≠ B.

#![forbid(unsafe_code)]

pub mod mock;
pub mod payload;
pub mod registry;
pub mod udp;

pub use mock::{MockTcn, TcnError};
pub use payload::{TcnPayload, TrafficClass};
pub use registry::{TopicId, TopicRegistry};
pub use udp::{UdpTcn, HEADER_LEN, MAX_PAYLOAD_LEN};
