//! Simulation-only JSON-lines adapter for native embedded evaluators.
//! Each city/site key retains its controller states for this process lifetime.
use std::collections::HashMap;
use std::io::{self, BufRead, Write};

use osr_aux_power::{aux_evaluate, AuxInputs, AuxParams, AuxState};
use osr_bms::{bms_evaluate, BmsInputs, BmsParams, BmsState, ContactorCommand, ContactorState};
use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams};
use osr_energy_site::{energy_site_evaluate, EnergySiteInputs, EnergySiteParams};
use osr_hvac::{hvac_evaluate, HvacInputs, HvacParams, HvacState};
use osr_station_scada::{
    station_scada_evaluate, CctvNvrStatus, LightingZoneStatus, StationHvacStatus,
    StationScadaInputs, StationScadaParams,
};
use serde::Deserialize;
use serde_json::{json, Value};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Input {
    key: String,
    now_ns: u64,
    lighting_pct: u16,
    #[serde(default)]
    station_fault: bool,
    #[serde(default)]
    battery_trip: bool,
    #[serde(default)]
    aux_fault: bool,
    #[serde(default)]
    cbm_service: bool,
}

struct State {
    bms: BmsState,
    aux: AuxState,
    hvac: HvacState,
    last_ns: u64,
}
impl Default for State {
    fn default() -> Self {
        Self {
            bms: BmsState::initial(720),
            aux: AuxState::default(),
            hvac: HvacState::default(),
            last_ns: 0,
        }
    }
}

fn evaluate(input: &Input, state: &mut State) -> Result<Value, &'static str> {
    if input.key.is_empty() || input.key.len() > 160 || !(20..=100).contains(&input.lighting_pct) {
        return Err("Invalid simulation key or lighting range");
    }
    if input.now_ns <= state.last_ns {
        return Err("Non-monotonic controller time");
    }
    let dt_ns = if state.last_ns == 0 {
        0
    } else {
        input.now_ns - state.last_ns
    };
    let temperatures = [if input.battery_trip { 650 } else { 350 }; 4];
    let bms = bms_evaluate(
        &state.bms,
        &BmsInputs {
            now_ns: input.now_ns,
            cell_voltages_mv: &[3300; 4],
            cell_temps_dc: &temperatures,
            pack_current_ma: 0,
            pack_voltage_mv: 13200,
            off_gas_detected: false,
            external_fire_trip: false,
            hazard_module_id: None,
            hazard_string_id: None,
            external_command: ContactorCommand::RequestClose,
            dt_ns,
        },
        &BmsParams::lfp_default(4, 100_000),
    );
    let aux = aux_evaluate(
        &state.aux,
        &AuxInputs {
            now_ns: input.now_ns,
            pack_soc_ppt: bms.state.soc_ppt,
            pack_contactor_closed: bms.contactor == ContactorState::Closed,
            v24_over_temp: false,
            v110_over_temp: false,
            direct_hv_over_temp: input.aux_fault,
            v24_drive_fault: false,
            v110_drive_fault: false,
            direct_hv_drive_fault: false,
            v24_enable_request: true,
            v110_enable_request: true,
            direct_hv_enable_request: true,
        },
        &AuxParams::light_metro_default(),
    );
    let hvac = hvac_evaluate(
        &state.hvac,
        &HvacInputs {
            now_ns: input.now_ns,
            dt_ns,
            cabin_temp_dc: 300,
            ambient_temp_dc: 420,
            setpoint_dc: 250,
            direct_hv_enabled: aux.direct_hv_enabled,
            hvac_enable_request: true,
        },
        &HvacParams::light_metro_default(),
    );
    let cbm = cbm_evaluate(
        &CbmInputs {
            now_ns: input.now_ns,
            train_id: 1,
            bearing_vib_ppt: vec![1000],
            motor_temp_dc: vec![800],
            brake_pad_remaining_ppt: vec![if input.cbm_service { 100 } else { 900 }],
            wheel_tread_remaining_ppt: vec![900],
        },
        &CbmParams::default_metro(),
    );
    let zone = LightingZoneStatus {
        enabled: true,
        dim_ppt: input.lighting_pct * 10,
        faulted: input.station_fault,
    };
    let station = station_scada_evaluate(
        &StationScadaInputs {
            now_ns: input.now_ns,
            emergency_stop: false,
            escalators: &[],
            lifts: &[],
            lighting_zones: &[zone],
            hvac: StationHvacStatus {
                setpoint_dc: 250,
                faulted: false,
            },
            cctv: CctvNvrStatus {
                online: true,
                free_storage_ppt: 800,
                channels_offline: 0,
            },
            escalator_commands: &[],
            lift_calls: &[],
        },
        &StationScadaParams::default_metro(),
    );
    let energy = energy_site_evaluate(
        &EnergySiteInputs {
            now_ns: input.now_ns,
            pv_w: 240_000,
            pad_request_w: 180_000,
            battery_soc_ppt: 720,
            battery_charge_limit_w: 250_000,
            battery_discharge_limit_w: 250_000,
            grid_up: true,
            export_allowed: false,
        },
        &EnergySiteParams::default_samawah(),
    );
    state.bms = bms.state;
    state.aux = aux.state;
    state.hvac = hvac.state;
    state.last_ns = input.now_ns;
    Ok(json!({
        "schema":"osr-operating-bridge/1", "environment":"simulation", "key":input.key,
        "source_time_ns":input.now_ns,
        "energy":{"schema":"osr-energy-site/1","pv_w":240000,"battery_soc_ppt":720,"to_pad_w":energy.to_pad_w},
        "station":station,"lighting":zone,"bms":bms,"aux":aux,"hvac":hvac,"cbm":cbm,
        "fixtures":{"cell_temperature_dc":temperatures[0],"cabin_temperature_dc":300}
    }))
}

