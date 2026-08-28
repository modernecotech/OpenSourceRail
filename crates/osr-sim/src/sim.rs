//! Time-stepped simulation engine.
//!
//! Service-level model:
//! - Trains move between adjacent stations over a computed travel time
//!   derived from section length and a continuous kinematic velocity profile.
//! - Energy is debited progressively while travelling (distance × kWh/km)
//!   and credited from station chargers and onboard roof PV.
//! - The `osr-interlocking` MA computer is the authoritative source of
//!   section occupancy (RFC 0004 M5). Every section entry is gated by
//!   `section_available_to`; the corresponding `TrainPositionReport`
//!   entry becomes the record that any follower sees. The pre-M5
//!   in-memory `OccupancyMap` is retired.
//! - Lines can be linear or ring. Linear lines flip heading at terminals;
//!   rings wrap around.

use osr_core::{
    ConsistDescriptor, Direction, EntryId, Line, Network, Position, Section, SectionId, StationId,
    TrainId,
};
use serde::{Deserialize, Serialize};

use crate::consensus_log::ConsensusBackend;
use crate::energy::{pv_output_kw, EnergySiteConfig, EnergySiteSummary, EnergySystem};
use crate::fault::{Fault, FaultEngine, FaultLogEntry};
use crate::ma_check::{self, MaCheckSummary};
use crate::onboard::{self, OnboardShadow, OnboardSummary};
use crate::physics::{kinematic_profile, sample_kinematic_profile, MotionSample};
use crate::schedule::{DispatchThrottle, LineSchedule};
use crate::train::{Heading, Train, TrainPhase};
use crate::vehicle_systems::{self, VehicleSystemsShadow, VehicleSystemsSummary};

use osr_core::TrackRef;
use osr_interlocking::{
    log::{
        Entry, EntryPayload, IntrusionState, PositionSource, SectionIntrusion, TrainDeparture,
        TrainPositionReport, TrainRegistration,
    },
    section_available_to, DerivedState,
};

/// Consensus-backed movement-authority log used by every simulation run.
#[derive(Debug)]
pub enum MaLogBackend {
    Consensus(Box<ConsensusBackend>),
    Direct(Box<DirectMaBackend>),
}

/// Bounded-memory movement-authority state for runs that explicitly disable
/// consensus auditing (`--ma-check-every 0`). It applies the exact same
/// interlocking entries to `DerivedState`, but retains only the latest entry
/// instead of three complete Raft logs plus a decoded committed prefix.
#[derive(Debug, Default)]
pub struct DirectMaBackend {
    registered: std::collections::BTreeSet<TrainId>,
    next_entry_id: u64,
    last_entry: Option<Entry>,
    derived: DerivedState,
}

impl MaLogBackend {
    fn new(consensus_audit_enabled: bool) -> Self {
        if consensus_audit_enabled {
            Self::Consensus(Box::default())
        } else {
            Self::Direct(Box::new(DirectMaBackend {
                next_entry_id: 1,
                ..DirectMaBackend::default()
            }))
        }
    }

    pub fn ensure_registered(&mut self, train: &Train, initial_head: TrackRef, t_s: u32) {
        match self {
            Self::Consensus(consensus) => consensus.ensure_registered(train, initial_head, t_s),
            Self::Direct(direct) => direct.ensure_registered(train, initial_head, t_s),
        }
    }

    pub fn emit_position(&mut self, train: &Train, head: TrackRef, tail: Option<i64>, t_s: u32) {
        match self {
            Self::Consensus(consensus) => consensus.emit_position(train, head, tail, t_s),
            Self::Direct(direct) => direct.emit_position(train, head, tail, t_s),
        }
    }

    /// Clear the interstation section footprint once the complete train is
    /// berthed at a platform. Station berths are outside the simplified MA
    /// section graph; the train registers again on its next section entry.
    pub fn emit_platform_handoff(&mut self, train_id: TrainId, t_s: u32) {
        match self {
            Self::Consensus(consensus) => consensus.emit_platform_handoff(train_id, t_s),
            Self::Direct(direct) => direct.emit_platform_handoff(train_id, t_s),
        }
    }

    /// Emit a wayside `SectionIntrusion` verdict (RFC 0016 v3).
    pub fn emit_intrusion(
        &mut self,
        section: SectionId,
        state: osr_interlocking::IntrusionState,
        issued_by: osr_core::EntityId,
        t_s: u32,
    ) {
        match self {
            Self::Consensus(consensus) => {
                consensus.emit_intrusion(section, state, issued_by, t_s);
            }
            Self::Direct(direct) => direct.emit_intrusion(section, state, issued_by, t_s),
        }
    }

    pub fn entries(&self) -> &[osr_interlocking::log::Entry] {
        match self {
            Self::Consensus(consensus) => consensus.entries(),
            Self::Direct(direct) => direct.last_entry.as_slice(),
        }
    }

    pub fn tick(&mut self, dt_ns: u64) {
        if let Self::Consensus(consensus) = self {
            consensus.tick(dt_ns);
        }
    }

    /// Cached `DerivedState` from whichever backend is in use.
    pub fn derived_state(&self) -> &DerivedState {
        match self {
            Self::Consensus(consensus) => consensus.derived_state(),
            Self::Direct(direct) => &direct.derived,
        }
    }

    /// Is `section` available for `train_id` to enter right now, per the
    /// MA computer's reading of the log? Delegates to
    /// `osr_interlocking::section_available_to` — the same primitive
    /// `compute_self_ma` uses when clipping the forward chain.
    pub fn section_available_to(&self, train_id: TrainId, section: SectionId) -> bool {
        section_available_to(train_id, section, self.derived_state())
    }

    /// Who currently occupies `section` per the derived state, if anyone.
    /// Used only for violation diagnostics; the gate uses
    /// `section_available_to` directly.
    pub fn occupant_of(&self, section: SectionId) -> Option<TrainId> {
        self.derived_state()
            .section_occupancy
            .get(&section)
            .copied()
    }

    /// Register + emit a position report for a train that has just
    /// entered `section`. The head offset is placed at `consist.length_mm`
    /// (clamped to section length) so the tail lands at offset 0 in the
    /// same section and the derived footprint is exactly `{section}` —
    /// matching the OccupancyMap contract M5 replaces.
    pub fn register_and_enter(
        &mut self,
        train: &Train,
        section: SectionId,
        direction: Direction,
        network: &Network,
        t_s: u32,
    ) {
        let section_len_mm = network.section(section).length_mm as i64;
        let head_offset = i64::from(train.consist.length_mm).min(section_len_mm);
        let head = TrackRef {
            section,
            offset_mm: head_offset,
            direction,
        };
        self.ensure_registered(train, head, t_s);
        self.emit_position(train, head, Some(0), t_s);
    }
}

impl DirectMaBackend {
    fn apply(&mut self, entry: Entry) {
        self.derived.apply(&entry);
        self.last_entry = Some(entry);
    }

    fn next_id(&mut self) -> EntryId {
        let id = EntryId::new(self.next_entry_id);
        self.next_entry_id += 1;
        id
    }

    fn ensure_registered(&mut self, train: &Train, initial_head: TrackRef, t_s: u32) {
        if self.registered.insert(train.id) {
            let entry = Entry {
                entry_id: self.next_id(),
                term: 1,
                timestamp_ns: sim_timestamp_ns(t_s),
                payload: EntryPayload::TrainRegistration(TrainRegistration {
                    train_id: train.id,
                    consist: train.consist.clone(),
                    initial_position: Position::certain(initial_head),
                }),
            };
            self.apply(entry);
        }
    }

    fn emit_position(
        &mut self,
        train: &Train,
        head: TrackRef,
        tail_offset_in_head_section: Option<i64>,
        t_s: u32,
    ) {
        let tail_offset = tail_offset_in_head_section.unwrap_or_else(|| {
            head.offset_mm
                .saturating_sub(i64::from(train.consist.length_mm))
        });
        let tail = TrackRef {
            section: head.section,
            offset_mm: tail_offset.max(0),
            direction: head.direction,
        };
        let timestamp_ns = sim_timestamp_ns(t_s);
        let entry = Entry {
            entry_id: self.next_id(),
            term: 1,
            timestamp_ns,
            payload: EntryPayload::TrainPositionReport(TrainPositionReport {
                train_id: train.id,
                head_position: Position::certain(head),
                tail_position: Position::certain(tail),
                speed_mmps: 15_000,
                speed_uncertainty_mmps: 500,
                heading: head.direction,
                contributing_sources: vec![PositionSource::Gnss, PositionSource::Odometry],
                onboard_time_ns: timestamp_ns.saturating_sub(100),
                pack_soc_ppt: (train.soc.clamp(0.0, 1.0) * 1000.0) as u16,
            }),
        };
        self.apply(entry);
    }

    fn emit_platform_handoff(&mut self, train_id: TrainId, t_s: u32) {
        let timestamp_ns = sim_timestamp_ns(t_s);
        let entry = Entry {
            entry_id: self.next_id(),
            term: 1,
            timestamp_ns,
            payload: EntryPayload::TrainDeparture(TrainDeparture {
                train_id,
                handed_off_to: None,
                handoff_time_ns: timestamp_ns,
            }),
        };
        self.registered.remove(&train_id);
        self.apply(entry);
    }

    fn emit_intrusion(
        &mut self,
        section: SectionId,
        state: IntrusionState,
        issued_by: osr_core::EntityId,
        t_s: u32,
    ) {
        let timestamp_ns = sim_timestamp_ns(t_s);
        let entry = Entry {
            entry_id: self.next_id(),
            term: 1,
            timestamp_ns,
            payload: EntryPayload::SectionIntrusion(SectionIntrusion {
                section,
                state,
                issued_by,
                observed_at_ns: timestamp_ns,
            }),
        };
        self.apply(entry);
    }
}

fn sim_timestamp_ns(t_s: u32) -> u64 {
    u64::from(t_s).saturating_mul(1_000_000_000)
}

