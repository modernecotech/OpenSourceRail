//! OpenSourceRail auxiliary power controller.
//!
//! Manages the isolated DC auxiliary domains a light-metro car runs from
//! its 650–700 V nominal traction pack. There is no central auxiliary AC
//! inverter or train-wide 400 V AC bus.
//!
//! | Rail | Loads | Priority |
//! |------|-------|----------|
//! | **24 V DC** | Safety-critical controllers, emergency lighting, comm radios | Highest |
//! | **110 V DC** | Primary interior lighting, door actuators, PIS displays | Medium |
//! | **direct HV DC** | HVAC internal drive, coolant pumps, other high-power comfort loads | Lowest |
//!
//! Phase 2c crate 2 of [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 because failure degrades ride quality (HVAC off, lights dim)
//! but does not directly endanger passengers — emergency lighting on
//! the 24 V rail is independently battery-backed at the fixture
//! level.
//!
//! # Load-shed ladder
//!
//! When the BMS reports a low pack SoC the controller sheds rails in
//! priority order to extend the reserve for safety-critical loads:
//!
//! - **SoC ≤ `shed_direct_hv_ppt`** (e.g., 300 ppt = 30 %) → drop the
//!   direct-HV comfort branch. HVAC and coolant pumps switch off; passenger comfort
//!   suffers but the train keeps moving.
//! - **SoC ≤ `shed_110v_ppt`** (e.g., 150 ppt = 15 %) → also drop
//!   the 110 V DC rail. Interior lighting reduced to the
//!   emergency-lighting fixtures on the 24 V rail.
//! - **24 V DC is never shed** under low SoC. Only a converter
//!   fault (over-temp, drive fault) disables it.
//!
//! # Properties (proptest-verified)
//!
//! - **AP1 determinism.**
//! - **AP2 shedding is monotone in SoC:** as SoC drops, the set of
//!   enabled rails only shrinks.
//! - **AP3 fault disables that rail** regardless of SoC.
//! - **AP4 24 V rail enabled under normal operation:** with no
//!   faults and a nominal BMS state the 24 V rail is enabled.
//! - **AP5 contactor-open disables all rails.**

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/// Three aux rails; indexed by priority.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Rail {
    /// Safety-critical 24 V DC.
    V24 = 0,
    /// Primary 110 V DC.
    V110 = 1,
    /// Direct-HV DC comfort branch.
    DirectHv = 2,
}

impl Rail {
    pub const ALL: [Rail; 3] = [Rail::V24, Rail::V110, Rail::DirectHv];
}

/// Per-rail fault bits.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct RailFaultMask(pub u8);

impl RailFaultMask {
    pub fn insert(&mut self, r: Rail) {
        self.0 |= 1u8 << (r as u8);
    }
    #[must_use]
    pub fn contains(self, r: Rail) -> bool {
        (self.0 >> (r as u8)) & 1 == 1
    }
    #[must_use]
    pub fn any(self) -> bool {
        self.0 != 0
    }
}

