//! Property tests SC1–SC4.

use osr_station_scada::{
    station_scada_evaluate, CctvNvrStatus, EscalatorDirection, EscalatorStatus, LiftStatus,
    LightingZoneStatus, StationHealth, StationHvacStatus, StationScadaInputs, StationScadaParams,
};
use proptest::prelude::*;

fn params() -> StationScadaParams {
    StationScadaParams::default_metro()
}

fn arb_escalator() -> impl Strategy<Value = EscalatorStatus> {
    (any::<bool>(), any::<bool>(), any::<bool>()).prop_map(|(f, ol, es)| EscalatorStatus {
        commanded: EscalatorDirection::Up,
        running: EscalatorDirection::Up,
        faulted: f,
        overload: ol,
        estop: es,
    })
}

fn arb_lift() -> impl Strategy<Value = LiftStatus> {
    (-2i8..5, -2i8..5, any::<bool>(), any::<bool>()).prop_map(|(c, r, door, f)| LiftStatus {
        current_floor: c,
        requested_floor: r,
        door_open: door,
        faulted: f,
    })
}

fn arb_zone() -> impl Strategy<Value = LightingZoneStatus> {
    (any::<bool>(), 0u16..=1000, any::<bool>()).prop_map(|(e, d, f)| LightingZoneStatus {
        enabled: e,
        dim_ppt: d,
        faulted: f,
    })
}

fn arb_hvac() -> impl Strategy<Value = StationHvacStatus> {
    (100i16..350, any::<bool>()).prop_map(|(sp, f)| StationHvacStatus {
        setpoint_dc: sp,
        faulted: f,
    })
}

fn arb_cctv() -> impl Strategy<Value = CctvNvrStatus> {
    (any::<bool>(), 0u16..=1000, 0u8..16).prop_map(|(o, s, c)| CctvNvrStatus {
        online: o,
        free_storage_ppt: s,
        channels_offline: c,
    })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn sc1_determinism(
        escalators in prop::collection::vec(arb_escalator(), 1..=4),
        lifts in prop::collection::vec(arb_lift(), 0..=3),
        zones in prop::collection::vec(arb_zone(), 1..=4),
        hvac in arb_hvac(),
        cctv in arb_cctv(),
        em in any::<bool>(),
    ) {
        let p = params();
        let esc_cmd: Vec<_> = escalators.iter().map(|_| None).collect();
        let lift_call: Vec<_> = lifts.iter().map(|_| None).collect();
        let inputs = StationScadaInputs {
            now_ns: 0,
            emergency_stop: em,
            escalators: &escalators,
            lifts: &lifts,
            lighting_zones: &zones,
            hvac,
            cctv,
            escalator_commands: &esc_cmd,
            lift_calls: &lift_call,
        };
        let a = station_scada_evaluate(&inputs, &p);
        let b = station_scada_evaluate(&inputs, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn sc2_emergency_stops_escalators_and_hvac(
        escalators in prop::collection::vec(arb_escalator(), 1..=4),
        lifts in prop::collection::vec(arb_lift(), 0..=3),
        zones in prop::collection::vec(arb_zone(), 1..=4),
        hvac in arb_hvac(),
        cctv in arb_cctv(),
    ) {
        let p = params();
        let esc_cmd: Vec<_> = escalators.iter().map(|_| Some(EscalatorDirection::Up)).collect();
        let lift_call: Vec<_> = lifts.iter().map(|_| Some(5)).collect();
        let inputs = StationScadaInputs {
            now_ns: 0,
            emergency_stop: true,
            escalators: &escalators,
            lifts: &lifts,
            lighting_zones: &zones,
            hvac,
            cctv,
            escalator_commands: &esc_cmd,
            lift_calls: &lift_call,
        };
        let out = station_scada_evaluate(&inputs, &p);
        for d in &out.escalator_commands {
            prop_assert_eq!(*d, EscalatorDirection::Stop);
        }
        for (k, l) in lifts.iter().enumerate() {
            prop_assert_eq!(out.lift_requests[k], l.current_floor);
        }
        prop_assert_eq!(out.hvac_setpoint_dc, p.hvac_off_setpoint_dc);
        prop_assert_eq!(out.health, StationHealth::Degraded);
    }

    #[test]
    fn sc3_any_fault_not_nominal(
        escalators in prop::collection::vec(arb_escalator(), 1..=4),
        lifts in prop::collection::vec(arb_lift(), 0..=3),
        zones in prop::collection::vec(arb_zone(), 1..=4),
        hvac in arb_hvac(),
        cctv in arb_cctv(),
    ) {
        let p = params();
        let esc_cmd: Vec<_> = escalators.iter().map(|_| None).collect();
        let lift_call: Vec<_> = lifts.iter().map(|_| None).collect();
        let inputs = StationScadaInputs {
            now_ns: 0,
            emergency_stop: false,
            escalators: &escalators,
            lifts: &lifts,
            lighting_zones: &zones,
            hvac,
            cctv,
            escalator_commands: &esc_cmd,
            lift_calls: &lift_call,
        };
        let out = station_scada_evaluate(&inputs, &p);
        if out.fault_count > 0 {
            prop_assert_ne!(out.health, StationHealth::Nominal);
        }
    }

    #[test]
    fn sc4_cctv_low_storage_warns(
        escalators in prop::collection::vec(arb_escalator(), 1..=4),
        lifts in prop::collection::vec(arb_lift(), 0..=3),
        zones in prop::collection::vec(arb_zone(), 1..=4),
        hvac in arb_hvac(),
        storage in 0u16..100,
    ) {
        let p = params();
        let esc_cmd: Vec<_> = escalators.iter().map(|_| None).collect();
        let lift_call: Vec<_> = lifts.iter().map(|_| None).collect();
        let cctv = CctvNvrStatus { online: true, free_storage_ppt: storage, channels_offline: 0 };
        // Filter out scenarios where healthy systems also have
        // no faults to make this a clean test of the CCTV path.
        let inputs = StationScadaInputs {
            now_ns: 0,
            emergency_stop: false,
            escalators: &escalators,
            lifts: &lifts,
            lighting_zones: &zones,
            hvac,
            cctv,
            escalator_commands: &esc_cmd,
            lift_calls: &lift_call,
        };
        let out = station_scada_evaluate(&inputs, &p);
        prop_assert_ne!(out.health, StationHealth::Nominal);
    }
}
