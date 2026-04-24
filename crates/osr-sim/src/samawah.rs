//! Samawah reference scenario — **LEGACY** hard-coded 2-line network.
//!
//! **Status:** frozen at the pre-2026-04-24 2-line geometry. Kept
//! alive only so the existing Rust integration tests + sim / OCC
//! GUI apps keep running against stable fixture data. New code
//! should load `designs/west-asia/Iraq/Samawah/samawah.toml` via `scenario_file::load`
//! — that file is auto-generated from the authoritative
//! `designs/west-asia/Iraq/Samawah/design.toml` and matches the
//! current 3-line network (L1 Nahrain + L2 Sharqiyyeh + L3
//! Mahatta) with real OSM-verified coordinates.
//!
//! The station IDs and inter-station distances below are legacy
//! fixture values — they are *not* the current reference design.
//! Corresponds to [RFC 0003](../../docs/rfcs/0003-samawah-reference-deployment.md)
//! at a point-in-time snapshot before the 3-line redesign.
//!
//! Migration path: tests that rely on a fixed topology should port
//! to loading the generated scenario file, same as the `--config`
//! CLI path already does.

use osr_core::{
    ConsistDescriptor, Line, Network, Section, SectionId, Station, StationId,
};

use crate::schedule::{hm, LineSchedule, TimeWindow};
use crate::sim::{ClimateModel, LineFleet, ScenarioConfig};
use crate::train::Heading;

// --------------------------------------------------------------------------
// Station identifiers
// --------------------------------------------------------------------------
//
// Line 1 uses IDs 1–12 (west-to-east). Line 2 uses IDs 6 and 11 (shared
// interchanges) plus 13–20 for its eight line-specific stations.

mod ids {
    use osr_core::StationId;
    // Line 1 (radial, west-to-east)
    pub const SAMAWAH_RWS: StationId = StationId::new(1);
    pub const NORTH_GATE: StationId = StationId::new(2);
    pub const OLD_SOUQ: StationId = StationId::new(3);
    pub const SAMAWAH_CENTRAL: StationId = StationId::new(4);
    pub const RIVERSIDE: StationId = StationId::new(5);
    pub const EASTERN_BRIDGE: StationId = StationId::new(6); // interchange L1/L2
    pub const AL_SALAM: StationId = StationId::new(7);
    pub const GOVERNORATE_HOSPITAL: StationId = StationId::new(8);
    pub const NEW_GERMAN_HOSPITAL: StationId = StationId::new(9);
    pub const ENGINEERING_QUARTER: StationId = StationId::new(10);
    pub const AL_MUTHANNA_UNIVERSITY: StationId = StationId::new(11); // interchange L1/L2
    pub const EAST_DEPOT: StationId = StationId::new(12);

    // Line 2 (ring, counterclockwise from Eastern Bridge)
    pub const NORTHERN_SUBURBS_A: StationId = StationId::new(13);
    pub const NORTHERN_SUBURBS_B: StationId = StationId::new(14);
    pub const NORTHWEST_JUNCTION: StationId = StationId::new(15);
    pub const INDUSTRIAL_WEST: StationId = StationId::new(16);
    pub const WESTERN_RESIDENTIAL: StationId = StationId::new(17);
    pub const SOUTH_WEST_RESIDENTIAL: StationId = StationId::new(18);
    pub const SOUTHERN_MARKETS: StationId = StationId::new(19);
    pub const SOUTH_EAST_RESIDENTIAL: StationId = StationId::new(20);
}

// --------------------------------------------------------------------------
// Station definitions
// --------------------------------------------------------------------------

struct StationSpec {
    id: StationId,
    name: &'static str,
    charging_power_kw: u32,
    dwell_seconds: u32,
    is_terminal: bool,
    is_depot: bool,
}

