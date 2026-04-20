//! Continuously run the `osr-interlocking` Movement Authority computer
//! against the running simulation and verify consistency.
//!
//! This is M5 of [RFC 0004](../../../docs/rfcs/0004-osr-interlocking-plan.md):
//! the MA computer (proven pure in M1 and structurally correct in M2)
//! is wired into `osr-sim` so that every scenario run continuously
//! produces MA outputs that can be checked against the sim's own
//! ground-truth state.
//!
//! Integration model (v1 — additive, not replacing):
//! - The sim continues to manage an `OccupancyMap` for its own operation.
//! - In parallel, it synthesizes a log of `Entry` objects as trains
//!   move (registration on first encounter, position report on each
//!   section change).
//! - Periodically, it computes each train's MA from that log and
//!   records any cases where the MA-covered sections conflict with
//!   the sim's occupancy — a cross-check that reveals bugs in either
//!   the MA computer or the sim's state tracking.
//!
//! Later milestones may replace the sim's `OccupancyMap` entirely with
//! the MA-derived state. For now this is shadow-mode verification.

use osr_core::topology::OccupancyMap;
use osr_core::{
    ConsistDescriptor, Direction, EntryId, Network, Position, SectionId, TrackRef, TrainId,
};
use osr_interlocking::log::{
    Entry, EntryPayload, PositionSource, TrainPositionReport, TrainRegistration,
};
use osr_interlocking::{
    compute_self_ma_from_state, derive_state, forward_chain, DerivedState, MovementAuthority,
    MAX_MA_DISTANCE_MM,
};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};

use crate::train::{Train, TrainPhase};

/// One summary record of an MA check tick.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct MaCheckSummary {
    /// Number of check ticks executed (every `ma_check_every_s` sim-seconds).
    pub checks_run: u32,
    /// Total MAs computed across all checks (checks × trains).
    pub total_mas_computed: u32,
    /// MAs where `has_known_position` was false — fail-restrictive outputs.
    pub fail_restrictive_mas: u32,
    /// Any consistency violations surfaced by the check.
    pub violations: Vec<MaConsistencyViolation>,
}

/// A consistency violation between the MA computer's output and the sim's
/// own occupancy record. Either direction signals a bug.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MaConsistencyViolation {
    pub sim_time_s: u32,
    pub train: String,
    /// Section the MA purported to grant.
    pub granted_section: String,
    /// Sim-observed occupant of that section.
    pub actually_occupied_by: String,
}

/// Internal log that `osr-sim` builds up as trains move, feeding the MA
/// computer. One entry per phase transition, plus initial registration
/// per train.
#[derive(Debug, Default)]
pub struct SimulatedLog {
    entries: Vec<Entry>,
    /// Trains that have a registration entry in the log. We only emit a
    /// registration once per train-id; subsequent activity goes into
    /// position reports.
    registered: BTreeSet<TrainId>,
    next_entry_id: u64,
}

impl SimulatedLog {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
            registered: BTreeSet::new(),
            next_entry_id: 1,
        }
    }

    pub fn entries(&self) -> &[Entry] {
        &self.entries
    }

    /// Register a train if this is the first time we've seen it.
    pub fn ensure_registered(&mut self, train: &Train, initial_head: TrackRef, t_s: u32) {
        if self.registered.insert(train.id) {
            let ts_ns = Self::ts_ns_from_s(t_s);
            self.append(EntryPayload::TrainRegistration(TrainRegistration {
                train_id: train.id,
                consist: train.consist.clone(),
                initial_position: Position {
                    track_ref: initial_head,
                    uncertainty_mm: 0,
                },
            }), ts_ns);
        }
    }

    /// Emit a position report for a train currently on section `head_section`.
    /// Head offset is `head_offset_mm`; tail is derived from consist length.
    pub fn emit_position(
        &mut self,
        train: &Train,
        head: TrackRef,
        tail_offset_in_head_section: Option<i64>,
        t_s: u32,
    ) {
        let tail_position = match tail_offset_in_head_section {
            Some(off) => Position {
                track_ref: TrackRef {
                    section: head.section,
                    offset_mm: off.max(0),
                    direction: head.direction,
                },
                uncertainty_mm: 0,
            },
            None => {
                // Simplified: place tail at head offset minus consist length,
                // clamping to 0 (a more accurate computation would walk
                // backward through the previous section).
                let tail_off = head.offset_mm.saturating_sub(train.consist.length_mm as i64);
                Position {
                    track_ref: TrackRef {
                        section: head.section,
                        offset_mm: tail_off.max(0),
                        direction: head.direction,
                    },
                    uncertainty_mm: 0,
                }
            }
        };

        let ts_ns = Self::ts_ns_from_s(t_s);
        self.append(
            EntryPayload::TrainPositionReport(TrainPositionReport {
                train_id: train.id,
                head_position: Position {
                    track_ref: head,
                    uncertainty_mm: 0,
                },
                tail_position,
                speed_mmps: 15_000, // 15 m/s cruise — placeholder, kinematic model could inform
                speed_uncertainty_mmps: 500,
                heading: head.direction,
                contributing_sources: vec![PositionSource::Gnss, PositionSource::Odometry],
                onboard_time_ns: ts_ns.saturating_sub(100),
                pack_soc_ppt: (train.soc.clamp(0.0, 1.0) * 1000.0) as u16,
            }),
            ts_ns,
        );
    }

    fn append(&mut self, payload: EntryPayload, ts_ns: u64) {
        let entry = Entry {
            entry_id: EntryId::new(self.next_entry_id),
            term: 1,
            timestamp_ns: ts_ns,
            payload,
        };
        self.next_entry_id += 1;
        self.entries.push(entry);
    }

    fn ts_ns_from_s(t_s: u32) -> u64 {
        (t_s as u64).saturating_mul(1_000_000_000)
    }
}

