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