fn line1_station_specs() -> Vec<StationSpec> {
    use ids::*;
    vec![
        StationSpec { id: SAMAWAH_RWS,             name: "Samawah Railway Station", charging_power_kw: 1000, dwell_seconds: 60,  is_terminal: true,  is_depot: false },
        StationSpec { id: NORTH_GATE,              name: "North Gate",              charging_power_kw: 0,    dwell_seconds: 30,  is_terminal: false, is_depot: false },
        StationSpec { id: OLD_SOUQ,                name: "Old Souq",                charging_power_kw: 0,    dwell_seconds: 30,  is_terminal: false, is_depot: false },
        StationSpec { id: SAMAWAH_CENTRAL,         name: "Samawah Central",         charging_power_kw: 500,  dwell_seconds: 45,  is_terminal: false, is_depot: false },
        StationSpec { id: RIVERSIDE,               name: "Riverside",               charging_power_kw: 0,    dwell_seconds: 30,  is_terminal: false, is_depot: false },
        StationSpec { id: EASTERN_BRIDGE,          name: "Eastern Bridge",          charging_power_kw: 500,  dwell_seconds: 45,  is_terminal: false, is_depot: false },
        StationSpec { id: AL_SALAM,                name: "Al-Salam",                charging_power_kw: 0,    dwell_seconds: 30,  is_terminal: false, is_depot: false },
        StationSpec { id: GOVERNORATE_HOSPITAL,    name: "Governorate Hospital",    charging_power_kw: 500,  dwell_seconds: 45,  is_terminal: false, is_depot: false },
        StationSpec { id: NEW_GERMAN_HOSPITAL,     name: "New German Hospital",     charging_power_kw: 500,  dwell_seconds: 45,  is_terminal: false, is_depot: false },
        StationSpec { id: ENGINEERING_QUARTER,     name: "Engineering Quarter",     charging_power_kw: 0,    dwell_seconds: 30,  is_terminal: false, is_depot: false },
        StationSpec { id: AL_MUTHANNA_UNIVERSITY,  name: "Al-Muthanna University",  charging_power_kw: 500,  dwell_seconds: 60,  is_terminal: false, is_depot: false },
        StationSpec { id: EAST_DEPOT,              name: "East Depot & Yard",      charging_power_kw: 1000, dwell_seconds: 240, is_terminal: true,  is_depot: true },
    ]
}

fn line2_new_station_specs() -> Vec<StationSpec> {
    use ids::*;
    vec![
        StationSpec { id: NORTHERN_SUBURBS_A,      name: "Northern Suburbs A",      charging_power_kw: 0,   dwell_seconds: 30, is_terminal: false, is_depot: false },
        StationSpec { id: NORTHERN_SUBURBS_B,      name: "Northern Suburbs B",      charging_power_kw: 0,   dwell_seconds: 30, is_terminal: false, is_depot: false },
        StationSpec { id: NORTHWEST_JUNCTION,      name: "Northwest Junction",      charging_power_kw: 500, dwell_seconds: 45, is_terminal: false, is_depot: true },
        StationSpec { id: INDUSTRIAL_WEST,         name: "Industrial West",         charging_power_kw: 0,   dwell_seconds: 30, is_terminal: false, is_depot: false },
        StationSpec { id: WESTERN_RESIDENTIAL,     name: "Western Residential",     charging_power_kw: 0,   dwell_seconds: 30, is_terminal: false, is_depot: false },
        StationSpec { id: SOUTH_WEST_RESIDENTIAL,  name: "South-West Residential",  charging_power_kw: 0,   dwell_seconds: 30, is_terminal: false, is_depot: false },
        StationSpec { id: SOUTHERN_MARKETS,        name: "Southern Markets",        charging_power_kw: 500, dwell_seconds: 45, is_terminal: false, is_depot: false },
        StationSpec { id: SOUTH_EAST_RESIDENTIAL,  name: "South-East Residential",  charging_power_kw: 0,   dwell_seconds: 30, is_terminal: false, is_depot: false },
    ]
}

// --------------------------------------------------------------------------
// Line topology
// --------------------------------------------------------------------------

/// Line 1 station order, west→east, with inter-station distances in metres.
/// Total: ~13 km matching RFC 0003 §3.3 ("~14 km" includes depot headshunts).
const LINE1_SEQ: &[(StationId, u32)] = &[
    (ids::SAMAWAH_RWS, 0),
    (ids::NORTH_GATE, 1_000),
    (ids::OLD_SOUQ, 1_300),
    (ids::SAMAWAH_CENTRAL, 1_100),
    (ids::RIVERSIDE, 900),
    (ids::EASTERN_BRIDGE, 1_200),
    (ids::AL_SALAM, 1_400),
    (ids::GOVERNORATE_HOSPITAL, 1_300),
    (ids::NEW_GERMAN_HOSPITAL, 1_500),
    (ids::ENGINEERING_QUARTER, 1_300),
    (ids::AL_MUTHANNA_UNIVERSITY, 1_400),
    (ids::EAST_DEPOT, 600),
];

/// Line 2 ring, counterclockwise starting at Eastern Bridge, closed by the
/// Al-Muthanna University → Eastern Bridge segment. Distances sum to ~16 km
/// matching RFC 0003 §3.2.
const LINE2_SEQ: &[(StationId, u32)] = &[
    (ids::EASTERN_BRIDGE, 0),
    (ids::NORTHERN_SUBURBS_A, 1_800),
    (ids::NORTHERN_SUBURBS_B, 1_500),
    (ids::NORTHWEST_JUNCTION, 1_700),
    (ids::INDUSTRIAL_WEST, 1_600),
    (ids::WESTERN_RESIDENTIAL, 1_500),
    (ids::SOUTH_WEST_RESIDENTIAL, 1_800),
    (ids::SOUTHERN_MARKETS, 1_400),
    (ids::SOUTH_EAST_RESIDENTIAL, 1_600),
    (ids::AL_MUTHANNA_UNIVERSITY, 1_500),
    // wrap-back segment: Al-Muthanna University → Eastern Bridge
    // handled as the final section in forward_sections; see build_ring_line.
];