// --------------------------------------------------------------------------
// Configuration
// --------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct ScenarioConfig {
    pub name: String,
    pub network: Network,
    /// Per-line fleet configuration. One entry per line.
    pub fleets: Vec<LineFleet>,
    /// Shared reference consist used by every trainset in every line.
    pub consist: ConsistDescriptor,
    /// Buildable trainset systems contract exercised by the component shadow.
    pub trainset_systems: TrainsetSystemsConfig,
    /// Nominal net traction + auxiliary energy before climate uplift.
    pub energy_kwh_per_car_km: f32,
    /// Onboard roof PV package shared by the fleet.
    pub roof_pv: RoofPvConfig,
    pub climate: ClimateModel,
    /// Sim-clock start time in seconds since midnight. Used for status display
    /// and dispatch-gate timing.
    pub start_time_s_after_midnight: u32,
    /// Required clean/inspect/recharge time at a designated service depot.
    pub depot_service_seconds: u32,
    /// Deterministic service controller that widens non-peak headways when a
    /// departing train's usable battery margin is low.  Actual charging
    /// delivery (PV, storage, grid and outages) is therefore reflected in the
    /// offered service without allowing a dispatch below the protected
    /// reserve.
    pub energy_adaptive_service: EnergyAdaptiveServiceConfig,
    /// Depot terminals that perform the scheduled service. Other depot-tagged
    /// terminals remain available for stabling and low-C top-up.
    pub depot_service_stations: std::collections::BTreeSet<StationId>,
    /// Trackside energy sites (PV + storage + grid tie). A station without a
    /// configured site cannot deliver charging energy.
    pub energy_sites: Vec<EnergySiteConfig>,
    /// Declared fault events (dust, grid outages, charging pad outages).
    /// Optional.
    pub faults: Vec<Fault>,
}

/// Per-car physical quantities that bind the simulator to the buildable
/// rolling-stock model instead of an unversioned, aggregate train shape.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TrainsetSystemsConfig {
    pub mechanical_standard_revision: String,
    pub door_cassettes_per_car: u32,
    pub window_cassettes_per_car: u32,
    pub service_rails_per_car: u32,
    pub fastener_family_count: u32,
    pub connector_family_count: u32,
    pub main_light_modules_per_car: u32,
    pub emergency_light_modules_per_car: u32,
    pub door_threshold_light_modules_per_car: u32,
    pub lighting_power_w_per_car: f32,
    pub hvac_thermal_kw_per_car: f32,
}

impl Default for TrainsetSystemsConfig {
    fn default() -> Self {
        Self {
            mechanical_standard_revision: "A-DRAFT".to_string(),
            door_cassettes_per_car: 4,
            window_cassettes_per_car: 6,
            service_rails_per_car: 8,
            fastener_family_count: 4,
            connector_family_count: 2,
            main_light_modules_per_car: 22,
            emergency_light_modules_per_car: 4,
            door_threshold_light_modules_per_car: 4,
            lighting_power_w_per_car: 500.0,
            hvac_thermal_kw_per_car: 24.0,
        }
    }
}

#[derive(Clone, Debug)]
pub struct EnergyAdaptiveServiceConfig {
    pub enabled: bool,
    /// SoC at or above which the published headway is offered unchanged.
    pub normal_service_soc: f32,
    /// Largest permitted non-peak headway relative to the published value.
    pub maximum_headway_multiplier: f32,
    /// Published headways at or below this value are protected peak service.
    pub protected_peak_headway_s: u32,
}

impl Default for EnergyAdaptiveServiceConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            normal_service_soc: 0.40,
            maximum_headway_multiplier: 3.0,
            protected_peak_headway_s: 3 * 60,
        }
    }
}

#[derive(Clone, Debug)]
pub struct LineFleet {
    pub line_index: usize,
    /// Stations from which trains dispatch, paired with their initial heading.
    /// Trains are distributed round-robin across this list.
    pub dispatch_points: Vec<(StationId, Heading)>,
    pub trainset_count: u32,
    /// Time-of-day schedule. Headway varies by window per RFC 0003 §4.1.
    pub schedule: LineSchedule,
}

#[derive(Clone, Debug)]
pub struct ClimateModel {
    pub ambient_c: f32,
    pub peak_sun_hours: f32,
    pub hvac_uplift_frac: f32,
}

#[derive(Clone, Debug)]
pub struct RoofPvConfig {
    pub nameplate_kw: f32,
    pub usable_factor: f32,
    pub charges_while_moving: bool,
    pub charges_while_dwelled: bool,
    pub air_cleaner: RoofPvAirCleanerConfig,
}

#[derive(Clone, Debug)]
pub struct RoofPvAirCleanerConfig {
    pub enabled: bool,
    pub compressor_power_kw: f32,
    pub dust_loss_recovery_frac: f32,
}

impl Default for RoofPvConfig {
    fn default() -> Self {
        Self {
            nameplate_kw: 0.0,
            usable_factor: 1.0,
            charges_while_moving: true,
            charges_while_dwelled: true,
            air_cleaner: RoofPvAirCleanerConfig::default(),
        }
    }
}

impl Default for RoofPvAirCleanerConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            compressor_power_kw: 0.0,
            dust_loss_recovery_frac: 0.0,
        }
    }
}

#[derive(Clone, Debug)]
pub struct RuntimeConfig {
    pub duration_s: u32,
    pub time_step_s: u32,
    pub status_every_s: u32,
    /// Optional path to write per-train CSV snapshots. When set, the
    /// simulator opens the file and writes one row per train per
    /// `csv_every_s` seconds of sim time.
    pub csv_out: Option<std::path::PathBuf>,
    /// Interval between CSV rows, in sim seconds. Defaults to 60.
    pub csv_every_s: u32,
    /// Interval between consensus-backed MA consistency checks, in sim
    /// seconds. Zero retains the same movement-authority gates with bounded
    /// direct derived state, but disables Raft history/auditing. Defaults to
    /// 30.
    pub ma_check_every_s: u32,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            duration_s: 3600,
            time_step_s: 1,
            status_every_s: 60,
            csv_out: None,
            csv_every_s: 60,
            ma_check_every_s: 30,
        }
    }
}

