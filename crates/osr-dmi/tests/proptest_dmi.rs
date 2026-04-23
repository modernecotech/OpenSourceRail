//! Property tests for osr-dmi.

use osr_dmi::{dmi_evaluate, BuzzerRequest, DisplayPage, DriverInput, DriverPageRequest};
use osr_tcms::{AlarmLevel, ConsistStatus, EmergencySources};
use proptest::prelude::*;

fn arb_alarm() -> impl Strategy<Value = AlarmLevel> {
    prop_oneof![
        Just(AlarmLevel::Nominal),
        Just(AlarmLevel::Warning),
        Just(AlarmLevel::Trip),
    ]
}

fn arb_page() -> impl Strategy<Value = DriverPageRequest> {
    prop_oneof![
        Just(DriverPageRequest::Main),
        Just(DriverPageRequest::Diagnostics),
        Just(DriverPageRequest::Energy),
        Just(DriverPageRequest::Route),
    ]
}

fn arb_status() -> impl Strategy<Value = ConsistStatus> {
    (
        -30_000i32..30_000,
        any::<bool>(),
        arb_alarm(),
        (any::<bool>(), any::<bool>(), any::<bool>(), any::<bool>(), any::<bool>(), any::<bool>()),
        any::<bool>(),
        0u16..=1000,
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(|(speed, at_s, alarm, src, ready, soc, r24, r110, r400)| {
            let (atp, vig, fire, derail, driver, obstacle) = src;
            let sources = EmergencySources {
                atp,
                vigilance: vig,
                fire,
                derailment: derail,
                driver,
                obstacle,
            };
            let any_em = sources.any();
            ConsistStatus {
                now_ns: 0,
                speed_mmps: speed,
                section_id: None,
                at_station: at_s,
                worst_alarm: alarm,
                emergency_sources: sources,
                any_emergency: any_em,
                ready_to_move: ready && !any_em,
                v24_rail_enabled: r24,
                v110_rail_enabled: r110,
                v400_rail_enabled: r400,
                soc_ppt: soc,
            }
        })
}

fn arb_input() -> impl Strategy<Value = DriverInput> {
    (
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        arb_page(),
        any::<bool>(),
    )
        .prop_map(|(ep, va, ae, d_open, d_close, pg, back)| DriverInput {
            now_ns: 0,
            emergency_plunger: ep,
            vigilance_ack: va,
            ato_engage: ae,
            doors_open_request: d_open,
            doors_close_request: d_close,
            page_request: pg,
            buzzer_ack: back,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn dmi1_determinism(s in arb_status(), i in arb_input()) {
        prop_assert_eq!(dmi_evaluate(&s, &i), dmi_evaluate(&s, &i));
    }

    #[test]
    fn dmi2_emergency_dominates_page(s in arb_status(), i in arb_input()) {
        let out = dmi_evaluate(&s, &i);
        if s.any_emergency {
            prop_assert_eq!(out.display_page, DisplayPage::Emergency);
        }
    }

    #[test]
    fn dmi3_buzzer_on_trip(s in arb_status(), i in arb_input()) {
        let out = dmi_evaluate(&s, &i);
        if s.worst_alarm == AlarmLevel::Trip {
            prop_assert_eq!(out.buzzer, BuzzerRequest::Alarm);
        }
    }

    #[test]
    fn dmi4_ready_lamp_tracks_ready(s in arb_status(), i in arb_input()) {
        let out = dmi_evaluate(&s, &i);
        if s.ready_to_move {
            prop_assert_eq!(out.ready_to_move, osr_dmi::IndicatorColour::Green);
        }
    }
}