/// Length of the closing wrap segment on Line 2, in metres.
const LINE2_WRAP_LEN_M: u32 = 1_600;

// --------------------------------------------------------------------------
// Section ID allocation
// --------------------------------------------------------------------------

// Line 1 forward 1000..1010, reverse 2000..2010.
// Line 2 forward 3000..3009 (10 including wrap), reverse 4000..4009.

fn build_linear_line(
    net: &mut Network,
    name: &str,
    seq: &[(StationId, u32)],
    fwd_section_id_base: u64,
    rev_section_id_base: u64,
) {
    let mut forward_sections = Vec::new();
    let mut reverse_sections = Vec::new();

    for (i, pair) in seq.windows(2).enumerate() {
        let from = pair[0].0;
        let to = pair[1].0;
        let length_mm = u64::from(pair[1].1) * 1_000;

        let fwd_id = SectionId::new(fwd_section_id_base + i as u64);
        let rev_id = SectionId::new(rev_section_id_base + i as u64);

        net.sections.insert(fwd_id, Section {
            id: fwd_id, from_station: from, to_station: to,
            length_mm, max_speed_mps: 22.0,
        });
        net.sections.insert(rev_id, Section {
            id: rev_id, from_station: to, to_station: from,
            length_mm, max_speed_mps: 22.0,
        });
        forward_sections.push(fwd_id);
        reverse_sections.push(rev_id);
    }

    net.lines.push(Line {
        name: name.to_string(),
        stations: seq.iter().map(|(s, _)| *s).collect(),
        forward_sections,
        reverse_sections,
        is_ring: false,
    });
}

fn build_ring_line(
    net: &mut Network,
    name: &str,
    seq: &[(StationId, u32)],
    wrap_length_m: u32,
    fwd_section_id_base: u64,
    rev_section_id_base: u64,
) {
    let mut forward_sections = Vec::new();
    let mut reverse_sections = Vec::new();

    // Non-wrap sections.
    for (i, pair) in seq.windows(2).enumerate() {
        let from = pair[0].0;
        let to = pair[1].0;
        let length_mm = u64::from(pair[1].1) * 1_000;

        let fwd_id = SectionId::new(fwd_section_id_base + i as u64);
        let rev_id = SectionId::new(rev_section_id_base + i as u64);

        net.sections.insert(fwd_id, Section {
            id: fwd_id, from_station: from, to_station: to,
            length_mm, max_speed_mps: 22.0,
        });
        net.sections.insert(rev_id, Section {
            id: rev_id, from_station: to, to_station: from,
            length_mm, max_speed_mps: 22.0,
        });
        forward_sections.push(fwd_id);
        reverse_sections.push(rev_id);
    }

    // Wrap section: last station → first station.
    let last = seq.last().unwrap().0;
    let first = seq.first().unwrap().0;
    let wrap_len_mm = u64::from(wrap_length_m) * 1_000;
    let wrap_fwd_id = SectionId::new(fwd_section_id_base + (seq.len() - 1) as u64);
    let wrap_rev_id = SectionId::new(rev_section_id_base + (seq.len() - 1) as u64);

    net.sections.insert(wrap_fwd_id, Section {
        id: wrap_fwd_id, from_station: last, to_station: first,
        length_mm: wrap_len_mm, max_speed_mps: 22.0,
    });
    net.sections.insert(wrap_rev_id, Section {
        id: wrap_rev_id, from_station: first, to_station: last,
        length_mm: wrap_len_mm, max_speed_mps: 22.0,
    });
    forward_sections.push(wrap_fwd_id);
    reverse_sections.push(wrap_rev_id);

    net.lines.push(Line {
        name: name.to_string(),
        stations: seq.iter().map(|(s, _)| *s).collect(),
        forward_sections,
        reverse_sections,
        is_ring: true,
    });
}

