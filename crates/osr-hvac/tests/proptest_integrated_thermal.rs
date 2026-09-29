use osr_hvac::{
    thermal_evaluate, BatteryThermalMode, IntegratedThermalInputs, IntegratedThermalParams,
};
use proptest::prelude::*;

proptest! {
    #[test]
    fn allocation_never_exceeds_common_compressor(cell in -400i16..900, cabin in -400i16..900) {
        let params = IntegratedThermalParams::light_metro_hot_climate();
        let out = thermal_evaluate(&IntegratedThermalInputs { cabin_temp_dc: cabin, ambient_temp_dc: 500,
            cabin_setpoint_dc: 230, battery_coolant_temp_dc: cell, battery_max_cell_temp_dc: cell,
            compressor_available: true, cabin_fan_available: true, battery_pump_available: true,
            battery_circuit_pressure_ok: true, battery_temperature_sensor_plausible: true }, &params);
        prop_assert!(u32::from(out.battery_chiller_ppt) + u32::from(out.cabin_compressor_ppt) <= u32::from(params.compressor_capacity_ppt));
    }

    #[test]
    fn failed_battery_circuit_never_reports_nominal(cell in -400i16..900) {
        let out = thermal_evaluate(&IntegratedThermalInputs { cabin_temp_dc: 230, ambient_temp_dc: 300,
            cabin_setpoint_dc: 230, battery_coolant_temp_dc: cell, battery_max_cell_temp_dc: cell,
            compressor_available: true, cabin_fan_available: true, battery_pump_available: false,
            battery_circuit_pressure_ok: false, battery_temperature_sensor_plausible: true },
            &IntegratedThermalParams::light_metro_hot_climate());
        prop_assert_eq!(out.battery_mode, BatteryThermalMode::Protect);
        prop_assert!(out.battery_isolation_request);
    }
}