// --------------------------------------------------------------------------
// Events and result
// --------------------------------------------------------------------------

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum EventKind {
    Dispatched,
    ArriveStation {
        soc: f32,
    },
    DepartStation,
    ChargingTick {
        power_kw: f32,
        energy_added_kwh: f32,
    },
    Turnaround,
    DepotServiceStart {
        duration_s: u32,
    },
    DepotServiceComplete,
    SocWarning {
        soc: f32,
    },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Event {
    pub sim_time_s: u32,
    pub train: TrainId,
    pub line: String,
    pub station: Option<StationId>,
    pub station_name: Option<String>,
    pub kind: EventKind,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct InvariantViolation {
    pub sim_time_s: u32,
    pub description: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct SimResult {
    pub scenario_name: String,
    pub sim_duration_s: u32,
    pub total_train_km: f64,
    pub total_energy_consumed_kwh: f64,
    pub total_energy_charged_kwh: f64,
    #[serde(default)]
    pub total_roof_pv_charged_kwh: f64,
    /// Train-seconds held at dispatch points during service hours (fleet
    /// oversized for the headway). High values mean off-peak overstaffing.
    pub in_service_held_s: u64,
    /// Train-seconds spent parked at dispatch points outside service hours
    /// (overnight idle). Expected to be roughly `(fleet_size × night_hours)`.
    pub out_of_service_held_s: u64,
    /// Departures whose non-peak headway was widened by the deterministic
    /// energy-adaptive service controller.
    #[serde(default)]
    pub energy_adaptive_dispatches: u64,
    /// Sum of seconds added to headways at those dispatches.
    #[serde(default)]
    pub energy_adaptive_headway_added_s: u64,
    /// Longest effective headway selected by the controller.
    #[serde(default)]
    pub maximum_effective_headway_s: u32,
    pub per_train_final_soc: Vec<(String, String, f32, f32)>, // (train_id, line, final_soc, min_soc)
    pub per_line_km: Vec<(String, f64)>,
    pub events: Vec<Event>,
    /// Event tallies retained even when a validation run omits the full event
    /// trace. This keeps acceptance evidence compact without weakening the
    /// service/depot/SoC checks that consume these counts.
    #[serde(default)]
    pub event_counts: std::collections::BTreeMap<String, u64>,
    pub invariant_violations: Vec<InvariantViolation>,
    /// Trackside energy system summary (empty if scenario has no sites).
    #[serde(default)]
    pub energy_sites: Vec<EnergySiteSummary>,
    #[serde(default)]
    pub total_pv_generated_kwh: f64,
    #[serde(default)]
    pub total_grid_imported_kwh: f64,
    #[serde(default)]
    pub total_grid_exported_kwh: f64,
    #[serde(default)]
    pub total_curtailed_kwh: f64,
    #[serde(default)]
    pub total_delivered_to_trains_kwh: f64,
    #[serde(default)]
    pub faults_fired: Vec<FaultSummary>,
    /// Summary of the osr-interlocking MA-computer integration
    /// (checks run, MAs computed, any consistency violations).
    #[serde(default = "default_ma_summary")]
    pub ma_check: MaCheckSummary,
    /// Summary of the onboard shadow stack (osr-odometry + osr-atp +
    /// osr-brake). Produced by [`crate::onboard`] per-tick per-train
    /// during Traveling phase. Integration evidence for the Phase 2a
    /// SBC crates per RFC 0005 §11.
    #[serde(default)]
    pub onboard: OnboardSummary,
    /// Every-tick integration evidence for door, auxiliary-power, HVAC,
    /// lighting and passenger-information controllers.
    #[serde(default)]
    pub vehicle_systems: VehicleSystemsSummary,
}

fn default_ma_summary() -> MaCheckSummary {
    MaCheckSummary::default()
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FaultSummary {
    pub name: String,
    pub started_at_sim_s: u32,
    pub duration_s: u32,
    pub description: String,
}

impl FaultSummary {
    fn from_log(entry: &FaultLogEntry) -> Self {
        Self {
            name: entry.name.clone(),
            started_at_sim_s: entry.started_at_sim_s,
            duration_s: entry.duration_s,
            description: entry.kind_description.clone(),
        }
    }
}

// --------------------------------------------------------------------------
// Engine
// --------------------------------------------------------------------------

const SOC_WARNING_THRESHOLD: f32 = 0.30;
/// RFC 0021 requires the traction pack to retain 20% SoC so a train can
/// reach a charging point without deep-cycling the pack.  A train may only
/// enter a section when it can cover that section's planning energy and
/// still arrive with this reserve intact.
const SOC_OPERATING_RESERVE: f32 = 0.20;
/// Depot stabling roads use low-C 150 kW chargers (RFC 0002 §7.3). Trains
/// released from a depot duty cycle are topped back to the normal 95% start
/// target before returning to the passenger platform.
const DEPOT_CHARGE_POWER_KW: f32 = 150.0;
const DEPOT_TOP_UP_SOC: f32 = 0.95;

/// Compute section travel time from rest-to-rest using a simple trapezoidal
/// velocity profile: accelerate at `a`, cruise at `v_max`, decelerate at `d`.
/// Falls back to a triangular profile when the section is too short to
/// reach `v_max`. All units in SI (m, m/s, m/s²).
pub fn kinematic_travel_time(length_m: f32, v_max: f32, a: f32, d: f32) -> f32 {
    kinematic_profile(length_m, v_max, a, d).total_s
}

pub fn run(config: &ScenarioConfig, runtime: &RuntimeConfig) -> SimResult {
    run_with_event_recording(config, runtime, true)
}

/// Run the simulator with optional retention of the detailed event trace.
///
/// City acceptance runs only need aggregate event counts. Disabling detailed
/// retention avoids serialising and parsing very large daily event logs while
/// preserving the same simulation and safety calculations.
pub fn run_with_event_recording(
    config: &ScenarioConfig,
    runtime: &RuntimeConfig,
    record_events: bool,
) -> SimResult {
    use std::io::Write;

    let mut trains = init_fleet(config);
    let mut throttle = DispatchThrottle::new();
    let mut energy = EnergySystem::new(config.energy_sites.clone(), config.climate.peak_sun_hours);
    let mut faults = FaultEngine::new(config.faults.clone());

    // MA-computer integration (RFC 0004 §M5 + RFC 0001). The sim
    // maintains a log of Entry objects as trains move; every
    // `ma_check_every_s` sim seconds we compute each train's MA and
    // verify consistency through the real three-node Raft cluster.
    let ma_check_interval = runtime.ma_check_every_s;
    let mut ma_log = MaLogBackend::new(ma_check_interval > 0);
    let wayside_identity = osr_core::EntityId::new(0xBEEF);
    for section in config.network.sections.keys().copied() {
        ma_log.emit_intrusion(
            section,
            osr_interlocking::IntrusionState::Clear,
            wayside_identity,
            0,
        );
    }
    let mut ma_summary = default_ma_summary();
    let mut next_ma_check = if ma_check_interval > 0 { 0 } else { u32::MAX };

    // Onboard shadow stack: one shadow per train, built from
    // each train's consist. The shadow runs every tick during
    // Traveling phase; see crate::onboard.
    let mut onboard_shadows: Vec<OnboardShadow> = trains.iter().map(OnboardShadow::new).collect();
    let mut vehicle_system_shadows: Vec<VehicleSystemsShadow> = trains
        .iter()
        .map(|train| {
            VehicleSystemsShadow::new(train, &config.trainset_systems, config.climate.ambient_c)
        })
        .collect();

    // Optional CSV trace.
    let mut csv_writer: Option<std::io::BufWriter<std::fs::File>> = None;
    if let Some(path) = &runtime.csv_out {
        match std::fs::File::create(path) {
            Ok(f) => {
                let mut w = std::io::BufWriter::new(f);
                let _ = writeln!(
                    w,
                    "sim_time_s,clock_tod_hms,train_id,line,phase,station,soc,odometer_km,energy_consumed_kwh,energy_charged_kwh,roof_pv_charged_kwh,section_id,section_position_m,section_speed_mps,section_accel_mps2,motion_phase,battery_draw_power_kw,mechanical_traction_power_kw,mechanical_brake_power_kw,roof_pv_kw,roof_pv_cleaner_power_kw,station_charge_power_kw"
                );
                csv_writer = Some(w);
            }
            Err(e) => {
                eprintln!(
                    "warning: could not open CSV {}: {}; continuing without CSV",
                    path.display(),
                    e
                );
            }
        }
    }
    let csv_every = runtime.csv_every_s.max(1);
    let mut next_csv = if csv_writer.is_some() { 0 } else { u32::MAX };
    let mut events = EventLog::new(record_events);
    let mut violations: Vec<InvariantViolation> = Vec::new();

    // Register throttle points from each line's dispatch configuration.
    for fleet in &config.fleets {
        let initial_next_allowed =
            seconds_until_next_service(&fleet.schedule, config.start_time_s_after_midnight);
        for (station, heading) in &fleet.dispatch_points {
            throttle.register((fleet.line_index, *station, *heading), initial_next_allowed);
        }
    }

    let dt = runtime.time_step_s as f32;
    let status_every = runtime.status_every_s;

    print_header(config, runtime, &trains);

    let mut t: u32 = 0;
    let mut next_status = if status_every > 0 {
        status_every
    } else {
        u32::MAX
    };

    while t < runtime.duration_s {
        let clock_absolute = t + config.start_time_s_after_midnight;
        let clock_tod = clock_absolute % 86400;

        // Update fault state for this tick.
        faults.tick(t);

        // Emit wayside intrusion entries driven by any active
        // `WaysideIntrusion` fault (RFC 0016 v3). The sim re-asserts
        // the latest state each tick so that a fault clearing
        // produces a matching `Clear` entry on the following tick.
        //
        // `issued_by` is a fixed sim-wayside identity; real
        // deployments would use the W-SBC entity id per section.
        for (section, state) in faults.active_wayside_intrusions() {
            ma_log.emit_intrusion(section, state, wayside_identity, t);
        }

        // PV generation, battery storage, grid export/curtail (time-of-day).
        energy.tick_pv(clock_tod, dt, &faults);

        for idx in 0..trains.len() {
            step_train(
                idx,
                &mut trains,
                &config.network,
                &config.climate,
                &config.roof_pv,
                &config.fleets,
                config.depot_service_seconds,
                &config.depot_service_stations,
                &config.energy_adaptive_service,
                clock_tod,
                &mut ma_log,
                &mut throttle,
                &mut energy,
                &faults,
                dt,
                t,
                &mut events,
                &mut violations,
            );

            // Shadow onboard stack: only during Traveling phase. If
            // the train just left Traveling (arrived at a station
            // or transitioned elsewhere), reset the shadow so the
            // next section entry re-seeds cleanly.
            match trains[idx].phase {
                TrainPhase::Traveling { .. } => {
                    let _ = onboard::onboard_tick(
                        &mut onboard_shadows[idx],
                        &trains[idx],
                        &config.network,
                        &faults,
                        t,
                        dt,
                    );
                }
                _ => onboard_shadows[idx].on_leave_section(),
            }

            vehicle_systems::vehicle_systems_tick(
                &mut vehicle_system_shadows[idx],
                &trains[idx],
                &config.network,
                &config.trainset_systems,
                config.climate.ambient_c,
                t,
                dt,
            );
        }

        if status_every > 0 && t >= next_status {
            print_status_line(
                t,
                &trains,
                &config.network,
                config.start_time_s_after_midnight,
            );
            next_status = t.saturating_add(status_every);
        }

        if let Some(w) = csv_writer.as_mut() {
            if t >= next_csv {
                write_csv_snapshot(
                    w,
                    t,
                    clock_tod,
                    &trains,
                    &config.network,
                    &config.climate,
                    &config.roof_pv,
                    &faults,
                );
                next_csv = t.saturating_add(csv_every);
            }
        }

        // Advance the consensus backend.
        ma_log.tick(u64::from(runtime.time_step_s).saturating_mul(1_000_000_000));

        if ma_check_interval > 0 && t >= next_ma_check {
            let derived_from = ma_log.entries().last().map(|e| e.entry_id);
            ma_check::run_check_state(
                &trains,
                ma_log.derived_state(),
                &config.network,
                derived_from,
                t,
                &mut ma_summary,
            );
            next_ma_check = t.saturating_add(ma_check_interval);
        }

        t = t.saturating_add(runtime.time_step_s);
    }

    if let Some(mut w) = csv_writer.take() {
        let _ = std::io::Write::flush(&mut w);
        if let Some(path) = &runtime.csv_out {
            println!("CSV trace written to {}", path.display());
        }
    }

    if status_every > 0 {
        print_status_line(
            runtime.duration_s,
            &trains,
            &config.network,
            config.start_time_s_after_midnight,
        );
    }

    // Aggregate per-line km.
    let mut per_line_km: Vec<(String, f64)> = config
        .network
        .lines
        .iter()
        .map(|l| (l.name.clone(), 0.0))
        .collect();
    for tr in &trains {
        per_line_km[tr.line_index].1 += tr.odometer_km;
    }

    // Onboard shadow summary.
    let onboard_summary = onboard::summarise(&onboard_shadows, &trains);
    let vehicle_systems_summary = vehicle_systems::summarise(
        &vehicle_system_shadows,
        &config.trainset_systems,
        config.consist.car_count,
    );

    // Build per-site summaries.
    let energy_sites: Vec<EnergySiteSummary> = energy
        .sites
        .values()
        .map(|site| {
            let name = config.network.station(site.config.station).name.clone();
            site.summary(name)
        })
        .collect();

    SimResult {
        scenario_name: config.name.clone(),
        sim_duration_s: runtime.duration_s,
        total_train_km: trains.iter().map(|t| t.odometer_km).sum(),
        total_energy_consumed_kwh: trains.iter().map(|t| t.energy_consumed_kwh).sum(),
        total_energy_charged_kwh: trains.iter().map(|t| t.energy_charged_kwh).sum(),
        total_roof_pv_charged_kwh: trains.iter().map(|t| t.energy_roof_pv_kwh).sum(),
        in_service_held_s: throttle.in_service_held_s,
        out_of_service_held_s: throttle.out_of_service_held_s,
        energy_adaptive_dispatches: throttle.energy_adaptive_dispatches,
        energy_adaptive_headway_added_s: throttle.energy_adaptive_headway_added_s,
        maximum_effective_headway_s: throttle.maximum_effective_headway_s,
        per_train_final_soc: trains
            .iter()
            .map(|t| {
                let line_name = config.network.lines[t.line_index].name.clone();
                (t.id.to_string(), line_name, t.soc, t.min_soc_seen)
            })
            .collect(),
        per_line_km,
        events: events.events,
        event_counts: events.counts,
        invariant_violations: violations,
        total_pv_generated_kwh: energy.total_pv_generated_kwh(),
        total_grid_imported_kwh: energy.total_grid_imported_kwh(),
        total_grid_exported_kwh: energy.total_grid_exported_kwh(),
        total_curtailed_kwh: energy.total_curtailed_kwh(),
        total_delivered_to_trains_kwh: energy.total_delivered_to_trains_kwh(),
        energy_sites,
        faults_fired: faults
            .fault_log
            .iter()
            .map(FaultSummary::from_log)
            .collect(),
        ma_check: ma_summary,
        onboard: onboard_summary,
        vehicle_systems: vehicle_systems_summary,
    }
}

fn print_header(config: &ScenarioConfig, runtime: &RuntimeConfig, trains: &[Train]) {
    println!("OpenSourceRail sim — scenario \"{}\"", config.name);
    println!("Network:");
    for (i, line) in config.network.lines.iter().enumerate() {
        let line_km: f64 = line
            .forward_sections
            .iter()
            .map(|sid| config.network.section(*sid).length_km())
            .sum();
        let kind = if line.is_ring { "ring" } else { "linear" };
        let train_count = trains.iter().filter(|t| t.line_index == i).count();
        let fleet_opt = config.fleets.iter().find(|f| f.line_index == i);
        if let Some(fleet) = fleet_opt {
            println!(
                "  {} ({}, {:.1} km, {} stations, {} trainsets) — headways {} over {}–{}",
                line.name,
                kind,
                line_km,
                line.stations.len(),
                train_count,
                fleet.schedule.headway_summary(),
                fmt_time_of_day(fleet.schedule.service_start_s),
                fmt_time_of_day(fleet.schedule.service_end_s),
            );
        } else {
            println!(
                "  {} ({}, {:.1} km, {} stations, no fleet assigned)",
                line.name,
                kind,
                line_km,
                line.stations.len(),
            );
        }
    }
    println!(
        "Climate: ambient {:.0}°C, PSH {:.1} h, HVAC uplift {:+.0}%",
        config.climate.ambient_c,
        config.climate.peak_sun_hours,
        config.climate.hvac_uplift_frac * 100.0
    );
    println!(
        "Rolling stock: {}-car consist, {} kWh per trainset",
        trains[0].consist.car_count,
        trains[0].consist.battery_capacity_wh / 1000
    );
    println!(
        "Nominal energy: {:.1} kWh/car-km before climate uplift",
        config.energy_kwh_per_car_km
    );
    if config.roof_pv.nameplate_kw > 0.0 {
        println!(
            "Roof PV: {:.1} kW nameplate × {:.0}% usable",
            config.roof_pv.nameplate_kw,
            config.roof_pv.usable_factor * 100.0
        );
        if config.roof_pv.air_cleaner.enabled {
            println!(
                "Roof PV cleaner: {:.1} kW air pump, recovers {:.0}% of dust loss",
                config.roof_pv.air_cleaner.compressor_power_kw,
                config.roof_pv.air_cleaner.dust_loss_recovery_frac * 100.0
            );
        }
    }
    println!(
        "Running {} s ({}) at {}s step, start {}…\n",
        runtime.duration_s,
        fmt_duration(runtime.duration_s),
        runtime.time_step_s,
        fmt_time_of_day(config.start_time_s_after_midnight)
    );
}

fn init_fleet(config: &ScenarioConfig) -> Vec<Train> {
    let mut trains = Vec::new();
    let mut next_train_num: u64 = 1;

    for fleet in &config.fleets {
        assert!(
            !fleet.dispatch_points.is_empty(),
            "fleet for line {} has no dispatch points",
            fleet.line_index
        );
        for i in 0..fleet.trainset_count {
            let dp_idx = (i as usize) % fleet.dispatch_points.len();
            let (start_station, heading) = fleet.dispatch_points[dp_idx];

            trains.push(Train {
                id: TrainId::new(next_train_num),
                line_index: fleet.line_index,
                consist: config.consist.clone(),
                energy_kwh_per_car_km: config.energy_kwh_per_car_km,
                heading,
                phase: TrainPhase::AwaitingDispatch {
                    station: start_station,
                },
                soc: 0.95,
                odometer_km: 0.0,
                energy_consumed_kwh: 0.0,
                energy_charged_kwh: 0.0,
                energy_roof_pv_kwh: 0.0,
                min_soc_seen: 0.95,
            });
            next_train_num += 1;
        }
    }

    trains
}

fn fleet_for_line(fleets: &[LineFleet], line_index: usize) -> &LineFleet {
    fleets
        .iter()
        .find(|f| f.line_index == line_index)
        .unwrap_or_else(|| panic!("no fleet configured for line {line_index}"))
}

fn seconds_until_next_service(schedule: &LineSchedule, start_tod_s: u32) -> u32 {
    if schedule.headway_at(start_tod_s).is_some() {
        return 0;
    }
    for delta in 1..=86_400 {
        let tod = (start_tod_s + delta) % 86_400;
        if schedule.headway_at(tod).is_some() {
            return delta;
        }
    }
    u32::MAX
}

#[allow(clippy::too_many_arguments)]
fn step_train(
    idx: usize,
    trains: &mut [Train],
    network: &Network,
    climate: &ClimateModel,
    roof_pv: &RoofPvConfig,
    fleets: &[LineFleet],
    depot_service_seconds: u32,
    depot_service_stations: &std::collections::BTreeSet<StationId>,
    adaptive_service: &EnergyAdaptiveServiceConfig,
    clock_tod: u32,
    ma_log: &mut MaLogBackend,
    throttle: &mut DispatchThrottle,
    energy: &mut EnergySystem,
    faults: &FaultEngine,
    dt: f32,
    t: u32,
    events: &mut EventLog,
    violations: &mut Vec<InvariantViolation>,
) {
    let phase = trains[idx].phase.clone();
    let clock = clock_tod;
    apply_roof_pv_tick(
        &mut trains[idx],
        &phase,
        climate,
        roof_pv,
        faults,
        clock,
        dt,
    );

    match phase {
        TrainPhase::AwaitingDispatch { station } => {
            // A train waiting in a depot stabling road remains connected to
            // its low-C charger. This matters for spare sets rotated into
            // service later in the day and for overnight recovery runs.
            if network.station(station).is_depot
                && !faults.pad_disabled_at(station)
                && trains[idx].soc < DEPOT_TOP_UP_SOC
            {
                let requested = (DEPOT_CHARGE_POWER_KW / 3600.0) * dt;
                let delivered = energy.draw_at_station(station, requested, dt, faults);
                let applied = trains[idx].apply_energy_kwh(delivered);
                trains[idx].energy_charged_kwh += f64::from(applied);
            }
            let line_idx = trains[idx].line_index;
            let heading = trains[idx].heading;
            let key = (line_idx, station, heading);
            let fleet = fleet_for_line(fleets, line_idx);

            match fleet.schedule.headway_at(clock) {
                Some(hw)
                    if throttle.can_dispatch(&key, t)
                        && entry_candidate(idx, trains, network, climate, heading, ma_log)
                            .is_some() =>
                {
                    let effective_hw =
                        energy_adjusted_headway_s(hw, trains[idx].soc, adaptive_service, clock);
                    throttle.mark_dispatched(&key, t, hw, effective_hw);
                    let mut entry = SectionEntryContext {
                        network,
                        climate,
                        t,
                        ma_log,
                        violations,
                    };
                    enter_first_section(idx, trains, events, &mut entry);
                }
                Some(_) => throttle.record_in_service_held(dt),
                None => throttle.record_out_of_service_held(dt),
            }
        }
        TrainPhase::Dwelling {
            station,
            mut remaining_s,
            mut depot_service_remaining_s,
            mut energy_added_kwh,
        } => {
            let depot_service_was_active = depot_service_remaining_s > 0.0;
            let s = network.station(station);
            let pad_up = !faults.pad_disabled_at(station);
            if pad_up && s.charging_power_kw > 0 && trains[idx].soc < 1.0 {
                // Once normal platform dwell has elapsed at a depot, the
                // train transfers to a stabling charger for its top-up.
                let depot_top_up = s.is_depot && remaining_s <= 0.0;
                let charging_power_kw = if depot_top_up {
                    DEPOT_CHARGE_POWER_KW
                } else {
                    s.charging_power_kw as f32
                };
                let pad_rate_kwh = (charging_power_kw / 3600.0) * dt;
                let target_soc = if depot_top_up { DEPOT_TOP_UP_SOC } else { 1.0 };
                let headroom_kwh =
                    (target_soc - trains[idx].soc).max(0.0) * trains[idx].battery_capacity_kwh();
                let requested = pad_rate_kwh.min(headroom_kwh);
                if requested > 0.0 {
                    let delivered = energy.draw_at_station(station, requested, dt, faults);
                    let applied = trains[idx].apply_energy_kwh(delivered);
                    trains[idx].energy_charged_kwh += f64::from(applied);
                    energy_added_kwh += applied;
                }
            }
            remaining_s -= dt;
            depot_service_remaining_s = (depot_service_remaining_s - dt).max(0.0);
            if depot_service_was_active && depot_service_remaining_s <= 0.0 {
                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: network.lines[trains[idx].line_index].name.clone(),
                        station: Some(station),
                        station_name: Some(s.name.clone()),
                        kind: EventKind::DepotServiceComplete,
                    },
                );
            }

            if remaining_s > 0.0 || depot_service_remaining_s > 0.0 {
                trains[idx].phase = TrainPhase::Dwelling {
                    station,
                    remaining_s,
                    depot_service_remaining_s,
                    energy_added_kwh,
                };
                return;
            }

            // Dwell expired. Check if this station + departure heading is a
            // throttle point; if so, honor the schedule.
            let line_idx = trains[idx].line_index;
            let line = &network.lines[line_idx];
            let terminal_flip = s.is_terminal && !line.is_ring;
            let departure_heading = if terminal_flip {
                trains[idx].heading.flip()
            } else {
                trains[idx].heading
            };
            let key = (line_idx, station, departure_heading);

            // Do not consume a timetable slot or emit departure/turnaround
            // events until both the energy-reserve gate and the movement-
            // authority gate admit the next section.  A held train keeps
            // charging and retries on the next tick.
            if entry_candidate(idx, trains, network, climate, departure_heading, ma_log).is_none() {
                trains[idx].phase = TrainPhase::Dwelling {
                    station,
                    remaining_s: if s.is_depot { 0.0 } else { dt },
                    depot_service_remaining_s,
                    energy_added_kwh,
                };
                return;
            }

            if throttle.is_throttle_point(&key) {
                let fleet = fleet_for_line(fleets, line_idx);
                let in_service = fleet.schedule.headway_at(clock);
                match in_service {
                    Some(hw) if throttle.can_dispatch(&key, t) => {
                        let effective_hw =
                            energy_adjusted_headway_s(hw, trains[idx].soc, adaptive_service, clock);
                        throttle.mark_dispatched(&key, t, hw, effective_hw);
                        // Fall through to departure logic below.
                    }
                    _ => {
                        trains[idx].phase = TrainPhase::Dwelling {
                            station,
                            remaining_s: if s.is_depot { 0.0 } else { dt },
                            depot_service_remaining_s,
                            energy_added_kwh,
                        };
                        if in_service.is_some() {
                            throttle.record_in_service_held(dt);
                        } else {
                            throttle.record_out_of_service_held(dt);
                        }
                        return;
                    }
                }
            }

            // Proceed with departure.
            if terminal_flip {
                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: line.name.clone(),
                        station: Some(station),
                        station_name: Some(s.name.clone()),
                        kind: EventKind::Turnaround,
                    },
                );
            }
            if energy_added_kwh > 0.1 {
                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: line.name.clone(),
                        station: Some(station),
                        station_name: Some(s.name.clone()),
                        kind: EventKind::ChargingTick {
                            power_kw: s.charging_power_kw as f32,
                            energy_added_kwh,
                        },
                    },
                );
            }
            emit_event(
                events,
                Event {
                    sim_time_s: t,
                    train: trains[idx].id,
                    line: line.name.clone(),
                    station: Some(station),
                    station_name: Some(s.name.clone()),
                    kind: EventKind::DepartStation,
                },
            );
            let mut entry = SectionEntryContext {
                network,
                climate,
                t,
                ma_log,
                violations,
            };
            enter_next_section(idx, trains, departure_heading, &mut entry);
        }
        TrainPhase::Traveling {
            section,
            from_station,
            to_station,
            total_travel_s,
            mut remaining_s,
        } => {
            let previous_remaining_s = remaining_s;
            remaining_s = (remaining_s - dt).max(0.0);

            let sec = network.section(section);
            let consist = trains[idx].consist.clone();
            let elapsed_start = (total_travel_s - previous_remaining_s).max(0.0);
            let elapsed_end = (total_travel_s - remaining_s).max(elapsed_start);
            let start_sample = motion_sample_for_section(&consist, sec, elapsed_start);
            let end_sample = motion_sample_for_section(&consist, sec, elapsed_end);
            let delta_m = (end_sample.position_m - start_sample.position_m).max(0.0);
            if delta_m > 0.0 {
                let delta_km = f64::from(delta_m) / 1000.0;
                let kwh_per_km = trains[idx].kwh_per_km(climate.hvac_uplift_frac);
                let consumed = kwh_per_km * (delta_m / 1000.0);
                let applied = -trains[idx].apply_energy_kwh(-consumed);
                trains[idx].energy_consumed_kwh += f64::from(applied);
                trains[idx].odometer_km += delta_km;
            }

            if remaining_s <= 0.0 {
                // The full consist is now berthed clear of the interstation
                // block. Hand it to the station/platform domain so the MA
                // computer releases the inbound section. Retaining that
                // section while dwelling eventually fills every block and
                // deadlocks an otherwise healthy line.
                ma_log.emit_platform_handoff(trains[idx].id, t);

                let line = &network.lines[trains[idx].line_index];

                if trains[idx].soc < SOC_WARNING_THRESHOLD {
                    emit_event(
                        events,
                        Event {
                            sim_time_s: t,
                            train: trains[idx].id,
                            line: line.name.clone(),
                            station: Some(to_station),
                            station_name: Some(network.station(to_station).name.clone()),
                            kind: EventKind::SocWarning {
                                soc: trains[idx].soc,
                            },
                        },
                    );
                }

                emit_event(
                    events,
                    Event {
                        sim_time_s: t,
                        train: trains[idx].id,
                        line: line.name.clone(),
                        station: Some(to_station),
                        station_name: Some(network.station(to_station).name.clone()),
                        kind: EventKind::ArriveStation {
                            soc: trains[idx].soc,
                        },
                    },
                );

                let dst = network.station(to_station);
                let performs_depot_service = depot_service_stations.contains(&to_station)
                    && depot_service_fits_off_peak_window(
                        &fleets[trains[idx].line_index].schedule,
                        clock_tod,
                        depot_service_seconds,
                    );
                if performs_depot_service && depot_service_seconds > 0 {
                    emit_event(
                        events,
                        Event {
                            sim_time_s: t,
                            train: trains[idx].id,
                            line: line.name.clone(),
                            station: Some(to_station),
                            station_name: Some(dst.name.clone()),
                            kind: EventKind::DepotServiceStart {
                                duration_s: depot_service_seconds,
                            },
                        },
                    );
                }
                trains[idx].phase = TrainPhase::Dwelling {
                    station: to_station,
                    remaining_s: dst.dwell_seconds as f32,
                    depot_service_remaining_s: if performs_depot_service {
                        depot_service_seconds as f32
                    } else {
                        0.0
                    },
                    energy_added_kwh: 0.0,
                };

                let _ = (from_station, total_travel_s);
            } else {
                trains[idx].phase = TrainPhase::Traveling {
                    section,
                    from_station,
                    to_station,
                    total_travel_s,
                    remaining_s,
                };
            }
        }
    }
}

