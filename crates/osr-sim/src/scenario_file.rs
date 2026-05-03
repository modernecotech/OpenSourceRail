//! TOML-based scenario definition.
//!
//! Users describe a scenario — stations, lines, fleets, schedules, climate —
//! in a plain-text `.toml` file. The loader validates it and builds the
//! in-memory `ScenarioConfig` that the sim engine consumes.
//!
//! Schema reference: see `lib/examples/README.md` at the repository root.

use osr_core::{
    ConsistDescriptor, Line, Network, Section, SectionId, Station, StationId,
};
use serde::Deserialize;
use std::collections::HashMap;

use crate::energy::EnergySiteConfig;
use crate::fault::{Fault, FaultKind, FaultScope, TrainFaultScope};
use crate::schedule::{LineSchedule, TimeWindow};
use crate::sim::{ClimateModel, LineFleet, ScenarioConfig};
use crate::train::Heading;

// ===========================================================================
// Wire schema — matches the TOML file structure 1:1
// ===========================================================================

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ScenarioFile {
    pub scenario: ScenarioMeta,
    pub climate: ClimateSpec,
    #[serde(default)]
    pub consist: Option<ConsistSpec>,
    pub stations: Vec<StationSpec>,
    pub lines: Vec<LineSpec>,
    pub fleets: Vec<FleetSpec>,
    /// Optional trackside energy sites. Scenarios without `[[sites]]` run in
    /// unlimited-charging mode (no PV, no storage, no grid).
    #[serde(default)]
    pub sites: Vec<SiteSpec>,
    /// Optional fault events: dust storms, grid outages, charging pad failures.
    #[serde(default)]
    pub faults: Vec<FaultSpec>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ScenarioMeta {
    pub name: String,
    /// "HH:MM" — sim wall clock start.
    pub start_time: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ClimateSpec {
    pub ambient_c: f32,
    pub peak_sun_hours: f32,
    /// Optional explicit uplift. If omitted, computed linearly from ambient_c
    /// over the baseline of 25°C, capped at 25%.
    #[serde(default)]
    pub hvac_uplift_frac: Option<f32>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ConsistSpec {
    #[serde(default)]
    pub car_count: Option<u32>,
    #[serde(default)]
    pub length_m: Option<u32>,
    #[serde(default)]
    pub mass_kg: Option<u32>,
    #[serde(default)]
    pub max_speed_kmh: Option<f32>,
    #[serde(default)]
    pub battery_capacity_kwh: Option<u32>,
    #[serde(default)]
    pub passenger_capacity: Option<u32>,
    #[serde(default)]
    pub seat_count: Option<u32>,
    #[serde(default)]
    pub crush_capacity: Option<u32>,
    /// Service-brake acceleration, m/s² (default 1.0).
    #[serde(default)]
    pub service_accel_mps2: Option<f32>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StationSpec {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub charging_power_kw: u32,
    pub dwell_seconds: u32,
    #[serde(default)]
    pub is_terminal: bool,
    #[serde(default)]
    pub is_depot: bool,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LineSpec {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub is_ring: bool,
    pub stations: Vec<LineStationRef>,
    /// Required for rings; forbidden for linear lines.
    #[serde(default)]
    pub ring_wrap_length_m: Option<u32>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LineStationRef {
    pub id: String,
    /// Distance from the previous station in the sequence, in metres.
    /// For the first station, use 0.
    pub distance_from_prev_m: u32,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FleetSpec {
    pub line: String,
    pub trainset_count: u32,
    pub dispatch_points: Vec<DispatchPointSpec>,
    /// "HH:MM"
    pub service_start: String,
    /// "HH:MM"
    pub service_end: String,
    pub schedule: Vec<WindowSpec>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DispatchPointSpec {
    pub station: String,
    pub heading: String, // "forward" | "reverse"
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct WindowSpec {
    pub from: String, // "HH:MM"
    pub to: String,   // "HH:MM"
    pub headway_min: u32,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SiteSpec {
    pub station: String,
    /// Site tier (`halt` / `standard` / `major` / `terminal` /
    /// `depot-terminal` / `interchange`) emitted by the
    /// `osr_scenario` python generator. Read for grouping /
    /// reporting; the simulator's energy-balance logic uses the
    /// per-site numeric fields below, not the tier.
    #[serde(default)]
    pub tier: String,
    #[serde(default)]
    pub pv_nameplate_kw: f32,
    pub storage_capacity_kwh: f32,
    pub storage_max_charge_kw: f32,
    pub storage_max_discharge_kw: f32,
    /// Initial SoC 0.0..1.0 (default 0.5).
    #[serde(default = "default_initial_soc")]
    pub storage_initial_soc: f32,
    #[serde(default)]
    pub grid_import_kw: f32,
    #[serde(default)]
    pub grid_export_kw: f32,
}

fn default_initial_soc() -> f32 {
    0.5
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FaultSpec {
    pub name: String,
    /// One of: `"dust_event"`, `"grid_outage"`, `"charging_pad_outage"`,
    /// `"lidar_offline"`, `"radar_offline"`, `"ultrasonic_channel_stale"`,
    /// `"obstacle_peer_disagreement"`.
    pub kind: String,
    /// Start time "HH:MM" (relative to `day`).
    pub from: String,
    /// End time "HH:MM" (relative to `day`).
    pub to: String,
    /// Day of the simulation, 1-based. Defaults to 1.
    #[serde(default = "default_fault_day")]
    pub day: u32,
    /// For dust_event: fraction of normal PV output (0.0–1.0). Required.
    #[serde(default)]
    pub pv_output_factor: Option<f32>,
    /// For scoped infrastructure faults: which station this affects. If
    /// omitted, the fault is all-sites (for dust_event and grid_outage).
    /// Required for charging_pad_outage.
    #[serde(default)]
    pub station: Option<String>,
    /// For onboard obstacle-detect faults (RFC 0015): which train this
    /// affects (e.g. `"T1"`). If omitted the fault applies to every
    /// train in the fleet.
    #[serde(default)]
    pub train: Option<String>,
    /// For `ultrasonic_channel_stale`: which of the 4 ultrasonic
    /// transducers (0..=3). Required for that kind.
    #[serde(default)]
    pub channel: Option<u8>,
    /// For `wayside_intrusion` (RFC 0016 v3): the numeric section id
    /// where the intrusion is staged. Section ids are auto-assigned
    /// by the scenario builder in the order stations are listed;
    /// forward-direction sections start at 1 000 and reverse-direction
    /// at 2 000 per-line.
    #[serde(default)]
    pub section_id: Option<u64>,
    /// For `wayside_intrusion`: the verdict state to inject —
    /// `"clear"`, `"unknown"`, or `"present"`. Default `"present"`.
    #[serde(default)]
    pub intrusion_state: Option<String>,
}

fn default_fault_day() -> u32 {
    1
}

// ===========================================================================
// Errors
// ===========================================================================

#[derive(Debug)]
pub enum LoadError {
    Parse(String),
    InvalidTime { field: &'static str, value: String },
    InvalidHeading(String),
    DuplicateStationId(String),
    DuplicateLineId(String),
    UnknownStation { referenced_by: String, id: String },
    UnknownLine { referenced_by: String, id: String },
    RingMissingWrapLength(String),
    LinearWithWrapLength(String),
    LineWithFewerThanTwoStations(String),
    EmptyFleetDispatchPoints(String),
    EmptySchedule(String),
    ZeroHeadway { line: String, from: String, to: String },
    ServiceWindowInverted { line: String },
    ScheduleWindowInverted { line: String, from: String, to: String },
    DispatchPointNotOnLine { line: String, station: String },
    InconsistentFirstStationDistance(String),
    DuplicateSite(String),
    InvalidSocInitial { station: String, soc: f32 },
    InvalidFaultKind(String),
    InvalidFaultDay { name: String, day: u32 },
    InvalidFaultWindow { name: String },
    DustEventMissingFactor(String),
    InvalidDustFactor { name: String, factor: f32 },
    ChargingPadOutageMissingStation(String),
    UltrasonicChannelOutOfRange { name: String, channel: u8 },
    UltrasonicChannelMissing(String),
    UnknownTrain { referenced_by: String, id: String },
    WaysideIntrusionMissingSection(String),
    InvalidIntrusionState { name: String, state: String },
}

impl std::fmt::Display for LoadError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        use LoadError::*;
        match self {
            Parse(m) => write!(f, "parse error: {m}"),
            InvalidTime { field, value } => write!(f, "invalid time in {field}: '{value}' (expected HH:MM)"),
            InvalidHeading(h) => write!(f, "invalid heading '{h}' (expected 'forward' or 'reverse')"),
            DuplicateStationId(id) => write!(f, "duplicate station id '{id}'"),
            DuplicateLineId(id) => write!(f, "duplicate line id '{id}'"),
            UnknownStation { referenced_by, id } => {
                write!(f, "station '{id}' referenced by {referenced_by} is not defined")
            }
            UnknownLine { referenced_by, id } => {
                write!(f, "line '{id}' referenced by {referenced_by} is not defined")
            }
            RingMissingWrapLength(line) => {
                write!(f, "line '{line}' is a ring but missing ring_wrap_length_m")
            }
            LinearWithWrapLength(line) => {
                write!(f, "line '{line}' is linear but specifies ring_wrap_length_m")
            }
            LineWithFewerThanTwoStations(line) => {
                write!(f, "line '{line}' must have at least two stations")
            }
            EmptyFleetDispatchPoints(line) => {
                write!(f, "fleet for line '{line}' has no dispatch_points")
            }
            EmptySchedule(line) => write!(f, "schedule for line '{line}' has no windows"),
            ZeroHeadway { line, from, to } => {
                write!(f, "schedule window {from}–{to} on line '{line}' has headway_min = 0")
            }
            ServiceWindowInverted { line } => {
                write!(f, "service_end must be after service_start for line '{line}'")
            }
            ScheduleWindowInverted { line, from, to } => {
                write!(f, "schedule window {from}–{to} on line '{line}' is inverted")
            }
            DispatchPointNotOnLine { line, station } => {
                write!(f, "dispatch point station '{station}' is not on line '{line}'")
            }
            InconsistentFirstStationDistance(line) => {
                write!(
                    f,
                    "first station on line '{line}' should have distance_from_prev_m = 0"
                )
            }
            DuplicateSite(s) => write!(f, "duplicate site for station '{s}'"),
            InvalidSocInitial { station, soc } => {
                write!(f, "site for station '{station}' has storage_initial_soc={soc}; must be in [0.0, 1.0]")
            }
            InvalidFaultKind(k) => write!(
                f,
                "unknown fault kind '{k}' (expected one of: dust_event, grid_outage, \
                 charging_pad_outage, lidar_offline, radar_offline, \
                 ultrasonic_channel_stale, obstacle_peer_disagreement, \
                 wayside_intrusion)"
            ),
            UltrasonicChannelOutOfRange { name, channel } => write!(
                f,
                "fault '{name}' (ultrasonic_channel_stale) has channel={channel}; must be 0..=3"
            ),
            UltrasonicChannelMissing(n) => write!(
                f,
                "fault '{n}' (ultrasonic_channel_stale) requires a 'channel' field (0..=3)"
            ),
            UnknownTrain { referenced_by, id } => {
                write!(f, "train '{id}' referenced by {referenced_by} is not defined")
            }
            WaysideIntrusionMissingSection(n) => write!(
                f,
                "fault '{n}' (wayside_intrusion) requires a numeric 'section_id' field"
            ),
            InvalidIntrusionState { name, state } => write!(
                f,
                "fault '{name}' has intrusion_state='{state}'; must be 'clear', 'unknown', or 'present'"
            ),
            InvalidFaultDay { name, day } => {
                write!(f, "fault '{name}' has day={day}; must be >= 1")
            }
            InvalidFaultWindow { name } => {
                write!(f, "fault '{name}' has 'to' not after 'from'")
            }
            DustEventMissingFactor(n) => {
                write!(f, "fault '{n}' (dust_event) requires pv_output_factor in [0.0, 1.0]")
            }
            InvalidDustFactor { name, factor } => {
                write!(f, "fault '{name}' has pv_output_factor={factor}; must be in [0.0, 1.0]")
            }
            ChargingPadOutageMissingStation(n) => {
                write!(f, "fault '{n}' (charging_pad_outage) requires a 'station'")
            }
        }
    }
}

impl std::error::Error for LoadError {}

// ===========================================================================
// Loader entry points
// ===========================================================================

pub fn load_scenario_from_str(s: &str) -> Result<ScenarioConfig, LoadError> {
    let file: ScenarioFile = toml::from_str(s).map_err(|e| LoadError::Parse(e.to_string()))?;
    build_scenario(file)
}

pub fn load_scenario_from_path(path: &std::path::Path) -> Result<ScenarioConfig, LoadError> {
    let s = std::fs::read_to_string(path)
        .map_err(|e| LoadError::Parse(format!("reading {}: {}", path.display(), e)))?;
    load_scenario_from_str(&s)
}

/// Compile-time-bundled canonical Samawah scenario.
///
/// The osr-design pipeline emits
/// `designs/west-asia/Iraq/Samawah/samawah.toml` as the project's
/// reference scenario. This function returns a parsed
/// [`ScenarioConfig`] from a snapshot of that file taken at build
/// time (`include_str!`). Used by the CLI and GUI binaries as the
/// default scenario when the operator hasn't passed `--config`,
/// and by the integration tests as a hermetic fixture that doesn't
/// depend on the working directory.
///
/// Panics on parse failure — the bundled file is regenerated by
/// `scripts/regenerate-city.sh samawah` and committed to git, so a
/// parse failure means the schema drifted and the build was wrong.
#[must_use]
pub fn canonical_samawah_scenario() -> ScenarioConfig {
    const SAMAWAH_TOML: &str = include_str!(
        "../../../designs/west-asia/Iraq/Samawah/samawah.toml"
    );
    load_scenario_from_str(SAMAWAH_TOML)
        .expect("bundled samawah.toml failed to parse — schema drifted vs scenario_file.rs")
}

// ===========================================================================
// Builder: TOML structure → ScenarioConfig
// ===========================================================================

fn build_scenario(file: ScenarioFile) -> Result<ScenarioConfig, LoadError> {
    let start_time_s = parse_time("scenario.start_time", &file.scenario.start_time)?;

    // --- Stations: assign u64 IDs ------------------------------------------
    let mut station_ids: HashMap<String, StationId> = HashMap::new();
    let mut next_station_id: u64 = 1;
    let mut network = Network::default();

    for spec in &file.stations {
        if station_ids.contains_key(&spec.id) {
            return Err(LoadError::DuplicateStationId(spec.id.clone()));
        }
        let id = StationId::new(next_station_id);
        next_station_id += 1;
        station_ids.insert(spec.id.clone(), id);

        network.stations.insert(
            id,
            Station {
                id,
                name: spec.name.clone(),
                charging_power_kw: spec.charging_power_kw,
                dwell_seconds: spec.dwell_seconds,
                is_terminal: spec.is_terminal,
                is_depot: spec.is_depot,
            },
        );
    }

    // --- Lines --------------------------------------------------------------
    let mut line_indices: HashMap<String, usize> = HashMap::new();
    let mut next_fwd_section: u64 = 1_000;
    let mut next_rev_section: u64 = 100_000;

    for spec in &file.lines {
        if line_indices.contains_key(&spec.id) {
            return Err(LoadError::DuplicateLineId(spec.id.clone()));
        }
        if spec.stations.len() < 2 {
            return Err(LoadError::LineWithFewerThanTwoStations(spec.id.clone()));
        }
        if spec.is_ring && spec.ring_wrap_length_m.is_none() {
            return Err(LoadError::RingMissingWrapLength(spec.id.clone()));
        }
        if !spec.is_ring && spec.ring_wrap_length_m.is_some() {
            return Err(LoadError::LinearWithWrapLength(spec.id.clone()));
        }
        if spec.stations[0].distance_from_prev_m != 0 {
            return Err(LoadError::InconsistentFirstStationDistance(spec.id.clone()));
        }

        // Resolve station IDs.
        let mut station_seq: Vec<StationId> = Vec::with_capacity(spec.stations.len());
        for sref in &spec.stations {
            let id = *station_ids
                .get(&sref.id)
                .ok_or_else(|| LoadError::UnknownStation {
                    referenced_by: format!("line '{}'", spec.id),
                    id: sref.id.clone(),
                })?;
            station_seq.push(id);
        }

        // Build sections.
        let mut forward_sections = Vec::new();
        let mut reverse_sections = Vec::new();

        for (i, win) in spec.stations.windows(2).enumerate() {
            let from = station_seq[i];
            let to = station_seq[i + 1];
            let length_mm = u64::from(win[1].distance_from_prev_m) * 1_000;

            let fwd_id = SectionId::new(next_fwd_section);
            let rev_id = SectionId::new(next_rev_section);
            next_fwd_section += 1;
            next_rev_section += 1;

            network.sections.insert(fwd_id, Section {
                id: fwd_id, from_station: from, to_station: to,
                length_mm, max_speed_mps: 22.0,
            });
            network.sections.insert(rev_id, Section {
                id: rev_id, from_station: to, to_station: from,
                length_mm, max_speed_mps: 22.0,
            });
            forward_sections.push(fwd_id);
            reverse_sections.push(rev_id);
        }

        if spec.is_ring {
            let wrap_len_mm = u64::from(spec.ring_wrap_length_m.unwrap()) * 1_000;
            let last = *station_seq.last().unwrap();
            let first = *station_seq.first().unwrap();
            let fwd_id = SectionId::new(next_fwd_section);
            let rev_id = SectionId::new(next_rev_section);
            next_fwd_section += 1;
            next_rev_section += 1;
            network.sections.insert(fwd_id, Section {
                id: fwd_id, from_station: last, to_station: first,
                length_mm: wrap_len_mm, max_speed_mps: 22.0,
            });
            network.sections.insert(rev_id, Section {
                id: rev_id, from_station: first, to_station: last,
                length_mm: wrap_len_mm, max_speed_mps: 22.0,
            });
            forward_sections.push(fwd_id);
            reverse_sections.push(rev_id);
        }

        let line_index = network.lines.len();
        line_indices.insert(spec.id.clone(), line_index);

        network.lines.push(Line {
            name: spec.name.clone(),
            stations: station_seq,
            forward_sections,
            reverse_sections,
            is_ring: spec.is_ring,
        });
    }

    // --- Fleets -------------------------------------------------------------
    let mut fleets: Vec<LineFleet> = Vec::new();

    for spec in &file.fleets {
        let &line_index = line_indices
            .get(&spec.line)
            .ok_or_else(|| LoadError::UnknownLine {
                referenced_by: "fleet".to_string(),
                id: spec.line.clone(),
            })?;

        if spec.dispatch_points.is_empty() {
            return Err(LoadError::EmptyFleetDispatchPoints(spec.line.clone()));
        }
        if spec.schedule.is_empty() {
            return Err(LoadError::EmptySchedule(spec.line.clone()));
        }

        // Resolve dispatch points.
        let line = &network.lines[line_index];
        let line_station_set: std::collections::HashSet<StationId> =
            line.stations.iter().copied().collect();

        let mut dispatch_points: Vec<(StationId, Heading)> = Vec::new();
        for dp in &spec.dispatch_points {
            let station = *station_ids
                .get(&dp.station)
                .ok_or_else(|| LoadError::UnknownStation {
                    referenced_by: format!("fleet for line '{}'", spec.line),
                    id: dp.station.clone(),
                })?;
            if !line_station_set.contains(&station) {
                return Err(LoadError::DispatchPointNotOnLine {
                    line: spec.line.clone(),
                    station: dp.station.clone(),
                });
            }
            let heading = parse_heading(&dp.heading)?;
            dispatch_points.push((station, heading));
        }

        // Schedule.
        let service_start_s = parse_time("service_start", &spec.service_start)?;
        let service_end_s = parse_time("service_end", &spec.service_end)?;
        if service_end_s <= service_start_s {
            return Err(LoadError::ServiceWindowInverted { line: spec.line.clone() });
        }

        let mut windows = Vec::new();
        for w in &spec.schedule {
            let start_s = parse_time("schedule.from", &w.from)?;
            let end_s = parse_time("schedule.to", &w.to)?;
            if end_s <= start_s {
                return Err(LoadError::ScheduleWindowInverted {
                    line: spec.line.clone(),
                    from: w.from.clone(),
                    to: w.to.clone(),
                });
            }
            if w.headway_min == 0 {
                return Err(LoadError::ZeroHeadway {
                    line: spec.line.clone(),
                    from: w.from.clone(),
                    to: w.to.clone(),
                });
            }
            windows.push(TimeWindow {
                start_s,
                end_s,
                headway_s: w.headway_min * 60,
            });
        }

        fleets.push(LineFleet {
            line_index,
            dispatch_points,
            trainset_count: spec.trainset_count,
            schedule: LineSchedule {
                service_start_s,
                service_end_s,
                windows,
            },
        });
    }

    // --- Energy sites -------------------------------------------------------
    let mut energy_sites: Vec<EnergySiteConfig> = Vec::new();
    let mut seen_sites: std::collections::HashSet<String> = std::collections::HashSet::new();
    for site in &file.sites {
        if !seen_sites.insert(site.station.clone()) {
            return Err(LoadError::DuplicateSite(site.station.clone()));
        }
        let station_id = *station_ids
            .get(&site.station)
            .ok_or_else(|| LoadError::UnknownStation {
                referenced_by: "site".to_string(),
                id: site.station.clone(),
            })?;
        if !(0.0..=1.0).contains(&site.storage_initial_soc) {
            return Err(LoadError::InvalidSocInitial {
                station: site.station.clone(),
                soc: site.storage_initial_soc,
            });
        }
        energy_sites.push(EnergySiteConfig {
            station: station_id,
            pv_nameplate_kw: site.pv_nameplate_kw,
            storage_capacity_kwh: site.storage_capacity_kwh,
            storage_max_charge_kw: site.storage_max_charge_kw,
            storage_max_discharge_kw: site.storage_max_discharge_kw,
            storage_initial_soc: site.storage_initial_soc,
            grid_import_kw: site.grid_import_kw,
            grid_export_kw: site.grid_export_kw,
        });
    }

    // --- Faults -------------------------------------------------------------
    let faults = build_faults(&file.faults, &station_ids, start_time_s)?;

    // --- Consist & climate --------------------------------------------------
    let consist = build_consist(file.consist.as_ref());
    let climate = ClimateModel {
        ambient_c: file.climate.ambient_c,
        peak_sun_hours: file.climate.peak_sun_hours,
        hvac_uplift_frac: file.climate.hvac_uplift_frac.unwrap_or_else(|| {
            ((file.climate.ambient_c - 25.0) / 25.0).clamp(0.0, 0.25)
        }),
    };

    Ok(ScenarioConfig {
        name: file.scenario.name,
        network,
        fleets,
        consist,
        climate,
        start_time_s_after_midnight: start_time_s,
        energy_sites,
        faults,
    })
}

fn build_faults(
    specs: &[FaultSpec],
    station_ids: &HashMap<String, StationId>,
    sim_start_s: u32,
) -> Result<Vec<Fault>, LoadError> {
    let mut faults = Vec::new();
    for spec in specs {
        if spec.day < 1 {
            return Err(LoadError::InvalidFaultDay {
                name: spec.name.clone(),
                day: spec.day,
            });
        }

        let from_tod = parse_time("fault.from", &spec.from)?;
        let to_tod = parse_time("fault.to", &spec.to)?;
        if to_tod <= from_tod {
            return Err(LoadError::InvalidFaultWindow { name: spec.name.clone() });
        }

        // Absolute seconds since midnight of day 1, then shift by -sim_start_s
        // to get absolute sim seconds.
        let abs_from = (spec.day - 1) * 86400 + from_tod;
        let abs_to = (spec.day - 1) * 86400 + to_tod;
        let from_sim_s = abs_from.saturating_sub(sim_start_s);
        let to_sim_s = abs_to.saturating_sub(sim_start_s);
        if to_sim_s <= from_sim_s {
            // The whole fault window is before sim start; skip silently.
            continue;
        }

        // Resolve station scope if present.
        let scope = match &spec.station {
            Some(s) => FaultScope::Station(*station_ids.get(s).ok_or_else(|| {
                LoadError::UnknownStation {
                    referenced_by: format!("fault '{}'", spec.name),
                    id: s.clone(),
                }
            })?),
            None => FaultScope::All,
        };

        let kind = match spec.kind.as_str() {
            "dust_event" => {
                let factor = spec
                    .pv_output_factor
                    .ok_or_else(|| LoadError::DustEventMissingFactor(spec.name.clone()))?;
                if !(0.0..=1.0).contains(&factor) {
                    return Err(LoadError::InvalidDustFactor {
                        name: spec.name.clone(),
                        factor,
                    });
                }
                FaultKind::DustEvent {
                    pv_output_factor: factor,
                    scope,
                }
            }
            "grid_outage" => FaultKind::GridOutage { scope },
            "charging_pad_outage" => match scope {
                FaultScope::Station(station) => FaultKind::ChargingPadOutage { station },
                FaultScope::All => {
                    return Err(LoadError::ChargingPadOutageMissingStation(
                        spec.name.clone(),
                    ));
                }
            },
            "lidar_offline" => FaultKind::LidarOffline {
                scope: train_scope(spec)?,
            },
            "radar_offline" => FaultKind::RadarOffline {
                scope: train_scope(spec)?,
            },
            "ultrasonic_channel_stale" => {
                let channel = spec
                    .channel
                    .ok_or_else(|| LoadError::UltrasonicChannelMissing(spec.name.clone()))?;
                if channel > 3 {
                    return Err(LoadError::UltrasonicChannelOutOfRange {
                        name: spec.name.clone(),
                        channel,
                    });
                }
                FaultKind::UltrasonicChannelStale {
                    scope: train_scope(spec)?,
                    channel,
                }
            }
            "obstacle_peer_disagreement" => FaultKind::ObstaclePeerDisagreement {
                scope: train_scope(spec)?,
            },
            "wayside_intrusion" => {
                let sid = spec
                    .section_id
                    .ok_or_else(|| LoadError::WaysideIntrusionMissingSection(spec.name.clone()))?;
                let state = match spec.intrusion_state.as_deref().unwrap_or("present") {
                    "clear" => osr_interlocking::IntrusionState::Clear,
                    "unknown" => osr_interlocking::IntrusionState::Unknown,
                    "present" => osr_interlocking::IntrusionState::Present,
                    other => {
                        return Err(LoadError::InvalidIntrusionState {
                            name: spec.name.clone(),
                            state: other.to_string(),
                        });
                    }
                };
                FaultKind::WaysideIntrusion {
                    section: SectionId::new(sid),
                    state,
                }
            }
            other => return Err(LoadError::InvalidFaultKind(other.to_string())),
        };

        faults.push(Fault {
            name: spec.name.clone(),
            from_sim_s,
            to_sim_s,
            kind,
        });
    }
    Ok(faults)
}

/// Resolve the `train` field of a fault spec into a `TrainFaultScope`.
/// Absent → `All`; `"T{n}"` → `Train(TrainId(n))`; anything else → error.
fn train_scope(spec: &FaultSpec) -> Result<TrainFaultScope, LoadError> {
    match &spec.train {
        None => Ok(TrainFaultScope::All),
        Some(s) => {
            let digits = s.strip_prefix('T').ok_or_else(|| LoadError::UnknownTrain {
                referenced_by: format!("fault '{}'", spec.name),
                id: s.clone(),
            })?;
            let n: u64 = digits.parse().map_err(|_| LoadError::UnknownTrain {
                referenced_by: format!("fault '{}'", spec.name),
                id: s.clone(),
            })?;
            Ok(TrainFaultScope::Train(osr_core::TrainId::new(n)))
        }
    }
}

fn build_consist(spec: Option<&ConsistSpec>) -> ConsistDescriptor {
    let mut c = ConsistDescriptor::reference_3car();
    let Some(s) = spec else { return c };
    if let Some(v) = s.car_count { c.car_count = v; }
    if let Some(v) = s.length_m { c.length_mm = v * 1_000; }
    if let Some(v) = s.mass_kg { c.mass_kg = v; }
    if let Some(v) = s.max_speed_kmh { c.max_speed_mps = v / 3.6; }
    if let Some(v) = s.battery_capacity_kwh { c.battery_capacity_wh = v * 1_000; }
    if let Some(v) = s.service_accel_mps2 { c.service_accel_mps2 = v; }
    c
}

fn parse_time(field: &'static str, s: &str) -> Result<u32, LoadError> {
    let parts: Vec<&str> = s.split(':').collect();
    let bad = || LoadError::InvalidTime { field, value: s.to_string() };
    if parts.len() != 2 {
        return Err(bad());
    }
    let h: u32 = parts[0].parse().map_err(|_| bad())?;
    let m: u32 = parts[1].parse().map_err(|_| bad())?;
    if h >= 24 || m >= 60 {
        return Err(bad());
    }
    Ok(h * 3600 + m * 60)
}

fn parse_heading(s: &str) -> Result<Heading, LoadError> {
    match s.to_ascii_lowercase().as_str() {
        "forward" | "fwd" | "f" => Ok(Heading::Forward),
        "reverse" | "rev" | "r" => Ok(Heading::Reverse),
        _ => Err(LoadError::InvalidHeading(s.to_string())),
    }
}