// ---------------------------------------------------------------------------
// MA consistency checker
// ---------------------------------------------------------------------------

/// Compute every train's MA from the simulated log and check that each MA
/// is consistent with the sim's own occupancy ground truth.
pub fn run_check(
    trains: &[Train],
    log: &SimulatedLog,
    network: &Network,
    occupancy: &OccupancyMap,
    sim_time_s: u32,
    summary: &mut MaCheckSummary,
) {
    summary.checks_run = summary.checks_run.saturating_add(1);
    let state: DerivedState = derive_state(log.entries());
    let now_ns = (sim_time_s as u64).saturating_mul(1_000_000_000);

    // Each train's footprint from its awareness.
    let footprints: BTreeMap<TrainId, BTreeSet<SectionId>> = state
        .trains
        .iter()
        .map(|(&tid, aware)| {
            let head = aware.last_head_position.map(|p| p.track_ref);
            let sections: BTreeSet<SectionId> = match head {
                Some(h) => osr_interlocking::footprint_from(network, h, aware.consist.length_mm)
                    .into_iter()
                    .collect(),
                None => BTreeSet::new(),
            };
            (tid, sections)
        })
        .collect();

    for train in trains {
        let ma: MovementAuthority = compute_self_ma_from_state(
            train.id,
            &state,
            network,
            now_ns,
            log.entries().last().map(|e| e.entry_id),
        );
        summary.total_mas_computed = summary.total_mas_computed.saturating_add(1);
        if !ma.has_known_position {
            summary.fail_restrictive_mas =
                summary.fail_restrictive_mas.saturating_add(1);
            continue;
        }

        // The MA covers sections from the train's head to the MA end.
        let head = match state.trains.get(&train.id).and_then(|a| a.last_head_position) {
            Some(p) => p.track_ref,
            None => continue,
        };
        // Chain from head spans the MA. Clip it to the end section.
        let chain = forward_chain(network, head, MAX_MA_DISTANCE_MM);
        let mut ma_covered: BTreeSet<SectionId> = BTreeSet::new();
        for s in &chain {
            ma_covered.insert(*s);
            if *s == ma.end.section {
                break;
            }
        }

        // Subtract the train's own footprint — those are its own sections
        // by definition.
        let own_footprint = footprints.get(&train.id).cloned().unwrap_or_default();

        for sec in ma_covered.difference(&own_footprint) {
            if let Some(occupant) = occupancy.occupant(*sec) {
                if occupant != train.id {
                    summary.violations.push(MaConsistencyViolation {
                        sim_time_s,
                        train: train.id.to_string(),
                        granted_section: sec.to_string(),
                        actually_occupied_by: occupant.to_string(),
                    });
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Translation helpers — sim phase to TrackRef
// ---------------------------------------------------------------------------

/// Best-effort TrackRef for a train given its current phase and heading.
/// Returns None if the phase provides insufficient information (rare —
/// only happens when a dwelling train is at a terminal with no outgoing
/// section in its heading, which is handled elsewhere).
pub fn trackref_for(
    train: &Train,
    network: &Network,
) -> Option<TrackRef> {
    match &train.phase {
        TrainPhase::Traveling { section, .. } => Some(TrackRef {
            section: *section,
            offset_mm: 0, // sim doesn't track in-section offset; use 0 (conservative)
            direction: direction_for_section(*section, network)?,
        }),
        TrainPhase::Dwelling { station, .. }
        | TrainPhase::AwaitingDispatch { station } => {
            // Find the section the train will depart onto next.
            let line = &network.lines[train.line_index];
            let station_idx = line.stations.iter().position(|s| *s == *station)?;
            use crate::train::Heading;
            let (array, target_idx) = match train.heading {
                Heading::Forward => (&line.forward_sections, station_idx),
                Heading::Reverse => (&line.reverse_sections, station_idx.checked_sub(1)?),
            };
            if target_idx >= array.len() {
                return None;
            }
            let section = array[target_idx];
            Some(TrackRef {
                section,
                offset_mm: 0,
                direction: direction_for_section(section, network)?,
            })
        }
    }
}

fn direction_for_section(section: SectionId, network: &Network) -> Option<Direction> {
    for line in &network.lines {
        if line.forward_sections.contains(&section) {
            return Some(Direction::Forward);
        }
        if line.reverse_sections.contains(&section) {
            return Some(Direction::Reverse);
        }
    }
    None
}

/// Suppress the unused warning on ConsistDescriptor import in this file.
#[allow(dead_code)]
fn _ensure_unused_imports_compile(_: ConsistDescriptor) {}
