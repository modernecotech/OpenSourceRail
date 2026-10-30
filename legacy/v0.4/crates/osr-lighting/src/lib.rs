//! OpenSourceRail lighting controller.
//!
//! SIL-0: normal failure degrades passenger experience. The
//! safety-critical piece is the **emergency egress lighting**,
//! which is hardware-backed: egress fixtures are directly on the
//! 24 V safety rail and include local battery backup at the
//! fixture level. This crate coordinates the *commanded* brightness
//! but is not load-bearing for fail-safe egress.
//!
//! Phase 2c crate 5 of [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # Controlled fixture groups
//!
//! - **Interior** (primary saloon lighting, 110 V rail). Falls back
//!   to "emergency egress only" when the 110 V rail sheds under low
//!   SoC.
//! - **Emergency egress** (aisles, exit paths, 24 V rail). Always on
//!   during motion; automatically elevated on `emergency_unlock` or
//!   loss of interior lighting.
//! - **Headlight + taillight** (exterior, 110 V). Direction-aware:
//!   headlight on the leading end, taillight on the trailing end.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum LightingMode {
    /// Train in service. Full interior, exterior headlight+taillight.
    #[default]
    Normal,
    /// Night-dimmed interior (driver request), same exterior.
    Dimmed,
    /// 110 V rail down OR emergency unlock asserted. Interior off;
    /// emergency egress fixtures bright.
    Emergency,
    /// Parked at depot — all off.
    Off,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Heading {
    Forward,
    Reverse,
}

