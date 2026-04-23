//! The `osr-interlocking` Movement Authority computer, wired into
//! `osr-sim` as the authoritative source of train occupancy.
//!
//! This is M5 of [RFC 0004](../../../docs/rfcs/0004-osr-interlocking-plan.md):
//! the sim no longer keeps its own `OccupancyMap`. Every time a train
//! enters a new section, the sim:
//! 1. asks the MA computer whether the section is available for this
//!    train (via `osr_interlocking::section_available_to`),
//! 2. if yes, emits a `TrainPositionReport` entry into the log so the
//!    derived state now records this train as the section's occupant.
//!
//! Conflicts surface as real `InvariantViolation`s — a train never
//! enters a section another train holds because the gate refuses it.
//!
//! A periodic fleet-wide MA sweep (`ma_check_every_s`) populates
//! health stats (checks run, MAs computed, fail-restrictive count) so
//! the run report can report MA-computer behaviour even though the
//! computer is always on.

use osr_core::{EntityId, EntryId, Network, Position, SectionId, TrackRef, TrainId};
use osr_interlocking::log::{
    Entry, EntryPayload, IntrusionState, PositionSource, SectionIntrusion, TrainPositionReport,
    TrainRegistration,
};
use osr_interlocking::{compute_self_ma_from_state, DerivedState, MovementAuthority};
use serde::{Deserialize, Serialize};
use std::collections::BTreeSet;

use crate::train::Train;

/// Summary of the MA-computer integration over a sim run.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct MaCheckSummary {
    /// Number of fleet-wide MA sweeps executed (every `ma_check_every_s`
    /// sim-seconds). Each sweep computes an MA for every train.
    pub checks_run: u32,
    /// Total MAs computed across all sweeps (sweeps × trains). Does not
    /// count the per-tick gate checks, which use `section_available_to`
    /// directly rather than computing a full MA.
    pub total_mas_computed: u32,
    /// MAs where `has_known_position` was false — fail-restrictive outputs.
    /// Expected to spike briefly at startup (before the first position
    /// report lands) and stay at zero during steady service.
    pub fail_restrictive_mas: u32,
}

/// Internal log that `osr-sim` builds up as trains move, feeding the MA
/// computer. One entry per section change, plus initial registration
/// per train. Maintains a cached `DerivedState` updated incrementally
/// on each append so per-tick gate checks are O(1) in log length.
#[derive(Debug, Default)]
pub struct SimulatedLog {
    entries: Vec<Entry>,
    /// Trains that have a registration entry in the log. We only emit a
    /// registration once per train-id; subsequent activity goes into
    /// position reports.
    registered: BTreeSet<TrainId>,
    next_entry_id: u64,
    /// Cached fold of `entries`. Updated on every append, so callers can
    /// read it without rederiving.
    state: DerivedState,
}

impl SimulatedLog {
    pub fn new() -> Self {
        Self {
            entries: Vec::new(),
            registered: BTreeSet::new(),
            next_entry_id: 1,
            state: DerivedState::default(),
        }
    }

    pub fn entries(&self) -> &[Entry] {
        &self.entries
    }

    /// Cached derived state — kept in sync with `entries` on every append.
    pub fn derived_state(&self) -> &DerivedState {
        &self.state
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

    /// Emit a `SectionIntrusion` consensus entry carrying a wayside
    /// intrusion verdict for one section (RFC 0016 v3). Called from
    /// the sim tick when the fault engine has an active
    /// `WaysideIntrusion` fault.
    pub fn emit_intrusion(
        &mut self,
        section: SectionId,
        state: IntrusionState,
        issued_by: EntityId,
        t_s: u32,
    ) {
        let ts = Self::ts_ns_from_s(t_s);
        self.append(
            EntryPayload::SectionIntrusion(SectionIntrusion {
                section,
                state,
                issued_by,
                observed_at_ns: ts,
            }),
            ts,
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
        self.state.apply(&entry);
        self.entries.push(entry);
    }

    fn ts_ns_from_s(t_s: u32) -> u64 {
        (t_s as u64).saturating_mul(1_000_000_000)
    }
}

// ---------------------------------------------------------------------------
// MA fleet-wide health sweep
// ---------------------------------------------------------------------------

/// Compute every train's MA from the given derived state and update
/// the run-wide summary (checks run, MAs computed, fail-restrictive count).
///
/// Unlike the pre-M5 version this does not cross-check against an
/// `OccupancyMap` — occupancy is now owned by the MA computer itself, so
/// any cross-check would be tautological. The sweep's purpose is purely
/// telemetry: did each train produce a valid MA at this sampling point?
pub fn run_check_state(
    trains: &[Train],
    state: &DerivedState,
    network: &Network,
    derived_from: Option<EntryId>,
    sim_time_s: u32,
    summary: &mut MaCheckSummary,
) {
    summary.checks_run = summary.checks_run.saturating_add(1);
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);

    for train in trains {
        let ma: MovementAuthority =
            compute_self_ma_from_state(train.id, state, network, now_ns, derived_from);
        summary.total_mas_computed = summary.total_mas_computed.saturating_add(1);
        if !ma.has_known_position {
            summary.fail_restrictive_mas = summary.fail_restrictive_mas.saturating_add(1);
        }
    }
}

