//! Train roster types.

use serde::{Deserialize, Serialize};

/// Per-train situational awareness snapshot.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct RosterEntry {
    pub train_id: u32,
    pub last_seen_ns: u64,
    pub position_section: Option<u32>,
    pub speed_mmps: i32,
    pub any_emergency: bool,
    /// Mirrors `osr_tcms::AlarmLevel` as 0=Nominal, 1=Warning, 2=Trip.
    pub worst_alarm: u8,
    pub soc_ppt: u16,
}

impl RosterEntry {
    #[must_use]
    pub fn default_for(train_id: u32) -> Self {
        Self {
            train_id,
            ..Self::default()
        }
    }
}

/// One telemetry report arriving at the OCC this tick.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TrainReport {
    pub train_id: u32,
    pub now_ns: u64,
    pub position_section: Option<u32>,
    pub speed_mmps: i32,
    pub any_emergency: bool,
    pub worst_alarm: u8,
    pub soc_ppt: u16,
}
