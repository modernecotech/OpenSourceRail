//! Research-only software-in-loop boundary; commissioning and target I/O remain open.
//! Parameters are supplied explicitly, never selected from a chemistry label.
use osr_bms::{bms_evaluate, BmsInputs, BmsParams, BmsState, ContactorCommand, ContactorState};
use osr_brake::{brake_evaluate, BrakeInputs, BrakeParams};
use osr_hvac::integrated_thermal::{
    thermal_evaluate, IntegratedThermalInputs, IntegratedThermalParams,
};
use osr_traction::{traction_evaluate, TractionInputs, TractionParams, TractionState};
use serde::Deserialize;
use serde_json::{json, Value};
use std::io::{self, BufRead, Write};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    now_ns: u64,
    dt_ns: u64,
    configuration_sha256: String,
    initial_soc_ppt: u16,
    bms_params: BmsParams,
    cell_voltages_mv: Vec<u16>,
    cell_temps_dc: Vec<i16>,
    pack_voltage_mv: u32,
    /// Plant discharge-positive convention; converted once at the BMS boundary.
    plant_discharge_current_ma: i32,
    off_gas_detected: bool,
    external_fire_trip: bool,
    contactor_command: ContactorCommand,
    thermal_inputs: IntegratedThermalInputs,
    thermal_params: IntegratedThermalParams,
    brake_inputs: BrakeInputs,
    brake_params: BrakeParams,
    traction_inputs: TractionInputs,
    traction_params: TractionParams,
    /// Research calibration: effective wheel torque at full normalized braking.
    regen_full_effort_torque_mnm: u32,
}
#[derive(Default)]
struct State {
    bms: Option<BmsState>,
    traction: TractionState,
    last_ns: u64,
    configuration: Option<String>,
    params: Option<String>,
}
fn evaluate(input: Input, state: &mut State) -> Result<Value, &'static str> {
    if input.configuration_sha256.len() != 64
        || !input
            .configuration_sha256
            .bytes()
            .all(|b| b.is_ascii_hexdigit())
    {
        return Err("Invalid configuration identity");
    }
    if input.now_ns <= state.last_ns
        || input.dt_ns == 0
        || input.dt_ns > 30_000_000_000
        || (state.last_ns != 0 && input.now_ns - state.last_ns != input.dt_ns)
    {
        return Err("Controller clock discontinuity");
    }
    if state
        .configuration
        .as_ref()
        .is_some_and(|v| v != &input.configuration_sha256)
    {
        return Err("Configuration changed without explicit state migration");
    }
    let params = serde_json::to_string(&json!([
        input.bms_params,
        input.thermal_params,
        input.brake_params,
        input.traction_params,
        input.regen_full_effort_torque_mnm
    ]))
    .map_err(|_| "Parameter encoding failed")?;
    if state.params.as_ref().is_some_and(|p| p != &params) {
        return Err("Controller calibration changed during a run");
    }
    let p = &input.bms_params;
    if input.initial_soc_ppt > 1000
        || input.regen_full_effort_torque_mnm == 0
        || p.cell_count == 0
        || p.cell_capacity_mah == 0
        || !(p.v_trip_min_mv < p.v_warn_min_mv
            && p.v_warn_min_mv < p.v_warn_max_mv
            && p.v_warn_max_mv < p.v_trip_max_mv)
        || !(p.t_trip_min_dc < p.t_warn_min_dc
            && p.t_warn_min_dc < p.t_warn_max_dc
            && p.t_warn_max_dc < p.t_trip_max_dc)
        || p.max_charge_ma >= p.current_trip_ma
        || p.max_discharge_ma >= p.current_trip_ma
    {
        return Err("Invalid research BMS calibration");
    }
    let current = input
        .plant_discharge_current_ma
        .checked_neg()
        .ok_or("BMS current sign conversion overflow")?;
    let thermal = thermal_evaluate(&input.thermal_inputs, &input.thermal_params);
    let previous = state
        .bms
        .unwrap_or_else(|| BmsState::initial(input.initial_soc_ppt));
    let bms = bms_evaluate(
        &previous,
        &BmsInputs {
            now_ns: input.now_ns,
            dt_ns: input.dt_ns,
            cell_voltages_mv: &input.cell_voltages_mv,
            cell_temps_dc: &input.cell_temps_dc,
            pack_current_ma: current,
            pack_voltage_mv: input.pack_voltage_mv,
            off_gas_detected: input.off_gas_detected,
            external_fire_trip: input.external_fire_trip || thermal.battery_isolation_request,
            hazard_module_id: None,
            hazard_string_id: None,
            external_command: input.contactor_command,
        },
        &input.bms_params,
    );
    let mut brake_inputs = input.brake_inputs;
    brake_inputs.now_ns = input.now_ns;
    let accepted_torque_mnm = u64::from(bms.charge_limit_ma)
        * u64::from(input.traction_params.torque_constant_unmpma)
        / 1000;
    let accepted_effort_ppt = (accepted_torque_mnm * 1000
        / u64::from(input.regen_full_effort_torque_mnm))
    .min(1000) as u16;
    brake_inputs.regen_available_ppt = brake_inputs.regen_available_ppt.min(accepted_effort_ppt);
    let brake = brake_evaluate(&brake_inputs, &input.brake_params);
    let mut traction_inputs = input.traction_inputs;
    traction_inputs.now_ns = input.now_ns;
    traction_inputs.bms_contactor_closed = bms.contactor == ContactorState::Closed;
    traction_inputs.bms_discharge_limit_ma = bms.discharge_limit_ma;
    traction_inputs.bms_charge_limit_ma = bms.charge_limit_ma;
    traction_inputs.pack_voltage_mv = input.pack_voltage_mv;
    if thermal.traction_derate_request {
        traction_inputs.torque_setpoint_mnm /= 2;
    }
    if brake.traction_cut && traction_inputs.torque_setpoint_mnm > 0 {
        traction_inputs.torque_setpoint_mnm = 0;
    }
    // Regeneration is limited by both native brake blending and BMS acceptance.
    if traction_inputs.torque_setpoint_mnm < 0 {
        traction_inputs.torque_setpoint_mnm = ((i64::from(traction_inputs.torque_setpoint_mnm)
            * i64::from(brake.regen_request_ppt))
            / 1000) as i32;
    }
    let traction = traction_evaluate(&state.traction, &traction_inputs, &input.traction_params);
    state.bms = Some(bms.state);
    state.traction = traction.state;
    state.last_ns = input.now_ns;
    state.configuration = Some(input.configuration_sha256.clone());
    state.params = Some(params);
    Ok(
        json!({"configuration_sha256":input.configuration_sha256,"now_ns":input.now_ns,
        "bms":bms,"thermal":thermal,"brake":brake,"traction":traction,
        "physical_validation":false,"commissioned":false,"hardware_in_loop":false}),
    )
}
fn main() {
    let mut state = State::default();
    let stdin = io::stdin();
    let mut stdout = io::stdout().lock();
    for line in stdin.lock().lines() {
        let result = line
            .map_err(|_| "Input read failed")
            .and_then(|line| {
                serde_json::from_str::<Input>(&line).map_err(|_| "Invalid controller input")
            })
            .and_then(|input| evaluate(input, &mut state));
        let value = match result {
            Ok(value) => value,
            Err(error) => json!({"error":error}),
        };
        if writeln!(stdout, "{value}")
            .and_then(|_| stdout.flush())
            .is_err()
        {
            break;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> Input {
        serde_json::from_str(include_str!(
            "../../../engineering/integration_programme/data/controller-input.json"
        ))
        .unwrap()
    }
    #[test]
    fn feedback_sign_and_protection_cross_actual_native_evaluators() {
        let mut s = State::default();
        let first = evaluate(fixture(), &mut s).unwrap();
        assert_eq!(first["bms"]["contactor"], "Closed");
        let mut second = fixture();
        second.now_ns = 11_000_000_000;
        second.dt_ns = 10_000_000_000;
        second.plant_discharge_current_ma = 100_000;
        let out = evaluate(second, &mut s).unwrap();
        assert!(out["bms"]["state"]["soc_ppt"].as_u64().unwrap() < 800);
        let mut fault = fixture();
        fault.now_ns = 12_000_000_000;
        fault.thermal_inputs.battery_pump_available = false;
        fault.brake_inputs.fire_emergency = true;
        let out = evaluate(fault, &mut s).unwrap();
        assert_eq!(out["bms"]["discharge_limit_ma"], 0);
        assert_eq!(out["traction"]["commanded_torque_mnm"], 0);
        assert_eq!(out["brake"]["friction_effort_ppt"], 1000);
    }
    #[test]
    fn clock_and_configuration_errors_do_not_advance_persistent_state() {
        let mut s = State::default();
        evaluate(fixture(), &mut s).unwrap();
        assert!(evaluate(fixture(), &mut s).is_err());
        assert_eq!(s.last_ns, 1_000_000_000);
        let mut r = fixture();
        r.now_ns = 2_000_000_000;
        r.configuration_sha256 = "b".repeat(64);
        assert!(evaluate(r, &mut s).is_err());
        assert_eq!(s.last_ns, 1_000_000_000);
        let mut r = fixture();
        r.now_ns = 2_000_000_000;
        r.bms_params.max_charge_ma = 1;
        assert!(evaluate(r, &mut s).is_err());
        assert_eq!(s.last_ns, 1_000_000_000);
    }

    #[test]
    fn partial_charge_derating_is_replaced_by_native_friction_braking() {
        let mut s = State::default();
        let mut r = fixture();
        r.cell_voltages_mv.fill(2750);
        r.pack_voltage_mv = 2750 * 336;
        r.brake_inputs.atp_command = osr_atp::BrakeCommand::Service(500);
        r.traction_inputs.torque_setpoint_mnm = -1_000_000;
        let out = evaluate(r, &mut s).unwrap();
        assert!(out["bms"]["charge_limit_ma"].as_u64().unwrap() < 180_000);
        assert!(out["brake"]["regen_request_ppt"].as_u64().unwrap() < 500);
        assert!(out["brake"]["friction_effort_ppt"].as_u64().unwrap() > 0);
        assert_eq!(
            out["brake"]["regen_request_ppt"].as_u64().unwrap()
                + out["brake"]["friction_effort_ppt"].as_u64().unwrap(),
            500
        );
    }
}
