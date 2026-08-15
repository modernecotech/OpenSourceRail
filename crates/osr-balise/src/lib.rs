//! OpenSourceRail wayside balise registry + sighting audit.
//!
//! Balises are passive transponders embedded in the track at
//! surveyed points (platform edges, switches, section boundaries).
//! The train's antenna reads them and reports the ID via
//! [`osr_odometry::BaliseFix`]; this wayside crate provides:
//!
//! - a **canonical registry** mapping `BaliseId → surveyed position +
//!   installation metadata`, consulted during commissioning and
//!   safety-case audit,
//! - a **sighting auditor** that consumes train position reports
//!   and the expected-sightings list, flagging missed or extra
//!   balises for maintenance.
//!
//! Phase 2d crate of [RFC 0005 §4.6](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2: the primary position fix is still the onboard odometry;
//! a missing balise degrades confidence and triggers a maintenance
//! work order but does not directly endanger passengers.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize, Deserialize)]
pub struct BaliseId(pub u32);

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum BaliseType {
    #[default]
    Passive,
    Active,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct SurveyedPosition {
    pub section_id: u32,
    pub offset_mm: i64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct BaliseRecord {
    pub id: BaliseId,
    pub balise_type: BaliseType,
    pub position: SurveyedPosition,
    /// Commissioning timestamp (ns-since-epoch).
    pub installed_ns: u64,
    /// Last known healthy sighting time.
    pub last_seen_ns: Option<u64>,
    /// Expected-sighting age before marking `Missing`.
    pub stale_after_ns: u64,
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct BaliseRegistry {
    pub by_id: BTreeMap<BaliseId, BaliseRecord>,
}

impl BaliseRegistry {
    pub fn insert(&mut self, record: BaliseRecord) {
        self.by_id.insert(record.id, record);
    }

    #[must_use]
    pub fn get(&self, id: BaliseId) -> Option<&BaliseRecord> {
        self.by_id.get(&id)
    }

    /// Update the last-seen timestamp for an observed balise.
    /// Called whenever a `BaliseFix` is committed to the log.
    pub fn mark_seen(&mut self, id: BaliseId, now_ns: u64) {
        if let Some(rec) = self.by_id.get_mut(&id) {
            rec.last_seen_ns = Some(now_ns);
        }
    }
}

// ---------------------------------------------------------------------------
// Sighting audit
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum SightingEvent {
    /// Balise id was sighted; position matched the registry.
    Seen { id: BaliseId, now_ns: u64 },
    /// Balise id was sighted but its claimed position disagrees
    /// with the survey (possible sensor fault or installation
    /// error).
    PositionMismatch {
        id: BaliseId,
        claimed: SurveyedPosition,
        surveyed: SurveyedPosition,
    },
    /// An unknown id was reported — not in registry.
    Unknown { id: BaliseId },
    /// A balise has not been sighted in longer than its
    /// `stale_after_ns` window.
    Stale {
        id: BaliseId,
        last_seen_ns: Option<u64>,
    },
}

/// One passing train's balise sighting.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SightingReport {
    pub id: BaliseId,
    pub reported_position: SurveyedPosition,
    pub now_ns: u64,
}

/// Process a batch of sighting reports against the registry.
/// Pure: consumes the input but does NOT mutate the registry
/// (caller chooses when to apply).
#[must_use]
pub fn audit_sightings(
    registry: &BaliseRegistry,
    reports: &[SightingReport],
    now_ns: u64,
) -> Vec<SightingEvent> {
    let mut events = Vec::new();

    for rep in reports {
        match registry.get(rep.id) {
            None => events.push(SightingEvent::Unknown { id: rep.id }),
            Some(rec) => {
                if rec.position == rep.reported_position {
                    events.push(SightingEvent::Seen {
                        id: rep.id,
                        now_ns: rep.now_ns,
                    });
                } else {
                    events.push(SightingEvent::PositionMismatch {
                        id: rep.id,
                        claimed: rep.reported_position,
                        surveyed: rec.position,
                    });
                }
            }
        }
    }

    // Sweep for stale balises.
    for (id, rec) in &registry.by_id {
        let last = rec.last_seen_ns.unwrap_or(rec.installed_ns);
        if now_ns.saturating_sub(last) >= rec.stale_after_ns {
            events.push(SightingEvent::Stale {
                id: *id,
                last_seen_ns: rec.last_seen_ns,
            });
        }
    }

    events
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn record(id: u32, sec: u32, off: i64) -> BaliseRecord {
        BaliseRecord {
            id: BaliseId(id),
            balise_type: BaliseType::Passive,
            position: SurveyedPosition {
                section_id: sec,
                offset_mm: off,
            },
            installed_ns: 0,
            last_seen_ns: Some(0),
            stale_after_ns: 86_400_000_000_000, // 24 h
        }
    }

    #[test]
    fn unknown_id_reports_unknown() {
        let reg = BaliseRegistry::default();
        let ev = audit_sightings(
            &reg,
            &[SightingReport {
                id: BaliseId(99),
                reported_position: SurveyedPosition {
                    section_id: 1,
                    offset_mm: 0,
                },
                now_ns: 0,
            }],
            0,
        );
        assert!(matches!(ev[0], SightingEvent::Unknown { .. }));
    }

    #[test]
    fn matching_position_is_seen() {
        let mut reg = BaliseRegistry::default();
        reg.insert(record(5, 100, 200_000));
        let ev = audit_sightings(
            &reg,
            &[SightingReport {
                id: BaliseId(5),
                reported_position: SurveyedPosition {
                    section_id: 100,
                    offset_mm: 200_000,
                },
                now_ns: 1000,
            }],
            1000,
        );
        let is_seen = ev.iter().any(|e| matches!(e, SightingEvent::Seen { .. }));
        assert!(is_seen);
    }

    #[test]
    fn position_mismatch_flagged() {
        let mut reg = BaliseRegistry::default();
        reg.insert(record(5, 100, 200_000));
        let ev = audit_sightings(
            &reg,
            &[SightingReport {
                id: BaliseId(5),
                reported_position: SurveyedPosition {
                    section_id: 100,
                    offset_mm: 999_999,
                },
                now_ns: 1000,
            }],
            1000,
        );
        let mismatch = ev
            .iter()
            .any(|e| matches!(e, SightingEvent::PositionMismatch { .. }));
        assert!(mismatch);
    }

    #[test]
    fn stale_balise_flagged() {
        let mut reg = BaliseRegistry::default();
        let mut r = record(5, 100, 0);
        r.stale_after_ns = 1000;
        r.last_seen_ns = Some(0);
        reg.insert(r);
        let ev = audit_sightings(&reg, &[], 10_000);
        let stale = ev.iter().any(|e| matches!(e, SightingEvent::Stale { .. }));
        assert!(stale);
    }

    #[test]
    fn mark_seen_updates_record() {
        let mut reg = BaliseRegistry::default();
        reg.insert(record(5, 100, 0));
        reg.mark_seen(BaliseId(5), 5000);
        assert_eq!(reg.get(BaliseId(5)).unwrap().last_seen_ns, Some(5000));
    }
}
