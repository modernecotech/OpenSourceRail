//! Deterministic IEEE 1588 clock-lock integration.
//!
//! The simulator feeds the real `osr-ptp` slave state machine a symmetric
//! trackside exchange once per simulation tick. This proves acquisition and
//! lock behavior without pretending to model production Ethernet hardware.

use osr_ptp::{ptp_update, LockState, PtpParams, PtpSample, PtpState};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug)]
pub struct TimeSyncShadow {
    state: PtpState,
    params: PtpParams,
    summary: TimeSyncSummary,
}

impl Default for TimeSyncShadow {
    fn default() -> Self {
        Self {
            state: PtpState::default(),
            params: PtpParams::default_trackside(),
            summary: TimeSyncSummary::default(),
        }
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct TimeSyncSummary {
    pub controller_ticks: u64,
    pub acquiring_ticks: u64,
    pub locked_ticks: u64,
    pub free_running_ticks: u64,
    pub lock_transitions: u64,
    pub maximum_absolute_offset_ns: u64,
    pub maximum_path_delay_ns: u64,
    pub final_lock_state: String,
}

pub fn time_sync_tick(shadow: &mut TimeSyncShadow, sim_time_s: u32) {
    let base_ns = i64::from(sim_time_s).saturating_mul(1_000_000_000);
    let sample = PtpSample {
        t1_master_tx_ns: base_ns,
        t2_slave_rx_ns: base_ns.saturating_add(500),
        t3_slave_tx_ns: base_ns.saturating_add(1_000),
        t4_master_rx_ns: base_ns.saturating_add(1_500),
    };
    let previous_lock = shadow.state.lock;
    let output = ptp_update(&shadow.state, &sample, &shadow.params);
    shadow.state = output.state;

    shadow.summary.controller_ticks = shadow.summary.controller_ticks.saturating_add(1);
    match output.state.lock {
        LockState::Acquiring => {
            shadow.summary.acquiring_ticks = shadow.summary.acquiring_ticks.saturating_add(1);
        }
        LockState::Locked => {
            shadow.summary.locked_ticks = shadow.summary.locked_ticks.saturating_add(1);
        }
        LockState::FreeRunning => {
            shadow.summary.free_running_ticks = shadow.summary.free_running_ticks.saturating_add(1);
        }
    }
    if output.state.lock != previous_lock {
        shadow.summary.lock_transitions = shadow.summary.lock_transitions.saturating_add(1);
    }
    shadow.summary.maximum_absolute_offset_ns = shadow
        .summary
        .maximum_absolute_offset_ns
        .max(output.offset_ns.unsigned_abs());
    shadow.summary.maximum_path_delay_ns = shadow
        .summary
        .maximum_path_delay_ns
        .max(output.path_delay_ns.unsigned_abs());
    shadow.summary.final_lock_state = format!("{:?}", output.state.lock);
}

#[must_use]
pub fn summarise(shadow: &TimeSyncShadow) -> TimeSyncSummary {
    shadow.summary.clone()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deterministic_exchange_acquires_and_holds_lock() {
        let mut first = TimeSyncShadow::default();
        let mut second = TimeSyncShadow::default();
        for tick in 0..6 {
            time_sync_tick(&mut first, tick);
            time_sync_tick(&mut second, tick);
        }
        let summary = summarise(&first);
        assert_eq!(summary, summarise(&second));
        assert_eq!(summary.controller_ticks, 6);
        assert_eq!(summary.acquiring_ticks, 3);
        assert_eq!(summary.locked_ticks, 3);
        assert_eq!(summary.lock_transitions, 2);
        assert_eq!(summary.maximum_absolute_offset_ns, 0);
        assert_eq!(summary.maximum_path_delay_ns, 500);
        assert_eq!(summary.final_lock_state, "Locked");
    }
}