// ---------------------------------------------------------------------------
// Inputs / params
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LightingInputs {
    pub now_ns: u64,
    pub mode_request: LightingMode,
    pub v110_rail_enabled: bool,
    pub v24_rail_enabled: bool,
    pub emergency_unlock: bool,
    pub heading: Heading,
    /// External light-sensor reading (lux). Used for headlight
    /// auto-dim. `None` if no sensor.
    pub ambient_lux: Option<u32>,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LightingParams {
    pub interior_normal_ppt: u16,
    pub interior_dimmed_ppt: u16,
    pub emergency_egress_bright_ppt: u16,
    pub emergency_egress_dim_ppt: u16,
    pub headlight_high_ppt: u16,
    pub headlight_low_ppt: u16,
    pub taillight_ppt: u16,
    /// Below this ambient lux, headlights switch to high beam
    /// (daylight sensor fallback is "always low" if `None`).
    pub auto_dim_threshold_lux: u32,
}

impl LightingParams {
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            interior_normal_ppt: 1000,
            interior_dimmed_ppt: 400,
            emergency_egress_bright_ppt: 1000,
            emergency_egress_dim_ppt: 300,
            headlight_high_ppt: 1000,
            headlight_low_ppt: 500,
            taillight_ppt: 700,
            auto_dim_threshold_lux: 200, // twilight
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct LightingOutput {
    pub mode: LightingMode,
    pub interior_ppt: u16,
    pub emergency_egress_ppt: u16,
    /// Leading end (forward-facing) headlight brightness.
    pub headlight_front_ppt: u16,
    /// Trailing end (rear-facing) tail light brightness.
    pub taillight_rear_ppt: u16,
    /// Leading end is the forward end of the consist.
    pub leading_end_is_forward: bool,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

/// One lighting-control tick. Pure.
#[must_use]
pub fn lighting_evaluate(inputs: &LightingInputs, params: &LightingParams) -> LightingOutput {
    // Effective mode is the union of the request and forced downgrades.
    let effective_mode = if inputs.emergency_unlock || !inputs.v110_rail_enabled {
        LightingMode::Emergency
    } else {
        inputs.mode_request
    };

    let leading_end_is_forward = matches!(inputs.heading, Heading::Forward);

    match effective_mode {
        LightingMode::Off => LightingOutput {
            mode: LightingMode::Off,
            interior_ppt: 0,
            emergency_egress_ppt: 0,
            headlight_front_ppt: 0,
            taillight_rear_ppt: 0,
            leading_end_is_forward,
        },
        LightingMode::Emergency => {
            // Interior off; egress bright if 24 V is up, dim
            // otherwise (fixture-level battery provides residual
            // illumination).
            let egress = if inputs.v24_rail_enabled {
                params.emergency_egress_bright_ppt
            } else {
                params.emergency_egress_dim_ppt
            };
            // Exterior runs on 110 V; if rail is down, no headlight.
            let head = if inputs.v110_rail_enabled {
                params.headlight_low_ppt
            } else {
                0
            };
            let tail = if inputs.v110_rail_enabled {
                params.taillight_ppt
            } else {
                0
            };
            LightingOutput {
                mode: LightingMode::Emergency,
                interior_ppt: 0,
                emergency_egress_ppt: egress,
                headlight_front_ppt: head,
                taillight_rear_ppt: tail,
                leading_end_is_forward,
            }
        }
        other => {
            // Normal / Dimmed — both require 110 V (checked above).
            let interior = match other {
                LightingMode::Normal => params.interior_normal_ppt,
                LightingMode::Dimmed => params.interior_dimmed_ppt,
                _ => 0,
            };
            let egress = if inputs.v24_rail_enabled {
                params.emergency_egress_dim_ppt
            } else {
                0
            };
            // Headlight beam choice.
            let headlight = match inputs.ambient_lux {
                Some(lx) if lx < params.auto_dim_threshold_lux => params.headlight_high_ppt,
                _ => params.headlight_low_ppt,
            };
            LightingOutput {
                mode: other,
                interior_ppt: interior,
                emergency_egress_ppt: egress,
                headlight_front_ppt: headlight,
                taillight_rear_ppt: params.taillight_ppt,
                leading_end_is_forward,
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal() -> LightingInputs {
        LightingInputs {
            now_ns: 0,
            mode_request: LightingMode::Normal,
            v110_rail_enabled: true,
            v24_rail_enabled: true,
            emergency_unlock: false,
            heading: Heading::Forward,
            ambient_lux: Some(1000),
        }
    }

    #[test]
    fn normal_mode_full_interior() {
        let out = lighting_evaluate(&nominal(), &LightingParams::light_metro_default());
        assert_eq!(out.mode, LightingMode::Normal);
        assert!(out.interior_ppt > 0);
        assert!(out.headlight_front_ppt > 0);
        assert!(out.taillight_rear_ppt > 0);
    }

    #[test]
    fn dimmed_mode_reduces_interior() {
        let p = LightingParams::light_metro_default();
        let mut i = nominal();
        i.mode_request = LightingMode::Dimmed;
        let out = lighting_evaluate(&i, &p);
        assert_eq!(out.interior_ppt, p.interior_dimmed_ppt);
    }

    #[test]
    fn v110_down_forces_emergency() {
        let mut i = nominal();
        i.v110_rail_enabled = false;
        let out = lighting_evaluate(&i, &LightingParams::light_metro_default());
        assert_eq!(out.mode, LightingMode::Emergency);
        assert_eq!(out.interior_ppt, 0);
        assert!(out.emergency_egress_ppt > 0);
    }

    #[test]
    fn emergency_unlock_forces_emergency() {
        let mut i = nominal();
        i.emergency_unlock = true;
        let out = lighting_evaluate(&i, &LightingParams::light_metro_default());
        assert_eq!(out.mode, LightingMode::Emergency);
    }

    #[test]
    fn night_auto_dim_uses_high_beam() {
        let p = LightingParams::light_metro_default();
        let mut i = nominal();
        i.ambient_lux = Some(50); // below threshold
        let out = lighting_evaluate(&i, &p);
        assert_eq!(out.headlight_front_ppt, p.headlight_high_ppt);
    }

    #[test]
    fn daylight_uses_low_beam() {
        let p = LightingParams::light_metro_default();
        let i = nominal();
        let out = lighting_evaluate(&i, &p);
        assert_eq!(out.headlight_front_ppt, p.headlight_low_ppt);
    }

    #[test]
    fn reverse_heading_swaps_leading_end() {
        let p = LightingParams::light_metro_default();
        let mut i = nominal();
        i.heading = Heading::Reverse;
        let out = lighting_evaluate(&i, &p);
        assert!(!out.leading_end_is_forward);
    }

    #[test]
    fn v24_down_in_emergency_degrades_egress() {
        let p = LightingParams::light_metro_default();
        let mut i = nominal();
        i.v110_rail_enabled = false;
        i.v24_rail_enabled = false;
        let out = lighting_evaluate(&i, &p);
        assert_eq!(out.emergency_egress_ppt, p.emergency_egress_dim_ppt);
    }

    #[test]
    fn off_mode_is_all_zero() {
        let mut i = nominal();
        i.mode_request = LightingMode::Off;
        let out = lighting_evaluate(&i, &LightingParams::light_metro_default());
        assert_eq!(out.interior_ppt, 0);
        assert_eq!(out.headlight_front_ppt, 0);
    }

    #[test]
    fn determinism() {
        let p = LightingParams::light_metro_default();
        let i = nominal();
        let a = lighting_evaluate(&i, &p);
        let b = lighting_evaluate(&i, &p);
        assert_eq!(a, b);
    }
}
