//! TOML-based scenario definition.
//!
//! Users describe a scenario — stations, lines, fleets, schedules, climate —
//! in a plain-text `.toml` file. The loader validates it and builds the
//! in-memory `ScenarioConfig` that the sim engine consumes.
//!
//! Schema reference: see `lib/examples/README.md` at the repository root.

use osr_core::{ConsistDescriptor, Line, Network, Section, SectionId, Station, StationId};
use serde::Deserialize;
use std::collections::HashMap;

use crate::energy::EnergySiteConfig;
use crate::fault::{Fault, FaultKind, FaultScope, TrainFaultScope};
use crate::habd_systems::{HabdDetectorConfig, HabdResetAction, HabdTrackPosition};
use crate::schedule::{LineSchedule, TimeWindow};
use crate::sim::{
    ClimateModel, EnergyAdaptiveServiceConfig, LineFleet, RoofPvAirCleanerConfig, RoofPvConfig,
    ScenarioConfig, TrainsetSystemsConfig,
};
use crate::train::Heading;
use crate::wayside_asset_systems::{LevelCrossingAssetConfig, SwitchAssetConfig};

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
    /// Trackside energy sites. A station without a site cannot charge.
    #[serde(default)]
    pub sites: Vec<SiteSpec>,
    /// Explicit physical hot-axle detector sites.
    #[serde(default)]
    pub habd_detectors: Vec<HabdDetectorSpec>,
    /// Inspected, named-authority releases for latched HABD stop orders.
    #[serde(default)]
    pub habd_resets: Vec<HabdResetSpec>,
    /// Explicit point machines generated from city switch assets.
    #[serde(default)]
    pub switches: Vec<SwitchAssetSpec>,
    /// Explicit at-grade road/rail crossings; grade-separated cities omit it.
    #[serde(default)]
    pub level_crossings: Vec<LevelCrossingAssetSpec>,
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
    /// Concurrent depot clean, safety inspection, and low-C recharge slot.
    #[serde(default)]
    pub depot_service_seconds: u32,
    /// Automatically widen off-peak headways when actual charging delivery
    /// leaves a train below the normal operating SoC target.
    #[serde(default)]
    pub energy_adaptive_service: bool,
    #[serde(default = "default_normal_service_soc")]
    pub normal_service_soc: f32,
    #[serde(default = "default_maximum_headway_multiplier")]
    pub maximum_headway_multiplier: f32,
    #[serde(default = "default_protected_peak_headway_min")]
    pub protected_peak_headway_min: u32,
}

fn default_normal_service_soc() -> f32 {
    0.40
}

fn default_maximum_headway_multiplier() -> f32 {
    3.0
}

fn default_protected_peak_headway_min() -> u32 {
    3
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
    pub length_m: Option<f32>,
    #[serde(default)]
    pub mass_kg: Option<u32>,
    #[serde(default)]
    pub max_speed_kmh: Option<f32>,
    #[serde(default)]
    pub battery_capacity_kwh: Option<u32>,
    /// Nominal net traction + auxiliary energy at the car level. Older
    /// scenarios default to the conservative 4.0 kWh/car-km planning case.
    #[serde(default)]
    pub energy_kwh_per_car_km: Option<f32>,
    #[serde(default)]
    pub passenger_capacity: Option<u32>,
    #[serde(default)]
    pub seat_count: Option<u32>,
    #[serde(default)]
    pub crush_capacity: Option<u32>,
    /// Service-brake acceleration, m/s² (default 1.0).
    #[serde(default)]
    pub service_accel_mps2: Option<f32>,
    /// Optional onboard PV package. In TOML this is written as
    /// `[consist.roof_pv]`.
    #[serde(default)]
    pub roof_pv: Option<RoofPvSpec>,
    /// Buildable trainset small-component contract (`[consist.systems]`).
    #[serde(default)]
    pub systems: Option<TrainsetSystemsSpec>,
}

