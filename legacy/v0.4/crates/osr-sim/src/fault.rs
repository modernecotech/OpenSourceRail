//! Scenario-declared fault injection.
//!
//! Fault kinds include energy/infrastructure failures and onboard
//! safety/assistance events:
//!
//! Energy / infrastructure faults:
//!
//! - **Dust event** — scales PV output (affected sites produce less power
//!   for the duration). Simulates a sandstorm, heavy haze, or module
//!   soiling incident that will be cleaned in `to_sim_s` seconds.
//! - **Grid outage** — disables grid import/export at affected sites.
//!   Simulates a utility-grid failure; sites run in islanded mode off
//!   PV + battery only.
//! - **Charging pad outage** — disables a specific station's charging pad.
//!   Simulates an equipment failure or scheduled maintenance.
//! - **Platform-door obstruction** — sets the affected station's PSD
//!   obstruction sensor while the command/sensor evaluator continues to run.
//! - **Station-SCADA failure** — degrades the affected station's monitored
//!   lift, escalator, HVAC, lighting, and CCTV reference equipment.
//!
//! Onboard obstacle-detect faults (RFC 0015 §5.1.1). These exercise the
//! five O-series safety properties through the sim's shadow stack:
//!
//! - **LIDAR offline** — forces `ObsFrame::lidar_offline = true` on the
//!   affected train(s). The evaluator emits `RestrictedSpeed` (O4b)
//!   under nominal radar, or `EmergencyBrake` (O4a) if radar is also
//!   down at speed.
//! - **Radar offline** — forces `ObsFrame::radar_offline = true`.
//!   Alone (LIDAR up) produces no restriction; combined with LIDAR
//!   offline exercises the O4a EB path at mainline speed.
//! - **Ultrasonic channel stale** — marks one ultrasonic channel with
//!   stale `age_ms`, forcing the O2 EB path.
//! - **Obstacle peer disagreement** — forces `peer_clear = false` in
//!   the 2oo2 cross-check, forcing the O3 EB path.
//! - **Battery off-gas** — injects a qualified electrolyte off-gas signal
//!   into the affected train's battery compartment.
//! - **Battery mist failure** — makes the affected train's local reservoir,
//!   pump, pressure, and flow checks unavailable.
//! - **Battery fire escalation** — marks continued movement unsafe and
//!   immediate danger present, exercising the emergency-stop branch.
//! - **T2G primary/all offline** — removes the 5G path or both 5G and backup
//!   paths, exercising deterministic radio failover and store-and-forward.
//! - **Hot axle overheat** — raises both axle channels above the trip limit.
//! - **Wayside HABD warning/overheat** — raises only the physical detector
//!   reading into the warning or trip band, allowing both authoritative
//!   trackside feedback paths to be tested independently.
//! - **CBM degradation** — drives bearing, motor, brake-pad, and wheel
//!   measurements into their service bands.
//! - **Balise missed/mismatch** — suppresses a passing train's absolute fix
//!   or corrupts its claimed position so the real registry audit rejects it.
//! - **Fare-token tamper** — flips a signature bit after TVM issuance so the
//!   affected station's real AFC gate and back office exercise denial/fraud.
//!
//! Wayside intrusion-detect faults (RFC 0016 v3). These exercise the
//! full wayside→interlocking→train chain:
//!
//! - **Wayside intrusion** — synthesises the required sensor frame, runs the
//!   intrusion evaluator, and emits its verdict transition into consensus.
//!   `Present` or `Unknown` triggers gate (d) of `section_available_to` and
//!   withholds MA from trains that need to enter the section.
//!
//! Faults are declared in the scenario TOML under `[[faults]]`; see
//! `lib/examples/README.md` for the format.

use osr_core::{SectionId, StationId, TrainId};
use osr_interlocking::IntrusionState;
use std::collections::{HashMap, HashSet};

// ---------------------------------------------------------------------------
// Fault types
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FaultScope {
    /// All energy sites / all charging pads (per fault kind).
    All,
    /// A specific station.
    Station(StationId),
}

/// Scope for onboard (per-train) faults.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TrainFaultScope {
    /// Apply to every train in the fleet.
    All,
    /// Apply to one specific train.
    Train(TrainId),
}

