//! Property tests for osr-pis-onboard.

use osr_pis_onboard::{
    pis_evaluate, AnnouncementKind, DisplayMessage, PisInputs, PisMode, PisParams, PisState,
};
use proptest::prelude::*;

fn params() -> PisParams {
    PisParams::light_metro_default()
}

fn arb_inputs() -> impl Strategy<Value = PisInputs> {
    (
        0u64..60_000_000_000,
        -30_000i32..30_000,
        prop_oneof![Just(None), (0u32..1000).prop_map(Some)],
        prop_oneof![Just(None), (0i64..3_000_000).prop_map(Some)],
        any::<bool>(),
        prop_oneof![Just(None), (0u16..10).prop_map(Some)],
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(
            |(now, speed, sid, dist, at_s, em, v110, v24)| PisInputs {
                now_ns: now,
                speed_mmps: speed,
                station_id: sid,
                distance_to_stop_mm: dist,
                at_station: at_s,
                emergency_broadcast: em,
                v110_rail_enabled: v110,
                v24_rail_enabled: v24,
            },
        )
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn determinism(i in arb_inputs()) {
        let p = params();
        let a = pis_evaluate(&PisState::default(), &i, &p);
        let b = pis_evaluate(&PisState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn emergency_dominates(mut i in arb_inputs()) {
        let p = params();
        i.emergency_broadcast = Some(5);
        let out = pis_evaluate(&PisState::default(), &i, &p);
        prop_assert_eq!(out.mode, PisMode::Emergency);
        let is_emergency = matches!(out.display_message, DisplayMessage::Emergency { .. });
        prop_assert!(is_emergency);
    }

    #[test]
    fn v110_down_blanks_display(mut i in arb_inputs()) {
        let p = params();
        i.emergency_broadcast = None;
        i.v110_rail_enabled = false;
        let out = pis_evaluate(&PisState::default(), &i, &p);
        prop_assert_eq!(out.display_message, DisplayMessage::Blank);
        prop_assert_eq!(out.mode, PisMode::Off);
    }

    #[test]
    fn cctv_tracks_v24(i in arb_inputs()) {
        let p = params();
        let out = pis_evaluate(&PisState::default(), &i, &p);
        prop_assert_eq!(out.cctv_enabled, i.v24_rail_enabled);
    }

    #[test]
    fn announcement_always_none_when_blank_or_no_station(mut i in arb_inputs()) {
        let p = params();
        i.emergency_broadcast = None;
        i.station_id = None;
        i.v110_rail_enabled = true;
        let out = pis_evaluate(&PisState::default(), &i, &p);
        prop_assert_eq!(out.audio_announcement, AnnouncementKind::None);
    }
}