pub fn build_network() -> Network {
    let mut net = Network::default();

    let mut insert_station = |spec: StationSpec| {
        net.stations.insert(spec.id, Station {
            id: spec.id,
            name: spec.name.to_string(),
            charging_power_kw: spec.charging_power_kw,
            dwell_seconds: spec.dwell_seconds,
            is_terminal: spec.is_terminal,
            is_depot: spec.is_depot,
        });
    };

    // Line 1 stations (includes the two shared interchanges).
    for spec in line1_station_specs() {
        insert_station(spec);
    }
    // Line 2 stations that aren't already on Line 1.
    for spec in line2_new_station_specs() {
        insert_station(spec);
    }

    build_linear_line(&mut net, "Line 1 Nahrain", LINE1_SEQ, 1_000, 2_000);
    build_ring_line(&mut net, "Line 2 Halqa", LINE2_SEQ, LINE2_WRAP_LEN_M, 3_000, 4_000);

    net
}

// --------------------------------------------------------------------------
// Scenario config
// --------------------------------------------------------------------------

/// Line 1 "Nahrain" schedule — RFC 0003 §4.1.
/// 05:30–07:00 pre-peak, 07:00–09:30 AM peak, 09:30–16:00 midday,
/// 16:00–19:00 PM peak, 19:00–22:00 evening, 22:00–23:30 late.
pub fn line1_schedule() -> LineSchedule {
    LineSchedule {
        service_start_s: hm(5, 30),
        service_end_s: hm(23, 30),
        windows: vec![
            TimeWindow { start_s: hm(5, 30),  end_s: hm(7, 0),   headway_s: 600 },
            TimeWindow { start_s: hm(7, 0),   end_s: hm(9, 30),  headway_s: 240 },
            TimeWindow { start_s: hm(9, 30),  end_s: hm(16, 0),  headway_s: 480 },
            TimeWindow { start_s: hm(16, 0),  end_s: hm(19, 0),  headway_s: 240 },
            TimeWindow { start_s: hm(19, 0),  end_s: hm(22, 0),  headway_s: 600 },
            TimeWindow { start_s: hm(22, 0),  end_s: hm(23, 30), headway_s: 900 },
        ],
    }
}

/// Line 2 "Halqa" schedule — RFC 0003 §4.1.
pub fn line2_schedule() -> LineSchedule {
    LineSchedule {
        service_start_s: hm(5, 30),
        service_end_s: hm(23, 30),
        windows: vec![
            TimeWindow { start_s: hm(5, 30),  end_s: hm(7, 0),   headway_s: 720 },
            TimeWindow { start_s: hm(7, 0),   end_s: hm(9, 30),  headway_s: 360 },
            TimeWindow { start_s: hm(9, 30),  end_s: hm(16, 0),  headway_s: 600 },
            TimeWindow { start_s: hm(16, 0),  end_s: hm(19, 0),  headway_s: 360 },
            TimeWindow { start_s: hm(19, 0),  end_s: hm(22, 0),  headway_s: 720 },
            TimeWindow { start_s: hm(22, 0),  end_s: hm(23, 30), headway_s: 900 },
        ],
    }
}

pub fn full_scenario() -> ScenarioConfig {
    let network = build_network();

    let fleets = vec![
        LineFleet {
            line_index: 0, // Line 1 Nahrain
            dispatch_points: vec![
                (ids::SAMAWAH_RWS, Heading::Forward),
                (ids::EAST_DEPOT, Heading::Reverse),
            ],
            trainset_count: 6,
            schedule: line1_schedule(),
        },
        LineFleet {
            line_index: 1, // Line 2 Halqa
            dispatch_points: vec![
                (ids::EASTERN_BRIDGE, Heading::Forward),         // CCW from EB
                (ids::AL_MUTHANNA_UNIVERSITY, Heading::Reverse), // CW from AMU
                (ids::EASTERN_BRIDGE, Heading::Reverse),
                (ids::AL_MUTHANNA_UNIVERSITY, Heading::Forward),
            ],
            trainset_count: 4,
            schedule: line2_schedule(),
        },
    ];

    ScenarioConfig {
        name: "Samawah — Line 1 Nahrain + Line 2 Halqa (RFC 0003)".to_string(),
        network,
        fleets,
        consist: ConsistDescriptor::reference_3car(),
        climate: ClimateModel {
            ambient_c: 42.0,
            peak_sun_hours: 6.0,
            hvac_uplift_frac: ((42.0_f32 - 25.0) / 25.0).clamp(0.0, 0.25),
        },
        start_time_s_after_midnight: hm(6, 0),
        // Built-in Samawah scenario runs in unlimited-charging mode; for the
        // full catenary-free + solar model, use designs/west-asia/Iraq/Samawah/samawah.toml which
        // includes the [[sites]] configuration.
        energy_sites: Vec::new(),
        faults: Vec::new(),
    }
}

/// Line-1-only scenario, kept for scale comparisons and regression.
pub fn line1_only_scenario() -> ScenarioConfig {
    let mut s = full_scenario();
    s.name = "Samawah Line 1 only".to_string();
    s.fleets.retain(|f| f.line_index == 0);
    s
}
