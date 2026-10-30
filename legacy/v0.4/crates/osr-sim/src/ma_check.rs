//! Movement-authority health checks for the consensus-backed simulator.
//!
//! Train occupancy is derived from committed track-state entries. A periodic
//! fleet sweep computes every train's movement authority and records whether
//! any result had to fail restrictively because its position was unknown.

use osr_core::{EntryId, Network};
use osr_interlocking::{compute_self_ma_from_state, DerivedState, MovementAuthority};
use serde::{Deserialize, Serialize};

use crate::train::Train;

/// Summary of movement-authority checks over one simulation run.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct MaCheckSummary {
    /// Number of fleet-wide sweeps executed.
    pub checks_run: u32,
    /// Total movement authorities computed across all sweeps.
    pub total_mas_computed: u32,
    /// Authorities that failed restrictively because position was unknown.
    pub fail_restrictive_mas: u32,
}

/// Compute every train's authority from committed state and update health
/// counters. Per-tick section entry gates use `section_available_to` directly.
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