#[derive(Clone, Debug)]
pub enum FaultKind {
    DustEvent {
        pv_output_factor: f32,
        scope: FaultScope,
    },
    GridOutage {
        scope: FaultScope,
    },
    ChargingPadOutage {
        station: StationId,
    },
    /// Obstruct one or every station's platform-door close cycle.
    PlatformDoorObstruction {
        scope: FaultScope,
    },
    /// Fail the reference station SCADA equipment set.
    StationScadaFailure {
        scope: FaultScope,
    },
    /// RFC 0015 §5.1.1 — LIDAR offline on affected train(s).
    LidarOffline {
        scope: TrainFaultScope,
    },
    /// RFC 0015 §5.1.1 — mmWave radar offline.
    RadarOffline {
        scope: TrainFaultScope,
    },
    /// RFC 0015 §5.1.1 — one ultrasonic channel stale (0..=3).
    UltrasonicChannelStale {
        scope: TrainFaultScope,
        channel: u8,
    },
    /// RFC 0015 §5.1.1 — force the 2oo2 peer cross-check to disagree.
    ObstaclePeerDisagreement {
        scope: TrainFaultScope,
    },
    /// RFC 0015 §5.3 — press a passenger emergency intercom.
    PassengerIntercomPress {
        scope: TrainFaultScope,
    },
    /// RFC 0021 — qualified electrolyte off-gas in a battery compartment.
    BatteryOffGas {
        scope: TrainFaultScope,
    },
    /// RFC 0021 — local battery water-mist system unavailable.
    BatteryMistFailure {
        scope: TrainFaultScope,
    },
    /// RFC 0021 — containment lost or continued movement unsafe.
    BatteryFireEscalation {
        scope: TrainFaultScope,
    },
    /// Disable the primary T2G channel; the backup should carry telemetry.
    T2gPrimaryOffline {
        scope: TrainFaultScope,
    },
    /// Disable both T2G channels; telemetry must remain queued.
    T2gAllOffline {
        scope: TrainFaultScope,
    },
    /// Inject a dual-channel hot-axle reading above the trip threshold.
    HotAxleOverheat {
        scope: TrainFaultScope,
    },
    /// Inject a hot bearing at physical HABD passage without altering the
    /// onboard advisory sensor channels.
    HabdOverheat {
        scope: TrainFaultScope,
    },
    /// Inject a warm bearing in the physical HABD warning band without
    /// altering the onboard advisory sensor channels.
    HabdWarning {
        scope: TrainFaultScope,
    },
    /// Inject service-level degradation across the onboard CBM sensors.
    CbmDegradation {
        scope: TrainFaultScope,
    },
    /// Suppress the physical balise sighting for the affected train(s).
    BaliseMissed {
        scope: TrainFaultScope,
    },
    /// Shift the reported balise position so the registry rejects the fix.
    BalisePositionMismatch {
        scope: TrainFaultScope,
    },
    /// Corrupt the TVM-issued token before presentation at affected gate(s).
    FareTokenTamper {
        scope: FaultScope,
    },
    /// RFC 0016 v3 — inject a wayside intrusion verdict on a named
    /// section. The sim emits a `SectionIntrusion` consensus entry
    /// carrying this state for as long as the fault is active; the
    /// interlocking's gate (d) then withholds MA to any train that
    /// needs to cross the affected section.
    WaysideIntrusion {
        section: SectionId,
        state: IntrusionState,
    },
}

#[derive(Clone, Debug)]
pub struct Fault {
    pub name: String,
    /// Absolute simulation-time seconds when the fault activates.
    pub from_sim_s: u32,
    /// Absolute simulation-time seconds when the fault deactivates.
    pub to_sim_s: u32,
    pub kind: FaultKind,
}

// ---------------------------------------------------------------------------
// FaultEngine — evaluated each tick, exposes current overrides
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, Default)]
pub struct FaultEngine {
    pub faults: Vec<Fault>,
    /// Active PV output factor per station (default 1.0 when not present).
    pv_factor: HashMap<StationId, f32>,
    /// All-sites dust event currently active (multiplier if active).
    global_pv_factor: f32,
    /// Sites with grid currently disabled.
    grid_disabled: HashSet<StationId>,
    global_grid_disabled: bool,
    /// Stations with charging pad currently disabled.
    pad_disabled: HashSet<StationId>,
    psd_obstructed: HashSet<StationId>,
    psd_obstructed_all: bool,
    station_scada_failed: HashSet<StationId>,
    station_scada_failed_all: bool,
    // Onboard obstacle-sensor faults (RFC 0015). Per-train sets; plus
    // a global bool for fleet-wide faults that apply to every train.
    lidar_offline_trains: HashSet<TrainId>,
    lidar_offline_all: bool,
    radar_offline_trains: HashSet<TrainId>,
    radar_offline_all: bool,
    ultrasonic_stale_per_train: HashMap<TrainId, u8>, // bitmask of stale channels
    ultrasonic_stale_all: u8,
    peer_disagreement_trains: HashSet<TrainId>,
    peer_disagreement_all: bool,
    intercom_pressed_trains: HashSet<TrainId>,
    intercom_pressed_all: bool,
    battery_off_gas_trains: HashSet<TrainId>,
    battery_off_gas_all: bool,
    battery_mist_failure_trains: HashSet<TrainId>,
    battery_mist_failure_all: bool,
    battery_fire_escalation_trains: HashSet<TrainId>,
    battery_fire_escalation_all: bool,
    t2g_primary_offline_trains: HashSet<TrainId>,
    t2g_primary_offline_all: bool,
    t2g_all_offline_trains: HashSet<TrainId>,
    t2g_all_offline_all: bool,
    hot_axle_overheat_trains: HashSet<TrainId>,
    hot_axle_overheat_all: bool,
    habd_overheat_trains: HashSet<TrainId>,
    habd_overheat_all: bool,
    habd_warning_trains: HashSet<TrainId>,
    habd_warning_all: bool,
    cbm_degradation_trains: HashSet<TrainId>,
    cbm_degradation_all: bool,
    balise_missed_trains: HashSet<TrainId>,
    balise_missed_all: bool,
    balise_mismatch_trains: HashSet<TrainId>,
    balise_mismatch_all: bool,
    fare_token_tamper_stations: HashSet<StationId>,
    fare_token_tamper_all: bool,
    /// Active wayside intrusion injections — `section → state`. The sim
    /// emits a `SectionIntrusion` entry per tick for each key. Rebuilt
    /// in `tick()`.
    wayside_intrusions: HashMap<SectionId, IntrusionState>,
    /// Names of faults that ever activated during the run (for reporting).
    pub fault_log: Vec<FaultLogEntry>,
    fired_names: HashSet<String>,
}

