//! OpenSourceRail HVAC climate-control loop.
//!
//! SIL-0: failure degrades passenger comfort but not safety. The
//! controller produces three actuator outputs:
//!
//! - `compressor_ppt` — cooling load, 0..=1000 (AC compressor)
//! - `heater_ppt` — electric or heat-pump reverse cycle, 0..=1000
//! - `fan_ppt` — ventilation / recirculation, 0..=1000
//!
//! Phase 2c crate 4 of [RFC 0005 §4.2](../../../docs/rfcs/0005-sbc-software-architecture.md).
//!
//! # Control law
//!
//! A proportional-integral loop on `error = setpoint − cabin_temp`.
//! Positive error (cabin too cold) → heat; negative error → cool;
//! within the deadband → fan only.
//!
//! The 400 V AC rail (from [`osr_aux_power`]) powers the compressor
//! and heater. When that rail is off (either faulted or load-shed
//! under low SoC), the controller enters `Reduced` mode: fans-only
//! ventilation, no active heating or cooling.
//!
//! Under the Samawah reference climate (42 °C ambient, 25 °C
//! setpoint, [RFC 0003 §4.2](../../../docs/rfcs/0003-samawah-reference-deployment.md))
//! the controller spends most of its time commanding full compressor
//! and high fan; the load-shed gate is what actually drops
//! passenger-car HVAC when the pack's SoC runs low.

#![forbid(unsafe_code)]

use serde::{Deserialize, Serialize};