struct SectionEntryContext<'a> {
    network: &'a Network,
    climate: &'a ClimateModel,
    t: u32,
    ma_log: &'a mut MaLogBackend,
    violations: &'a mut Vec<InvariantViolation>,
}

fn enter_first_section(
    idx: usize,
    trains: &mut [Train],
    events: &mut EventLog,
    context: &mut SectionEntryContext<'_>,
) {
    let station = match trains[idx].phase {
        TrainPhase::AwaitingDispatch { station, .. } => station,
        _ => return,
    };
    let line_name = context.network.lines[trains[idx].line_index].name.clone();
    emit_event(
        events,
        Event {
            sim_time_s: context.t,
            train: trains[idx].id,
            line: line_name,
            station: Some(station),
            station_name: Some(context.network.station(station).name.clone()),
            kind: EventKind::Dispatched,
        },
    );
    let heading = trains[idx].heading;
    enter_next_section(idx, trains, heading, context);
}

fn enter_next_section(
    idx: usize,
    trains: &mut [Train],
    departure_heading: Heading,
    context: &mut SectionEntryContext<'_>,
) {
    let (to_station, section_id) = entry_candidate(
        idx,
        trains,
        context.network,
        context.climate,
        departure_heading,
        context.ma_log,
    )
    .expect("entry gates were checked immediately before section entry");
    let from_station = current_station(&trains[idx]);
    trains[idx].heading = departure_heading;

    // Authorised — emit a position report placing the train in the
    // new section. This is what a committed `TrainPositionReport`
    // would look like if published by `osr-odometry` + consensus on
    // real hardware.
    let direction = direction_for_heading(trains[idx].heading);
    context.ma_log.register_and_enter(
        &trains[idx],
        section_id,
        direction,
        context.network,
        context.t,
    );

    // Safety net: the derived state must now record this train as the
    // sole occupant of `section_id`. If something else is there, the
    // gate check above was unsound — surface it as an invariant bug
    // rather than charging ahead silently.
    if let Some(holder) = context.ma_log.occupant_of(section_id) {
        if holder != trains[idx].id {
            context.violations.push(InvariantViolation {
                sim_time_s: context.t,
                description: format!(
                    "MA-derived occupancy conflict: train {} entered {} while derived state holds {}",
                    trains[idx].id, section_id, holder
                ),
            });
        }
    }

    let sec = context.network.section(section_id);
    let length_m = sec.length_mm as f32 / 1_000.0;
    let consist = &trains[idx].consist;
    let v_max = sec.max_speed_mps.min(consist.max_speed_mps);
    let a = consist.service_accel_mps2;
    let d = consist.service_decel_mps2();
    let travel_s = kinematic_travel_time(length_m, v_max, a, d)
        + consist.braking.reaction_time_ms as f32 / 1000.0;

    trains[idx].phase = TrainPhase::Traveling {
        section: section_id,
        from_station,
        to_station,
        total_travel_s: travel_s,
        remaining_s: travel_s,
    };
}