#[derive(Debug, Default, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct TrainsetSystemsSpec {
    pub mechanical_standard_revision: Option<String>,
    pub door_cassettes_per_car: Option<u32>,
    pub window_cassettes_per_car: Option<u32>,
    pub service_rails_per_car: Option<u32>,
    pub fastener_family_count: Option<u32>,
    pub connector_family_count: Option<u32>,
    pub main_light_modules_per_car: Option<u32>,
    pub emergency_light_modules_per_car: Option<u32>,
    pub door_threshold_light_modules_per_car: Option<u32>,
    pub lighting_power_w_per_car: Option<f32>,
    pub hvac_thermal_kw_per_car: Option<f32>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RoofPvSpec {
    /// Trainset-level DC nameplate after module/string aggregation.
    pub nameplate_kw: f32,
    /// Usable output derate applied after the shared PV curve
    /// (module heat, MPPT, cable, dirt, and mounting losses). Default 1.0.
    #[serde(default = "default_roof_pv_usable_factor")]
    pub usable_factor: f32,
    /// Whether roof PV charges while the train is in a section. Default true.
    #[serde(default = "default_true")]
    pub charges_while_moving: bool,
    /// Whether roof PV charges during station dwell or dispatch hold. Default true.
    #[serde(default = "default_true")]
    pub charges_while_dwelled: bool,
    /// Optional low-pressure air-pump / air-knife cleaner for dusty service.
    #[serde(default)]
    pub air_cleaner: Option<RoofPvAirCleanerSpec>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RoofPvAirCleanerSpec {
    /// If the block is present, default to enabled unless explicitly disabled.
    #[serde(default = "default_true")]
    pub enabled: bool,
    /// Trainset-level compressor/blower parasitic load while PV is available.
    #[serde(default)]
    pub compressor_power_kw: f32,
    /// Fraction of dust-driven PV loss recovered by the cleaner, 0.0..1.0.
    #[serde(default)]
    pub dust_loss_recovery_frac: f32,
}

fn default_roof_pv_usable_factor() -> f32 {
    1.0
}

fn default_true() -> bool {
    true
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
    /// This depot performs the scheduled turnaround clean/inspection. Other
    /// depot/layup stations may still top up and stable trains.
    #[serde(default)]
    pub depot_service: bool,
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
    /// Standard stationary-LFP module size. Site capacity must be an
    /// integer multiple when non-zero.
    #[serde(default = "default_storage_module_kwh")]
    pub storage_module_kwh: f32,
    #[serde(default = "default_charger_max_kw")]
    pub charger_max_kw: f32,
    #[serde(default = "default_charger_max_current_a")]
    pub charger_max_current_a: f32,
    #[serde(default = "default_charger_bus_voltage_v")]
    pub charger_bus_voltage_v: f32,
    #[serde(default = "default_charger_efficiency")]
    pub charger_efficiency: f32,
    #[serde(default = "default_charger_contact_count")]
    pub charger_contact_count: u8,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HabdDetectorSpec {
    pub id: String,
    pub line: String,
    /// Lower-chainage station bounding the detector's interstation segment.
    pub after_station: String,
    /// Physical offset from `after_station`, valid for both directions.
    pub offset_m: u32,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct HabdResetSpec {
    /// Time of day at which the inspected train may be released.
    pub at: String,
    #[serde(default = "default_fault_day")]
    pub day: u32,
    pub train: String,
    pub authorised_by: String,
    pub inspection_reference: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SwitchAssetSpec {
    pub id: String,
    pub station: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LevelCrossingAssetSpec {
    pub id: String,
    pub line: String,
    pub after_station: String,
    pub offset_m: u32,
}

fn default_initial_soc() -> f32 {
    0.5
}

fn default_storage_module_kwh() -> f32 {
    500.0
}
fn default_charger_max_kw() -> f32 {
    500.0
}
fn default_charger_max_current_a() -> f32 {
    825.0
}
fn default_charger_bus_voltage_v() -> f32 {
    650.0
}
fn default_charger_efficiency() -> f32 {
    0.98
}
fn default_charger_contact_count() -> u8 {
    2
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FaultSpec {
    pub name: String,
    /// One of: `"dust_event"`, `"grid_outage"`, `"charging_pad_outage"`,
    /// `"platform_door_obstruction"`, `"station_scada_failure"`,
    /// `"lidar_offline"`, `"radar_offline"`, `"ultrasonic_channel_stale"`,
    /// `"obstacle_peer_disagreement"`, `"passenger_intercom_press"`,
    /// `"battery_off_gas"`, `"battery_mist_failure"`,
    /// `"battery_fire_escalation"`, `"t2g_primary_offline"`,
    /// `"t2g_all_offline"`, `"hot_axle_overheat"`,
    /// `"wayside_habd_warning"`, `"wayside_habd_overheat"`, `"cbm_degradation"`,
    /// `"balise_missed"`, `"balise_position_mismatch"`,
    /// `"fare_token_tamper"`,
    /// or `"wayside_intrusion"`.
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
    /// For scoped infrastructure faults: which station this affects. Omission
    /// applies the event to all stations/sites. Required for a pad outage.
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
    InvalidTime {
        field: &'static str,
        value: String,
    },
    InvalidHeading(String),
    DuplicateStationId(String),
    DuplicateLineId(String),
    UnknownStation {
        referenced_by: String,
        id: String,
    },
    UnknownLine {
        referenced_by: String,
        id: String,
    },
    RingMissingWrapLength(String),
    LinearWithWrapLength(String),
    LineWithFewerThanTwoStations(String),
    EmptyFleetDispatchPoints(String),
    EmptySchedule(String),
    ZeroHeadway {
        line: String,
        from: String,
        to: String,
    },
    ServiceWindowInverted {
        line: String,
    },
    ScheduleWindowInverted {
        line: String,
        from: String,
        to: String,
    },
    DispatchPointNotOnLine {
        line: String,
        station: String,
    },
    InconsistentFirstStationDistance(String),
    DuplicateSite(String),
    InvalidSocInitial {
        station: String,
        soc: f32,
    },
    InvalidEnergyIntensity(f32),
    InvalidTrainsetSystems(String),
    InvalidAdaptiveServiceTarget(f32),
    InvalidAdaptiveHeadwayMultiplier(f32),
    InvalidFaultKind(String),
    InvalidFaultDay {
        name: String,
        day: u32,
    },
    InvalidFaultWindow {
        name: String,
    },
    DustEventMissingFactor(String),
    InvalidDustFactor {
        name: String,
        factor: f32,
    },
    ChargingPadOutageMissingStation(String),
    UltrasonicChannelOutOfRange {
        name: String,
        channel: u8,
    },
    UltrasonicChannelMissing(String),
    UnknownTrain {
        referenced_by: String,
        id: String,
    },
    WaysideIntrusionMissingSection(String),
    InvalidIntrusionState {
        name: String,
        state: String,
    },
    DuplicateHabdDetector(String),
    InvalidHabdDetector(String),
    InvalidHabdReset(String),
    InvalidWaysideAsset(String),
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
                write!(
                    f,
                    "service_end must differ from service_start for line '{line}'"
                )
            }
            ScheduleWindowInverted { line, from, to } => {
                write!(
                    f,
                    "schedule window {from}–{to} on line '{line}' has zero duration"
                )
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
            InvalidEnergyIntensity(value) => write!(
                f,
                "consist energy_kwh_per_car_km={value}; must be finite and greater than zero"
            ),
            InvalidTrainsetSystems(message) => write!(f, "invalid consist.systems: {message}"),
            InvalidAdaptiveServiceTarget(value) => write!(
                f,
                "scenario.normal_service_soc={value}; must be finite and in (0.20, 1.0]"
            ),
            InvalidAdaptiveHeadwayMultiplier(value) => write!(
                f,
                "scenario.maximum_headway_multiplier={value}; must be finite and >= 1.0"
            ),
            InvalidFaultKind(k) => write!(
                f,
                "unknown fault kind '{k}' (expected one of: dust_event, grid_outage, \
                 charging_pad_outage, lidar_offline, radar_offline, \
                 platform_door_obstruction, station_scada_failure, \
                 ultrasonic_channel_stale, obstacle_peer_disagreement, \
                 passenger_intercom_press, battery_off_gas, \
                 battery_mist_failure, battery_fire_escalation, \
                 t2g_primary_offline, t2g_all_offline, \
                 hot_axle_overheat, wayside_habd_warning, wayside_habd_overheat, \
                 cbm_degradation, balise_missed, balise_position_mismatch, \
                 fare_token_tamper, \
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
            DuplicateHabdDetector(id) => write!(f, "duplicate HABD detector id '{id}'"),
            InvalidHabdDetector(message) => write!(f, "invalid HABD detector: {message}"),
            InvalidHabdReset(message) => write!(f, "invalid HABD reset: {message}"),
            InvalidWaysideAsset(message) => write!(f, "invalid wayside asset: {message}"),
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
/// `cities/catalogue/west-asia/Iraq/Samawah/samawah.toml` as the project's
/// reference scenario. This function returns a parsed
/// [`ScenarioConfig`] from a snapshot of that file taken at build
/// time (`include_str!`). Used by the CLI and GUI binaries as the
/// default scenario when the operator hasn't passed `--config`,
/// and by the integration tests as a hermetic fixture that doesn't
/// depend on the working directory.
///
/// Panics on parse failure — the bundled file is regenerated by
/// `tools/automation/regenerate-city.sh samawah` and committed to git, so a
/// parse failure means the schema drifted and the build was wrong.
#[must_use]
pub fn canonical_samawah_scenario() -> ScenarioConfig {
    const SAMAWAH_TOML: &str =
        include_str!("../../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml");
    load_scenario_from_str(SAMAWAH_TOML)
        .expect("bundled samawah.toml failed to parse — schema drifted vs scenario_file.rs")
}

// ===========================================================================
// Builder: TOML structure → ScenarioConfig
// ===========================================================================

fn build_scenario(file: ScenarioFile) -> Result<ScenarioConfig, LoadError> {
    let start_time_s = parse_time("scenario.start_time", &file.scenario.start_time)?;
    if !file.scenario.normal_service_soc.is_finite()
        || !(0.20..=1.0).contains(&file.scenario.normal_service_soc)
        || file.scenario.normal_service_soc <= 0.20
    {
        return Err(LoadError::InvalidAdaptiveServiceTarget(
            file.scenario.normal_service_soc,
        ));
    }
    if !file.scenario.maximum_headway_multiplier.is_finite()
        || file.scenario.maximum_headway_multiplier < 1.0
    {
        return Err(LoadError::InvalidAdaptiveHeadwayMultiplier(
            file.scenario.maximum_headway_multiplier,
        ));
    }

    // --- Stations: assign u64 IDs ------------------------------------------
    let mut station_ids: HashMap<String, StationId> = HashMap::new();
    let mut network = Network::default();

    let mut depot_service_stations = std::collections::BTreeSet::new();
    for (next_station_id, spec) in (1_u64..).zip(&file.stations) {
        if station_ids.contains_key(&spec.id) {
            return Err(LoadError::DuplicateStationId(spec.id.clone()));
        }
        let id = StationId::new(next_station_id);
        station_ids.insert(spec.id.clone(), id);
        if spec.depot_service {
            depot_service_stations.insert(id);
        }

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

            network.sections.insert(
                fwd_id,
                Section {
                    id: fwd_id,
                    from_station: from,
                    to_station: to,
                    length_mm,
                    max_speed_mps: 22.0,
                },
            );
            network.sections.insert(
                rev_id,
                Section {
                    id: rev_id,
                    from_station: to,
                    to_station: from,
                    length_mm,
                    max_speed_mps: 22.0,
                },
            );
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
            network.sections.insert(
                fwd_id,
                Section {
                    id: fwd_id,
                    from_station: last,
                    to_station: first,
                    length_mm: wrap_len_mm,
                    max_speed_mps: 22.0,
                },
            );
            network.sections.insert(
                rev_id,
                Section {
                    id: rev_id,
                    from_station: first,
                    to_station: last,
                    length_mm: wrap_len_mm,
                    max_speed_mps: 22.0,
                },
            );
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

    let habd_detectors =
        build_habd_detectors(&file.habd_detectors, &station_ids, &line_indices, &network)?;
    let switches = build_switch_assets(&file.switches, &station_ids)?;
    let level_crossings =
        build_level_crossing_assets(&file.level_crossings, &station_ids, &line_indices, &network)?;

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
            let station =
                *station_ids
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
        if service_end_s == service_start_s {
            return Err(LoadError::ServiceWindowInverted {
                line: spec.line.clone(),
            });
        }

        let mut windows = Vec::new();
        for w in &spec.schedule {
            let start_s = parse_time("schedule.from", &w.from)?;
            let end_s = parse_time("schedule.to", &w.to)?;
            if end_s == start_s {
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
        let station_id =
            *station_ids
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
            storage_module_kwh: site.storage_module_kwh,
            charger_max_kw: site.charger_max_kw,
            charger_max_current_a: site.charger_max_current_a,
            charger_bus_voltage_v: site.charger_bus_voltage_v,
            charger_efficiency: site.charger_efficiency,
            charger_contact_count: site.charger_contact_count,
        });
    }

    // --- Faults -------------------------------------------------------------
    let faults = build_faults(&file.faults, &station_ids, start_time_s)?;
    let habd_resets = build_habd_resets(&file.habd_resets, start_time_s)?;

    // --- Consist & climate --------------------------------------------------
    let consist = build_consist(file.consist.as_ref());
    let trainset_systems = build_trainset_systems(
        file.consist
            .as_ref()
            .and_then(|consist| consist.systems.as_ref()),
    )?;
    let energy_kwh_per_car_km = file
        .consist
        .as_ref()
        .and_then(|c| c.energy_kwh_per_car_km)
        .unwrap_or(4.0);
    if !energy_kwh_per_car_km.is_finite() || energy_kwh_per_car_km <= 0.0 {
        return Err(LoadError::InvalidEnergyIntensity(energy_kwh_per_car_km));
    }
    let roof_pv = build_roof_pv(file.consist.as_ref().and_then(|c| c.roof_pv.as_ref()));
    let climate = ClimateModel {
        ambient_c: file.climate.ambient_c,
        peak_sun_hours: file.climate.peak_sun_hours,
        hvac_uplift_frac: file
            .climate
            .hvac_uplift_frac
            .unwrap_or_else(|| ((file.climate.ambient_c - 25.0) / 25.0).clamp(0.0, 0.25)),
    };

    Ok(ScenarioConfig {
        name: file.scenario.name,
        network,
        fleets,
        consist,
        trainset_systems,
        energy_kwh_per_car_km,
        roof_pv,
        climate,
        start_time_s_after_midnight: start_time_s,
        depot_service_seconds: file.scenario.depot_service_seconds,
        energy_adaptive_service: EnergyAdaptiveServiceConfig {
            enabled: file.scenario.energy_adaptive_service,
            normal_service_soc: file.scenario.normal_service_soc,
            maximum_headway_multiplier: file.scenario.maximum_headway_multiplier,
            protected_peak_headway_s: file.scenario.protected_peak_headway_min * 60,
        },
        depot_service_stations,
        energy_sites,
        habd_detectors,
        habd_resets,
        switches,
        level_crossings,
        faults,
    })
}

fn build_switch_assets(
    specs: &[SwitchAssetSpec],
    station_ids: &HashMap<String, StationId>,
) -> Result<Vec<SwitchAssetConfig>, LoadError> {
    let mut seen = std::collections::BTreeSet::new();
    specs
        .iter()
        .map(|spec| {
            if spec.id.trim().is_empty() || !seen.insert(spec.id.clone()) {
                return Err(LoadError::InvalidWaysideAsset(format!(
                    "switch id '{}' is empty or duplicated",
                    spec.id
                )));
            }
            let station =
                *station_ids
                    .get(&spec.station)
                    .ok_or_else(|| LoadError::UnknownStation {
                        referenced_by: format!("switch '{}'", spec.id),
                        id: spec.station.clone(),
                    })?;
            Ok(SwitchAssetConfig {
                id: spec.id.clone(),
                station,
            })
        })
        .collect()
}

fn build_level_crossing_assets(
    specs: &[LevelCrossingAssetSpec],
    station_ids: &HashMap<String, StationId>,
    line_indices: &HashMap<String, usize>,
    network: &Network,
) -> Result<Vec<LevelCrossingAssetConfig>, LoadError> {
    let mut seen = std::collections::BTreeSet::new();
    let mut crossings = Vec::with_capacity(specs.len());
    for spec in specs {
        if spec.id.trim().is_empty() || !seen.insert(spec.id.clone()) {
            return Err(LoadError::InvalidWaysideAsset(format!(
                "level-crossing id '{}' is empty or duplicated",
                spec.id
            )));
        }
        let &line_index = line_indices
            .get(&spec.line)
            .ok_or_else(|| LoadError::UnknownLine {
                referenced_by: format!("level crossing '{}'", spec.id),
                id: spec.line.clone(),
            })?;
        let station =
            *station_ids
                .get(&spec.after_station)
                .ok_or_else(|| LoadError::UnknownStation {
                    referenced_by: format!("level crossing '{}'", spec.id),
                    id: spec.after_station.clone(),
                })?;
        let line = &network.lines[line_index];
        let section_index = line
            .stations
            .iter()
            .position(|candidate| *candidate == station)
            .ok_or_else(|| {
                LoadError::InvalidWaysideAsset(format!(
                    "level crossing '{}' station is not on line '{}'",
                    spec.id, spec.line
                ))
            })?;
        let Some(&forward) = line.forward_sections.get(section_index) else {
            return Err(LoadError::InvalidWaysideAsset(format!(
                "level crossing '{}' has no following section",
                spec.id
            )));
        };
        let reverse = line.reverse_sections[section_index];
        let length_mm = network.section(forward).length_mm;
        let offset_mm = u64::from(spec.offset_m).saturating_mul(1_000);
        if offset_mm == 0 || offset_mm >= length_mm {
            return Err(LoadError::InvalidWaysideAsset(format!(
                "level crossing '{}' offset_m={} must be inside its section",
                spec.id, spec.offset_m
            )));
        }
        crossings.push(LevelCrossingAssetConfig {
            id: spec.id.clone(),
            sections: vec![forward, reverse],
        });
    }
    Ok(crossings)
}

fn build_habd_detectors(
    specs: &[HabdDetectorSpec],
    station_ids: &HashMap<String, StationId>,
    line_indices: &HashMap<String, usize>,
    network: &Network,
) -> Result<Vec<HabdDetectorConfig>, LoadError> {
    let mut seen = std::collections::BTreeSet::new();
    let mut detectors = Vec::with_capacity(specs.len());
    for spec in specs {
        if spec.id.trim().is_empty() {
            return Err(LoadError::InvalidHabdDetector(
                "id must not be empty".to_string(),
            ));
        }
        if !seen.insert(spec.id.clone()) {
            return Err(LoadError::DuplicateHabdDetector(spec.id.clone()));
        }
        let &line_index = line_indices
            .get(&spec.line)
            .ok_or_else(|| LoadError::UnknownLine {
                referenced_by: format!("HABD detector '{}'", spec.id),
                id: spec.line.clone(),
            })?;
        let station =
            *station_ids
                .get(&spec.after_station)
                .ok_or_else(|| LoadError::UnknownStation {
                    referenced_by: format!("HABD detector '{}'", spec.id),
                    id: spec.after_station.clone(),
                })?;
        let line = &network.lines[line_index];
        let section_index = line
            .stations
            .iter()
            .position(|candidate| *candidate == station)
            .ok_or_else(|| {
                LoadError::InvalidHabdDetector(format!(
                    "'{}' is not on line '{}'",
                    spec.after_station, spec.line
                ))
            })?;
        let Some(&forward_section) = line.forward_sections.get(section_index) else {
            return Err(LoadError::InvalidHabdDetector(format!(
                "'{}' has no following section on line '{}'",
                spec.after_station, spec.line
            )));
        };
        let reverse_section = line.reverse_sections[section_index];
        let section_length_mm = network.section(forward_section).length_mm;
        let offset_mm = u64::from(spec.offset_m).saturating_mul(1_000);
        if offset_mm == 0 || offset_mm >= section_length_mm {
            return Err(LoadError::InvalidHabdDetector(format!(
                "'{}' offset_m={} must be inside its {} m section",
                spec.id,
                spec.offset_m,
                section_length_mm / 1_000
            )));
        }
        detectors.push(HabdDetectorConfig {
            id: spec.id.clone(),
            track_positions: vec![
                HabdTrackPosition {
                    section: forward_section,
                    offset_mm,
                },
                HabdTrackPosition {
                    section: reverse_section,
                    offset_mm: section_length_mm - offset_mm,
                },
            ],
        });
    }
    Ok(detectors)
}

fn build_habd_resets(
    specs: &[HabdResetSpec],
    sim_start_s: u32,
) -> Result<Vec<HabdResetAction>, LoadError> {
    let mut resets = Vec::with_capacity(specs.len());
    for spec in specs {
        if spec.day == 0 {
            return Err(LoadError::InvalidHabdReset(
                "day must be at least 1".to_string(),
            ));
        }
        if spec.authorised_by.trim().is_empty() || spec.inspection_reference.trim().is_empty() {
            return Err(LoadError::InvalidHabdReset(
                "authorised_by and inspection_reference are required".to_string(),
            ));
        }
        let at_tod = parse_time("habd_reset.at", &spec.at)?;
        let absolute = (spec.day - 1).saturating_mul(86_400).saturating_add(at_tod);
        if absolute < sim_start_s {
            continue;
        }
        resets.push(HabdResetAction {
            at_sim_s: absolute - sim_start_s,
            train: parse_train_id("HABD reset", &spec.train)?,
            authorised_by: spec.authorised_by.clone(),
            inspection_reference: spec.inspection_reference.clone(),
        });
    }
    Ok(resets)
}

fn build_trainset_systems(
    spec: Option<&TrainsetSystemsSpec>,
) -> Result<TrainsetSystemsConfig, LoadError> {
    let mut config = TrainsetSystemsConfig::default();
    let Some(spec) = spec else { return Ok(config) };
    macro_rules! assign {
        ($field:ident) => {
            if let Some(value) = spec.$field {
                config.$field = value;
            }
        };
    }
    if let Some(value) = &spec.mechanical_standard_revision {
        config.mechanical_standard_revision = value.clone();
    }
    assign!(door_cassettes_per_car);
    assign!(window_cassettes_per_car);
    assign!(service_rails_per_car);
    assign!(fastener_family_count);
    assign!(connector_family_count);
    assign!(main_light_modules_per_car);
    assign!(emergency_light_modules_per_car);
    assign!(door_threshold_light_modules_per_car);
    assign!(lighting_power_w_per_car);
    assign!(hvac_thermal_kw_per_car);

    if config.mechanical_standard_revision.trim().is_empty() {
        return Err(LoadError::InvalidTrainsetSystems(
            "mechanical_standard_revision must not be empty".to_string(),
        ));
    }
    let counts = [
        ("door_cassettes_per_car", config.door_cassettes_per_car),
        ("window_cassettes_per_car", config.window_cassettes_per_car),
        ("service_rails_per_car", config.service_rails_per_car),
        ("fastener_family_count", config.fastener_family_count),
        ("connector_family_count", config.connector_family_count),
        (
            "main_light_modules_per_car",
            config.main_light_modules_per_car,
        ),
        (
            "emergency_light_modules_per_car",
            config.emergency_light_modules_per_car,
        ),
        (
            "door_threshold_light_modules_per_car",
            config.door_threshold_light_modules_per_car,
        ),
    ];
    if let Some((name, _)) = counts.into_iter().find(|(_, value)| *value == 0) {
        return Err(LoadError::InvalidTrainsetSystems(format!(
            "{name} must be greater than zero"
        )));
    }
    for (name, value) in [
        ("lighting_power_w_per_car", config.lighting_power_w_per_car),
        ("hvac_thermal_kw_per_car", config.hvac_thermal_kw_per_car),
    ] {
        if !value.is_finite() || value <= 0.0 {
            return Err(LoadError::InvalidTrainsetSystems(format!(
                "{name} must be finite and greater than zero"
            )));
        }
    }
    Ok(config)
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
            return Err(LoadError::InvalidFaultWindow {
                name: spec.name.clone(),
            });
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
            "platform_door_obstruction" => FaultKind::PlatformDoorObstruction { scope },
            "station_scada_failure" => FaultKind::StationScadaFailure { scope },
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
            "passenger_intercom_press" => FaultKind::PassengerIntercomPress {
                scope: train_scope(spec)?,
            },
            "battery_off_gas" => FaultKind::BatteryOffGas {
                scope: train_scope(spec)?,
            },
            "battery_mist_failure" => FaultKind::BatteryMistFailure {
                scope: train_scope(spec)?,
            },
            "battery_fire_escalation" => FaultKind::BatteryFireEscalation {
                scope: train_scope(spec)?,
            },
            "t2g_primary_offline" => FaultKind::T2gPrimaryOffline {
                scope: train_scope(spec)?,
            },
            "t2g_all_offline" => FaultKind::T2gAllOffline {
                scope: train_scope(spec)?,
            },
            "hot_axle_overheat" => FaultKind::HotAxleOverheat {
                scope: train_scope(spec)?,
            },
            "wayside_habd_overheat" => FaultKind::HabdOverheat {
                scope: train_scope(spec)?,
            },
            "wayside_habd_warning" => FaultKind::HabdWarning {
                scope: train_scope(spec)?,
            },
            "cbm_degradation" => FaultKind::CbmDegradation {
                scope: train_scope(spec)?,
            },
            "balise_missed" => FaultKind::BaliseMissed {
                scope: train_scope(spec)?,
            },
            "balise_position_mismatch" => FaultKind::BalisePositionMismatch {
                scope: train_scope(spec)?,
            },
            "fare_token_tamper" => FaultKind::FareTokenTamper { scope },
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
        Some(s) => Ok(TrainFaultScope::Train(parse_train_id(
            &format!("fault '{}'", spec.name),
            s,
        )?)),
    }
}

fn parse_train_id(referenced_by: &str, value: &str) -> Result<osr_core::TrainId, LoadError> {
    let digits = value
        .strip_prefix('T')
        .filter(|digits| !digits.is_empty())
        .ok_or_else(|| LoadError::UnknownTrain {
            referenced_by: referenced_by.to_string(),
            id: value.to_string(),
        })?;
    let number: u64 = digits.parse().map_err(|_| LoadError::UnknownTrain {
        referenced_by: referenced_by.to_string(),
        id: value.to_string(),
    })?;
    if number == 0 {
        return Err(LoadError::UnknownTrain {
            referenced_by: referenced_by.to_string(),
            id: value.to_string(),
        });
    }
    Ok(osr_core::TrainId::new(number))
}

fn build_consist(spec: Option<&ConsistSpec>) -> ConsistDescriptor {
    let mut c = ConsistDescriptor::reference_3car();
    let Some(s) = spec else { return c };
    if let Some(v) = s.car_count {
        c.car_count = v;
    }
    if let Some(v) = s.length_m {
        c.length_mm = (v.max(0.0) * 1_000.0).round() as u32;
    }
    if let Some(v) = s.mass_kg {
        c.mass_kg = v;
    }
    if let Some(v) = s.max_speed_kmh {
        c.max_speed_mps = v / 3.6;
    }
    if let Some(v) = s.battery_capacity_kwh {
        c.battery_capacity_wh = v * 1_000;
    }
    if let Some(v) = s.service_accel_mps2 {
        c.service_accel_mps2 = v;
    }
    c
}

fn build_roof_pv(spec: Option<&RoofPvSpec>) -> RoofPvConfig {
    let Some(s) = spec else {
        return RoofPvConfig::default();
    };
    RoofPvConfig {
        nameplate_kw: s.nameplate_kw.max(0.0),
        usable_factor: s.usable_factor.clamp(0.0, 1.0),
        charges_while_moving: s.charges_while_moving,
        charges_while_dwelled: s.charges_while_dwelled,
        air_cleaner: build_roof_pv_air_cleaner(s.air_cleaner.as_ref()),
    }
}

fn build_roof_pv_air_cleaner(spec: Option<&RoofPvAirCleanerSpec>) -> RoofPvAirCleanerConfig {
    let Some(s) = spec else {
        return RoofPvAirCleanerConfig::default();
    };
    RoofPvAirCleanerConfig {
        enabled: s.enabled,
        compressor_power_kw: s.compressor_power_kw.max(0.0),
        dust_loss_recovery_frac: s.dust_loss_recovery_frac.clamp(0.0, 1.0),
    }
}

fn parse_time(field: &'static str, s: &str) -> Result<u32, LoadError> {
    let parts: Vec<&str> = s.split(':').collect();
    let bad = || LoadError::InvalidTime {
        field,
        value: s.to_string(),
    };
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

#[cfg(test)]
mod trainset_system_tests {
    use super::*;

    #[test]
    fn canonical_scenario_loads_explicit_buildable_system_contract() {
        let scenario = canonical_samawah_scenario();
        assert_eq!(
            scenario.trainset_systems.mechanical_standard_revision,
            "A-DRAFT"
        );
        assert_eq!(scenario.trainset_systems.door_cassettes_per_car, 4);
        assert_eq!(scenario.trainset_systems.main_light_modules_per_car, 22);
        assert_eq!(scenario.habd_detectors.len(), 3);
        assert!(scenario
            .habd_detectors
            .iter()
            .all(|detector| detector.track_positions.len() == 2));
    }

    #[test]
    fn zero_component_count_fails_closed() {
        let source = include_str!("../../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml")
            .replace("door_cassettes_per_car = 4", "door_cassettes_per_car = 0");
        let error = load_scenario_from_str(&source).expect_err("zero door count must fail");
        assert!(error.to_string().contains("door_cassettes_per_car"));
    }

    #[test]
    fn expanded_fault_kinds_parse_with_applicable_scope() {
        let additions = [
            ("t2g_primary_offline", "train = \"T1\""),
            ("t2g_all_offline", "train = \"T1\""),
            ("hot_axle_overheat", "train = \"T1\""),
            ("wayside_habd_warning", "train = \"T1\""),
            ("wayside_habd_overheat", "train = \"T1\""),
            ("cbm_degradation", "train = \"T1\""),
            ("balise_missed", "train = \"T1\""),
            ("balise_position_mismatch", "train = \"T1\""),
            (
                "fare_token_tamper",
                "station = \"line-1-0147-0558-s000000\"",
            ),
            (
                "platform_door_obstruction",
                "station = \"line-1-0147-0558-s000000\"",
            ),
            (
                "station_scada_failure",
                "station = \"line-1-0147-0558-s000000\"",
            ),
        ]
        .into_iter()
        .enumerate()
        .map(|(index, (kind, scope))| {
            format!(
                "\n[[faults]]\nname = \"expanded-{index}\"\nkind = \"{kind}\"\nfrom = \"05:31\"\nto = \"05:32\"\n{scope}\n"
            )
        })
        .collect::<String>();
        let source = format!(
            "{}{}",
            include_str!("../../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml"),
            additions
        );
        let scenario = load_scenario_from_str(&source).expect("embedded faults should parse");
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::T2gPrimaryOffline { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::T2gAllOffline { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::HotAxleOverheat { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::HabdOverheat { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::HabdWarning { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::CbmDegradation { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::PlatformDoorObstruction { .. })));
        assert!(scenario
            .faults
            .iter()
            .any(|fault| matches!(fault.kind, FaultKind::StationScadaFailure { .. })));
    }

    #[test]
    fn inspected_habd_reset_parses_to_relative_sim_time() {
        let source = format!(
            "{}\n[[habd_resets]]\nat = \"05:32\"\ntrain = \"T1\"\nauthorised_by = \"rolling-stock-technician\"\ninspection_reference = \"inspection-42\"\n",
            include_str!("../../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml")
        );
        let scenario = load_scenario_from_str(&source).expect("qualified reset should parse");
        assert_eq!(scenario.habd_resets.len(), 1);
        assert_eq!(scenario.habd_resets[0].at_sim_s, 120);
        assert_eq!(scenario.habd_resets[0].train, osr_core::TrainId::new(1));
    }

    #[test]
    fn habd_location_must_be_inside_declared_section() {
        let source = include_str!("../../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml")
            .replace("offset_m = 5806", "offset_m = 999999");
        let error = load_scenario_from_str(&source).expect_err("invalid offset must fail");
        assert!(error.to_string().contains("must be inside"));
    }
}
