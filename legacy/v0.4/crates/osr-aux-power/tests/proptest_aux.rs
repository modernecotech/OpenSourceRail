//! Property tests AP1–AP5.

use osr_aux_power::{aux_evaluate, AuxInputs, AuxParams, AuxState, Rail};
use proptest::prelude::*;

fn params() -> AuxParams {
    AuxParams::light_metro_default()
}

fn arb_inputs() -> impl Strategy<Value = AuxInputs> {
    (
        0u64..60_000_000_000,
        0u16..=1000,
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(
            |(now, soc, cc, ot24, ot110, ot_hv, df24, df110, df_hv, e24, e110, e_hv)| AuxInputs {
                now_ns: now,
                pack_soc_ppt: soc,
                pack_contactor_closed: cc,
                v24_over_temp: ot24,
                v110_over_temp: ot110,
                direct_hv_over_temp: ot_hv,
                v24_drive_fault: df24,
                v110_drive_fault: df110,
                direct_hv_drive_fault: df_hv,
                v24_enable_request: e24,
                v110_enable_request: e110,
                direct_hv_enable_request: e_hv,
            },
        )
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn ap1_determinism(i in arb_inputs()) {
        let p = params();
        let a = aux_evaluate(&AuxState::default(), &i, &p);
        let b = aux_evaluate(&AuxState::default(), &i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn ap2_shedding_monotone_in_soc(
        now in 0u64..60_000_000_000,
        soc_hi in 500u16..=1000,
        delta in 100u16..=500,
    ) {
        let p = params();
        let soc_lo = soc_hi.saturating_sub(delta);
        let base = AuxInputs {
            now_ns: now,
            pack_soc_ppt: soc_hi,
            pack_contactor_closed: true,
            v24_over_temp: false, v110_over_temp: false, direct_hv_over_temp: false,
            v24_drive_fault: false, v110_drive_fault: false, direct_hv_drive_fault: false,
            v24_enable_request: true, v110_enable_request: true, direct_hv_enable_request: true,
        };
        let lower = AuxInputs { pack_soc_ppt: soc_lo, ..base };
        let out_hi = aux_evaluate(&AuxState::default(), &base, &p);
        let out_lo = aux_evaluate(&AuxState::default(), &lower, &p);

        // Each rail's enabled flag at lower SoC ≤ the same at higher SoC.
        prop_assert!(!out_lo.v110_enabled || out_hi.v110_enabled);
        prop_assert!(!out_lo.direct_hv_enabled || out_hi.direct_hv_enabled);
        // 24 V is SoC-insensitive — identical.
        prop_assert_eq!(out_lo.v24_enabled, out_hi.v24_enabled);
    }

    #[test]
    fn ap3_fault_disables_rail(mut i in arb_inputs()) {
        let p = params();
        // Force a DirectHv fault.
        i.direct_hv_drive_fault = true;
        let out = aux_evaluate(&AuxState::default(), &i, &p);
        prop_assert!(!out.direct_hv_enabled);
    }

    #[test]
    fn ap4_nominal_24v_enabled(mut i in arb_inputs()) {
        let p = params();
        // Force nominal: contactor ok, no faults, enable request true.
        i.pack_contactor_closed = true;
        i.v24_over_temp = false;
        i.v24_drive_fault = false;
        i.v24_enable_request = true;
        let out = aux_evaluate(&AuxState::default(), &i, &p);
        prop_assert!(out.v24_enabled);
    }

    #[test]
    fn ap5_contactor_open_all_off(mut i in arb_inputs()) {
        let p = params();
        i.pack_contactor_closed = false;
        let out = aux_evaluate(&AuxState::default(), &i, &p);
        prop_assert!(!out.v24_enabled);
        prop_assert!(!out.v110_enabled);
        prop_assert!(!out.direct_hv_enabled);
    }

    #[test]
    fn rails_sheddable_do_not_exceed_enabled_parent(i in arb_inputs()) {
        // Sanity: at any tick, direct HV enabled ⇒ 110 V also enabled
        // (since V110 sheds earlier in SoC and both rails are
        // gated on contactor + enable_request). NOT a hard guarantee
        // when per-rail faults differ — but holds when the only
        // asymmetry is SoC.
        let p = params();
        let mut clean = i;
        clean.v110_over_temp = false;
        clean.v110_drive_fault = false;
        clean.v110_enable_request = true;
        clean.direct_hv_over_temp = false;
        clean.direct_hv_drive_fault = false;
        clean.direct_hv_enable_request = true;
        let out = aux_evaluate(&AuxState::default(), &clean, &p);
        if out.direct_hv_enabled {
            prop_assert!(out.v110_enabled, "direct HV enabled but 110 V not: soc={}", clean.pack_soc_ppt);
        }
        let _ = Rail::V24; // silence unused
    }
}