/// Resolve the next section and apply the two pre-entry gates without
/// mutating train, timetable, or event state.  Keeping this check pure lets a
/// different ready train use the dispatch slot when this one is held.
fn entry_candidate(
    idx: usize,
    trains: &[Train],
    network: &Network,
    climate: &ClimateModel,
    departure_heading: Heading,
    ma_log: &MaLogBackend,
) -> Option<(StationId, SectionId)> {
    let train = &trains[idx];
    let line = &network.lines[train.line_index];
    let current = current_station(train);
    let (to_station, section_id) = next_station_for_heading(line, current, departure_heading)?;

    let section = network.section(section_id);
    let section_km = section.length_mm as f32 / 1_000_000.0;
    let required_kwh = train.kwh_per_km(climate.hvac_uplift_frac) * section_km;
    let reserve_kwh = train.battery_capacity_kwh() * SOC_OPERATING_RESERVE;
    let stored_kwh = train.soc * train.battery_capacity_kwh();
    if stored_kwh + f32::EPSILON < required_kwh + reserve_kwh {
        return None;
    }

    // `section_available_to` folds together occupancy, route grants, and
    // maintenance overrides, matching the onboard MA predicate.
    ma_log
        .section_available_to(train.id, section_id)
        .then_some((to_station, section_id))
}

