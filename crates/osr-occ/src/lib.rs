//! OpenSourceRail Operations Control Centre (OCC).
//!
//! The OCC is the dispatcher's seat. This crate holds the
//! authoritative operational state — known trains, their last
//! position / speed, active incidents, and dispatch holds — and
//! provides a pure evaluator that folds arriving telemetry into
//! that state. The web / HMI layer that humans interact with
//! renders this state; safety-relevant dispatch decisions are
//! enforced downstream by [`osr_interlocking`] and the SIL-4
//! partition.
//!
//! Phase 2e crate of [RFC 0005 §4.8](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2: a bad dispatch decision here can degrade service or
//! strand passengers but will not cause motion onto occupied
//! track — the interlocking has final say on every movement.
//!
//! # Scope
//!
//! - **Train roster** — keyed by train ID, holds last-known
//!   position / speed / alarm / consist_status / last-seen timestamp.
//! - **Incident log** — append-only, with open/closed state and
//!   severity.
//! - **Dispatch holds** — a map `(line, station, heading) → hold?`
//!   that [`osr_interlocking`] consumers read to decide whether a
//!   train may depart.
//!
//! # Properties
//!
//! - **OCC1 determinism.**
//! - **OCC2 telemetry monotone in time:** the roster entry for a
//!   train is only updated by a report whose `now_ns` is ≥ the
//!   stored value (stale-update suppression).
//! - **OCC3 incident open/close invariant:** an incident's
//!   `closed_ns` is set iff `state == Closed`.
//! - **OCC4 emergency incidents auto-hold dispatch on their line**
//!   (a Critical-severity incident on line L sets the hold on all
//!   stations of L).

#![forbid(unsafe_code)]

pub mod dispatch;
pub mod incident;
pub mod roster;

pub use dispatch::{DispatchHold, HoldKey};
pub use incident::{Incident, IncidentSeverity, IncidentState};
pub use roster::{RosterEntry, TrainReport};

use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

/// The authoritative OCC state.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct OccState {
    /// Known trains keyed by ID.
    pub roster: BTreeMap<u32, RosterEntry>,
    /// Incident log keyed by incident ID.
    pub incidents: BTreeMap<u64, Incident>,
    /// Active dispatch holds.
    pub holds: BTreeMap<HoldKey, DispatchHold>,
    /// Next incident ID to assign.
    pub next_incident_id: u64,
}

/// Inputs for one OCC tick.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct OccInputs {
    pub now_ns: u64,
    /// Telemetry reports arriving this tick.
    pub train_reports: Vec<TrainReport>,
    /// New incidents declared this tick.
    pub new_incidents: Vec<NewIncident>,
    /// Incidents to close this tick (by ID).
    pub close_incident_ids: Vec<u64>,
    /// Manual dispatch holds (operator placed / cleared).
    pub manual_holds_set: Vec<HoldKey>,
    pub manual_holds_clear: Vec<HoldKey>,
}

/// Incident to be opened this tick. ID is assigned by the OCC.
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct NewIncident {
    pub severity: IncidentSeverity,
    pub line_id: u32,
    pub description: String,
}

/// What the OCC produces each tick — a complete roster view for
/// the HMI plus a diff of observable changes.
#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct OccOutput {
    pub state: OccState,
    /// Newly-opened incident IDs this tick.
    pub opened_incident_ids: Vec<u64>,
    /// Newly-closed incident IDs this tick.
    pub closed_incident_ids: Vec<u64>,
    /// Hold keys set / cleared as side-effects of incidents.
    pub auto_holds_set: Vec<HoldKey>,
    pub auto_holds_cleared: Vec<HoldKey>,
}

