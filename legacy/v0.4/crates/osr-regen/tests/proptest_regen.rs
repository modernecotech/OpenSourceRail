//! Property tests for the regen arbiter (R1–R7).

use osr_regen::{regen_evaluate, RegenInputs, RegenParams};
use proptest::prelude::*;

fn arb_inputs() -> impl Strategy<Value = RegenInputs> {
    (
        0u32..2_000_000,
        0u32..2_000_000,
        any::<bool>(),
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(|(req, charge, cc, ra, rot)| RegenInputs {
            now_ns: 0,
            requested_ma: req,
            bms_charge_limit_ma: charge,
            bms_contactor_closed: cc,
            resistor_available: ra,
            resistor_over_temp: rot,
        })
}

fn params(resistor_max: u32, prefer_pack: bool) -> RegenParams {
    RegenParams {
        resistor_max_ma: resistor_max,
        prefer_pack,
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, .. ProptestConfig::default() })]

    #[test]
    fn r1_determinism(i in arb_inputs(), resistor_max in 0u32..1_000_000, prefer in any::<bool>()) {
        let p = params(resistor_max, prefer);
        let a = regen_evaluate(&i, &p);
        let b = regen_evaluate(&i, &p);
        prop_assert_eq!(a, b);
    }

    #[test]
    fn r2_current_conservation(i in arb_inputs(), resistor_max in 0u32..1_000_000, prefer in any::<bool>()) {
        let p = params(resistor_max, prefer);
        let out = regen_evaluate(&i, &p);
        prop_assert_eq!(out.to_pack_ma + out.to_resistor_ma + out.refused_ma, i.requested_ma);
    }

    #[test]
    fn r3_pack_limit(i in arb_inputs(), resistor_max in 0u32..1_000_000, prefer in any::<bool>()) {
        let p = params(resistor_max, prefer);
        let out = regen_evaluate(&i, &p);
        prop_assert!(out.to_pack_ma <= i.bms_charge_limit_ma);
    }

    #[test]
    fn r4_contactor_open_no_pack(i in arb_inputs(), resistor_max in 0u32..1_000_000, prefer in any::<bool>()) {
        let p = params(resistor_max, prefer);
        let out = regen_evaluate(&i, &p);
        if !i.bms_contactor_closed {
            prop_assert_eq!(out.to_pack_ma, 0);
        }
    }

    #[test]
    fn r5_resistor_fault_no_resistor(i in arb_inputs(), resistor_max in 0u32..1_000_000, prefer in any::<bool>()) {
        let p = params(resistor_max, prefer);
        let out = regen_evaluate(&i, &p);
        if !i.resistor_available || i.resistor_over_temp {
            prop_assert_eq!(out.to_resistor_ma, 0);
        }
    }

    #[test]
    fn r6_resistor_bound(i in arb_inputs(), resistor_max in 0u32..1_000_000, prefer in any::<bool>()) {
        let p = params(resistor_max, prefer);
        let out = regen_evaluate(&i, &p);
        prop_assert!(out.to_resistor_ma <= p.resistor_max_ma);
    }

    #[test]
    fn r7_prefer_pack_uses_pack_fully_before_resistor(
        req in 0u32..1_000_000,
        charge in 0u32..1_000_000,
        resistor_max in 0u32..1_000_000,
    ) {
        // With prefer_pack and both sinks available, resistor is zero
        // whenever the pack can absorb the whole request.
        let i = RegenInputs {
            now_ns: 0,
            requested_ma: req,
            bms_charge_limit_ma: charge,
            bms_contactor_closed: true,
            resistor_available: true,
            resistor_over_temp: false,
        };
        let p = params(resistor_max, true);
        let out = regen_evaluate(&i, &p);
        if req <= charge {
            prop_assert_eq!(out.to_resistor_ma, 0);
        }
    }
}
