//! Payload trait + traffic class.

use serde::{de::DeserializeOwned, Serialize};

/// Traffic class for a payload. Drives the mock transport's
/// back-pressure policy and, in a real transport, the 802.1Q PCP.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub enum TrafficClass {
    /// SIL-4 bus — never drops, always delivered. PCP 7 in the
    /// production TSN profile.
    Safety,
    /// Control-loop bus — generous queue, drops after sustained
    /// overflow. PCP 5.
    Control,
    /// Best-effort application traffic. PCP 3.
    App,
}

/// Trait for any struct that can be sent on TCN.
///
/// The `Serialize + DeserializeOwned` bound lets the v1 mock
/// use `serde_json` for wire format. A real hardware transport
/// will switch to a compact fixed-layout encoding per RFC 0006
/// §6 — the trait boundary stays stable.
pub trait TcnPayload: Clone + core::fmt::Debug + PartialEq + Serialize + DeserializeOwned {
    /// Traffic class — fixed at the type level so a topic's class
    /// cannot drift at runtime.
    const CLASS: TrafficClass;
}
