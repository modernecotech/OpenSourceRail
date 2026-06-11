//! Property tests for osr-tcms.

use osr_tcms::{tcms_evaluate, AlarmLevel, TcmsInputs};
use proptest::prelude::*;

fn arb_alarm() -> impl Strategy<Value = AlarmLevel> {
    prop_oneof![
        Just(AlarmLevel::Nominal),
        Just(AlarmLevel::Warning),
        Just(AlarmLevel::Trip),
    ]
}

fn arb_inputs() -> impl Strategy<Value = TcmsInputs> {
    (
        0u64..60_000_000_000,
        -30_000i32..30_000,
        prop_oneof![Just(None), (0u32..1000).prop_map(Some)],
        any::<bool>(),
        (
            any::<bool>(),
            any::<bool>(),
            any::<bool>(),
            any::<bool>(),
            any::<bool>(),
            any::<bool>(),
        ),
        (any::<bool>(), any::<bool>(), any::<bool>()),
        (arb_alarm(), arb_alarm(), arb_alarm(), arb_alarm()),
        (arb_alarm(), arb_alarm(), arb_alarm(), arb_alarm()),
        0u16..=1000,
        (any::<bool>(), any::<bool>(), any::<bool>()),
    )
        .prop_map(
            |(
                now,
                speed,
                sid,
                at_s,
                (ae, ve, fe, de, dre, oe),
                (di, cc, ti),
                (ba, ta, fa, da_),
                (ha, hv, ca_, doa),
                soc,
                (r24, r110, r400),
            )| TcmsInputs {
                now_ns: now,
                speed_mmps: speed,
                section_id: sid,
                at_station: at_s,
                atp_emergency: ae,
                vigilance_emergency: ve,
                fire_emergency: fe,
                derailment_emergency: de,
                driver_emergency: dre,
                obstacle_emergency: oe,
                doors_interlock_ok: di,
                bms_contactor_closed: cc,
                traction_inverter_enabled: ti,
                bms_alarm: ba,
                traction_alarm: ta,
                fire_alarm: fa,
                derailment_alarm: da_,
                hot_axle_alarm: ha,
                hvac_alarm: hv,
                comfort_alarm: ca_,
                door_alarm: doa,
                soc_ppt: soc,
                v24_rail_enabled: r24,
                v110_rail_enabled: r110,
                v400_rail_enabled: r400,
            },
        )
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn tcms1_determinism(i in arb_inputs()) {
        prop_assert_eq!(tcms_evaluate(&i), tcms_evaluate(&i));
    }

    #[test]
    fn tcms2_ready_requires_all_green(i in arb_inputs()) {
        let out = tcms_evaluate(&i);
        if out.ready_to_move {
            prop_assert!(!out.any_emergency);
            prop_assert!(i.doors_interlock_ok);
            prop_assert!(i.bms_contactor_closed);
            prop_assert!(i.traction_inverter_enabled);
            prop_assert_ne!(i.bms_alarm, AlarmLevel::Trip);
            prop_assert_ne!(i.traction_alarm, AlarmLevel::Trip);
            prop_assert_ne!(i.fire_alarm, AlarmLevel::Trip);
            prop_assert_ne!(i.derailment_alarm, AlarmLevel::Trip);
        }
    }

    #[test]
    fn tcms3_worst_alarm_is_at_least_max_input(i in arb_inputs()) {
        let out = tcms_evaluate(&i);
        let max_input = [
            i.bms_alarm,
            i.traction_alarm,
            i.fire_alarm,
            i.derailment_alarm,
            i.hot_axle_alarm,
            i.hvac_alarm,
            i.comfort_alarm,
            i.door_alarm,
        ]
        .into_iter()
        .max()
        .unwrap_or(AlarmLevel::Nominal);
        prop_assert!(out.worst_alarm >= max_input);
    }

    #[test]
    fn tcms4_emergency_forces_trip(i in arb_inputs()) {
        let out = tcms_evaluate(&i);
        if out.any_emergency {
            prop_assert_eq!(out.worst_alarm, AlarmLevel::Trip);
        }
    }
}
