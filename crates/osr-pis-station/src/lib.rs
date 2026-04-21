//! OpenSourceRail station Passenger Information System.
//!
//! Station-side counterpart to [`osr_pis_onboard`]. Takes the next
//! N train arrivals, the time-of-day, and any emergency /
//! maintenance broadcast, and produces:
//!
//! - a **next-arrivals board** listing (top N trains with ETA
//!   badges like "Approaching" / "N min" / "Delayed"),
//! - per-direction **platform audio** announcement commands
//!   (approaching chime / arrival message / departing whistle),
//! - a station-wide **alert broadcast** channel (operator messages,
//!   delays, emergencies).
//!
//! Phase 2e crate of [RFC 0005 §4.7](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-0: failure degrades passenger experience but does not
//! directly endanger anyone; PA amplifier and CCTV are on the
//! 24 V station rail and have independent hardware backup.
//!
//! # Properties (proptest-verified)
//!
//! - **PS1 determinism.**
//! - **PS2 emergency broadcast dominates:** active emergency →
//!   display mode `Emergency`, audio `EmergencyBroadcast`,
//!   regardless of arrivals.
//! - **PS3 arrivals sorted by ETA ascending.**
//! - **PS4 approach band triggers announcement:** a train with
//!   `eta_s ≤ approach_threshold_s` and not already announced
//!   fires `AudioCue::Approaching` once.
//! - **PS5 ETA rollup caps at `max_entries_shown`** — the board
//!   never displays more lines than configured.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Arrivals
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Direction {
    Forward,
    Reverse,
}

/// A train expected to arrive at the platform.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PendingArrival {
    pub train_id: u32,
    pub line_id: u32,
    pub direction: Direction,
    /// ETA relative to `PisInputs::now_ns`, in seconds.
    pub eta_s: u32,
    /// `true` when the train is inside the station-approach band
    /// (≈ 500 m out or less).
    pub approaching: bool,
}

// ---------------------------------------------------------------------------
// Inputs / params
// ---------------------------------------------------------------------------

#[derive(Clone, Debug)]
pub struct PisStationInputs<'a> {
    pub now_ns: u64,
    /// Sorted or unsorted; the evaluator sorts on output.
    pub pending_arrivals: &'a [PendingArrival],
    /// If set, dominates everything (emergency broadcast).
    pub emergency_code: Option<u16>,
    /// Delay / operator broadcast — shown on the board under the
    /// arrivals list; does not trigger audio on its own.
    pub operator_banner: Option<String>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PisStationParams {
    /// ETA threshold for audio-cueing an "approaching" chime.
    pub approach_threshold_s: u32,
    /// Maximum entries rendered on the board.
    pub max_entries_shown: usize,
}

