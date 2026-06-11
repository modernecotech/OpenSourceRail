//! Property tests PS1–PS5.

use osr_pis_station::{
    pis_station_evaluate, AudioCue, Direction, PendingArrival, PisStationInputs, PisStationMode,
    PisStationParams, PisStationState,
};
use proptest::prelude::*;

fn params() -> PisStationParams {
    PisStationParams::default_metro()
}

fn arb_arrival() -> impl Strategy<Value = PendingArrival> {
    (0u32..100, 0u32..5, 0u32..1_000, any::<bool>()).prop_map(|(id, line, eta, app)| {
        PendingArrival {
            train_id: id,
            line_id: line,
            direction: Direction::Forward,
            eta_s: eta,
            approaching: app,
        }
    })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ps1_determinism(arrivals in prop::collection::vec(arb_arrival(), 0..10),
                        em in prop::option::of(0u16..100)) {
        let p = params();
        let i = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: em,
            operator_banner: None,
        };
        let a = pis_station_evaluate(&PisStationState::default(), &i, &p);
        let b = pis_station_evaluate(&PisStationState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn ps2_emergency_dominates(arrivals in prop::collection::vec(arb_arrival(), 0..10), code in any::<u16>()) {
        let p = params();
        let i = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: Some(code),
            operator_banner: None,
        };
        let out = pis_station_evaluate(&PisStationState::default(), &i, &p);
        prop_assert_eq!(out.mode, PisStationMode::Emergency);
        prop_assert_eq!(out.audio_cue, AudioCue::EmergencyBroadcast { code });
        prop_assert!(out.board.is_empty());
    }

    #[test]
    fn ps3_board_sorted_by_eta(arrivals in prop::collection::vec(arb_arrival(), 0..10)) {
        let p = params();
        let i = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: None,
            operator_banner: None,
        };
        let out = pis_station_evaluate(&PisStationState::default(), &i, &p);
        for w in out.board.windows(2) {
            prop_assert!(w[0].eta_s <= w[1].eta_s);
        }
    }

    #[test]
    fn ps4_approach_announced_once(within_band in prop::collection::vec(0u32..60, 1..=3)) {
        let p = params();
        let arrivals: Vec<_> = within_band
            .iter()
            .enumerate()
            .map(|(i, eta)| PendingArrival {
                train_id: i as u32,
                line_id: 1,
                direction: Direction::Forward,
                eta_s: *eta,
                approaching: true,
            })
            .collect();
        let i = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: None,
            operator_banner: None,
        };
        let first = pis_station_evaluate(&PisStationState::default(), &i, &p);
        let is_approaching = matches!(first.audio_cue, AudioCue::Approaching { .. });
        prop_assert!(is_approaching);
        // Second tick with the same arrivals: not re-announced.
        let second = pis_station_evaluate(&first.state, &i, &p);
        // At most one train announced each tick — the first
        // un-announced one. If all were announced, cue is None.
        // With ≤ 3 trains announced in first tick, second tick
        // might still announce a second new one. The invariant is:
        // previously-announced trains don't re-announce.
        if let AudioCue::Approaching { train_id } = second.audio_cue {
            prop_assert!(!first.state.announced_trains.contains(&train_id));
        }
    }

    #[test]
    fn ps5_board_bounded(arrivals in prop::collection::vec(arb_arrival(), 0..30)) {
        let p = params();
        let i = PisStationInputs {
            now_ns: 0,
            pending_arrivals: &arrivals,
            emergency_code: None,
            operator_banner: None,
        };
        let out = pis_station_evaluate(&PisStationState::default(), &i, &p);
        prop_assert!(out.board.len() <= p.max_entries_shown);
    }
}