fn direction_for_heading(h: Heading) -> Direction {
    match h {
        Heading::Forward => Direction::Forward,
        Heading::Reverse => Direction::Reverse,
    }
}

fn current_station(train: &Train) -> StationId {
    match &train.phase {
        TrainPhase::Dwelling { station, .. } | TrainPhase::AwaitingDispatch { station, .. } => {
            *station
        }
        TrainPhase::Traveling { to_station, .. } => *to_station,
    }
}

/// Peak-priority depot policy: trains use the normal terminal dwell whenever
/// the active headway is three minutes or tighter. The 12-minute clean,
/// release inspection, diagnostics, and low-C top-up is inserted only after
/// the timetable relaxes, when the peak-sized fleet supplies idle cover.
fn depot_service_fits_off_peak_window(
    schedule: &LineSchedule,
    clock_tod: u32,
    depot_service_seconds: u32,
) -> bool {
    depot_service_seconds > 0
        && schedule
            .headway_at(clock_tod)
            .is_some_and(|headway_s| headway_s > 3 * 60 && !is_protected_peak_window(clock_tod))
}

fn is_protected_peak_window(clock_tod: u32) -> bool {
    let clock = clock_tod % 86_400;
    (7 * 3_600..9 * 3_600).contains(&clock) || (15 * 3_600..17 * 3_600).contains(&clock)
}

/// Convert real charging availability into an offered-service headway.
///
/// SoC is the controller's deliberately simple energy-balance signal: it
/// already incorporates traction use and the energy actually delivered by
/// station PV, storage and grid import. Above `normal_service_soc` the
/// published headway is retained. Between that target and the protected 20%
/// reserve, non-peak headways are widened linearly up to the configured cap
/// and rounded up to a whole minute. Peak headways remain protected; the
/// existing section-entry reserve gate still has final safety authority.
fn energy_adjusted_headway_s(
    published_headway_s: u32,
    train_soc: f32,
    config: &EnergyAdaptiveServiceConfig,
    clock_tod: u32,
) -> u32 {
    if !config.enabled
        || is_protected_peak_window(clock_tod)
        || published_headway_s <= config.protected_peak_headway_s
    {
        return published_headway_s;
    }
    let target = config
        .normal_service_soc
        .clamp(SOC_OPERATING_RESERVE + 0.01, 1.0);
    if train_soc >= target {
        return published_headway_s;
    }
    let shortage = ((target - train_soc) / (target - SOC_OPERATING_RESERVE)).clamp(0.0, 1.0);
    let maximum = config.maximum_headway_multiplier.max(1.0);
    let multiplier = 1.0 + shortage * (maximum - 1.0);
    let adjusted = (published_headway_s as f32 * multiplier).ceil() as u32;
    adjusted.div_ceil(60) * 60
}

fn next_station_for_heading(
    line: &Line,
    current: StationId,
    heading: Heading,
) -> Option<(StationId, SectionId)> {
    let idx = line.stations.iter().position(|s| *s == current)?;
    let n = line.stations.len();
    match heading {
        Heading::Forward => {
            let next_idx = idx + 1;
            if next_idx >= n {
                if line.is_ring {
                    // Wrap: stations[N-1] -> stations[0] uses forward_sections[N-1].
                    Some((line.stations[0], line.forward_sections[n - 1]))
                } else {
                    None
                }
            } else {
                Some((line.stations[next_idx], line.forward_sections[idx]))
            }
        }
        Heading::Reverse => {
            if idx == 0 {
                if line.is_ring {
                    // Wrap: stations[0] -> stations[N-1] uses reverse_sections[N-1].
                    Some((line.stations[n - 1], line.reverse_sections[n - 1]))
                } else {
                    None
                }
            } else {
                Some((line.stations[idx - 1], line.reverse_sections[idx - 1]))
            }
        }
    }
}

#[derive(Debug)]
struct EventLog {
    events: Vec<Event>,
    counts: std::collections::BTreeMap<String, u64>,
    record_events: bool,
}

impl EventLog {
    fn new(record_events: bool) -> Self {
        Self {
            events: Vec::new(),
            counts: std::collections::BTreeMap::new(),
            record_events,
        }
    }
}

fn event_kind_name(kind: &EventKind) -> &'static str {
    match kind {
        EventKind::Dispatched => "Dispatched",
        EventKind::ArriveStation { .. } => "ArriveStation",
        EventKind::DepartStation => "DepartStation",
        EventKind::ChargingTick { .. } => "ChargingTick",
        EventKind::Turnaround => "Turnaround",
        EventKind::DepotServiceStart { .. } => "DepotServiceStart",
        EventKind::DepotServiceComplete => "DepotServiceComplete",
        EventKind::SocWarning { .. } => "SocWarning",
    }
}

fn emit_event(buf: &mut EventLog, ev: Event) {
    *buf.counts
        .entry(event_kind_name(&ev.kind).to_owned())
        .or_insert(0) += 1;
    if buf.record_events {
        buf.events.push(ev);
    }
}

fn apply_roof_pv_tick(
    train: &mut Train,
    phase: &TrainPhase,
    climate: &ClimateModel,
    roof_pv: &RoofPvConfig,
    faults: &FaultEngine,
    clock_tod: u32,
    dt: f32,
) {
    let eligible = match phase {
        TrainPhase::Traveling { .. } => roof_pv.charges_while_moving,
        TrainPhase::Dwelling { .. } | TrainPhase::AwaitingDispatch { .. } => {
            roof_pv.charges_while_dwelled
        }
    };
    if !eligible {
        return;
    }
    let power = roof_pv_power_breakdown(roof_pv, climate, faults, clock_tod);
    if power.net_kw <= 0.0 {
        return;
    }
    let generated_kwh = power.net_kw * dt / 3600.0;
    let applied = train.apply_energy_kwh(generated_kwh);
    if applied > 0.0 {
        train.energy_charged_kwh += f64::from(applied);
        train.energy_roof_pv_kwh += f64::from(applied);
    }
}

#[derive(Clone, Copy, Debug, Default)]
struct RoofPvPowerBreakdown {
    net_kw: f32,
    cleaner_power_kw: f32,
}

fn roof_pv_power_breakdown(
    roof_pv: &RoofPvConfig,
    climate: &ClimateModel,
    faults: &FaultEngine,
    clock_tod: u32,
) -> RoofPvPowerBreakdown {
    if roof_pv.nameplate_kw <= 0.0 {
        return RoofPvPowerBreakdown::default();
    }
    let base_kw = pv_output_kw(roof_pv.nameplate_kw, clock_tod, climate.peak_sun_hours)
        * roof_pv.usable_factor.clamp(0.0, 1.0);
    if base_kw <= 0.0 {
        return RoofPvPowerBreakdown::default();
    }

    let dust_factor = faults.global_pv_factor();
    let air = &roof_pv.air_cleaner;
    let effective_dust_factor = if air.enabled {
        dust_factor + (1.0 - dust_factor) * air.dust_loss_recovery_frac.clamp(0.0, 1.0)
    } else {
        dust_factor
    }
    .clamp(0.0, 1.0);

    let gross_kw = base_kw * effective_dust_factor;
    let cleaner_power_kw = if air.enabled {
        air.compressor_power_kw.max(0.0).min(gross_kw)
    } else {
        0.0
    };
    RoofPvPowerBreakdown {
        net_kw: (gross_kw - cleaner_power_kw).max(0.0),
        cleaner_power_kw,
    }
}

fn motion_sample_for_section(
    consist: &ConsistDescriptor,
    section: &Section,
    elapsed_s: f32,
) -> MotionSample {
    let length_m = section.length_mm as f32 / 1_000.0;
    let v_max = section.max_speed_mps.min(consist.max_speed_mps);
    sample_kinematic_profile(
        length_m,
        v_max,
        consist.service_accel_mps2,
        consist.service_decel_mps2(),
        elapsed_s,
        consist.mass_kg as f32,
    )
}

// --------------------------------------------------------------------------
// Display helpers
// --------------------------------------------------------------------------

fn print_status_line(t: u32, trains: &[Train], network: &Network, start_of_day_s: u32) {
    let clock = fmt_sim_clock(t, start_of_day_s);
    // Group by line so the status line stays readable as fleets grow.
    let mut by_line: Vec<Vec<String>> = vec![Vec::new(); network.lines.len()];
    for tr in trains {
        by_line[tr.line_index].push(format!(
            "{}={}·{:.2}",
            tr.id,
            abbrev_phase(tr, network),
            tr.soc
        ));
    }
    print!("[{clock}]");
    for (i, cells) in by_line.iter().enumerate() {
        if cells.is_empty() {
            continue;
        }
        let line_abbrev = short_line_name(&network.lines[i].name);
        print!("  {}:{}", line_abbrev, cells.join(" "));
    }
    println!();
}

fn short_line_name(name: &str) -> String {
    // "Line 1 Nahrain" → "L1". "Line 2 Halqa" → "L2".
    name.split_whitespace()
        .take(2)
        .map(|w| {
            if w.eq_ignore_ascii_case("line") {
                "L".to_string()
            } else {
                w.to_string()
            }
        })
        .collect()
}