#[derive(Clone, Debug)]
pub struct FaultLogEntry {
    pub name: String,
    pub started_at_sim_s: u32,
    pub duration_s: u32,
    pub kind_description: String,
}

impl FaultEngine {
    pub fn new(faults: Vec<Fault>) -> Self {
        Self {
            faults,
            pv_factor: HashMap::new(),
            global_pv_factor: 1.0,
            grid_disabled: HashSet::new(),
            global_grid_disabled: false,
            pad_disabled: HashSet::new(),
            psd_obstructed: HashSet::new(),
            psd_obstructed_all: false,
            station_scada_failed: HashSet::new(),
            station_scada_failed_all: false,
            lidar_offline_trains: HashSet::new(),
            lidar_offline_all: false,
            radar_offline_trains: HashSet::new(),
            radar_offline_all: false,
            ultrasonic_stale_per_train: HashMap::new(),
            ultrasonic_stale_all: 0,
            peer_disagreement_trains: HashSet::new(),
            peer_disagreement_all: false,
            intercom_pressed_trains: HashSet::new(),
            intercom_pressed_all: false,
            battery_off_gas_trains: HashSet::new(),
            battery_off_gas_all: false,
            battery_mist_failure_trains: HashSet::new(),
            battery_mist_failure_all: false,
            battery_fire_escalation_trains: HashSet::new(),
            battery_fire_escalation_all: false,
            t2g_primary_offline_trains: HashSet::new(),
            t2g_primary_offline_all: false,
            t2g_all_offline_trains: HashSet::new(),
            t2g_all_offline_all: false,
            hot_axle_overheat_trains: HashSet::new(),
            hot_axle_overheat_all: false,
            habd_overheat_trains: HashSet::new(),
            habd_overheat_all: false,
            habd_warning_trains: HashSet::new(),
            habd_warning_all: false,
            cbm_degradation_trains: HashSet::new(),
            cbm_degradation_all: false,
            balise_missed_trains: HashSet::new(),
            balise_missed_all: false,
            balise_mismatch_trains: HashSet::new(),
            balise_mismatch_all: false,
            fare_token_tamper_stations: HashSet::new(),
            fare_token_tamper_all: false,
            wayside_intrusions: HashMap::new(),
            fault_log: Vec::new(),
            fired_names: HashSet::new(),
        }
    }