fn main() {
    let mut states: HashMap<String, State> = HashMap::new();
    for line in io::stdin().lock().lines() {
        let result = line.map_err(|_| "Cannot read input").and_then(|line| {
            if line.len() > 4096 {
                return Err("Input too large");
            }
            let input: Input = serde_json::from_str(&line).map_err(|_| "Invalid input frame")?;
            if states.len() >= 4096 && !states.contains_key(&input.key) {
                return Err("Simulation key limit");
            }
            evaluate(&input, states.entry(input.key.clone()).or_default())
        });
        println!(
            "{}",
            result.unwrap_or_else(|message| json!({"error":message}))
        );
        if io::stdout().flush().is_err() {
            break;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn input(now_ns: u64) -> Input {
        Input {
            key: "samawah|SAM-RS-L1-001".into(),
            now_ns,
            lighting_pct: 75,
            station_fault: false,
            battery_trip: false,
            aux_fault: false,
            cbm_service: false,
        }
    }
    #[test]
    fn real_controller_gates_and_service_flags_are_exported() {
        let mut state = State::default();
        let mut i = input(1);
        let nominal = evaluate(&i, &mut state).unwrap();
        assert_eq!(nominal["bms"]["contactor"], "Closed");
        assert_eq!(nominal["hvac"]["mode"], "Cooling");
        i.now_ns = 2;
        i.battery_trip = true;
        i.cbm_service = true;
        i.station_fault = true;
        let fault = evaluate(&i, &mut state).unwrap();
        assert_eq!(fault["bms"]["contactor"], "OpenFault");
        assert_eq!(fault["aux"]["direct_hv_enabled"], false);
        assert_eq!(fault["hvac"]["mode"], "Reduced");
        assert_eq!(fault["cbm"]["sample"]["worst_health"], "Service");
        assert_eq!(fault["station"]["lighting_enabled"][0], false);
        i.now_ns = 3;
        i.battery_trip = false;
        assert_eq!(
            evaluate(&i, &mut state).unwrap()["bms"]["contactor"],
            "OpenFault"
        );
        assert!(evaluate(&i, &mut state).is_err());
        assert_eq!(
            evaluate(&i, &mut State::default()).unwrap()["bms"]["contactor"],
            "Closed"
        );
    }
}
