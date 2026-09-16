//! Simulation-only JSON-lines adapter for native embedded evaluators.
//! Each city/site key retains its controller states for this process lifetime.
use std::collections::{BTreeSet, HashMap};
use std::io::{self, BufRead, Write};

use osr_afc::{afc_evaluate, sign_token, AfcInputs, AfcParams, AfcState, Decision, FareToken};
use osr_aux_power::{aux_evaluate, AuxInputs, AuxParams, AuxState};
use osr_bms::{bms_evaluate, BmsInputs, BmsParams, BmsState, ContactorCommand, ContactorState};
use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams};
use osr_energy_site::{energy_site_evaluate, EnergySiteInputs, EnergySiteParams};
use osr_hvac::{hvac_evaluate, HvacInputs, HvacParams, HvacState};
use osr_level_crossing::{
    lc_evaluate, BarrierSensors, LcInputs, LcParams, LcState, LcStatePersistent,
};
use osr_station_scada::{
    station_scada_evaluate, CctvNvrStatus, LightingZoneStatus, StationHvacStatus,
    StationScadaInputs, StationScadaParams,
};
use osr_wayside_points::{switch_evaluate, RawSensor, SwitchInputs, SwitchParams, SwitchState};
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
    #[serde(default)]
    points_detection_fault: bool,
    #[serde(default)]
    crossing_motor_fault: bool,
    #[serde(default)]
    faregate_denial: bool,
}

struct State {
    bms: BmsState,
    aux: AuxState,
    hvac: HvacState,
    points: SwitchState,
    crossing: LcStatePersistent,
    faregate: AfcState,
    faregate_grants: u64,
    faregate_denials: u64,
    last_ns: u64,
}
impl Default for State {
    fn default() -> Self {
        Self {
            bms: BmsState::initial(720),
            aux: AuxState::default(),
            hvac: HvacState::default(),
            points: SwitchState::default(),
            crossing: LcStatePersistent::default(),
            faregate: AfcState::default(),
            faregate_grants: 0,
            faregate_denials: 0,
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
    let points = switch_evaluate(
        &state.points,
        &SwitchInputs {
            now_ns: input.now_ns,
            sensor_a: RawSensor::ReadNormal,
            sensor_b: if input.points_detection_fault {
                RawSensor::ReadReverse
            } else {
                RawSensor::ReadNormal
            },
            commanded: None,
            motor_over_temp: false,
            motor_drive_fault: false,
        },
        &SwitchParams::typical(),
    );
    let barrier = BarrierSensors {
        fully_up: true,
        fully_down: false,
        motor_fault: input.crossing_motor_fault,
    };
    let crossing = lc_evaluate(
        &state.crossing,
        &LcInputs {
            now_ns: input.now_ns,
            train_approaching: false,
            train_cleared: false,
            barrier_a: barrier,
            barrier_b: barrier,
            manual_emergency_lower: false,
            manual_reset: false,
        },
        &LcParams::default_metro(),
    );
    let secret = b"osr-simulation-faregate";
    let mut token = FareToken {
        account_id: 1,
        issued_ns: input.now_ns.saturating_sub(1),
        expires_ns: input.now_ns.saturating_add(60_000_000_000),
        station_restriction: None,
        signature: [0; osr_afc::HMAC_SHA256_LEN],
    };
    token.signature = sign_token(&token, secret);
    if input.faregate_denial {
        token.signature[0] ^= 1;
    }
    let blacklist = BTreeSet::new();
    let faregate = afc_evaluate(
        &state.faregate,
        &AfcInputs {
            now_ns: input.now_ns,
            gate_station_id: 1,
            scanned_token: Some(token),
            secret,
            blacklist: &blacklist,
        },
        &AfcParams::metro_default(),
    );
    match faregate.last_decision {
        Some(Decision::Grant) => state.faregate_grants = state.faregate_grants.saturating_add(1),
        Some(Decision::Deny(_)) => {
            state.faregate_denials = state.faregate_denials.saturating_add(1)
        }
        None => {}
    }
    state.bms = bms.state;
    state.aux = aux.state;
    state.hvac = hvac.state;
    state.points = points.state;
    state.crossing = crossing.state;
    state.faregate = faregate.state;
    state.last_ns = input.now_ns;
    Ok(json!({
        "schema":"osr-operating-bridge/2", "environment":"simulation", "key":input.key,
        "source_time_ns":input.now_ns,
        "energy":{"schema":"osr-energy-site/1","pv_w":240000,"battery_soc_ppt":720,"to_pad_w":energy.to_pad_w},
        "station":station,"lighting":zone,"bms":bms,"aux":aux,"hvac":hvac,"cbm":cbm,
        "points":{
            "detected":points.state.detected,
            "motor":points.motor,
            "fault_reason":points.state.fault_reason
        },
        "crossing":{
            "state":crossing.state.state,
            "faulted":crossing.state.state == LcState::Faulted,
            "warning_lights_on":crossing.warning_lights_on
        },
        "faregate":{
            "gate":faregate.gate,
            "last_decision":match faregate.last_decision {
                Some(Decision::Grant) => "Grant",
                Some(Decision::Deny(_)) => "Deny",
                None => "None",
            },
            "grant_count":state.faregate_grants,
            "denial_count":state.faregate_denials
        },
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
            points_detection_fault: false,
            crossing_motor_fault: false,
            faregate_denial: false,
        }
    }
    #[test]
    fn real_controller_gates_and_service_flags_are_exported() {
        let mut state = State::default();
        let mut i = input(1);
        let nominal = evaluate(&i, &mut state).unwrap();
        assert_eq!(nominal["bms"]["contactor"], "Closed");
        assert_eq!(nominal["hvac"]["mode"], "Cooling");
        assert_eq!(nominal["points"]["detected"], "Normal");
        assert_eq!(nominal["crossing"]["state"], "Idle");
        assert_eq!(nominal["faregate"]["last_decision"], "Grant");
        i.now_ns = 2;
        i.battery_trip = true;
        i.cbm_service = true;
        i.station_fault = true;
        i.points_detection_fault = true;
        i.crossing_motor_fault = true;
        i.faregate_denial = true;
        let fault = evaluate(&i, &mut state).unwrap();
        assert_eq!(fault["bms"]["contactor"], "OpenFault");
        assert_eq!(fault["aux"]["direct_hv_enabled"], false);
        assert_eq!(fault["hvac"]["mode"], "Reduced");
        assert_eq!(fault["cbm"]["sample"]["worst_health"], "Service");
        assert_eq!(fault["station"]["lighting_enabled"][0], false);
        assert_eq!(fault["points"]["detected"], "Unknown");
        assert_eq!(fault["crossing"]["state"], "Faulted");
        assert_eq!(fault["faregate"]["last_decision"], "Deny");
        assert_eq!(fault["faregate"]["denial_count"], 1);
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
