//! Scenario-declared fault injection.
//!
//! Three kinds of fault are supported in v1:
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
//! Faults are declared in the scenario TOML under `[[faults]]`; see
//! `scenarios/README.md` for the format.

use osr_core::StationId;
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
                        // Compose multiple simultaneous global dust events
                        // multiplicatively.
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