// ---------------------------------------------------------------------------
// Inputs
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AuxInputs {
    pub now_ns: u64,
    /// Pack state of charge, parts-per-thousand (0–1000).
    pub pack_soc_ppt: u16,
    /// Main pack contactor closed — required for any rail.
    pub pack_contactor_closed: bool,
    /// Per-rail converter over-temperature flags.
    pub v24_over_temp: bool,
    pub v110_over_temp: bool,
    pub direct_hv_over_temp: bool,
    /// Per-rail drive-fault flags.
    pub v24_drive_fault: bool,
    pub v110_drive_fault: bool,
    pub direct_hv_drive_fault: bool,
    /// Vehicle-controller "enable this rail" requests. Used as the
    /// final gate — even if SoC and faults allow a rail, a `false`
    /// here holds it off (e.g., depot shutdown).
    pub v24_enable_request: bool,
    pub v110_enable_request: bool,
    pub direct_hv_enable_request: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AuxParams {
    /// SoC at or below which the direct-HV comfort branch sheds (ppt).
    pub shed_direct_hv_ppt: u16,
    /// SoC at or below which the 110 V rail sheds (ppt).
    pub shed_110v_ppt: u16,
    /// Cooldown after any rail fault, ms.
    pub fault_cooldown_ms: u32,
}

impl AuxParams {
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            shed_direct_hv_ppt: 300,
            shed_110v_ppt: 150,
            fault_cooldown_ms: 10_000,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct AuxState {
    /// Per-rail latched faults.
    pub faults: RailFaultMask,
    /// ns-since-epoch at which each rail's fault may be cleared.
    /// 3-entry array indexed by `Rail as usize`.
    pub fault_until_ns: [Option<u64>; 3],
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct AuxOutput {
    pub state: AuxState,
    pub v24_enabled: bool,
    pub v110_enabled: bool,
    pub direct_hv_enabled: bool,
    pub load_shed_active: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

/// One tick of aux-power decision logic. Pure.
#[must_use]
pub fn aux_evaluate(prev: &AuxState, inputs: &AuxInputs, params: &AuxParams) -> AuxOutput {
    // --- Per-rail new-fault detection -------------------------------
    let mut current_faults = RailFaultMask(0);
    if inputs.v24_over_temp || inputs.v24_drive_fault {
        current_faults.insert(Rail::V24);
    }
    if inputs.v110_over_temp || inputs.v110_drive_fault {
        current_faults.insert(Rail::V110);
    }
    if inputs.direct_hv_over_temp || inputs.direct_hv_drive_fault {
        current_faults.insert(Rail::DirectHv);
    }

    // --- Cooldown update --------------------------------------------
    let mut fault_until_ns = prev.fault_until_ns;
    for &rail in &Rail::ALL {
        let idx = rail as usize;
        if current_faults.contains(rail) {
            let deadline = inputs
                .now_ns
                .saturating_add(u64::from(params.fault_cooldown_ms) * 1_000_000);
            fault_until_ns[idx] = Some(match fault_until_ns[idx] {
                Some(existing) => existing.max(deadline),
                None => deadline,
            });
        } else if let Some(until) = fault_until_ns[idx] {
            if inputs.now_ns >= until {
                fault_until_ns[idx] = None;
            }
        }
    }

    // Latched fault is `current OR still-in-cooldown`.
    let rail_faulted = |r: Rail| -> bool {
        let idx = r as usize;
        current_faults.contains(r) || fault_until_ns[idx].is_some()
    };

    // --- Rail gating logic ------------------------------------------
    //
    // A rail is enabled iff:
    //   - pack contactor is closed,
    //   - no latched fault for that rail,
    //   - vehicle-controller enable request is true,
    //   - SoC gate for that rail is satisfied.
    let contactor_ok = inputs.pack_contactor_closed;
    let soc = inputs.pack_soc_ppt;

    let v24_enabled = contactor_ok && !rail_faulted(Rail::V24) && inputs.v24_enable_request;

    let v110_enabled = contactor_ok
        && !rail_faulted(Rail::V110)
        && inputs.v110_enable_request
        && soc > params.shed_110v_ppt;

    let direct_hv_enabled = contactor_ok
        && !rail_faulted(Rail::DirectHv)
        && inputs.direct_hv_enable_request
        && soc > params.shed_direct_hv_ppt;

    // Shedding is any time at least one of the 110 V or direct-HV branches is down due
    // to SoC while the contactor is up and there's no fault.
    let load_shed_active = contactor_ok
        && (((soc <= params.shed_direct_hv_ppt) && !rail_faulted(Rail::DirectHv))
            || ((soc <= params.shed_110v_ppt) && !rail_faulted(Rail::V110)));

    // Latched fault mask: union of the now-faulted-and-in-cooldown.
    let mut faults = RailFaultMask(0);
    for &r in &Rail::ALL {
        if fault_until_ns[r as usize].is_some() {
            faults.insert(r);
        }
    }

    AuxOutput {
        state: AuxState {
            faults,
            fault_until_ns,
        },
        v24_enabled,
        v110_enabled,
        direct_hv_enabled,
        load_shed_active,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal_inputs(soc: u16) -> AuxInputs {
        AuxInputs {
            now_ns: 0,
            pack_soc_ppt: soc,
            pack_contactor_closed: true,
            v24_over_temp: false,
            v110_over_temp: false,
            direct_hv_over_temp: false,
            v24_drive_fault: false,
            v110_drive_fault: false,
            direct_hv_drive_fault: false,
            v24_enable_request: true,
            v110_enable_request: true,
            direct_hv_enable_request: true,
        }
    }

    #[test]
    fn high_soc_all_rails_enabled() {
        let out = aux_evaluate(
            &AuxState::default(),
            &nominal_inputs(800),
            &AuxParams::light_metro_default(),
        );
        assert!(out.v24_enabled);
        assert!(out.v110_enabled);
        assert!(out.direct_hv_enabled);
        assert!(!out.load_shed_active);
    }

    #[test]
    fn medium_soc_sheds_direct_hv() {
        let out = aux_evaluate(
            &AuxState::default(),
            &nominal_inputs(250), // below 300 shed_direct_hv
            &AuxParams::light_metro_default(),
        );
        assert!(out.v24_enabled);
        assert!(out.v110_enabled);
        assert!(!out.direct_hv_enabled);
        assert!(out.load_shed_active);
    }

    #[test]
    fn low_soc_sheds_110v_and_direct_hv() {
        let out = aux_evaluate(
            &AuxState::default(),
            &nominal_inputs(100),
            &AuxParams::light_metro_default(),
        );
        assert!(out.v24_enabled);
        assert!(!out.v110_enabled);
        assert!(!out.direct_hv_enabled);
        assert!(out.load_shed_active);
    }

    #[test]
    fn contactor_open_disables_all_rails() {
        let mut i = nominal_inputs(800);
        i.pack_contactor_closed = false;
        let out = aux_evaluate(&AuxState::default(), &i, &AuxParams::light_metro_default());
        assert!(!out.v24_enabled);
        assert!(!out.v110_enabled);
        assert!(!out.direct_hv_enabled);
    }

    #[test]
    fn rail_fault_disables_only_that_rail() {
        let mut i = nominal_inputs(800);
        i.v110_over_temp = true;
        let out = aux_evaluate(&AuxState::default(), &i, &AuxParams::light_metro_default());
        assert!(out.v24_enabled);
        assert!(!out.v110_enabled);
        assert!(out.direct_hv_enabled);
        assert!(out.state.faults.contains(Rail::V110));
    }

    #[test]
    fn fault_cooldown_latches() {
        let p = AuxParams::light_metro_default();
        let mut i = nominal_inputs(800);
        i.direct_hv_drive_fault = true;
        let state = aux_evaluate(&AuxState::default(), &i, &p).state;
        assert!(state.fault_until_ns[Rail::DirectHv as usize].is_some());

        // Clear fault at t=1s, still in 10s cooldown.
        let mut i = nominal_inputs(800);
        i.now_ns = 1_000_000_000;
        let out = aux_evaluate(&state, &i, &p);
        assert!(!out.direct_hv_enabled);
        assert!(out.state.faults.contains(Rail::DirectHv));

        // Past cooldown, rail re-enables.
        i.now_ns = 15_000_000_000;
        let out = aux_evaluate(&state, &i, &p);
        assert!(out.direct_hv_enabled);
    }

    #[test]
    fn disable_request_respected() {
        let mut i = nominal_inputs(800);
        i.direct_hv_enable_request = false;
        let out = aux_evaluate(&AuxState::default(), &i, &AuxParams::light_metro_default());
        assert!(!out.direct_hv_enabled);
        assert!(out.v24_enabled);
    }

    #[test]
    fn determinism() {
        let i = nominal_inputs(500);
        let p = AuxParams::light_metro_default();
        let a = aux_evaluate(&AuxState::default(), &i, &p);
        let b = aux_evaluate(&AuxState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