impl PisStationParams {
    #[must_use]
    pub fn default_metro() -> Self {
        Self {
            approach_threshold_s: 60,
            max_entries_shown: 4,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum PisStationMode {
    #[default]
    Nominal,
    Emergency,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum AudioCue {
    #[default]
    None,
    /// "The next train is approaching platform X." One-shot per train.
    Approaching { train_id: u32 },
    /// Arrival / departure tones could be added; v1 keeps to approach
    /// and emergency.
    EmergencyBroadcast { code: u16 },
}

#[derive(Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct PisStationState {
    /// Train IDs whose approach has already been announced, so we
    /// don't repeat on subsequent ticks.
    pub announced_trains: Vec<u32>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PisStationOutput {
    pub state: PisStationState,
    pub mode: PisStationMode,
    pub board: Vec<PendingArrival>,
    pub operator_banner: Option<String>,
    pub audio_cue: AudioCue,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

#[must_use]
pub fn pis_station_evaluate(
    prev: &PisStationState,
    inputs: &PisStationInputs<'_>,
    params: &PisStationParams,
) -> PisStationOutput {
    if let Some(code) = inputs.emergency_code {
        return PisStationOutput {
            state: prev.clone(),
            mode: PisStationMode::Emergency,
            board: Vec::new(),
            operator_banner: None,
            audio_cue: AudioCue::EmergencyBroadcast { code },
        };
    }

    // Sort by ETA ascending and take top N.
    let mut sorted: Vec<_> = inputs.pending_arrivals.to_vec();
    sorted.sort_by_key(|a| a.eta_s);
    sorted.truncate(params.max_entries_shown);

    // Decide audio cue: first un-announced approaching train.
    let mut audio_cue = AudioCue::None;
    let mut announced_trains = prev.announced_trains.clone();
    for a in &sorted {
        let within_band = a.approaching || a.eta_s <= params.approach_threshold_s;
        if within_band && !announced_trains.contains(&a.train_id) {
            audio_cue = AudioCue::Approaching { train_id: a.train_id };
            announced_trains.push(a.train_id);
            break;
        }
    }
    // Prune announced_trains that are no longer in the pending list.
    let current_ids: Vec<u32> = sorted.iter().map(|a| a.train_id).collect();
    announced_trains.retain(|id| current_ids.contains(id));

    PisStationOutput {
        state: PisStationState { announced_trains },
        mode: PisStationMode::Nominal,
        board: sorted,
        operator_banner: inputs.operator_banner.clone(),
        audio_cue,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn arr(id: u32, eta: u32, approaching: bool) -> PendingArrival {
        PendingArrival {
            train_id: id,
            line_id: 1,
            direction: Direction::Forward,
            eta_s: eta,
            approaching,
        }
    }

    #[test]
    fn empty_board_no_cue() {
        let p = PisStationParams::default_metro();
        let out = pis_station_evaluate(
            &PisStationState::default(),
            &PisStationInputs {
                now_ns: 0,
                pending_arrivals: &[],
                emergency_code: None,
                operator_banner: None,
            },
            &p,
        );
        assert!(out.board.is_empty());
        assert_eq!(out.audio_cue, AudioCue::None);
    }

    #[test]
    fn board_sorts_by_eta() {
        let p = PisStationParams::default_metro();
        let arrivals = vec![arr(3, 300, false), arr(1, 60, false), arr(2, 120, false)];
        let out = pis_station_evaluate(
            &PisStationState::default(),
            &PisStationInputs {
                now_ns: 0,
                pending_arrivals: &arrivals,
                emergency_code: None,
                operator_banner: None,
            },
            &p,
        );
        assert_eq!(
            out.board.iter().map(|a| a.train_id).collect::<Vec<_>>(),
            vec![1, 2, 3]
        );
    }

    #[test]
    fn emergency_broadcast_dominates() {
        let p = PisStationParams::default_metro();
        let arrivals = vec![arr(1, 30, true)];
        let out = pis_station_evaluate(
            &PisStationState::default(),
            &PisStationInputs {
                now_ns: 0,
                pending_arrivals: &arrivals,
                emergency_code: Some(7),
                operator_banner: None,
            },
            &p,
        );
        assert_eq!(out.mode, PisStationMode::Emergency);
        assert!(out.board.is_empty());
        assert_eq!(out.audio_cue, AudioCue::EmergencyBroadcast { code: 7 });
    }

    #[test]
    fn approach_cue_fires_once_per_train() {
        let p = PisStationParams::default_metro();
        let arrivals = vec![arr(42, 30, true)];
        let inputs = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: None,
            operator_banner: None,
        };
        let first = pis_station_evaluate(&PisStationState::default(), &inputs, &p);
        assert_eq!(first.audio_cue, AudioCue::Approaching { train_id: 42 });
        let second = pis_station_evaluate(&first.state, &inputs, &p);
        assert_eq!(second.audio_cue, AudioCue::None);
    }

    #[test]
    fn board_truncates_to_max_entries() {
        let p = PisStationParams::default_metro();
        let arrivals: Vec<_> = (0..10).map(|i| arr(i, i * 60, false)).collect();
        let out = pis_station_evaluate(
            &PisStationState::default(),
            &PisStationInputs {
                now_ns: 0,
                pending_arrivals: &arrivals,
                emergency_code: None,
                operator_banner: None,
            },
            &p,
        );
        assert_eq!(out.board.len(), p.max_entries_shown);
    }

    #[test]
    fn announcements_prune_when_train_leaves_list() {
        let p = PisStationParams::default_metro();
        let arrivals1 = vec![arr(1, 30, true)];
        let s1 = pis_station_evaluate(
            &PisStationState::default(),
            &PisStationInputs {
                now_ns: 0,
                pending_arrivals: &arrivals1,
                emergency_code: None,
                operator_banner: None,
            },
            &p,
        )
        .state;
        assert_eq!(s1.announced_trains, vec![1]);

        // Train 1 no longer in list (left the station).
        let arrivals2 = vec![arr(2, 120, false)];
        let s2 = pis_station_evaluate(
            &s1,
            &PisStationInputs {
                now_ns: 0,
                pending_arrivals: &arrivals2,
                emergency_code: None,
                operator_banner: None,
            },
            &p,
        )
        .state;
        assert!(!s2.announced_trains.contains(&1));
    }

    #[test]
    fn determinism() {
        let p = PisStationParams::default_metro();
        let arrivals = vec![arr(1, 30, false), arr(2, 120, false)];
        let inputs = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: None,
            operator_banner: None,
        };
        let a = pis_station_evaluate(&PisStationState::default(), &inputs, &p);
        let b = pis_station_evaluate(&PisStationState::default(), &inputs, &p);
        assert_eq!(a, b);
    }
}
