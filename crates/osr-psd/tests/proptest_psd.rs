//! Property tests for osr-psd — PSD1 through PSD6.

use osr_psd::{
    psd_evaluate, PsdCommand, PsdInputs, PsdMotorCommand, PsdParams, PsdSensors, PsdState,
};
use proptest::prelude::*;

fn params() -> PsdParams {
    PsdParams::default_station()
}

fn arb_cmd() -> impl Strategy<Value = PsdCommand> {
    prop_oneof![
        Just(PsdCommand::Hold),
        Just(PsdCommand::Open),
        Just(PsdCommand::Close),
    ]
}

fn arb_sensors() -> impl Strategy<Value = PsdSensors> {
    (any::<bool>(), any::<bool>(), 0u32..8_000, any::<bool>()).prop_map(|(cl, ol, cur, obs)| {
        PsdSensors {
            closed_limit: cl,
            open_limit: ol,
            motor_current_ma: cur,
            obstruction_detected: obs,
        }
    })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, .. ProptestConfig::default() })]

    #[test]
    fn psd1_determinism(
        panels in prop::collection::vec(arb_sensors(), 1..=8),
        train_at in any::<bool>(),
        inter in any::<bool>(),
        train_open in any::<bool>(),
        cmd in arb_cmd(),
        em in any::<bool>(),
    ) {
        let p = params();
        let i = PsdInputs {
            now_ns: 0,
            train_at_platform: train_at,
            train_interlock_ok: inter,
            train_doors_open_or_opening: train_open,
            occ_commanded: cmd,
            emergency_stop: em,
            panels: &panels,
        };
        let state = PsdState::initial(panels.len());
        let a = psd_evaluate(&state, &i, &p);
        let b = psd_evaluate(&state, &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn psd2_no_open_without_platform(
        panels in prop::collection::vec(arb_sensors(), 1..=8),
        inter in any::<bool>(),
        train_open in any::<bool>(),
        cmd in arb_cmd(),
    ) {
        let p = params();
        // train_at_platform = false, emergency_stop = false
        let i = PsdInputs {
            now_ns: 0,
            train_at_platform: false,
            train_interlock_ok: inter,
            train_doors_open_or_opening: train_open,
            occ_commanded: cmd,
            emergency_stop: false,
            panels: &panels,
        };
        let state = PsdState::initial(panels.len());
        let out = psd_evaluate(&state, &i, &p);
        for m in &out.panel_motors {
            prop_assert_ne!(*m, PsdMotorCommand::DriveOpen);
        }
    }

    #[test]
    fn psd3_no_open_without_interlock(
        panels in prop::collection::vec(arb_sensors(), 1..=8),
        train_at in any::<bool>(),
        train_open in any::<bool>(),
        cmd in arb_cmd(),
    ) {
        let p = params();
        let i = PsdInputs {
            now_ns: 0,
            train_at_platform: train_at,
            train_interlock_ok: false,
            train_doors_open_or_opening: train_open,
            occ_commanded: cmd,
            emergency_stop: false,
            panels: &panels,
        };
        let state = PsdState::initial(panels.len());
        let out = psd_evaluate(&state, &i, &p);
        for m in &out.panel_motors {
            prop_assert_ne!(*m, PsdMotorCommand::DriveOpen);
        }
    }

    #[test]
    fn psd4_obstruction_stops_close(
        panels in prop::collection::vec(arb_sensors(), 1..=8),
        em in any::<bool>(),
    ) {
        let p = params();
        // Force OCC close command, no emergency (so the close branch is active).
        let i = PsdInputs {
            now_ns: 0,
            train_at_platform: false,
            train_interlock_ok: false,
            train_doors_open_or_opening: false,
            occ_commanded: PsdCommand::Close,
            emergency_stop: em,
            panels: &panels,
        };
        let state = PsdState::initial(panels.len());
        let out = psd_evaluate(&state, &i, &p);
        for (k, sensors) in panels.iter().enumerate() {
            if !em && (sensors.obstruction_detected
                || sensors.motor_current_ma >= p.obstruction_current_trip_ma)
            {
                prop_assert_ne!(out.panel_motors[k], PsdMotorCommand::DriveClose);
            }
        }
    }

    #[test]
    fn psd5_emergency_stop_opens_all(
        panels in prop::collection::vec(arb_sensors(), 1..=8),
        train_at in any::<bool>(),
        inter in any::<bool>(),
        train_open in any::<bool>(),
        cmd in arb_cmd(),
    ) {
        let p = params();
        let i = PsdInputs {
            now_ns: 0,
            train_at_platform: train_at,
            train_interlock_ok: inter,
            train_doors_open_or_opening: train_open,
            occ_commanded: cmd,
            emergency_stop: true,
            panels: &panels,
        };
        let state = PsdState::initial(panels.len());
        let out = psd_evaluate(&state, &i, &p);
        for (k, sensors) in panels.iter().enumerate() {
            let expected = if sensors.open_limit {
                PsdMotorCommand::Stop
            } else {
                PsdMotorCommand::DriveOpen
            };
            prop_assert_eq!(out.panel_motors[k], expected);
        }
    }

    #[test]
    fn psd6_all_closed_and_reduction(
        panels in prop::collection::vec(arb_sensors(), 1..=8),
    ) {
        let p = params();
        let i = PsdInputs {
            now_ns: 0,
            train_at_platform: false,
            train_interlock_ok: false,
            train_doors_open_or_opening: false,
            occ_commanded: PsdCommand::Hold,
            emergency_stop: false,
            panels: &panels,
        };
        let state = PsdState::initial(panels.len());
        let out = psd_evaluate(&state, &i, &p);
        let expected = panels.iter().all(|s| s.closed_limit);
        prop_assert_eq!(out.all_closed, expected);
    }
}
