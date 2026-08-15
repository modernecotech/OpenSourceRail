//! Property tests ES1–ES4.

use osr_energy_site::{energy_site_evaluate, EnergySiteInputs, EnergySiteParams};
use proptest::prelude::*;

fn arb_inputs() -> impl Strategy<Value = EnergySiteInputs> {
    (
        0u32..2_000_000,
        0u32..1_500_000,
        0u16..=1000,
        0u32..1_000_000,
        0u32..1_000_000,
        any::<bool>(),
        any::<bool>(),
    )
        .prop_map(|(pv, pad, soc, cl, dl, grid, exp)| EnergySiteInputs {
            now_ns: 0,
            pv_w: pv,
            pad_request_w: pad,
            battery_soc_ppt: soc,
            battery_charge_limit_w: cl,
            battery_discharge_limit_w: dl,
            grid_up: grid,
            export_allowed: exp,
        })
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, .. ProptestConfig::default() })]

    #[test]
    fn es1_determinism(i in arb_inputs()) {
        let p = EnergySiteParams::default_samawah();
        prop_assert_eq!(energy_site_evaluate(&i, &p), energy_site_evaluate(&i, &p));
    }

    #[test]
    fn es3_train_served_up_to_cap(i in arb_inputs()) {
        let p = EnergySiteParams::default_samawah();
        let out = energy_site_evaluate(&i, &p);
        let demand_capped = i.pad_request_w.min(p.pad_max_w);
        prop_assert!(out.to_pad_w <= demand_capped);
    }

    #[test]
    fn es4_curtailment_nonneg(i in arb_inputs()) {
        let p = EnergySiteParams::default_samawah();
        let out = energy_site_evaluate(&i, &p);
        // u32 is always non-negative — just a presence check.
        prop_assert!(out.curtailed_w <= i.pv_w);
    }

    /// Conservation when net-positive generation (PV ≥ pad demand):
    /// the PV watts split across pad + battery + export + curtail.
    #[test]
    fn es2_conservation_when_surplus(i in arb_inputs()) {
        // Focus on the surplus case: PV above pad demand.
        prop_assume!(i.pv_w >= i.pad_request_w.min(1_000_000));
        let p = EnergySiteParams::default_samawah();
        let out = energy_site_evaluate(&i, &p);
        let to_pad_from_pv = out.to_pad_w.saturating_sub(out.battery_discharge_w + out.grid_import_w);
        prop_assert_eq!(
            to_pad_from_pv + out.battery_charge_w + out.grid_export_w + out.curtailed_w,
            i.pv_w
        );
    }
}