    /// Recompute all active-fault state for the given sim time. Called once
    /// per tick before anything that reads fault state.
    pub fn tick(&mut self, t: u32) {
        self.pv_factor.clear();
        self.global_pv_factor = 1.0;
        self.grid_disabled.clear();
        self.global_grid_disabled = false;
        self.pad_disabled.clear();
        self.psd_obstructed.clear();
        self.psd_obstructed_all = false;
        self.station_scada_failed.clear();
        self.station_scada_failed_all = false;
        self.lidar_offline_trains.clear();
        self.lidar_offline_all = false;
        self.radar_offline_trains.clear();
        self.radar_offline_all = false;
        self.ultrasonic_stale_per_train.clear();
        self.ultrasonic_stale_all = 0;
        self.peer_disagreement_trains.clear();
        self.peer_disagreement_all = false;
        self.intercom_pressed_trains.clear();
        self.intercom_pressed_all = false;
        self.battery_off_gas_trains.clear();
        self.battery_off_gas_all = false;
        self.battery_mist_failure_trains.clear();
        self.battery_mist_failure_all = false;
        self.battery_fire_escalation_trains.clear();
        self.battery_fire_escalation_all = false;
        self.t2g_primary_offline_trains.clear();
        self.t2g_primary_offline_all = false;
        self.t2g_all_offline_trains.clear();
        self.t2g_all_offline_all = false;
        self.hot_axle_overheat_trains.clear();
        self.hot_axle_overheat_all = false;
        self.habd_overheat_trains.clear();
        self.habd_overheat_all = false;
        self.habd_warning_trains.clear();
        self.habd_warning_all = false;
        self.cbm_degradation_trains.clear();
        self.cbm_degradation_all = false;
        self.balise_missed_trains.clear();
        self.balise_missed_all = false;
        self.balise_mismatch_trains.clear();
        self.balise_mismatch_all = false;
        self.fare_token_tamper_stations.clear();
        self.fare_token_tamper_all = false;
        self.wayside_intrusions.clear();

        for fault in &self.faults {
            let active = t >= fault.from_sim_s && t < fault.to_sim_s;
            if !active {
                continue;
            }
            if self.fired_names.insert(fault.name.clone()) {
                self.fault_log.push(FaultLogEntry {
                    name: fault.name.clone(),
                    started_at_sim_s: fault.from_sim_s,
                    duration_s: fault.to_sim_s.saturating_sub(fault.from_sim_s),
                    kind_description: describe_kind(&fault.kind),
                });
            }
            match &fault.kind {
                FaultKind::DustEvent {
                    pv_output_factor,
                    scope,
                } => match scope {
                    FaultScope::All => {
                        self.global_pv_factor *= pv_output_factor;
                    }
                    FaultScope::Station(s) => {
                        let entry = self.pv_factor.entry(*s).or_insert(1.0);
                        *entry *= pv_output_factor;
                    }
                },
                FaultKind::GridOutage { scope } => match scope {
                    FaultScope::All => self.global_grid_disabled = true,
                    FaultScope::Station(s) => {
                        self.grid_disabled.insert(*s);
                    }
                },
                FaultKind::ChargingPadOutage { station } => {
                    self.pad_disabled.insert(*station);
                }
                FaultKind::PlatformDoorObstruction { scope } => match scope {
                    FaultScope::All => self.psd_obstructed_all = true,
                    FaultScope::Station(station) => {
                        self.psd_obstructed.insert(*station);
                    }
                },
                FaultKind::StationScadaFailure { scope } => match scope {
                    FaultScope::All => self.station_scada_failed_all = true,
                    FaultScope::Station(station) => {
                        self.station_scada_failed.insert(*station);
                    }
                },
                FaultKind::LidarOffline { scope } => match scope {
                    TrainFaultScope::All => self.lidar_offline_all = true,
                    TrainFaultScope::Train(t) => {
                        self.lidar_offline_trains.insert(*t);
                    }
                },
                FaultKind::RadarOffline { scope } => match scope {
                    TrainFaultScope::All => self.radar_offline_all = true,
                    TrainFaultScope::Train(t) => {
                        self.radar_offline_trains.insert(*t);
                    }
                },
                FaultKind::UltrasonicChannelStale { scope, channel } => {
                    let bit = 1u8 << (channel & 0x03);
                    match scope {
                        TrainFaultScope::All => self.ultrasonic_stale_all |= bit,
                        TrainFaultScope::Train(train) => {
                            *self.ultrasonic_stale_per_train.entry(*train).or_insert(0) |= bit;
                        }
                    }
                }
                FaultKind::ObstaclePeerDisagreement { scope } => match scope {
                    TrainFaultScope::All => self.peer_disagreement_all = true,
                    TrainFaultScope::Train(t) => {
                        self.peer_disagreement_trains.insert(*t);
                    }
                },
                FaultKind::PassengerIntercomPress { scope } => match scope {
                    TrainFaultScope::All => self.intercom_pressed_all = true,
                    TrainFaultScope::Train(t) => {
                        self.intercom_pressed_trains.insert(*t);
                    }
                },
                FaultKind::BatteryOffGas { scope } => match scope {
                    TrainFaultScope::All => self.battery_off_gas_all = true,
                    TrainFaultScope::Train(t) => {
                        self.battery_off_gas_trains.insert(*t);
                    }
                },
                FaultKind::BatteryMistFailure { scope } => match scope {
                    TrainFaultScope::All => self.battery_mist_failure_all = true,
                    TrainFaultScope::Train(t) => {
                        self.battery_mist_failure_trains.insert(*t);
                    }
                },
                FaultKind::BatteryFireEscalation { scope } => match scope {
                    TrainFaultScope::All => self.battery_fire_escalation_all = true,
                    TrainFaultScope::Train(t) => {
                        self.battery_fire_escalation_trains.insert(*t);
                    }
                },
                FaultKind::T2gPrimaryOffline { scope } => match scope {
                    TrainFaultScope::All => self.t2g_primary_offline_all = true,
                    TrainFaultScope::Train(t) => {
                        self.t2g_primary_offline_trains.insert(*t);
                    }
                },
                FaultKind::T2gAllOffline { scope } => match scope {
                    TrainFaultScope::All => self.t2g_all_offline_all = true,
                    TrainFaultScope::Train(t) => {
                        self.t2g_all_offline_trains.insert(*t);
                    }
                },
                FaultKind::HotAxleOverheat { scope } => match scope {
                    TrainFaultScope::All => self.hot_axle_overheat_all = true,
                    TrainFaultScope::Train(t) => {
                        self.hot_axle_overheat_trains.insert(*t);
                    }
                },
                FaultKind::HabdOverheat { scope } => match scope {
                    TrainFaultScope::All => self.habd_overheat_all = true,
                    TrainFaultScope::Train(t) => {
                        self.habd_overheat_trains.insert(*t);
                    }
                },
                FaultKind::HabdWarning { scope } => match scope {
                    TrainFaultScope::All => self.habd_warning_all = true,
                    TrainFaultScope::Train(t) => {
                        self.habd_warning_trains.insert(*t);
                    }
                },
                FaultKind::CbmDegradation { scope } => match scope {
                    TrainFaultScope::All => self.cbm_degradation_all = true,
                    TrainFaultScope::Train(t) => {
                        self.cbm_degradation_trains.insert(*t);
                    }
                },
                FaultKind::BaliseMissed { scope } => match scope {
                    TrainFaultScope::All => self.balise_missed_all = true,
                    TrainFaultScope::Train(t) => {
                        self.balise_missed_trains.insert(*t);
                    }
                },
                FaultKind::BalisePositionMismatch { scope } => match scope {
                    TrainFaultScope::All => self.balise_mismatch_all = true,
                    TrainFaultScope::Train(t) => {
                        self.balise_mismatch_trains.insert(*t);
                    }
                },
                FaultKind::FareTokenTamper { scope } => match scope {
                    FaultScope::All => self.fare_token_tamper_all = true,
                    FaultScope::Station(station) => {
                        self.fare_token_tamper_stations.insert(*station);
                    }
                },
                FaultKind::WaysideIntrusion { section, state } => {
                    // Most-restrictive state wins when multiple faults
                    // overlap on the same section.
                    let slot = self
                        .wayside_intrusions
                        .entry(*section)
                        .or_insert(IntrusionState::Clear);
                    *slot = most_restrictive(*slot, *state);
                }
            }
        }
    }

