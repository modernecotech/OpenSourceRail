//! Dispatch-hold types.

use serde::{Deserialize, Serialize};

/// Compound key for a dispatch-hold map entry.
///
/// `station_id = 0` is the wildcard that means "all stations on
/// this line"; used by auto-holds from critical incidents.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub struct HoldKey {
    pub line_id: u32,
    pub station_id: u32,
    /// Direction encoded as `0 = Forward`, `1 = Reverse`.
    pub heading: u8,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct DispatchHold {
    pub set_ns: u64,
    pub reason: String,
    /// `true` when the hold was placed by an automatic rule (e.g.,
    /// a Critical incident), `false` when an operator placed it.
    pub auto: bool,
}
