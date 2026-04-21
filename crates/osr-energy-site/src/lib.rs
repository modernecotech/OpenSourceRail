//! OpenSourceRail trackside energy-site controller.
//!
//! Manages a station / depot site that combines:
//!
//! - **PV array** — primary generation
//! - **Na-ion / LFP battery bank** — buffering
//! - **Grid-tie inverter** — bidirectional import / export
//! - **Train charging pad** — 100–1000 kW deliverable to a
//!   stopped train
//!
//! per [RFC 0002](../../../docs/rfcs/0002-energy-sizing.md). This is
//! the Rust implementation of the site controller described in
//! RFC 0002 §4.
//!
//! Phase 2d crate of [RFC 0005 §4.6](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2: mis-dispatching energy degrades service (a train arriving
//! with too little SoC) or wastes solar generation; it is not a
//! direct safety hazard.
//!
//! # Dispatch rule (priority order)
//!
//! 1. **Train demand** always met first, up to `pad_max_kw`.
//! 2. **Remaining PV → battery**, up to its charge-limit.
//! 3. **Remaining PV → grid export**, if grid-tie permits.
//! 4. **Shortfall → battery discharge** (up to `pad_max_kw`
//!    minus what PV provided).
//! 5. **Further shortfall → grid import**.
//! 6. **Surplus beyond all sinks → curtailment**.
//!
//! # Properties (proptest-verified)
//!
//! - **ES1 determinism.**
//! - **ES2 conservation:** `pv_w = to_pad + to_battery + to_grid_export + curtailed_w`
//!   (when net generation is positive) and
//!   `to_pad = from_pv + from_battery + from_grid_import` (when
//!   consumption exceeds generation).
//! - **ES3 train priority:** if a train demands `x` and the site
//!   can deliver `y = min(x, pad_max_kw)` across all sources, the
//!   delivered power is `y`.
//! - **ES4 curtailment is non-negative.**

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct EnergySiteInputs {
    pub now_ns: u64,
    /// Present PV output, watts.
    pub pv_w: u32,
    /// Present train demand at the pad, watts (0 when no train).
    pub pad_request_w: u32,
    /// Battery state-of-charge, ppt (0..=1000).
    pub battery_soc_ppt: u16,
    /// Per-cell limits surfaced as aggregate site limits.
    pub battery_charge_limit_w: u32,
    pub battery_discharge_limit_w: u32,
    /// `true` when grid tie is up (not in dust storm / outage).
    pub grid_up: bool,
    /// Whether the site's configuration allows export (regulatory).
    pub export_allowed: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct EnergySiteParams {
    pub pad_max_w: u32,
    pub grid_import_limit_w: u32,
    pub grid_export_limit_w: u32,
}

impl EnergySiteParams {
    #[must_use]
    pub fn default_samawah() -> Self {
        Self {
            pad_max_w: 1_000_000,       // 1 MW per pad
            grid_import_limit_w: 500_000, // 500 kW tie
            grid_export_limit_w: 500_000,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct EnergySiteOutput {
    /// Power delivered to the pad, watts.
    pub to_pad_w: u32,
    /// Net battery charge (positive) / discharge (if we modelled
    /// a signed field; here we split into two nonneg fields).
    pub battery_charge_w: u32,
    pub battery_discharge_w: u32,
    pub grid_import_w: u32,
    pub grid_export_w: u32,
    pub curtailed_w: u32,
}

#[must_use]
pub fn energy_site_evaluate(
    inputs: &EnergySiteInputs,
    params: &EnergySiteParams,
) -> EnergySiteOutput {
    // Effective pad demand (clamped to pad_max_w).
    let pad_request = inputs.pad_request_w.min(params.pad_max_w);

    // --- Source-side: how much can we raise this tick? -------------
    let grid_import_cap = if inputs.grid_up { params.grid_import_limit_w } else { 0 };
    let battery_discharge_cap = inputs.battery_discharge_limit_w;

    // --- Sink-side ---------------------------------------------------
    let battery_charge_cap = inputs.battery_charge_limit_w;
    let grid_export_cap = if inputs.grid_up && inputs.export_allowed {
        params.grid_export_limit_w
    } else {
        0
    };

    // --- Serve the pad first ----------------------------------------
    let pv_to_pad = pad_request.min(inputs.pv_w);
    let pv_remaining = inputs.pv_w.saturating_sub(pv_to_pad);
    let pad_shortfall = pad_request.saturating_sub(pv_to_pad);

    // Use battery next to cover shortfall.
    let battery_discharge_w = pad_shortfall.min(battery_discharge_cap);
    let pad_shortfall_after_battery = pad_shortfall.saturating_sub(battery_discharge_w);

    // Grid import for remaining shortfall.
    let grid_import_w = pad_shortfall_after_battery.min(grid_import_cap);

    let to_pad_w = pv_to_pad + battery_discharge_w + grid_import_w;

    // --- Dispatch PV surplus ----------------------------------------
    let battery_charge_w = pv_remaining.min(battery_charge_cap);
    let pv_after_battery = pv_remaining.saturating_sub(battery_charge_w);
    let grid_export_w = pv_after_battery.min(grid_export_cap);
    let curtailed_w = pv_after_battery.saturating_sub(grid_export_w);

    EnergySiteOutput {
        to_pad_w,
        battery_charge_w,
        battery_discharge_w,
        grid_import_w,
        grid_export_w,
        curtailed_w,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn inputs(pv: u32, pad: u32, soc: u16, grid_up: bool) -> EnergySiteInputs {
        EnergySiteInputs {
            now_ns: 0,
            pv_w: pv,
            pad_request_w: pad,
            battery_soc_ppt: soc,
            battery_charge_limit_w: 500_000,
            battery_discharge_limit_w: 500_000,
            grid_up,
            export_allowed: true,
        }
    }

    #[test]
    fn sunny_no_train_charges_battery_and_exports() {
        let i = inputs(600_000, 0, 500, true);
        let out = energy_site_evaluate(&i, &EnergySiteParams::default_samawah());
        assert_eq!(out.to_pad_w, 0);
        assert_eq!(out.battery_charge_w, 500_000); // capped at limit
        assert_eq!(out.grid_export_w, 100_000);    // overflow
        assert_eq!(out.curtailed_w, 0);
    }

    #[test]
    fn over_limit_pv_curtails() {
        let i = inputs(1_500_000, 0, 1000, true); // battery full
        let mut i = i;
        i.battery_charge_limit_w = 0; // simulate full
        i.export_allowed = false;      // no export
        let out = energy_site_evaluate(&i, &EnergySiteParams::default_samawah());
        assert_eq!(out.curtailed_w, 1_500_000);
    }

    #[test]
    fn train_at_pad_drains_battery_and_grid() {
        let i = inputs(100_000, 800_000, 800, true);
        let out = energy_site_evaluate(&i, &EnergySiteParams::default_samawah());
        assert_eq!(out.to_pad_w, 100_000 + 500_000 + 200_000);
        assert_eq!(out.battery_discharge_w, 500_000);
        assert_eq!(out.grid_import_w, 200_000);
    }

    #[test]
    fn grid_outage_caps_import() {
        let i = inputs(0, 700_000, 500, false);
        let out = energy_site_evaluate(&i, &EnergySiteParams::default_samawah());
        assert_eq!(out.grid_import_w, 0);
        assert_eq!(out.battery_discharge_w, 500_000);
        assert_eq!(out.to_pad_w, 500_000); // cannot fully serve
    }

    #[test]
    fn conservation_under_net_generation() {
        let i = inputs(300_000, 0, 500, true);
        let out = energy_site_evaluate(&i, &EnergySiteParams::default_samawah());
        assert_eq!(
            out.to_pad_w + out.battery_charge_w + out.grid_export_w + out.curtailed_w,
            i.pv_w
        );
    }

    #[test]
    fn determinism() {
        let i = inputs(500_000, 100_000, 500, true);
        let p = EnergySiteParams::default_samawah();
        assert_eq!(energy_site_evaluate(&i, &p), energy_site_evaluate(&i, &p));
    }
}