    /// Iterator of `(section, state)` pairs for every active wayside-
    /// intrusion fault. Called once per sim tick to emit
    /// `SectionIntrusion` consensus entries.
    pub fn intrusion_state_for(&self, section: SectionId) -> IntrusionState {
        self.wayside_intrusions
            .get(&section)
            .copied()
            .unwrap_or(IntrusionState::Clear)
    }

    pub fn pv_factor_for(&self, station: StationId) -> f32 {
        let per_site = self.pv_factor.get(&station).copied().unwrap_or(1.0);
        (per_site * self.global_pv_factor).clamp(0.0, 1.0)
    }

    /// Fleet-wide PV derate for mobile sources such as train roof PV.
    ///
    /// Station-scoped dust events only affect fixed sites. A global dust event
    /// applies to all PV, including onboard arrays.
    pub fn global_pv_factor(&self) -> f32 {
        self.global_pv_factor.clamp(0.0, 1.0)
    }

    pub fn grid_disabled_at(&self, station: StationId) -> bool {
        self.global_grid_disabled || self.grid_disabled.contains(&station)
    }

    pub fn pad_disabled_at(&self, station: StationId) -> bool {
        self.pad_disabled.contains(&station)
    }

    pub fn psd_obstructed_at(&self, station: StationId) -> bool {
        self.psd_obstructed_all || self.psd_obstructed.contains(&station)
    }

    pub fn station_scada_failed_at(&self, station: StationId) -> bool {
        self.station_scada_failed_all || self.station_scada_failed.contains(&station)
    }

    // Onboard (obstacle-detect) fault getters. Each one OR-combines the
    // all-fleet fault with the per-train set.

    pub fn lidar_offline_for(&self, train: TrainId) -> bool {
        self.lidar_offline_all || self.lidar_offline_trains.contains(&train)
    }

    pub fn radar_offline_for(&self, train: TrainId) -> bool {
        self.radar_offline_all || self.radar_offline_trains.contains(&train)
    }

    /// Bitmask of stale ultrasonic channels for a given train (bit 0 =
    /// channel 0, …, bit 3 = channel 3). Returns 0 if no ultrasonic
    /// faults are active.
    pub fn ultrasonic_stale_mask_for(&self, train: TrainId) -> u8 {
        let per = self
            .ultrasonic_stale_per_train
            .get(&train)
            .copied()
            .unwrap_or(0);
        per | self.ultrasonic_stale_all
    }

    pub fn peer_disagreement_for(&self, train: TrainId) -> bool {
        self.peer_disagreement_all || self.peer_disagreement_trains.contains(&train)
    }

    pub fn passenger_intercom_pressed_for(&self, train: TrainId) -> bool {
        self.intercom_pressed_all || self.intercom_pressed_trains.contains(&train)
    }

    pub fn battery_off_gas_for(&self, train: TrainId) -> bool {
        self.battery_off_gas_all || self.battery_off_gas_trains.contains(&train)
    }

    pub fn battery_mist_failed_for(&self, train: TrainId) -> bool {
        self.battery_mist_failure_all || self.battery_mist_failure_trains.contains(&train)
    }

    pub fn battery_fire_escalated_for(&self, train: TrainId) -> bool {
        self.battery_fire_escalation_all || self.battery_fire_escalation_trains.contains(&train)
    }

    pub fn t2g_primary_offline_for(&self, train: TrainId) -> bool {
        self.t2g_primary_offline_all || self.t2g_primary_offline_trains.contains(&train)
    }

