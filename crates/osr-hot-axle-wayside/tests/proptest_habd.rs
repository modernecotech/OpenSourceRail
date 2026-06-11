//! Property tests HW1–HW3.

use osr_hot_axle_wayside::{
    habd_evaluate, AxleReading, HabdAction, HabdInputs, HabdParams, HwAlarmLevel,
};
use proptest::prelude::*;

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn hw1_determinism(peak in -200i16..1500, ambient in 0i16..500) {
        let axles = vec![AxleReading { axle_index: 0, peak_dc: peak }];
        let p = HabdParams::default_metro();
        let i = HabdInputs { now_ns: 0, train_id: 1, section_id: 1, ambient_dc: ambient, axles: &axles };
        prop_assert_eq!(habd_evaluate(&i, &p), habd_evaluate(&i, &p));
    }

    #[test]
    fn hw2_trip_produces_stop_order(peak in 1_000i16..1_500) {
        let axles = vec![AxleReading { axle_index: 2, peak_dc: peak }];
        let p = HabdParams::default_metro();
        let i = HabdInputs { now_ns: 0, train_id: 7, section_id: 1000, ambient_dc: 250, axles: &axles };
        let out = habd_evaluate(&i, &p);
        prop_assert_eq!(out.alarm, HwAlarmLevel::Trip);
        let is_stop = matches!(out.action, HabdAction::StopOrder { .. });
        prop_assert!(is_stop);
    }

    #[test]
    fn hw3_warning_produces_restriction(peak in 800i16..949) {
        let axles = vec![AxleReading { axle_index: 0, peak_dc: peak }];
        let p = HabdParams::default_metro();
        let i = HabdInputs { now_ns: 0, train_id: 1, section_id: 1, ambient_dc: 250, axles: &axles };
        let out = habd_evaluate(&i, &p);
        prop_assert_eq!(out.alarm, HwAlarmLevel::Warning);
        let is_sr = matches!(out.action, HabdAction::SpeedRestriction { .. });
        prop_assert!(is_sr);
    }
}
