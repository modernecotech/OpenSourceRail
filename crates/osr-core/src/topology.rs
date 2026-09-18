//! Static track topology: stations, sections, lines, network.
//!
//! This is the planning-grade topology the simulator operates on. A real
//! deployment would synthesize this from a surveyed alignment artifact;
//! RFC 0003 describes the Samawah indicative alignment that seeds the
//! simulator.

use crate::ids::{SectionId, StationId};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Station {
    pub id: StationId,
    pub name: String,
    /// Maximum sustained charging power deliverable at this station, in kW.
    /// Zero means "no charging available" (most mid-line stations).
    pub charging_power_kw: u32,
    /// Dwell time in seconds; longer at terminals.
    pub dwell_seconds: u32,
    pub is_terminal: bool,
    pub is_depot: bool,
}

/// Single-direction link between two stations.
///
/// For a double-track line we model this as a pair of logical sections (one
/// per direction). The simulator creates both when building a line.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Section {
    pub id: SectionId,
    pub from_station: StationId,
    pub to_station: StationId,
    pub length_mm: u64,
    /// Local max speed in m/s. Permanent speed restriction equivalent.
    pub max_speed_mps: f32,
}

impl Section {
    pub fn length_km(&self) -> f64 {
        self.length_mm as f64 / 1_000_000.0
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Line {
    pub name: String,
    /// Stations in line order. For a ring, the last and first are adjacent
    /// (closed loop). For a linear line, they are the two termini.
    pub stations: Vec<StationId>,
    /// Forward-direction sections. `forward_sections[i]` connects
    /// `stations[i] -> stations[i+1]` (and, for rings,
    /// `stations[N-1] -> stations[0]` as the last element).
    pub forward_sections: Vec<SectionId>,
    /// Reverse-direction sections, paired to `forward_sections` (same indexing).
    pub reverse_sections: Vec<SectionId>,
    /// If true, the line is a closed loop. Trains passing the last station
    /// wrap around rather than reaching a terminal.
    pub is_ring: bool,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Network {
    pub stations: BTreeMap<StationId, Station>,
    pub sections: BTreeMap<SectionId, Section>,
    pub lines: Vec<Line>,
}

impl Network {
    /// Return a station by ID.
    ///
    /// # Panics
    ///
    /// Panics when `id` is not present in this network.
    pub fn station(&self, id: StationId) -> &Station {
        self.stations
            .get(&id)
            .unwrap_or_else(|| panic!("unknown station {id}"))
    }

    /// Return a section by ID.
    ///
    /// # Panics
    ///
    /// Panics when `id` is not present in this network.
    pub fn section(&self, id: SectionId) -> &Section {
        self.sections
            .get(&id)
            .unwrap_or_else(|| panic!("unknown section {id}"))
    }

    pub fn total_route_length_km(&self) -> f64 {
        self.lines
            .iter()
            .flat_map(|l| &l.forward_sections)
            .map(|sid| self.section(*sid).length_km())
            .sum()
    }
}

// Pre-M5 had an `OccupancyMap` here — an in-memory oracle the simulator
// consulted for the "no two trains in the same section" invariant.
// RFC 0004 M5 retires it: `osr-interlocking`'s `DerivedState.section_occupancy`
// is now the single source of truth, and the sim gates every section
// entry through `osr_interlocking::section_available_to`.

/// Read-only geometry and line ordering required by the safety evaluators.
/// Implementations must provide stable views and uniquely resolve section IDs.
/// Station business metadata is outside this interface.
pub trait TrackTopology {
    fn line_count(&self) -> usize;
    fn line(&self, index: usize) -> TrackLine<'_>;
    /// Resolve a section, panicking if absent (as `Network::section` does).
    fn section(&self, id: SectionId) -> &Section;
}

/// Borrowed line ordering: no ownership, allocation or business metadata.
#[derive(Clone, Copy, Debug)]
pub struct TrackLine<'a> {
    pub forward_sections: &'a [SectionId],
    pub reverse_sections: &'a [SectionId],
    pub is_ring: bool,
}

impl<'a> From<&'a Line> for TrackLine<'a> {
    fn from(line: &'a Line) -> Self {
        Self {
            forward_sections: &line.forward_sections,
            reverse_sections: &line.reverse_sections,
            is_ring: line.is_ring,
        }
    }
}

impl TrackTopology for Network {
    fn line_count(&self) -> usize {
        self.lines.len()
    }
    fn line(&self, index: usize) -> TrackLine<'_> {
        (&self.lines[index]).into()
    }
    fn section(&self, id: SectionId) -> &Section {
        Network::section(self, id)
    }
}

