//! JSON telemetry export from the existing energy evaluator for the OSR gateway.
//! Sensor temperatures are explicit simulator fixtures, never inferred measurements.
use osr_energy_site::{energy_site_evaluate, EnergySiteInputs, EnergySiteParams};

fn main() {
    let inputs = EnergySiteInputs {
        now_ns: 0,
        pv_w: 240_000,
        pad_request_w: 180_000,
        battery_soc_ppt: 720,
        battery_charge_limit_w: 250_000,
        battery_discharge_limit_w: 250_000,
        grid_up: true,
        export_allowed: false,
    };
    let output = energy_site_evaluate(&inputs, &EnergySiteParams::default_samawah());
    println!(
        "{{\"schema\":\"osr-energy-site/1\",\"pv_w\":{},\"battery_soc_ppt\":{},\"to_pad_w\":{},\"battery_charge_w\":{},\"battery_discharge_w\":{},\"grid_import_w\":{}}}",
        inputs.pv_w, inputs.battery_soc_ppt, output.to_pad_w,
        output.battery_charge_w, output.battery_discharge_w, output.grid_import_w
    );
}
