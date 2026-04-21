//! OpenSourceRail regen arbiter.
//!
//! When the traction inverter is decelerating, the motor generates
//! current that has to go somewhere. `osr-regen` decides how that
//! current is divided between:
//!
//! 1. the **onboard pack** (via the BMS's `charge_limit_ma`),
//! 2. a **dump resistor** if one is present and healthy,
//! 3. **refusal** — tell traction to reduce regen torque (the
//!    remainder the pack + resistor can't absorb).
//!
//! Phase 2b crate 4 of
//! [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md).
//! SIL-2 — a bad decision here is an energy-efficiency issue or a
//! minor ride-quality issue (via refused regen), never a safety issue.
//!
//! # API shape
//!
//! One pure function [`regen_evaluate`]. The caller holds the state
//! (none needed for v1 — this is a stateless arbiter).
//!
//! # Properties (proptest-verified)
//!
//! - **R1 determinism:** pure.
//! - **R2 current conservation:**
//!   `to_pack + to_resistor + refused == requested`.
//! - **R3 pack limit:** `to_pack ≤ bms_charge_limit_ma`.
//! - **R4 contactor respected:** `to_pack == 0` when the BMS
//!   contactor is not closed.
//! - **R5 resistor fault:** `to_resistor == 0` when the resistor is
//!   unavailable or over-temp.
//! - **R6 resistor bound:** `to_resistor ≤ resistor_max_ma`.
//! - **R7 prefer pack:** if both sinks are available and the pack
//!   can absorb the full request, `to_resistor == 0`.
//!
//! # Coding-standard compliance
//!
//! - `#![forbid(unsafe_code)]`.
//! - Integer-only (mA, ns).
//! - No allocation.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Input
// ---------------------------------------------------------------------------

/// Per-tick inputs to the regen arbiter.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RegenInputs {
    pub now_ns: u64,
    /// Regen current offered by the traction converter (mA, positive).
    /// Zero when the train is motoring.
    pub requested_ma: u32,
    /// From [`osr_bms`]: current the pack will accept (mA).
    pub bms_charge_limit_ma: u32,
    /// Main pack contactor closed? If not, no current to pack.
    pub bms_contactor_closed: bool,
    /// Is a dump resistor installed and electrically available?
    pub resistor_available: bool,
    /// Dump-resistor thermal protection tripped?
    pub resistor_over_temp: bool,
}

/// Fixed arbiter parameters.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RegenParams {
    /// Maximum current the dump resistor can dissipate, mA.
    pub resistor_max_ma: u32,
    /// When `true` and both sinks are available, prefer the pack
    /// (the default — maximises energy recovery). Disable to
    /// prefer the resistor (used by bench tests).
    pub prefer_pack: bool,
}

impl RegenParams {
    #[must_use]
    pub fn default_with_resistor(resistor_max_ma: u32) -> Self {
        Self {
            resistor_max_ma,
            prefer_pack: true,
        }
    }