fn abbrev_phase(train: &Train, network: &Network) -> String {
    match &train.phase {
        TrainPhase::Dwelling { station, .. } => {
            format!("@{}", abbrev_name(&network.station(*station).name))
        }
        TrainPhase::Traveling { to_station, .. } => {
            format!("→{}", abbrev_name(&network.station(*to_station).name))
        }
        TrainPhase::AwaitingDispatch { station, .. } => {
            format!("…{}", abbrev_name(&network.station(*station).name))
        }
    }
}

fn abbrev_name(s: &str) -> String {
    s.split(|c: char| !c.is_alphanumeric())
        .filter(|w| !w.is_empty())
        .map(|w| w.chars().next().unwrap_or(' ').to_ascii_uppercase())
        .collect()
}

pub fn fmt_time_of_day(total_s: u32) -> String {
    let tod = total_s % 86400;
    let h = tod / 3600;
    let m = (tod / 60) % 60;
    let s = tod % 60;
    format!("{h:02}:{m:02}:{s:02}")
}

/// Format sim clock including a day prefix once the sim crosses midnight.
/// On day 1 (no wrap), prints "HH:MM:SS"; from day 2 onward prints
/// "D2 HH:MM:SS" etc.
pub fn fmt_sim_clock(t: u32, start_of_day_s: u32) -> String {
    let total = t + start_of_day_s;
    let day = total / 86400;
    let tod = total % 86400;
    let h = tod / 3600;
    let m = (tod / 60) % 60;
    let s = tod % 60;
    if day == 0 {
        format!("{h:02}:{m:02}:{s:02}")
    } else {
        format!("D{} {h:02}:{m:02}:{s:02}", day + 1)
    }
}

pub fn fmt_clock(t: u32) -> String {
    fmt_time_of_day(t)
}

#[allow(clippy::too_many_arguments)] // Flat CSV row context; grouping would hide column inputs.
fn write_csv_snapshot<W: std::io::Write>(
    w: &mut W,
    t: u32,
    clock_tod: u32,
    trains: &[Train],
    network: &Network,
    climate: &ClimateModel,
    roof_pv: &RoofPvConfig,
    faults: &FaultEngine,
) {
    let tod = fmt_time_of_day(clock_tod);
    for tr in trains {
        let line_name = network.lines[tr.line_index].name.clone();
        let (phase, station, section_id, motion, station_charge_power_kw) = match &tr.phase {
            TrainPhase::Dwelling { station, .. } => (
                "dwelling",
                network.station(*station).name.clone(),
                String::new(),
                None,
                if !faults.pad_disabled_at(*station) && tr.soc < 1.0 {
                    network.station(*station).charging_power_kw as f32
                } else {
                    0.0
                },
            ),
            TrainPhase::Traveling { to_station, .. } => (
                "traveling",
                format!("→{}", network.station(*to_station).name),
                traveling_section_id(&tr.phase),
                traveling_motion_sample(tr, network),
                0.0,
            ),
            TrainPhase::AwaitingDispatch { station } => (
                "awaiting",
                network.station(*station).name.clone(),
                String::new(),
                None,
                0.0,
            ),
        };
        let (
            position_m,
            speed_mps,
            accel_mps2,
            motion_phase,
            battery_draw_power_kw,
            traction_power_kw,
            brake_power_kw,
        ) = match motion {
            Some(sample) => {
                let draw_kw = tr.kwh_per_km(climate.hvac_uplift_frac) * sample.speed_mps * 3.6;
                (
                    sample.position_m,
                    sample.speed_mps,
                    sample.accel_mps2,
                    sample.phase.as_str(),
                    draw_kw,
                    sample.traction_power_kw,
                    sample.brake_power_kw,
                )
            }
            None => (0.0, 0.0, 0.0, "", 0.0, 0.0, 0.0),
        };
        let roof_pv_power = if roof_pv_active_for_phase(roof_pv, &tr.phase) {
            roof_pv_power_breakdown(roof_pv, climate, faults, clock_tod)
        } else {
            RoofPvPowerBreakdown::default()
        };
        let _ = writeln!(
            w,
            "{t},{tod},{id},{line},{phase},\"{station}\",{soc:.4},{odo:.3},{consumed:.2},{charged:.2},{roof_charged:.2},{section_id},{position_m:.2},{speed_mps:.3},{accel_mps2:.3},{motion_phase},{battery_draw_power_kw:.2},{traction_power_kw:.2},{brake_power_kw:.2},{roof_kw:.2},{cleaner_kw:.2},{station_charge_power_kw:.2}",
            id = tr.id,
            line = csv_escape(&line_name),
            station = csv_escape(&station),
            soc = tr.soc,
            odo = tr.odometer_km,
            consumed = tr.energy_consumed_kwh,
            charged = tr.energy_charged_kwh,
            roof_charged = tr.energy_roof_pv_kwh,
            roof_kw = roof_pv_power.net_kw,
            cleaner_kw = roof_pv_power.cleaner_power_kw,
        );
    }
}

fn traveling_section_id(phase: &TrainPhase) -> String {
    match phase {
        TrainPhase::Traveling { section, .. } => section.to_string(),
        _ => String::new(),
    }
}

fn traveling_motion_sample(train: &Train, network: &Network) -> Option<MotionSample> {
    match &train.phase {
        TrainPhase::Traveling {
            section,
            total_travel_s,
            remaining_s,
            ..
        } => {
            let elapsed_s = (total_travel_s - remaining_s).max(0.0);
            Some(motion_sample_for_section(
                &train.consist,
                network.section(*section),
                elapsed_s,
            ))
        }
        _ => None,
    }
}

fn roof_pv_active_for_phase(roof_pv: &RoofPvConfig, phase: &TrainPhase) -> bool {
    match phase {
        TrainPhase::Traveling { .. } => roof_pv.charges_while_moving,
        TrainPhase::Dwelling { .. } | TrainPhase::AwaitingDispatch { .. } => {
            roof_pv.charges_while_dwelled
        }
    }
}

fn csv_escape(s: &str) -> String {
    s.replace('"', "\"\"")
}

pub fn fmt_duration(s: u32) -> String {
    let days = s / 86400;
    let rem = s % 86400;
    let h = rem / 3600;
    let m = (rem / 60) % 60;
    let s = rem % 60;
    if days > 0 {
        format!("{days}d {h:02}h {m:02}m {s:02}s")
    } else {
        format!("{h}h {m:02}m {s:02}s")
    }
}

#[cfg(test)]
mod tests {
    use super::{
        energy_adjusted_headway_s, kinematic_travel_time, roof_pv_power_breakdown, run,
        run_with_event_recording, ClimateModel, EnergyAdaptiveServiceConfig, EventKind,
        RoofPvAirCleanerConfig, RoofPvConfig, RuntimeConfig,
    };
    use crate::fault::{Fault, FaultEngine, FaultKind, FaultScope};
    use crate::scenario_file::load_scenario_from_str;

    /// Approximate equality for time comparisons (±0.1 s).
    fn approx(a: f32, b: f32) {
        assert!((a - b).abs() < 0.1, "expected {b:.3}, got {a:.3}");
    }

    #[test]
    fn trapezoidal_long_section() {
        // 2000 m section, v_max = 20, a = d = 1.
        // Accel: 0→20 at 1 m/s² → 20s, covers 200m. Same for decel.
        // Cruise: 1600m at 20 m/s → 80s. Total 120s.
        approx(kinematic_travel_time(2000.0, 20.0, 1.0, 1.0), 120.0);
    }

    #[test]
    fn triangular_short_section() {
        // 200m section, v_max = 20, a = d = 1. Can't reach v_max.
        // v_peak = sqrt(2 * 200 * 1 * 1 / 2) = sqrt(200) ≈ 14.142
        // time = v_peak / 1 + v_peak / 1 ≈ 28.28 s
        approx(kinematic_travel_time(200.0, 20.0, 1.0, 1.0), 28.28);
    }

    #[test]
    fn asymmetric_accel_decel() {
        // Accel stronger than brake: slightly longer decel phase.
        let t_sym = kinematic_travel_time(1000.0, 20.0, 1.0, 1.0);
        let t_stronger_accel = kinematic_travel_time(1000.0, 20.0, 1.5, 1.0);
        // Stronger accel shortens the accel phase, so total time is lower.
        assert!(t_stronger_accel < t_sym);
    }

    #[test]
    fn boundary_section_exactly_reaches_vmax() {
        // length = accel_dist + decel_dist exactly.
        // v_max = 20, a = d = 1 → 200 + 200 = 400m section.
        // Trapezoidal with zero cruise: 20 + 0 + 20 = 40s.
        approx(kinematic_travel_time(400.0, 20.0, 1.0, 1.0), 40.0);
    }

    fn simple_two_station_scenario(extra_consist: &str, service_start: &str) -> String {
        format!(
            r#"
[scenario]
name = "unit"
start_time = "12:00"

[climate]
ambient_c = 30.0
peak_sun_hours = 6.0

[consist]
car_count = 3
length_m = 49.5
mass_kg = 78750
max_speed_kmh = 80.0
battery_capacity_kwh = 540
service_accel_mps2 = 1.0
{extra_consist}

[[stations]]
id = "a"
name = "A"
charging_power_kw = 0
dwell_seconds = 30
is_terminal = true

[[stations]]
id = "b"
name = "B"
charging_power_kw = 0
dwell_seconds = 30
is_terminal = true

[[lines]]
id = "l1"
name = "L1"
stations = [
  {{ id = "a", distance_from_prev_m = 0 }},
  {{ id = "b", distance_from_prev_m = 2000 }},
]

[[fleets]]
line = "l1"
trainset_count = 1
dispatch_points = [{{ station = "a", heading = "forward" }}]
service_start = "{service_start}"
service_end = "23:00"
schedule = [
  {{ from = "{service_start}", to = "23:00", headway_min = 5 }},
]
"#
        )
    }

    #[test]
    fn travel_energy_is_debited_before_station_arrival() {
        let scenario = load_scenario_from_str(&simple_two_station_scenario("", "12:00")).unwrap();
        let result = run(
            &scenario,
            &RuntimeConfig {
                duration_s: 30,
                time_step_s: 1,
                status_every_s: 0,
                csv_out: None,
                csv_every_s: 60,
                ma_check_every_s: 0,
            },
        );

        assert!(
            result.total_train_km > 0.0,
            "partial section run should accrue train-km"
        );
        assert!(
            result.total_energy_consumed_kwh > 0.0,
            "partial section run should accrue energy consumption"
        );
    }