// ---------------------------------------------------------------------------
// Inputs / params
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HvacInputs {
    pub now_ns: u64,
    pub dt_ns: u64,
    /// Cabin temperature, tenths of °C.
    pub cabin_temp_dc: i16,
    /// Ambient temperature, tenths of °C.
    pub ambient_temp_dc: i16,
    /// Target cabin temperature, tenths of °C. Typically 220–240 dC.
    pub setpoint_dc: i16,
    /// 400 V AC aux rail available — required for compressor/heater.
    pub v400_rail_enabled: bool,
    /// Driver's HVAC enable switch.
    pub hvac_enable_request: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HvacParams {
    /// Proportional gain in ppt per dC (tenths of °C) of error.
    pub kp_ppt_per_dc: i32,
    /// Integral gain in ppt per (dC · s).
    pub ki_ppt_per_dc_s: i32,
    /// Anti-windup clamp on the integral term (ppt).
    pub max_integral_ppt: i32,
    /// Deadband around setpoint (dC) where no active heat/cool.
    pub deadband_dc: i16,
    /// Maximum compressor effort (ppt). Usually 1000.
    pub max_compressor_ppt: u16,
    /// Maximum heater effort (ppt).
    pub max_heater_ppt: u16,
    /// Baseline fan speed when idle (ppt).
    pub idle_fan_ppt: u16,
    /// Max fan speed (ppt).
    pub max_fan_ppt: u16,
}

impl HvacParams {
    #[must_use]
    pub fn light_metro_default() -> Self {
        Self {
            kp_ppt_per_dc: 40, // 40 ppt per 0.1 °C = 400 ppt per °C
            ki_ppt_per_dc_s: 2,
            max_integral_ppt: 600,
            deadband_dc: 5,
            max_compressor_ppt: 1000,
            max_heater_ppt: 1000,
            idle_fan_ppt: 200,
            max_fan_ppt: 1000,
        }
    }
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

#[derive(Copy, Clone, Debug, PartialEq, Eq, Hash, Default, Serialize, Deserialize)]
pub enum HvacMode {
    #[default]
    Off,
    /// In deadband — fans only.
    Ventilating,
    Cooling,
    Heating,
    /// 400 V rail down; degraded fans-only mode.
    Reduced,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct HvacState {
    pub integral_ppt: i64,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct HvacOutput {
    pub state: HvacState,
    pub mode: HvacMode,
    pub compressor_ppt: u16,
    pub heater_ppt: u16,
    pub fan_ppt: u16,
}

// ---------------------------------------------------------------------------
// Evaluator
// ---------------------------------------------------------------------------

/// One HVAC tick. Pure.
#[must_use]
pub fn hvac_evaluate(prev: &HvacState, inputs: &HvacInputs, params: &HvacParams) -> HvacOutput {
    // Off when disabled.
    if !inputs.hvac_enable_request {
        return HvacOutput {
            state: HvacState { integral_ppt: 0 },
            mode: HvacMode::Off,
            compressor_ppt: 0,
            heater_ppt: 0,
            fan_ppt: 0,
        };
    }

    // Reduced mode when 400 V rail is unavailable.
    if !inputs.v400_rail_enabled {
        return HvacOutput {
            state: HvacState { integral_ppt: 0 },
            mode: HvacMode::Reduced,
            compressor_ppt: 0,
            heater_ppt: 0,
            fan_ppt: params.idle_fan_ppt,
        };
    }

    // Error: + = too cold (want heat), − = too hot (want cool).
    let err_dc = inputs.setpoint_dc.saturating_sub(inputs.cabin_temp_dc);

    // Integrator update.
    let dt_ms = inputs.dt_ns / 1_000_000;
    let mut integral = prev.integral_ppt;
    if err_dc.unsigned_abs() as i16 > params.deadband_dc {
        let delta = i64::from(err_dc)
            .saturating_mul(i64::from(params.ki_ppt_per_dc_s))
            .saturating_mul(dt_ms as i64)
            / 1_000;
        integral = integral.saturating_add(delta);
    }
    let clamp = i64::from(params.max_integral_ppt);
    integral = integral.clamp(-clamp, clamp);

    let p_term = i64::from(err_dc).saturating_mul(i64::from(params.kp_ppt_per_dc));
    let demand = p_term.saturating_add(integral);

    // Partition into heater (+demand) vs compressor (-demand).
    let (compressor_ppt, heater_ppt, mode) =
        if err_dc.unsigned_abs() as i16 <= params.deadband_dc {
            (0u16, 0u16, HvacMode::Ventilating)
        } else if demand > 0 {
            let h = demand.clamp(0, i64::from(params.max_heater_ppt)) as u16;
            (0u16, h, HvacMode::Heating)
        } else {
            let c = (-demand).clamp(0, i64::from(params.max_compressor_ppt)) as u16;
            (c, 0u16, HvacMode::Cooling)
        };

    // Fan ramps between idle and max based on the greater of
    // compressor/heater demand.
    let load = compressor_ppt.max(heater_ppt);
    let fan_range =
        i64::from(params.max_fan_ppt).saturating_sub(i64::from(params.idle_fan_ppt)).max(0);
    let fan_bonus = (i64::from(load) * fan_range / 1_000).max(0);
    let fan_ppt = (i64::from(params.idle_fan_ppt) + fan_bonus)
        .clamp(0, i64::from(params.max_fan_ppt)) as u16;

    HvacOutput {
        state: HvacState { integral_ppt: integral },
        mode,
        compressor_ppt,
        heater_ppt,
        fan_ppt,
    }
}

// ---------------------------------------------------------------------------
// Unit tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal(cabin: i16, setpoint: i16) -> HvacInputs {
        HvacInputs {
            now_ns: 0,
            dt_ns: 1_000_000_000,
            cabin_temp_dc: cabin,
            ambient_temp_dc: 400,
            setpoint_dc: setpoint,
            v400_rail_enabled: true,
            hvac_enable_request: true,
        }
    }

    #[test]
    fn disabled_outputs_zero() {
        let mut i = nominal(300, 230);
        i.hvac_enable_request = false;
        let out = hvac_evaluate(&HvacState::default(), &i, &HvacParams::light_metro_default());
        assert_eq!(out.mode, HvacMode::Off);
        assert_eq!(out.compressor_ppt, 0);
    }

    #[test]
    fn rail_down_is_reduced() {
        let mut i = nominal(400, 230);
        i.v400_rail_enabled = false;
        let out = hvac_evaluate(&HvacState::default(), &i, &HvacParams::light_metro_default());
        assert_eq!(out.mode, HvacMode::Reduced);
        assert_eq!(out.compressor_ppt, 0);
        assert_eq!(out.heater_ppt, 0);
        assert!(out.fan_ppt > 0);
    }

    #[test]
    fn hot_cabin_cools() {
        let out = hvac_evaluate(
            &HvacState::default(),
            &nominal(400, 230), // 40 °C cabin, 23 °C target
            &HvacParams::light_metro_default(),
        );
        assert_eq!(out.mode, HvacMode::Cooling);
        assert!(out.compressor_ppt > 0);
        assert_eq!(out.heater_ppt, 0);
    }

    #[test]
    fn cold_cabin_heats() {
        let out = hvac_evaluate(
            &HvacState::default(),
            &nominal(100, 230), // 10 °C cabin
            &HvacParams::light_metro_default(),
        );
        assert_eq!(out.mode, HvacMode::Heating);
        assert!(out.heater_ppt > 0);
        assert_eq!(out.compressor_ppt, 0);
    }

    #[test]
    fn in_deadband_ventilates() {
        let p = HvacParams::light_metro_default();
        // cabin = setpoint: within deadband
        let out = hvac_evaluate(&HvacState::default(), &nominal(230, 230), &p);
        assert_eq!(out.mode, HvacMode::Ventilating);
        assert_eq!(out.compressor_ppt, 0);
        assert_eq!(out.heater_ppt, 0);
        assert_eq!(out.fan_ppt, p.idle_fan_ppt);
    }

    #[test]
    fn determinism() {
        let p = HvacParams::light_metro_default();
        let i = nominal(400, 230);
        let a = hvac_evaluate(&HvacState::default(), &i, &p);
        let b = hvac_evaluate(&HvacState::default(), &i, &p);
        assert_eq!(a, b);
    }
}