pub fn occ_evaluate(prev: &OccState, inputs: &OccInputs) -> OccOutput {
    let mut state = prev.clone();
    let mut opened = Vec::new();
    let mut closed = Vec::new();
    let mut auto_set = Vec::new();
    let mut auto_cleared = Vec::new();

    // 1. Fold telemetry into roster (OCC2 monotone-in-time).
    for rep in &inputs.train_reports {
        let entry = state
            .roster
            .entry(rep.train_id)
            .or_insert_with(|| RosterEntry::default_for(rep.train_id));
        if rep.now_ns >= entry.last_seen_ns {
            entry.last_seen_ns = rep.now_ns;
            entry.position_section = rep.position_section;
            entry.speed_mmps = rep.speed_mmps;
            entry.any_emergency = rep.any_emergency;
            entry.worst_alarm = rep.worst_alarm;
            entry.soc_ppt = rep.soc_ppt;
        }
    }

    // 2. Close incidents as requested.
    for id in &inputs.close_incident_ids {
        if let Some(inc) = state.incidents.get_mut(id) {
            if inc.state == IncidentState::Open {
                inc.state = IncidentState::Closed;
                inc.closed_ns = Some(inputs.now_ns);
                closed.push(*id);
                // Clear any auto-hold from this incident.
                if inc.severity == IncidentSeverity::Critical {
                    // Clear all auto-holds on the incident's line.
                    let line = inc.line_id;
                    let to_clear: Vec<HoldKey> = state
                        .holds
                        .iter()
                        .filter(|(k, h)| k.line_id == line && h.auto)
                        .map(|(k, _)| *k)
                        .collect();
                    for k in to_clear {
                        state.holds.remove(&k);
                        auto_cleared.push(k);
                    }
                }
            }
        }
    }

    // 3. Open new incidents.
    for ni in &inputs.new_incidents {
        let id = state.next_incident_id;
        state.next_incident_id = state.next_incident_id.saturating_add(1);
        let inc = Incident {
            id,
            severity: ni.severity,
            line_id: ni.line_id,
            description: ni.description.clone(),
            opened_ns: inputs.now_ns,
            closed_ns: None,
            state: IncidentState::Open,
        };
        state.incidents.insert(id, inc);
        opened.push(id);
        // OCC4: Critical severity auto-holds the whole line.
        if ni.severity == IncidentSeverity::Critical {
            // Represent "hold the line" as a single wildcard hold
            // keyed by (line, 0, Forward) — the OCC's HMI maps this
            // to "hold all dispatch points." A real system would
            // enumerate stations; this minimal v1 uses a single
            // aggregate key per line.
            let key = HoldKey {
                line_id: ni.line_id,
                station_id: 0,
                heading: 0,
            };
            state.holds.insert(
                key,
                DispatchHold {
                    set_ns: inputs.now_ns,
                    reason: format!("incident {}", id),
                    auto: true,
                },
            );
            auto_set.push(key);
        }
    }

    // 4. Manual hold adjustments.
    for k in &inputs.manual_holds_set {
        state.holds.insert(
            *k,
            DispatchHold {
                set_ns: inputs.now_ns,
                reason: "operator".to_string(),
                auto: false,
            },
        );
    }
    for k in &inputs.manual_holds_clear {
        state.holds.remove(k);
    }

    OccOutput {
        state,
        opened_incident_ids: opened,
        closed_incident_ids: closed,
        auto_holds_set: auto_set,
        auto_holds_cleared: auto_cleared,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn report(train: u32, now_ns: u64, section: u32, speed: i32) -> TrainReport {
        TrainReport {
            train_id: train,
            now_ns,
            position_section: Some(section),
            speed_mmps: speed,
            any_emergency: false,
            worst_alarm: 0,
            soc_ppt: 800,
        }
    }

    #[test]
    fn empty_tick_no_change() {
        let out = occ_evaluate(&OccState::default(), &OccInputs::default());
        assert!(out.state.roster.is_empty());
        assert!(out.state.incidents.is_empty());
    }

    #[test]
    fn telemetry_builds_roster() {
        let mut i = OccInputs::default();
        i.now_ns = 1_000_000_000;
        i.train_reports = vec![report(7, 1_000_000_000, 1000, 15_000)];
        let out = occ_evaluate(&OccState::default(), &i);
        let entry = out.state.roster.get(&7).unwrap();
        assert_eq!(entry.position_section, Some(1000));
        assert_eq!(entry.speed_mmps, 15_000);
    }

    #[test]
    fn stale_update_suppressed() {
        let mut state = OccState::default();
        let mut e = RosterEntry::default_for(7);
        e.last_seen_ns = 1_000_000_000;
        e.speed_mmps = 15_000;
        state.roster.insert(7, e);

        let mut i = OccInputs::default();
        i.now_ns = 500_000_000;
        i.train_reports = vec![report(7, 500_000_000, 1000, 0)]; // older
        let out = occ_evaluate(&state, &i);
        let entry = out.state.roster.get(&7).unwrap();
        assert_eq!(entry.last_seen_ns, 1_000_000_000);
        assert_eq!(entry.speed_mmps, 15_000); // not overwritten
    }

    #[test]
    fn critical_incident_auto_holds_line() {
        let mut i = OccInputs::default();
        i.now_ns = 1;
        i.new_incidents = vec![NewIncident {
            severity: IncidentSeverity::Critical,
            line_id: 1,
            description: "fire at platform 3".into(),
        }];
        let out = occ_evaluate(&OccState::default(), &i);
        assert_eq!(out.opened_incident_ids, vec![0]);
        let key = HoldKey {
            line_id: 1,
            station_id: 0,
            heading: 0,
        };
        assert!(out.state.holds.contains_key(&key));
        assert!(out.state.holds[&key].auto);
    }

    #[test]
    fn closing_critical_incident_clears_auto_hold() {
        let mut s1 = OccState::default();
        let out = occ_evaluate(
            &s1,
            &OccInputs {
                now_ns: 1,
                new_incidents: vec![NewIncident {
                    severity: IncidentSeverity::Critical,
                    line_id: 1,
                    description: "X".into(),
                }],
                ..Default::default()
            },
        );
        s1 = out.state;
        assert!(!s1.holds.is_empty());
        let id = out.opened_incident_ids[0];

        let out = occ_evaluate(
            &s1,
            &OccInputs {
                now_ns: 10,
                close_incident_ids: vec![id],
                ..Default::default()
            },
        );
        assert_eq!(out.closed_incident_ids, vec![id]);
        assert!(out.state.holds.is_empty());
        assert_eq!(out.state.incidents[&id].state, IncidentState::Closed);
    }

    #[test]
    fn manual_hold_set_and_cleared() {
        let key = HoldKey {
            line_id: 1,
            station_id: 5,
            heading: 0,
        };
        let out = occ_evaluate(
            &OccState::default(),
            &OccInputs {
                now_ns: 1,
                manual_holds_set: vec![key],
                ..Default::default()
            },
        );
        assert!(out.state.holds.contains_key(&key));
        let out = occ_evaluate(
            &out.state,
            &OccInputs {
                now_ns: 10,
                manual_holds_clear: vec![key],
                ..Default::default()
            },
        );
        assert!(!out.state.holds.contains_key(&key));
    }

    #[test]
    fn determinism() {
        let mut i = OccInputs::default();
        i.now_ns = 1_000_000_000;
        i.train_reports = vec![report(1, 1_000_000_000, 1, 100)];
        i.new_incidents = vec![NewIncident {
            severity: IncidentSeverity::Warning,
            line_id: 1,
            description: "test".into(),
        }];
        let a = occ_evaluate(&OccState::default(), &i);
        let b = occ_evaluate(&OccState::default(), &i);
        assert_eq!(a, b);
    }
}
