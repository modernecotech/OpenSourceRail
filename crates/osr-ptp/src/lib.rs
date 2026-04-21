//! OpenSourceRail IEEE 1588 (PTPv2) offset + path-delay tracker.
//!
//! PTP in OpenSourceRail is shared by the onboard TSN trainbus and
//! the wayside W-SBCs; this crate is the pure-function core of the
//! slave-side state machine, with the wire-protocol side deferred
//! to a follow-up (there is no real network here yet). Given the
//! four timestamps of a Sync / Follow-Up / Delay-Req / Delay-Resp
//! exchange:
//!
//! ```text
//!     master                                slave
//!       │ t1 ─────── Sync ───────────►  t2
//!       │     (Follow-Up carries t1)
//!       │
//!       │ t4 ◄───── Delay-Req ────── t3
//!       │ ──────── Delay-Resp ─────►
//!                       (carries t4)
//! ```
//!
//! The classical estimator is
//!
//! ```text
//!     offset     = ((t2 − t1) − (t4 − t3)) / 2
//!     path_delay = ((t2 − t1) + (t4 − t3)) / 2
//! ```
//!
//! Negative offsets mean the slave is *ahead* of master; positive
//! means behind. All timestamps are signed nanoseconds since some
//! common epoch (TAI is intended but the math is epoch-agnostic).
//!
//! Phase 2f infrastructure crate per
//! [RFC 0005 §4.5](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 — loss of time sync degrades TSN determinism and trips the
//! `grace_ns` watchdog in consumers (like `osr-tcn`), but does not
//! directly command the brake.
//!
//! # Properties (proptest-verified)
//!
//! - **PT1 determinism.**
//! - **PT2 zero-offset case:** if the slave clock is already
//!   perfectly synced and the path is symmetric, the estimator
//!   returns `offset = 0`.
//! - **PT3 path delay is non-negative** (any negative result is a
//!   protocol error and gets clamped to 0).
//! - **PT4 lock transitions:** a slave holds Locked while samples
//!   stay within `lock_threshold_ns`, and drops out when they don't.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

/// One complete four-timestamp measurement from a PTP exchange.
/// All fields are `i64` nanoseconds; negative is permitted so the
/// caller does not have to pre-align epochs.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PtpSample {
    pub t1_master_tx_ns: i64,
    pub t2_slave_rx_ns: i64,
    pub t3_slave_tx_ns: i64,
    pub t4_master_rx_ns: i64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PtpParams {
    /// |offset| below this means the slave is considered Locked.
    pub lock_threshold_ns: i64,
    /// After this many consecutive in-range samples, declare Locked.
    pub lock_streak: u16,
    /// After this many consecutive out-of-range samples, declare
    /// FreeRunning.
    pub unlock_streak: u16,
}

impl PtpParams {
    #[must_use]
    pub fn default_trackside() -> Self {
        Self {
            lock_threshold_ns: 1_000, // 1 µs
            lock_streak: 4,
            unlock_streak: 3,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum LockState {
    #[default]
    FreeRunning,
    Acquiring,
    Locked,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct PtpState {
    pub lock: LockState,
    pub in_streak: u16,
    pub out_streak: u16,
    pub last_offset_ns: i64,
    pub last_path_delay_ns: i64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PtpOutput {
    pub state: PtpState,
    pub offset_ns: i64,
    pub path_delay_ns: i64,
}

/// Estimate `(offset, path_delay)` from the four-timestamp sample.
/// Path delay is clamped to ≥ 0 because a negative value means the
/// network path is asymmetric beyond PTP's ability to model.
#[must_use]
pub fn estimate(sample: &PtpSample) -> (i64, i64) {
    let master_to_slave = sample.t2_slave_rx_ns.saturating_sub(sample.t1_master_tx_ns);
    let slave_to_master = sample.t4_master_rx_ns.saturating_sub(sample.t3_slave_tx_ns);
    let offset = master_to_slave.saturating_sub(slave_to_master) / 2;
    let raw_delay = master_to_slave.saturating_add(slave_to_master) / 2;
    let delay = raw_delay.max(0);
    (offset, delay)
}

/// Advance the slave state machine with one sample.
#[must_use]
pub fn ptp_update(prev: &PtpState, sample: &PtpSample, params: &PtpParams) -> PtpOutput {
    let (offset, path_delay_ns) = estimate(sample);
    let in_range = offset.abs() <= params.lock_threshold_ns;

    let mut state = *prev;
    state.last_offset_ns = offset;
    state.last_path_delay_ns = path_delay_ns;

    if in_range {
        state.in_streak = state.in_streak.saturating_add(1);
        state.out_streak = 0;
        if state.in_streak >= params.lock_streak {
            state.lock = LockState::Locked;
        } else if state.lock == LockState::FreeRunning {
            state.lock = LockState::Acquiring;
        }
    } else {
        state.out_streak = state.out_streak.saturating_add(1);
        state.in_streak = 0;
        if state.out_streak >= params.unlock_streak {
            state.lock = LockState::FreeRunning;
        }
    }

    PtpOutput { state, offset_ns: offset, path_delay_ns }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn perfect_sample() -> PtpSample {
        // Symmetric path delay of 500 ns, zero offset.
        PtpSample {
            t1_master_tx_ns: 0,
            t2_slave_rx_ns: 500,
            t3_slave_tx_ns: 1_000,
            t4_master_rx_ns: 1_500,
        }
    }

    #[test]
    fn perfect_sample_yields_zero_offset() {
        let (offset, delay) = estimate(&perfect_sample());
        assert_eq!(offset, 0);
        assert_eq!(delay, 500);
    }

    #[test]
    fn slave_ahead_by_100ns() {
        // Slave clock is 100 ns ahead → t2 and t3 stamps are 100 ns earlier.
        let s = PtpSample {
            t1_master_tx_ns: 0,
            t2_slave_rx_ns: 400,
            t3_slave_tx_ns: 900,
            t4_master_rx_ns: 1_500,
        };
        let (offset, _) = estimate(&s);
        assert_eq!(offset, -100);
    }

    #[test]
    fn slave_behind_by_100ns() {
        let s = PtpSample {
            t1_master_tx_ns: 0,
            t2_slave_rx_ns: 600,
            t3_slave_tx_ns: 1_100,
            t4_master_rx_ns: 1_500,
        };
        let (offset, _) = estimate(&s);
        assert_eq!(offset, 100);
    }

    #[test]
    fn lock_transitions_up_then_down() {
        let p = PtpParams { lock_threshold_ns: 50, lock_streak: 3, unlock_streak: 2 };
        let mut st = PtpState::default();
        // Feed 3 good samples → Locked
        for _ in 0..3 {
            let o = ptp_update(&st, &perfect_sample(), &p);
            st = o.state;
        }
        assert_eq!(st.lock, LockState::Locked);

        // Feed 2 bad samples → back to FreeRunning
        let bad = PtpSample {
            t1_master_tx_ns: 0,
            t2_slave_rx_ns: 10_000, // wildly asymmetric
            t3_slave_tx_ns: 10_000,
            t4_master_rx_ns: 11_000,
        };
        for _ in 0..2 {
            let o = ptp_update(&st, &bad, &p);
            st = o.state;
        }
        assert_eq!(st.lock, LockState::FreeRunning);
    }

    #[test]
    fn determinism() {
        let p = PtpParams::default_trackside();
        let a = ptp_update(&PtpState::default(), &perfect_sample(), &p);
        let b = ptp_update(&PtpState::default(), &perfect_sample(), &p);
        assert_eq!(a, b);
    }
}