    pub fn t2g_all_offline_for(&self, train: TrainId) -> bool {
        self.t2g_all_offline_all || self.t2g_all_offline_trains.contains(&train)
    }

    pub fn hot_axle_overheat_for(&self, train: TrainId) -> bool {
        self.hot_axle_overheat_all || self.hot_axle_overheat_trains.contains(&train)
    }

    pub fn habd_overheat_for(&self, train: TrainId) -> bool {
        self.habd_overheat_all || self.habd_overheat_trains.contains(&train)
    }

    pub fn habd_warning_for(&self, train: TrainId) -> bool {
        self.habd_warning_all || self.habd_warning_trains.contains(&train)
    }

    pub fn cbm_degradation_for(&self, train: TrainId) -> bool {
        self.cbm_degradation_all || self.cbm_degradation_trains.contains(&train)
    }

    pub fn balise_missed_for(&self, train: TrainId) -> bool {
        self.balise_missed_all || self.balise_missed_trains.contains(&train)
    }

    pub fn balise_mismatch_for(&self, train: TrainId) -> bool {
        self.balise_mismatch_all || self.balise_mismatch_trains.contains(&train)
    }

    pub fn fare_token_tampered_at(&self, station_id: u32) -> bool {
        self.fare_token_tamper_all
            || self
                .fare_token_tamper_stations
                .contains(&StationId::new(u64::from(station_id)))
    }
}

fn most_restrictive(a: IntrusionState, b: IntrusionState) -> IntrusionState {
    // Present > Unknown > Clear on the severity order defined in
    // RFC 0016 §5.2.
    fn rank(s: IntrusionState) -> u8 {
        match s {
            IntrusionState::Clear => 0,
            IntrusionState::Unknown => 1,
            IntrusionState::Present => 2,
        }
    }
    if rank(a) >= rank(b) {
        a
    } else {
        b
    }
}