/// Validated immutable tables, usable with runtime slices or constant fixtures.
/// Construction and lookup allocate nothing. Existing city serialization and
/// default evaluator calls continue to use the `Network` adapter.
#[derive(Clone, Copy, Debug)]
pub struct StaticTopology<'a> {
    lines: &'a [TrackLine<'a>],
    sections: &'a [Section],
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TopologyError {
    DuplicateSection(SectionId),
    UnknownSection(SectionId),
}

impl<'a> StaticTopology<'a> {
    /// Reject duplicate IDs and dangling references. `const` permits the same
    /// validation at compile time for fixed fixtures; no unchecked constructor
    /// or verification-only storage implementation is needed.
    pub const fn try_new(
        lines: &'a [TrackLine<'a>],
        sections: &'a [Section],
    ) -> Result<Self, TopologyError> {
        let mut i = 0;
        while i < sections.len() {
            let mut j = 0;
            while j < i {
                if sections[j].id.0 == sections[i].id.0 {
                    return Err(TopologyError::DuplicateSection(sections[i].id));
                }
                j += 1;
            }
            i += 1;
        }
        let mut line = 0;
        while line < lines.len() {
            let arrays = [lines[line].forward_sections, lines[line].reverse_sections];
            let mut side = 0;
            while side < arrays.len() {
                let mut index = 0;
                while index < arrays[side].len() {
                    let id = arrays[side][index];
                    let mut found = false;
                    let mut section = 0;
                    while section < sections.len() {
                        if sections[section].id.0 == id.0 {
                            found = true;
                            break;
                        }
                        section += 1;
                    }
                    if !found {
                        return Err(TopologyError::UnknownSection(id));
                    }
                    index += 1;
                }
                side += 1;
            }
            line += 1;
        }
        Ok(Self { lines, sections })
    }
}

impl TrackTopology for StaticTopology<'_> {
    fn line_count(&self) -> usize {
        self.lines.len()
    }
    fn line(&self, index: usize) -> TrackLine<'_> {
        self.lines[index]
    }
    fn section(&self, id: SectionId) -> &Section {
        let mut index = 0;
        while index < self.sections.len() {
            if self.sections[index].id == id {
                return &self.sections[index];
            }
            index += 1;
        }
        panic!("unknown section {id}")
    }
}

#[cfg(test)]
mod static_tests {
    use super::*;
    const SECTION: Section = Section {
        id: SectionId::new(1),
        from_station: StationId::new(1),
        to_station: StationId::new(2),
        length_mm: 1000,
        max_speed_mps: 22.0,
    };
    const TOPOLOGY: StaticTopology<'static> = match StaticTopology::try_new(&[], &[SECTION]) {
        Ok(topology) => topology,
        Err(_) => panic!("invalid constant topology"),
    };

    #[test]
    fn reject_duplicate_ids_and_dangling_references() {
        assert_eq!(
            StaticTopology::try_new(&[], &[SECTION, SECTION]).unwrap_err(),
            TopologyError::DuplicateSection(SectionId::new(1))
        );
        for reverse in [false, true] {
            let ids = [SectionId::new(2)];
            let lines = [TrackLine {
                forward_sections: if reverse { &[] } else { &ids },
                reverse_sections: if reverse { &ids } else { &[] },
                is_ring: false,
            }];
            assert_eq!(
                StaticTopology::try_new(&lines, &[SECTION]).unwrap_err(),
                TopologyError::UnknownSection(SectionId::new(2))
            );
        }
        assert_eq!(TOPOLOGY.section(SectionId::new(1)).length_mm, 1000);
        assert_eq!(StaticTopology::try_new(&[], &[]).unwrap().line_count(), 0);
    }

    #[test]
    #[should_panic(expected = "unknown section")]
    fn unknown_lookup_retains_network_failure_contract() {
        TOPOLOGY.section(SectionId::new(2));
    }
}
