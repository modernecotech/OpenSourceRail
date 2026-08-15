//! Incident log types.

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum IncidentSeverity {
    /// Informational — no operational impact.
    Info,
    /// Service affected but safe to continue.
    Warning,
    /// Significant service disruption.
    Major,
    /// Safety event (fire, derailment, major fault). Auto-holds
    /// dispatch on the affected line.
    Critical,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum IncidentState {
    Open,
    Closed,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct Incident {
    pub id: u64,
    pub severity: IncidentSeverity,
    pub line_id: u32,
    pub description: String,
    pub opened_ns: u64,
    pub closed_ns: Option<u64>,
    pub state: IncidentState,
}
