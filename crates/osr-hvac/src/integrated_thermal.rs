//! Integrated but physically separated cabin and battery thermal management.
//!
//! A compact common refrigerant plant can serve two isolated coolant/air
//! circuits, similar in architecture to modern rail combined cooling packs.
//! Battery temperature protection always has priority over passenger comfort.
//! A leak, pump fault, implausible sensor, or unavailable compressor never
//! suppresses the protection request sent to the BMS/traction boundary.
//!
//! This is deterministic controller logic and design-screening evidence. It
//! does not replace refrigerant, pressure, fire, environmental, EMC, vibration,
//! type, routine, or first-article tests on the selected physical equipment.

use serde::{Deserialize, Serialize};

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct IntegratedThermalInputs {
    /// Cabin and ambient temperatures in tenths of a degree Celsius.
    pub cabin_temp_dc: i16,
    pub ambient_temp_dc: i16,
    pub cabin_setpoint_dc: i16,
    /// Battery coolant and hottest-cell temperatures in tenths of °C.
    pub battery_coolant_temp_dc: i16,
    pub battery_max_cell_temp_dc: i16,
    pub compressor_available: bool,
    pub cabin_fan_available: bool,
    pub battery_pump_available: bool,
    pub battery_circuit_pressure_ok: bool,
    pub battery_temperature_sensor_plausible: bool,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct IntegratedThermalParams {
    pub battery_target_dc: i16,
    pub battery_derate_dc: i16,
    pub battery_trip_dc: i16,
    pub battery_deadband_dc: i16,
    /// Total common compressor capacity in parts per thousand.
    pub compressor_capacity_ppt: u16,
    pub cabin_min_ventilation_ppt: u16,
}

impl IntegratedThermalParams {
    #[must_use]
    pub fn light_metro_hot_climate() -> Self {
        Self {
            battery_target_dc: 280,
            battery_derate_dc: 450,
            battery_trip_dc: 550,
            battery_deadband_dc: 20,
            compressor_capacity_ppt: 1000,
            cabin_min_ventilation_ppt: 250,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum BatteryThermalMode {
    Nominal,
    Cooling,
    Derate,
    Protect,
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct IntegratedThermalOutput {
    pub battery_mode: BatteryThermalMode,
    pub battery_chiller_ppt: u16,
    pub battery_pump_ppt: u16,
    pub cabin_compressor_ppt: u16,
    pub cabin_fan_ppt: u16,
    pub traction_derate_request: bool,
    pub battery_isolation_request: bool,
    pub cabin_comfort_degraded: bool,
}

/// Allocate a shared refrigerant plant while keeping cabin and battery media
/// separated and prioritising battery protection.
#[must_use]
pub fn thermal_evaluate(
    inputs: &IntegratedThermalInputs,
    params: &IntegratedThermalParams,
) -> IntegratedThermalOutput {
    let sensor_or_circuit_fault = !inputs.battery_temperature_sensor_plausible
        || !inputs.battery_circuit_pressure_ok
        || !inputs.battery_pump_available;
    let hot = inputs.battery_max_cell_temp_dc;
    let battery_mode = if sensor_or_circuit_fault || hot >= params.battery_trip_dc {
        BatteryThermalMode::Protect
    } else if hot >= params.battery_derate_dc {
        BatteryThermalMode::Derate
    } else if hot
        > params
            .battery_target_dc
            .saturating_add(params.battery_deadband_dc)
    {
        BatteryThermalMode::Cooling
    } else {
        BatteryThermalMode::Nominal
    };

    let requested_battery = match battery_mode {
        BatteryThermalMode::Protect | BatteryThermalMode::Derate => 1000,
        BatteryThermalMode::Cooling => {
            let excess = i32::from(hot.saturating_sub(params.battery_target_dc));
            (excess.saturating_mul(10)).clamp(250, 1000) as u16
        }
        BatteryThermalMode::Nominal => 0,
    };
    let battery_chiller_ppt = if inputs.compressor_available && !sensor_or_circuit_fault {
        requested_battery.min(params.compressor_capacity_ppt)
    } else {
        0
    };
    let remaining = params
        .compressor_capacity_ppt
        .saturating_sub(battery_chiller_ppt);
    let cabin_hot = inputs
        .cabin_temp_dc
        .saturating_sub(inputs.cabin_setpoint_dc);
    let cabin_request = (i32::from(cabin_hot).saturating_mul(20)).clamp(0, 1000) as u16;
    let cabin_compressor_ppt = if inputs.compressor_available && inputs.cabin_fan_available {
        cabin_request.min(remaining)
    } else {
        0
    };
    let cabin_fan_ppt = if inputs.cabin_fan_available {
        params.cabin_min_ventilation_ppt.max(cabin_compressor_ppt)
    } else {
        0
    };
    let cooling_unavailable = requested_battery > battery_chiller_ppt;

    IntegratedThermalOutput {
        battery_mode,
        battery_chiller_ppt,
        battery_pump_ppt: if inputs.battery_pump_available && inputs.battery_circuit_pressure_ok {
            requested_battery.max(200)
        } else {
            0
        },
        cabin_compressor_ppt,
        cabin_fan_ppt,
        traction_derate_request: matches!(
            battery_mode,
            BatteryThermalMode::Derate | BatteryThermalMode::Protect
        ) || cooling_unavailable,
        battery_isolation_request: matches!(battery_mode, BatteryThermalMode::Protect),
        cabin_comfort_degraded: cabin_request > cabin_compressor_ppt,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn nominal(cell: i16) -> IntegratedThermalInputs {
        IntegratedThermalInputs {
            cabin_temp_dc: 400,
            ambient_temp_dc: 500,
            cabin_setpoint_dc: 230,
            battery_coolant_temp_dc: 300,
            battery_max_cell_temp_dc: cell,
            compressor_available: true,
            cabin_fan_available: true,
            battery_pump_available: true,
            battery_circuit_pressure_ok: true,
            battery_temperature_sensor_plausible: true,
        }
    }

    #[test]
    fn battery_cooling_has_priority_over_cabin_comfort() {
        let out = thermal_evaluate(
            &nominal(470),
            &IntegratedThermalParams::light_metro_hot_climate(),
        );
        assert_eq!(out.battery_mode, BatteryThermalMode::Derate);
        assert_eq!(out.battery_chiller_ppt, 1000);
        assert_eq!(out.cabin_compressor_ppt, 0);
        assert!(out.traction_derate_request && out.cabin_comfort_degraded);
    }

    #[test]
    fn battery_loop_leak_requests_isolation() {
        let mut inputs = nominal(300);
        inputs.battery_circuit_pressure_ok = false;
        let out = thermal_evaluate(&inputs, &IntegratedThermalParams::light_metro_hot_climate());
        assert_eq!(out.battery_mode, BatteryThermalMode::Protect);
        assert!(out.battery_isolation_request);
        assert_eq!(out.battery_pump_ppt, 0);
    }

    #[test]
    fn nominal_battery_leaves_capacity_for_cabin() {
        let out = thermal_evaluate(
            &nominal(280),
            &IntegratedThermalParams::light_metro_hot_climate(),
        );
        assert_eq!(out.battery_mode, BatteryThermalMode::Nominal);
        assert!(out.cabin_compressor_ppt > 0);
        assert!(!out.traction_derate_request);
    }
}