    #[must_use]
    pub fn pack_only() -> Self {
        Self {
            resistor_max_ma: 0,
            prefer_pack: true,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

/// Where each chunk of regen current is routed.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct RegenOutput {
    /// Current absorbed by the pack, mA. `≤ bms_charge_limit_ma` and
    /// zero when the contactor is open.
    pub to_pack_ma: u32,
    /// Current dumped to the resistor, mA. `≤ resistor_max_ma` and
    /// zero when the resistor is unavailable / over-temp.
    pub to_resistor_ma: u32,
    /// Current the arbiter cannot absorb — traction must refuse this
    /// much torque (and the brake crate picks up friction to make
    /// up the difference).
    pub refused_ma: u32,
    pub mode: RegenMode,
}

/// Routing mode for diagnostics.
#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum RegenMode {
    /// Nothing to regenerate this tick.
    #[default]
    Idle,
    /// All regen to pack.
    AllPack,
    /// All regen to dump resistor.
    AllResistor,
    /// Split between pack and resistor.
    Blended,
    /// Some (or all) refused — sinks couldn't absorb.
    PartiallyRefused,
    /// Everything refused — no sink available.
    FullyRefused,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

/// Arbitrate one tick of regen current. Pure function.
#[must_use]
pub fn regen_evaluate(inputs: &RegenInputs, params: &RegenParams) -> RegenOutput {
    let requested = inputs.requested_ma;
    if requested == 0 {
        return RegenOutput {
            to_pack_ma: 0,
            to_resistor_ma: 0,
            refused_ma: 0,
            mode: RegenMode::Idle,
        };
    }

    // Effective sink capacities this tick.
    let pack_cap = if inputs.bms_contactor_closed {
        inputs.bms_charge_limit_ma
    } else {
        0
    };
    let resistor_cap = if inputs.resistor_available && !inputs.resistor_over_temp {
        params.resistor_max_ma
    } else {
        0
    };

    // Route. The `prefer_pack` flag chooses which sink gets filled
    // first; the other takes the overflow.
    let (first_cap, second_cap) = if params.prefer_pack {
        (pack_cap, resistor_cap)
    } else {
        (resistor_cap, pack_cap)
    };

    let first = requested.min(first_cap);
    let remainder = requested.saturating_sub(first);
    let second = remainder.min(second_cap);
    let refused = remainder.saturating_sub(second);

    let (to_pack, to_resistor) = if params.prefer_pack {
        (first, second)
    } else {
        (second, first)
    };

    // Mode rollup.
    let mode = match (to_pack, to_resistor, refused) {
        (0, 0, _) if refused > 0 => RegenMode::FullyRefused,
        (_, 0, 0) if to_pack == requested => RegenMode::AllPack,
        (0, _, 0) if to_resistor == requested => RegenMode::AllResistor,
        (_, _, 0) if to_pack > 0 && to_resistor > 0 => RegenMode::Blended,
        (_, _, _) if refused > 0 => RegenMode::PartiallyRefused,
        _ => RegenMode::Blended, // fallback; shouldn't hit
    };

    RegenOutput {
        to_pack_ma: to_pack,
        to_resistor_ma: to_resistor,
        refused_ma: refused,
        mode,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn inputs(req: u32, charge: u32, contactor: bool, res_ok: bool) -> RegenInputs {
        RegenInputs {
            now_ns: 0,
            requested_ma: req,
            bms_charge_limit_ma: charge,
            bms_contactor_closed: contactor,
            resistor_available: res_ok,
            resistor_over_temp: false,
        }
    }

    #[test]
    fn zero_request_is_idle() {
        let out = regen_evaluate(
            &inputs(0, 500_000, true, true),
            &RegenParams::default_with_resistor(500_000),
        );
        assert_eq!(out.to_pack_ma, 0);
        assert_eq!(out.to_resistor_ma, 0);
        assert_eq!(out.refused_ma, 0);
        assert_eq!(out.mode, RegenMode::Idle);
    }

    #[test]
    fn pack_absorbs_full_request() {
        let out = regen_evaluate(
            &inputs(200_000, 500_000, true, true),
            &RegenParams::default_with_resistor(500_000),
        );
        assert_eq!(out.to_pack_ma, 200_000);
        assert_eq!(out.to_resistor_ma, 0);
        assert_eq!(out.refused_ma, 0);
        assert_eq!(out.mode, RegenMode::AllPack);
    }

    #[test]
    fn resistor_picks_up_pack_shortfall() {
        let out = regen_evaluate(
            &inputs(800_000, 500_000, true, true),
            &RegenParams::default_with_resistor(500_000),
        );
        assert_eq!(out.to_pack_ma, 500_000);
        assert_eq!(out.to_resistor_ma, 300_000);
        assert_eq!(out.refused_ma, 0);
        assert_eq!(out.mode, RegenMode::Blended);
    }

    #[test]
    fn contactor_open_routes_all_to_resistor() {
        let out = regen_evaluate(
            &inputs(300_000, 500_000, false, true),
            &RegenParams::default_with_resistor(500_000),
        );
        assert_eq!(out.to_pack_ma, 0);
        assert_eq!(out.to_resistor_ma, 300_000);
        assert_eq!(out.mode, RegenMode::AllResistor);
    }

    #[test]
    fn no_sink_refuses_everything() {
        let out = regen_evaluate(
            &inputs(300_000, 0, true, false),
            &RegenParams::pack_only(),
        );
        assert_eq!(out.to_pack_ma, 0);
        assert_eq!(out.to_resistor_ma, 0);
        assert_eq!(out.refused_ma, 300_000);
        assert_eq!(out.mode, RegenMode::FullyRefused);
    }

    #[test]
    fn resistor_over_temp_disables_resistor() {
        let mut i = inputs(600_000, 200_000, true, true);
        i.resistor_over_temp = true;
        let out = regen_evaluate(&i, &RegenParams::default_with_resistor(500_000));
        assert_eq!(out.to_pack_ma, 200_000);
        assert_eq!(out.to_resistor_ma, 0);
        assert_eq!(out.refused_ma, 400_000);
        assert_eq!(out.mode, RegenMode::PartiallyRefused);
    }

    #[test]
    fn determinism() {
        let i = inputs(123_456, 100_000, true, true);
        let p = RegenParams::default_with_resistor(50_000);
        let a = regen_evaluate(&i, &p);
        let b = regen_evaluate(&i, &p);
        assert_eq!(a, b);
    }
}