fn describe_kind(kind: &FaultKind) -> String {
    match kind {
        FaultKind::DustEvent {
            pv_output_factor,
            scope,
        } => {
            let s = match scope {
                FaultScope::All => "all sites".to_string(),
                FaultScope::Station(_) => "one site".to_string(),
            };
            format!("dust event ({:.0}% PV at {s})", pv_output_factor * 100.0)
        }
        FaultKind::GridOutage { scope } => match scope {
            FaultScope::All => "grid outage (all sites)".to_string(),
            FaultScope::Station(_) => "grid outage (one site)".to_string(),
        },
        FaultKind::ChargingPadOutage { .. } => "charging pad outage".to_string(),
        FaultKind::PlatformDoorObstruction { scope } => match scope {
            FaultScope::All => "platform-door obstruction (all stations)".to_string(),
            FaultScope::Station(_) => "platform-door obstruction (one station)".to_string(),
        },
        FaultKind::StationScadaFailure { scope } => match scope {
            FaultScope::All => "station SCADA failure (all stations)".to_string(),
            FaultScope::Station(_) => "station SCADA failure (one station)".to_string(),
        },
        FaultKind::LidarOffline { scope } => match scope {
            TrainFaultScope::All => "LIDAR offline (fleet)".to_string(),
            TrainFaultScope::Train(_) => "LIDAR offline (one train)".to_string(),
        },
        FaultKind::RadarOffline { scope } => match scope {
            TrainFaultScope::All => "radar offline (fleet)".to_string(),
            TrainFaultScope::Train(_) => "radar offline (one train)".to_string(),
        },
        FaultKind::UltrasonicChannelStale { scope, channel } => {
            let s = match scope {
                TrainFaultScope::All => "fleet",
                TrainFaultScope::Train(_) => "one train",
            };
            format!("ultrasonic channel {channel} stale ({s})")
        }
        FaultKind::ObstaclePeerDisagreement { scope } => match scope {
            TrainFaultScope::All => "obstacle peer disagreement (fleet)".to_string(),
            TrainFaultScope::Train(_) => "obstacle peer disagreement (one train)".to_string(),
        },
        FaultKind::PassengerIntercomPress { scope } => match scope {
            TrainFaultScope::All => "passenger intercom pressed (fleet)".to_string(),
            TrainFaultScope::Train(_) => "passenger intercom pressed (one train)".to_string(),
        },
        FaultKind::BatteryOffGas { scope } => match scope {
            TrainFaultScope::All => "battery off-gas (fleet)".to_string(),
            TrainFaultScope::Train(_) => "battery off-gas (one train)".to_string(),
        },
        FaultKind::BatteryMistFailure { scope } => match scope {
            TrainFaultScope::All => "battery mist failure (fleet)".to_string(),
            TrainFaultScope::Train(_) => "battery mist failure (one train)".to_string(),
        },
        FaultKind::BatteryFireEscalation { scope } => match scope {
            TrainFaultScope::All => "battery fire escalation (fleet)".to_string(),
            TrainFaultScope::Train(_) => "battery fire escalation (one train)".to_string(),
        },
        FaultKind::T2gPrimaryOffline { scope } => match scope {
            TrainFaultScope::All => "T2G primary offline (fleet)".to_string(),
            TrainFaultScope::Train(_) => "T2G primary offline (one train)".to_string(),
        },
        FaultKind::T2gAllOffline { scope } => match scope {
            TrainFaultScope::All => "T2G primary and backup offline (fleet)".to_string(),
            TrainFaultScope::Train(_) => "T2G primary and backup offline (one train)".to_string(),
        },
        FaultKind::HotAxleOverheat { scope } => match scope {
            TrainFaultScope::All => "hot axle overheat (fleet)".to_string(),
            TrainFaultScope::Train(_) => "hot axle overheat (one train)".to_string(),
        },
        FaultKind::HabdOverheat { scope } => match scope {
            TrainFaultScope::All => "wayside HABD overheat (fleet)".to_string(),
            TrainFaultScope::Train(_) => "wayside HABD overheat (one train)".to_string(),
        },
        FaultKind::HabdWarning { scope } => match scope {
            TrainFaultScope::All => "wayside HABD warning (fleet)".to_string(),
            TrainFaultScope::Train(_) => "wayside HABD warning (one train)".to_string(),
        },
        FaultKind::CbmDegradation { scope } => match scope {
            TrainFaultScope::All => "CBM service-level degradation (fleet)".to_string(),
            TrainFaultScope::Train(_) => "CBM service-level degradation (one train)".to_string(),
        },
        FaultKind::BaliseMissed { scope } => match scope {
            TrainFaultScope::All => "balise missed (fleet)".to_string(),
            TrainFaultScope::Train(_) => "balise missed (one train)".to_string(),
        },
        FaultKind::BalisePositionMismatch { scope } => match scope {
            TrainFaultScope::All => "balise position mismatch (fleet)".to_string(),
            TrainFaultScope::Train(_) => "balise position mismatch (one train)".to_string(),
        },
        FaultKind::FareTokenTamper { scope } => match scope {
            FaultScope::All => "fare token tamper (all stations)".to_string(),
            FaultScope::Station(_) => "fare token tamper (one station)".to_string(),
        },
        FaultKind::WaysideIntrusion { section, state } => {
            let s = match state {
                IntrusionState::Clear => "Clear",
                IntrusionState::Unknown => "Unknown",
                IntrusionState::Present => "Present",
            };
            format!("wayside intrusion {s} on {section}")
        }
    }
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn mk(from: u32, to: u32, kind: FaultKind) -> Fault {
        Fault {
            name: "f".to_string(),
            from_sim_s: from,
            to_sim_s: to,
            kind,
        }
    }

    #[test]
    fn inactive_before_and_after() {
        let mut eng = FaultEngine::new(vec![mk(
            100,
            200,
            FaultKind::GridOutage {
                scope: FaultScope::All,
            },
        )]);
        eng.tick(50);
        assert!(!eng.grid_disabled_at(StationId::new(1)));
        eng.tick(250);
        assert!(!eng.grid_disabled_at(StationId::new(1)));
    }

    #[test]
    fn active_in_window() {
        let mut eng = FaultEngine::new(vec![mk(
            100,
            200,
            FaultKind::GridOutage {
                scope: FaultScope::All,
            },
        )]);
        eng.tick(150);
        assert!(eng.grid_disabled_at(StationId::new(1)));
    }

    #[test]
    fn dust_event_scales_pv() {
        let station = StationId::new(42);
        let mut eng = FaultEngine::new(vec![mk(
            0,
            1000,
            FaultKind::DustEvent {
                pv_output_factor: 0.3,
                scope: FaultScope::Station(station),
            },
        )]);
        eng.tick(500);
        assert!((eng.pv_factor_for(station) - 0.3).abs() < 1e-6);
        // Unaffected stations should still see full output.
        assert_eq!(eng.pv_factor_for(StationId::new(43)), 1.0);
    }

    #[test]
    fn pad_outage_scoped() {
        let s = StationId::new(1);
        let other = StationId::new(2);
        let mut eng = FaultEngine::new(vec![mk(
            0,
            1000,
            FaultKind::ChargingPadOutage { station: s },
        )]);
        eng.tick(500);
        assert!(eng.pad_disabled_at(s));
        assert!(!eng.pad_disabled_at(other));
    }

    #[test]
    fn station_controller_faults_respect_scope_and_clear_after_window() {
        let target = StationId::new(3);
        let other = StationId::new(4);
        let mut eng = FaultEngine::new(vec![
            mk(
                10,
                20,
                FaultKind::PlatformDoorObstruction {
                    scope: FaultScope::Station(target),
                },
            ),
            mk(
                10,
                20,
                FaultKind::StationScadaFailure {
                    scope: FaultScope::All,
                },
            ),
        ]);
        eng.tick(15);
        assert!(eng.psd_obstructed_at(target));
        assert!(!eng.psd_obstructed_at(other));
        assert!(eng.station_scada_failed_at(target));
        assert!(eng.station_scada_failed_at(other));

        eng.tick(20);
        assert!(!eng.psd_obstructed_at(target));
        assert!(!eng.station_scada_failed_at(other));
    }

    #[test]
    fn fault_log_records_first_firing_only() {
        let mut eng = FaultEngine::new(vec![mk(
            0,
            1000,
            FaultKind::GridOutage {
                scope: FaultScope::All,
            },
        )]);
        eng.tick(100);
        eng.tick(200);
        eng.tick(300);
        assert_eq!(eng.fault_log.len(), 1);
    }

    #[test]
    fn lidar_offline_all_propagates_to_every_train() {
        let mut eng = FaultEngine::new(vec![mk(
            0,
            1000,
            FaultKind::LidarOffline {
                scope: TrainFaultScope::All,
            },
        )]);
        eng.tick(500);
        assert!(eng.lidar_offline_for(TrainId::new(1)));
        assert!(eng.lidar_offline_for(TrainId::new(42)));
        // Other sensors unaffected.
        assert!(!eng.radar_offline_for(TrainId::new(1)));
        assert!(!eng.peer_disagreement_for(TrainId::new(1)));
    }

    #[test]
    fn lidar_offline_scoped_to_one_train() {
        let target = TrainId::new(3);
        let other = TrainId::new(7);
        let mut eng = FaultEngine::new(vec![mk(
            0,
            1000,
            FaultKind::LidarOffline {
                scope: TrainFaultScope::Train(target),
            },
        )]);
        eng.tick(500);
        assert!(eng.lidar_offline_for(target));
        assert!(!eng.lidar_offline_for(other));
    }

    #[test]
    fn ultrasonic_stale_bitmask_composes() {
        let target = TrainId::new(5);
        let mut eng = FaultEngine::new(vec![
            mk(
                0,
                1000,
                FaultKind::UltrasonicChannelStale {
                    scope: TrainFaultScope::Train(target),
                    channel: 0,
                },
            ),
            mk(
                0,
                1000,
                FaultKind::UltrasonicChannelStale {
                    scope: TrainFaultScope::Train(target),
                    channel: 2,
                },
            ),
        ]);
        eng.tick(500);
        let mask = eng.ultrasonic_stale_mask_for(target);
        assert_eq!(mask & 0b0001, 0b0001, "ch 0 should be set");
        assert_eq!(mask & 0b0100, 0b0100, "ch 2 should be set");
        assert_eq!(mask & 0b1010, 0, "ch 1 and 3 should be clear");
    }

    #[test]
    fn ultrasonic_stale_all_applies_to_every_train() {
        let mut eng = FaultEngine::new(vec![mk(
            0,
            1000,
            FaultKind::UltrasonicChannelStale {
                scope: TrainFaultScope::All,
                channel: 1,
            },
        )]);
        eng.tick(500);
        assert_eq!(
            eng.ultrasonic_stale_mask_for(TrainId::new(99)) & 0b0010,
            0b0010
        );
    }

    #[test]
    fn peer_disagreement_per_train() {
        let a = TrainId::new(1);
        let b = TrainId::new(2);
        let mut eng = FaultEngine::new(vec![mk(
            100,
            200,
            FaultKind::ObstaclePeerDisagreement {
                scope: TrainFaultScope::Train(a),
            },
        )]);
        eng.tick(50);
        assert!(!eng.peer_disagreement_for(a));
        eng.tick(150);
        assert!(eng.peer_disagreement_for(a));
        assert!(!eng.peer_disagreement_for(b));
        eng.tick(250);
        assert!(!eng.peer_disagreement_for(a));
    }

    #[test]
    fn battery_fire_faults_are_independently_scoped() {
        let target = TrainId::new(4);
        let other = TrainId::new(5);
        let mut eng = FaultEngine::new(vec![
            mk(
                0,
                1000,
                FaultKind::BatteryOffGas {
                    scope: TrainFaultScope::Train(target),
                },
            ),
            mk(
                0,
                1000,
                FaultKind::BatteryMistFailure {
                    scope: TrainFaultScope::Train(target),
                },
            ),
            mk(
                500,
                1000,
                FaultKind::BatteryFireEscalation {
                    scope: TrainFaultScope::Train(target),
                },
            ),
        ]);
        eng.tick(100);
        assert!(eng.battery_off_gas_for(target));
        assert!(eng.battery_mist_failed_for(target));
        assert!(!eng.battery_fire_escalated_for(target));
        assert!(!eng.battery_off_gas_for(other));

        eng.tick(600);
        assert!(eng.battery_fire_escalated_for(target));
        assert!(!eng.battery_fire_escalated_for(other));
    }

    #[test]
    fn multiple_dust_events_compose_multiplicatively() {
        let mut eng = FaultEngine::new(vec![
            mk(
                0,
                1000,
                FaultKind::DustEvent {
                    pv_output_factor: 0.5,
                    scope: FaultScope::All,
                },
            ),
            mk(
                0,
                1000,
                FaultKind::DustEvent {
                    pv_output_factor: 0.5,
                    scope: FaultScope::All,
                },
            ),
        ]);
        eng.tick(500);
        assert!((eng.pv_factor_for(StationId::new(1)) - 0.25).abs() < 1e-6);
    }
}
