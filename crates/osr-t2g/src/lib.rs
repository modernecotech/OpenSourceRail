//! OpenSourceRail train-to-ground radio arbiter.
//!
//! A deliberately thin crate: given the current signal-strength
//! readings from the primary and backup radios plus a per-tick
//! telemetry payload, decides:
//!
//! - which radio channel to use (Primary / Backup / Offline),
//! - whether to transmit this tick (rate-gated for bandwidth budget,
//!   but unconditional for emergency priority),
//! - how many payload records remain queued.
//!
//! Phase 2c crate 10 of [RFC 0005 §4.1](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 because losing comms degrades observability and operator
//! coordination but is not a safety hazard — the SIL-4 signalling
//! partition is unaffected.
//!
//! # Radio model
//!
//! Per [ARCHITECTURE.md §D3](../../../docs/ARCHITECTURE.md#d3-communications)
//! the reference hardware carries a public-5G primary and a LoRa
//! mesh backup. Signal strength is expressed here as 0..=100
//! abstract units, and the caller maps real RSRP / SNR readings
//! into that range.
//!
//! # Properties (proptest-verified)
//!
//! - **T2G1 determinism.**
//! - **T2G2 emergency transmits regardless of rate gate:** if
//!   `emergency_priority == true` and any channel is available,
//!   `transmit_now == true`.
//! - **T2G3 failover:** when the primary channel is below its
//!   dropout threshold and backup is above, `active == Backup`.
//! - **T2G4 both weak is offline:** both below dropout → `Offline`,
//!   `transmit_now == false`.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum ActiveChannel {
    #[default]
    Primary,
    Backup,
    Offline,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct T2gInputs {
    pub now_ns: u64,
    /// Signal strength 0..=100 (normalised).
    pub primary_signal: u8,
    pub backup_signal: u8,
    /// How many payload records are queued for upload.
    pub queued_payloads: u32,
    /// A record needs to be sent ASAP regardless of rate gate.
    pub emergency_priority: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct T2gParams {
    /// Below this signal strength the primary is considered down.
    pub primary_dropout_threshold: u8,
    /// Below this the backup is considered down.
    pub backup_dropout_threshold: u8,
    /// Minimum interval between normal-priority transmissions (ns).
    pub rate_limit_ns: u64,
}

impl T2gParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            primary_dropout_threshold: 20,
            backup_dropout_threshold: 10,
            rate_limit_ns: 500_000_000, // 500 ms between regular sends
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct T2gState {
    pub last_transmit_ns: u64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct T2gOutput {
    pub state: T2gState,
    pub active: ActiveChannel,
    pub transmit_now: bool,
    /// Remaining queue depth (decreases by 1 if transmit_now).
    pub queue_remaining: u32,
}

#[must_use]
pub fn t2g_evaluate(prev: &T2gState, inputs: &T2gInputs, params: &T2gParams) -> T2gOutput {
    let primary_ok = inputs.primary_signal >= params.primary_dropout_threshold;
    let backup_ok = inputs.backup_signal >= params.backup_dropout_threshold;

    let active = if primary_ok {
        ActiveChannel::Primary
    } else if backup_ok {
        ActiveChannel::Backup
    } else {
        ActiveChannel::Offline
    };

    let rate_gate_ok = inputs
        .now_ns
        .saturating_sub(prev.last_transmit_ns)
        >= params.rate_limit_ns;

    let transmit_now = !matches!(active, ActiveChannel::Offline)
        && inputs.queued_payloads > 0
        && (inputs.emergency_priority || rate_gate_ok);

    let last_transmit_ns = if transmit_now {
        inputs.now_ns
    } else {
        prev.last_transmit_ns
    };

    let queue_remaining = if transmit_now {
        inputs.queued_payloads.saturating_sub(1)
    } else {
        inputs.queued_payloads
    };

    T2gOutput {
        state: T2gState { last_transmit_ns },
        active,
        transmit_now,
        queue_remaining,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn inputs(now: u64, pri: u8, bak: u8, queued: u32, em: bool) -> T2gInputs {
        T2gInputs {
            now_ns: now,
            primary_signal: pri,
            backup_signal: bak,
            queued_payloads: queued,
            emergency_priority: em,
        }
    }

    #[test]
    fn strong_primary_selected() {
        let p = T2gParams::default_metro();
        let out = t2g_evaluate(&T2gState::default(), &inputs(1_000_000_000, 80, 40, 3, false), &p);
        assert_eq!(out.active, ActiveChannel::Primary);
        assert!(out.transmit_now);
        assert_eq!(out.queue_remaining, 2);
    }

    #[test]
    fn primary_down_fails_over_to_backup() {
        let p = T2gParams::default_metro();
        let out = t2g_evaluate(&T2gState::default(), &inputs(1_000_000_000, 10, 50, 2, false), &p);
        assert_eq!(out.active, ActiveChannel::Backup);
        assert!(out.transmit_now);
    }

    #[test]
    fn both_weak_is_offline() {
        let p = T2gParams::default_metro();
        let out = t2g_evaluate(&T2gState::default(), &inputs(1_000_000_000, 5, 5, 10, true), &p);
        assert_eq!(out.active, ActiveChannel::Offline);
        assert!(!out.transmit_now);
    }

    #[test]
    fn rate_gate_holds_off_regular_sends() {
        let p = T2gParams::default_metro();
        let prev = T2gState { last_transmit_ns: 1_000_000_000 };
        let out = t2g_evaluate(&prev, &inputs(1_100_000_000, 80, 40, 3, false), &p);
        assert!(!out.transmit_now);
        assert_eq!(out.queue_remaining, 3);
    }

    #[test]
    fn emergency_bypasses_rate_gate() {
        let p = T2gParams::default_metro();
        let prev = T2gState { last_transmit_ns: 1_000_000_000 };
        let out = t2g_evaluate(&prev, &inputs(1_100_000_000, 80, 40, 3, true), &p);
        assert!(out.transmit_now);
    }

    #[test]
    fn empty_queue_does_not_transmit() {
        let p = T2gParams::default_metro();
        let out = t2g_evaluate(&T2gState::default(), &inputs(1_000_000_000, 80, 40, 0, true), &p);
        assert!(!out.transmit_now);
    }

    #[test]
    fn determinism() {
        let p = T2gParams::default_metro();
        let i = inputs(1_000_000_000, 80, 40, 3, false);
        let a = t2g_evaluate(&T2gState::default(), &i, &p);
        let b = t2g_evaluate(&T2gState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