    #[test]
    fn compact_run_preserves_results_and_event_counts() {
        let scenario = load_scenario_from_str(&simple_two_station_scenario("", "12:00")).unwrap();
        let runtime = RuntimeConfig {
            duration_s: 900,
            time_step_s: 1,
            status_every_s: 0,
            csv_out: None,
            csv_every_s: 60,
            ma_check_every_s: 0,
        };

        let detailed = run(&scenario, &runtime);
        let compact = run_with_event_recording(&scenario, &runtime, false);

        assert!(!detailed.events.is_empty());
        assert!(compact.events.is_empty());
        assert_eq!(compact.event_counts, detailed.event_counts);
        assert_eq!(compact.total_train_km, detailed.total_train_km);
        assert_eq!(
            compact.total_energy_consumed_kwh,
            detailed.total_energy_consumed_kwh
        );
        assert_eq!(compact.per_train_final_soc, detailed.per_train_final_soc);
        assert_eq!(
            serde_json::to_value(&compact.onboard).unwrap(),
            serde_json::to_value(&detailed.onboard).unwrap()
        );
    }

    #[test]
    fn bounded_ma_state_matches_consensus_backed_movement() {
        let scenario = load_scenario_from_str(&simple_two_station_scenario("", "12:00")).unwrap();
        let direct_runtime = RuntimeConfig {
            duration_s: 300,
            time_step_s: 1,
            status_every_s: 0,
            csv_out: None,
            csv_every_s: 60,
            ma_check_every_s: 0,
        };
        let consensus_runtime = RuntimeConfig {
            ma_check_every_s: 30,
            ..direct_runtime.clone()
        };

        let direct = run(&scenario, &direct_runtime);
        let consensus = run(&scenario, &consensus_runtime);

        assert_eq!(direct.total_train_km, consensus.total_train_km);
        assert_eq!(
            direct.total_energy_consumed_kwh,
            consensus.total_energy_consumed_kwh
        );
        assert_eq!(direct.event_counts, consensus.event_counts);
        assert_eq!(direct.per_train_final_soc, consensus.per_train_final_soc);
        assert_eq!(
            direct.invariant_violations.len(),
            consensus.invariant_violations.len()
        );
    }

    #[test]
    fn train_does_not_enter_section_that_would_breach_energy_reserve() {
        let text = simple_two_station_scenario("", "12:00").replace(
            "distance_from_prev_m = 2000",
            "distance_from_prev_m = 40000",
        );
        let scenario = load_scenario_from_str(&text).unwrap();
        let result = run(
            &scenario,
            &RuntimeConfig {
                duration_s: 300,
                time_step_s: 1,
                status_every_s: 0,
                csv_out: None,
                csv_every_s: 60,
                ma_check_every_s: 0,
            },
        );

        assert_eq!(result.total_train_km, 0.0);
        assert_eq!(result.total_energy_consumed_kwh, 0.0);
        assert!(
            result.events.is_empty(),
            "a held train must not be dispatched"
        );
        assert_eq!(result.per_train_final_soc[0].3, 0.95);
    }

    #[test]
    fn designated_depot_service_holds_train_for_clean_inspect_recharge_slot() {
        let text = simple_two_station_scenario("", "12:00")
            .replace(
                "start_time = \"12:00\"",
                "start_time = \"12:00\"\ndepot_service_seconds = 120",
            )
            .replace(
                "id = \"b\"\nname = \"B\"\ncharging_power_kw = 0\ndwell_seconds = 30\nis_terminal = true",
                "id = \"b\"\nname = \"B\"\ncharging_power_kw = 0\ndwell_seconds = 30\nis_terminal = true\nis_depot = true\ndepot_service = true",
            )
            .replace("headway_min = 5", "headway_min = 6");
        let scenario = load_scenario_from_str(&text).unwrap();
        let result = run(
            &scenario,
            &RuntimeConfig {
                duration_s: 900,
                time_step_s: 1,
                status_every_s: 0,
                csv_out: None,
                csv_every_s: 60,
                ma_check_every_s: 0,
            },
        );

        let service_start = result
            .events
            .iter()
            .find(|event| matches!(event.kind, EventKind::DepotServiceStart { .. }))
            .expect("train never entered depot service")
            .sim_time_s;
        let service_complete = result
            .events
            .iter()
            .find(|event| matches!(event.kind, EventKind::DepotServiceComplete))
            .expect("train never completed depot service")
            .sim_time_s;
        let departure = result
            .events
            .iter()
            .find(|event| {
                event.sim_time_s >= service_start
                    && event.station_name.as_deref() == Some("B")
                    && matches!(event.kind, EventKind::DepartStation)
            })
            .expect("train never departed after depot service")
            .sim_time_s;

        assert!(service_complete >= service_start + 120);
        assert!(departure >= service_complete);
    }

    #[test]
    fn peak_priority_skips_depot_service_and_keeps_quick_turnaround() {
        let text = simple_two_station_scenario("", "12:00")
            .replace(
                "start_time = \"12:00\"",
                "start_time = \"12:00\"\ndepot_service_seconds = 120",
            )
            .replace(
                "id = \"b\"\nname = \"B\"\ncharging_power_kw = 0\ndwell_seconds = 30\nis_terminal = true",
                "id = \"b\"\nname = \"B\"\ncharging_power_kw = 0\ndwell_seconds = 30\nis_terminal = true\nis_depot = true\ndepot_service = true",
            )
            .replace("headway_min = 5", "headway_min = 3");
        let scenario = load_scenario_from_str(&text).unwrap();
        let result = run(
            &scenario,
            &RuntimeConfig {
                duration_s: 900,
                time_step_s: 1,
                status_every_s: 0,
                csv_out: None,
                csv_every_s: 60,
                ma_check_every_s: 0,
            },
        );

        assert!(
            !result.events.iter().any(|event| matches!(
                event.kind,
                EventKind::DepotServiceStart { .. } | EventKind::DepotServiceComplete
            )),
            "peak-priority operation must not insert depot service"
        );
        assert!(
            result.events.iter().any(|event| {
                event.station_name.as_deref() == Some("B")
                    && matches!(event.kind, EventKind::DepartStation)
            }),
            "train did not make its quick peak turnaround"
        );
    }

    #[test]
    fn energy_adaptive_service_preserves_peak_and_widens_low_soc_off_peak() {
        let config = EnergyAdaptiveServiceConfig {
            enabled: true,
            normal_service_soc: 0.40,
            maximum_headway_multiplier: 3.0,
            protected_peak_headway_s: 180,
        };

        assert_eq!(
            energy_adjusted_headway_s(180, 0.20, &config, 12 * 3600),
            180
        );
        assert_eq!(energy_adjusted_headway_s(360, 0.20, &config, 8 * 3600), 360);
        assert_eq!(
            energy_adjusted_headway_s(360, 0.40, &config, 12 * 3600),
            360
        );
        assert_eq!(
            energy_adjusted_headway_s(360, 0.30, &config, 12 * 3600),
            720
        );
        assert_eq!(
            energy_adjusted_headway_s(360, 0.20, &config, 12 * 3600),
            1080
        );
    }

    #[test]
    fn energy_adaptive_service_can_be_disabled() {
        let config = EnergyAdaptiveServiceConfig::default();
        assert_eq!(
            energy_adjusted_headway_s(360, 0.20, &config, 12 * 3600),
            360
        );
    }

    #[test]
    fn roof_pv_charges_held_train() {
        let roof = r#"
[consist.roof_pv]
nameplate_kw = 100.0
usable_factor = 1.0
charges_while_moving = true
charges_while_dwelled = true
"#;
        let scenario = load_scenario_from_str(&simple_two_station_scenario(roof, "13:00")).unwrap();
        let result = run(
            &scenario,
            &RuntimeConfig {
                duration_s: 600,
                time_step_s: 1,
                status_every_s: 0,
                csv_out: None,
                csv_every_s: 60,
                ma_check_every_s: 0,
            },
        );

        assert!(
            result.total_roof_pv_charged_kwh > 0.0,
            "roof PV should charge while train is awaiting dispatch"
        );
        assert_eq!(
            result.total_energy_charged_kwh,
            result.total_roof_pv_charged_kwh
        );
    }

    #[test]
    fn air_cleaner_recovers_dust_derated_roof_pv_after_parasitic_load() {
        let climate = ClimateModel {
            ambient_c: 30.0,
            peak_sun_hours: 6.0,
            hvac_uplift_frac: 0.0,
        };
        let mut faults = FaultEngine::new(vec![Fault {
            name: "dust".to_string(),
            from_sim_s: 0,
            to_sim_s: 3600,
            kind: FaultKind::DustEvent {
                pv_output_factor: 0.2,
                scope: FaultScope::All,
            },
        }]);
        faults.tick(60);

        let without_cleaner = RoofPvConfig {
            nameplate_kw: 100.0,
            usable_factor: 1.0,
            charges_while_moving: true,
            charges_while_dwelled: true,
            air_cleaner: RoofPvAirCleanerConfig::default(),
        };
        let with_cleaner = RoofPvConfig {
            air_cleaner: RoofPvAirCleanerConfig {
                enabled: true,
                compressor_power_kw: 1.0,
                dust_loss_recovery_frac: 0.75,
            },
            ..without_cleaner.clone()
        };

        let no_clean = roof_pv_power_breakdown(&without_cleaner, &climate, &faults, 12 * 3600);
        let cleaned = roof_pv_power_breakdown(&with_cleaner, &climate, &faults, 12 * 3600);

        assert!(cleaned.cleaner_power_kw > 0.0);
        assert!(
            cleaned.net_kw > no_clean.net_kw * 3.0,
            "cleaned net {:.2} kW should materially exceed dusty net {:.2} kW",
            cleaned.net_kw,
            no_clean.net_kw
        );
    }
}
