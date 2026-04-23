//! Scenario-declared fault injection.
//!
//! Seven kinds of fault are supported:
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
//!
//! Faults are declared in the scenario TOML under `[[faults]]`; see
//! `scenarios/README.md` for the format.

use osr_core::{StationId, TrainId};
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
            lidar_offline_trains: HashSet::new(),
            lidar_offline_all: false,
            radar_offline_trains: HashSet::new(),
            radar_offline_all: false,
            ultrasonic_stale_per_train: HashMap::new(),
            ultrasonic_stale_all: 0,
            peer_disagreement_trains: HashSet::new(),
            peer_disagreement_all: false,
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
        self.lidar_offline_trains.clear();
        self.lidar_offline_all = false;
        self.radar_offline_trains.clear();
        self.radar_offline_all = false;
        self.ultrasonic_stale_per_train.clear();
        self.ultrasonic_stale_all = 0;
        self.peer_disagreement_trains.clear();
        self.peer_disagreement_all = false;

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
                FaultKind::DustEvent { pv_output_factor, scope } => match scope {
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
                            *self
                                .ultrasonic_stale_per_train
                                .entry(*train)
                                .or_insert(0) |= bit;
                        }
                    }
                }
                FaultKind::ObstaclePeerDisagreement { scope } => match scope {
                    TrainFaultScope::All => self.peer_disagreement_all = true,
                    TrainFaultScope::Train(t) => {
                        self.peer_disagreement_trains.insert(*t);
                    }
                },
            }
        }
    }

    pub fn pv_factor_for(&self, station: StationId) -> f32 {
        let per_site = self.pv_factor.get(&station).copied().unwrap_or(1.0);
        (per_site * self.global_pv_factor).clamp(0.0, 1.0)
    }

    pub fn grid_disabled_at(&self, station: StationId) -> bool {
        self.global_grid_disabled || self.grid_disabled.contains(&station)
    }

    pub fn pad_disabled_at(&self, station: StationId) -> bool {
        self.pad_disabled.contains(&station)
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
}

fn describe_kind(kind: &FaultKind) -> String {
    match kind {
        FaultKind::DustEvent { pv_output_factor, scope } => {
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
            100, 200,
            FaultKind::GridOutage { scope: FaultScope::All },
        )]);
        eng.tick(50);
        assert!(!eng.grid_disabled_at(StationId::new(1)));
        eng.tick(250);
        assert!(!eng.grid_disabled_at(StationId::new(1)));
    }

    #[test]
    fn active_in_window() {
        let mut eng = FaultEngine::new(vec![mk(
            100, 200,
            FaultKind::GridOutage { scope: FaultScope::All },
        )]);
        eng.tick(150);
        assert!(eng.grid_disabled_at(StationId::new(1)));
    }

    #[test]
    fn dust_event_scales_pv() {
        let station = StationId::new(42);
        let mut eng = FaultEngine::new(vec![mk(
            0, 1000,
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
            0, 1000,
            FaultKind::ChargingPadOutage { station: s },
        )]);
        eng.tick(500);
        assert!(eng.pad_disabled_at(s));
        assert!(!eng.pad_disabled_at(other));
    }

    #[test]
    fn fault_log_records_first_firing_only() {
        let mut eng = FaultEngine::new(vec![mk(
            0, 1000,
            FaultKind::GridOutage { scope: FaultScope::All },
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
            FaultKind::LidarOffline { scope: TrainFaultScope::All },
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
            FaultKind::LidarOffline { scope: TrainFaultScope::Train(target) },
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
        assert_eq!(eng.ultrasonic_stale_mask_for(TrainId::new(99)) & 0b0010, 0b0010);
    }

    #[test]
    fn peer_disagreement_per_train() {
        let a = TrainId::new(1);
        let b = TrainId::new(2);
        let mut eng = FaultEngine::new(vec![mk(
            100,
            200,
            FaultKind::ObstaclePeerDisagreement { scope: TrainFaultScope::Train(a) },
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
    fn multiple_dust_events_compose_multiplicatively() {
        let mut eng = FaultEngine::new(vec![
            mk(0, 1000, FaultKind::DustEvent {
                pv_output_factor: 0.5,
                scope: FaultScope::All,
            }),
            mk(0, 1000, FaultKind::DustEvent {
                pv_output_factor: 0.5,
                scope: FaultScope::All,
            }),
        ]);
        eng.tick(500);
        assert!((eng.pv_factor_for(StationId::new(1)) - 0.25).abs() < 1e-6);
    }
}
