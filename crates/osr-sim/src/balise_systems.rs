//! Deterministic wayside-balise registry and onboard sighting integration.
//!
//! Every directed section receives one passive calibration balise ten metres
//! beyond its origin (or at the midpoint for an unusually short section).
//! The registry is derived from the generated topology in stable section-id
//! order, so city regeneration and repeated simulation runs produce the same
//! identifiers and positions without a second hand-maintained asset list.

use std::collections::BTreeMap;

use osr_balise::{
    audit_sightings, BaliseId, BaliseRecord, BaliseRegistry, BaliseType, SightingEvent,
    SightingReport, SurveyedPosition,
};
use osr_core::{Direction, Network, SectionId, TrackRef, TrainId};
use osr_odometry::{BaliseFix, BaliseId as OdomBaliseId};
use serde::{Deserialize, Serialize};

use crate::fault::FaultEngine;

const NOMINAL_OFFSET_MM: u64 = 10_000;
const FIX_UNCERTAINTY_MM: u32 = 100;
const STALE_AFTER_NS: u64 = 7 * 24 * 60 * 60 * 1_000_000_000;

#[derive(Clone, Debug)]
pub struct BaliseSystemsShadow {
    registry: BaliseRegistry,
    by_section: BTreeMap<SectionId, BaliseRecord>,
    summary: BaliseSystemsSummary,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct BaliseSystemsSummary {
    pub registry_count: u32,
    pub crossing_opportunities: u64,
    pub fixes_applied: u64,
    pub seen_sightings: u64,
    pub missed_sightings: u64,
    pub position_mismatches: u64,
    pub unknown_sightings: u64,
    pub stale_findings: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct BaliseCrossing {
    pub section: SectionId,
    pub direction: Direction,
    pub previous_offset_mm: i64,
    pub current_offset_mm: i64,
}

impl BaliseSystemsShadow {
    #[must_use]
    pub fn new(network: &Network) -> Self {
        let mut registry = BaliseRegistry::default();
        let mut by_section = BTreeMap::new();
        for (index, (section_id, section)) in network.sections.iter().enumerate() {
            let offset_mm = section
                .length_mm
                .saturating_div(2)
                .min(NOMINAL_OFFSET_MM)
                .min(i64::MAX as u64) as i64;
            let id = BaliseId((index + 1).min(u32::MAX as usize) as u32);
            let record = BaliseRecord {
                id,
                balise_type: BaliseType::Passive,
                position: SurveyedPosition {
                    section_id: section_id.0.min(u64::from(u32::MAX)) as u32,
                    offset_mm,
                },
                installed_ns: 0,
                last_seen_ns: None,
                stale_after_ns: STALE_AFTER_NS,
            };
            registry.insert(record);
            by_section.insert(*section_id, record);
        }
        Self {
            summary: BaliseSystemsSummary {
                registry_count: registry.by_id.len().min(u32::MAX as usize) as u32,
                ..BaliseSystemsSummary::default()
            },
            registry,
            by_section,
        }
    }

    /// Return a validated absolute-position fix when a train crosses the
    /// section's calibration balise. A missing or position-mismatched sighting
    /// is counted but never passed to the safety odometer.
    pub fn crossing_fix(
        &mut self,
        train: TrainId,
        crossing: BaliseCrossing,
        now_ns: u64,
        faults: &FaultEngine,
    ) -> Option<BaliseFix> {
        let record = *self.by_section.get(&crossing.section)?;
        if record.position.offset_mm <= crossing.previous_offset_mm
            || record.position.offset_mm > crossing.current_offset_mm
        {
            return None;
        }
        self.summary.crossing_opportunities = self.summary.crossing_opportunities.saturating_add(1);
        if faults.balise_missed_for(train) {
            self.summary.missed_sightings = self.summary.missed_sightings.saturating_add(1);
            return None;
        }

        let reported_position = if faults.balise_mismatch_for(train) {
            SurveyedPosition {
                offset_mm: record.position.offset_mm.saturating_add(1_000),
                ..record.position
            }
        } else {
            record.position
        };
        let events = audit_sightings(
            &self.registry,
            &[SightingReport {
                id: record.id,
                reported_position,
                now_ns,
            }],
            now_ns,
        );
        let mut valid = false;
        for event in events {
            match event {
                SightingEvent::Seen { id, .. } => {
                    self.summary.seen_sightings = self.summary.seen_sightings.saturating_add(1);
                    self.registry.mark_seen(id, now_ns);
                    valid = true;
                }
                SightingEvent::PositionMismatch { .. } => {
                    self.summary.position_mismatches =
                        self.summary.position_mismatches.saturating_add(1);
                }
                SightingEvent::Unknown { .. } => {
                    self.summary.unknown_sightings =
                        self.summary.unknown_sightings.saturating_add(1);
                }
                SightingEvent::Stale { .. } => {
                    self.summary.stale_findings = self.summary.stale_findings.saturating_add(1);
                }
            }
        }
        if !valid {
            return None;
        }
        self.summary.fixes_applied = self.summary.fixes_applied.saturating_add(1);
        Some(BaliseFix {
            balise_id: OdomBaliseId::new(record.id.0),
            position: TrackRef {
                section: crossing.section,
                offset_mm: record.position.offset_mm,
                direction: crossing.direction,
            },
            uncertainty_mm: FIX_UNCERTAINTY_MM,
        })
    }
}

#[must_use]
pub fn summarise(shadow: &BaliseSystemsShadow) -> BaliseSystemsSummary {
    shadow.summary.clone()
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{Section, StationId};

    fn network() -> Network {
        let mut network = Network::default();
        network.sections.insert(
            SectionId::new(42),
            Section {
                id: SectionId::new(42),
                from_station: StationId::new(1),
                to_station: StationId::new(2),
                length_mm: 1_000_000,
                max_speed_mps: 22.0,
            },
        );
        network
    }

    #[test]
    fn registry_and_fix_are_deterministic() {
        let mut first = BaliseSystemsShadow::new(&network());
        let mut second = BaliseSystemsShadow::new(&network());
        let faults = FaultEngine::default();
        let crossing = BaliseCrossing {
            section: SectionId::new(42),
            direction: Direction::Forward,
            previous_offset_mm: 9_000,
            current_offset_mm: 11_000,
        };
        let one = first.crossing_fix(TrainId::new(1), crossing, 1_000_000_000, &faults);
        let two = second.crossing_fix(TrainId::new(1), crossing, 1_000_000_000, &faults);
        assert_eq!(one, two);
        assert_eq!(summarise(&first), summarise(&second));
        assert_eq!(summarise(&first).fixes_applied, 1);
    }
}
