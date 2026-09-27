//! Simulation-only JSON-lines adapter for native embedded evaluators.
//! Each city/site key retains its controller states for this process lifetime.
use std::collections::{BTreeSet, HashMap};
use std::io::{self, BufRead, Write};

use osr_afc::{
    afc_evaluate, sign_token, AfcInputs, AfcParams, AfcState, Decision, FareToken, GateCommand,
};
use osr_aux_power::{aux_evaluate, AuxInputs, AuxParams, AuxState};
use osr_bms::{
    bms_evaluate, AlarmLevel, BmsInputs, BmsParams, BmsState, ContactorCommand, ContactorState,
};
use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams, ComponentHealth};
use osr_energy_site::{energy_site_evaluate, EnergySiteInputs, EnergySiteParams};
use osr_hvac::{hvac_evaluate, HvacInputs, HvacMode, HvacParams, HvacState};
use osr_level_crossing::{
    lc_evaluate, BarrierSensors, LcInputs, LcParams, LcState, LcStatePersistent,
};
use osr_station_scada::{
    station_scada_evaluate, CctvNvrStatus, LightingZoneStatus, StationHvacStatus,
    StationScadaInputs, StationScadaParams,
};
use osr_supervision_contract::{Observation, ObservationFrame};
use osr_wayside_points::{
    switch_evaluate, DetectedPosition, MotorCommand, RawSensor, SwitchInputs, SwitchParams,
    SwitchState,
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
    let observations = vec![
        Observation::new("pv", "power_kw", 240.0, "kW", &["osr-energy-site"]),
        Observation::new(
            "charger",
            "power_kw",
            f64::from(energy.to_pad_w) / 1000.0,
            "kW",
            &["osr-energy-site"],
        ),
        Observation::new("battery", "soc_pct", 72.0, "%", &["osr-energy-site"]),
        Observation::new(
            "facilities",
            "lighting_pct",
            if station.lighting_enabled[0] {
                f64::from(zone.dim_ppt) / 10.0
            } else {
                0.0
            },
            "%",
            &["osr-station-scada"],
        ),
        Observation::new(
            "facilities",
            "fault_count",
            station.fault_count,
            "count",
            &["osr-station-scada"],
        ),
        Observation::new(
            "vehicle-bms",
            "soc_pct",
            f64::from(bms.state.soc_ppt) / 10.0,
            "%",
            &["osr-bms"],
        ),
        Observation::new(
            "vehicle-bms",
            "charge_limit_a",
            f64::from(bms.charge_limit_ma) / 1000.0,
            "A",
            &["osr-bms"],
        ),
        Observation::new(
            "vehicle-bms",
            "trip",
            u8::from(bms.state.alarm == AlarmLevel::Trip),
            "bool",
            &["osr-bms"],
        ),
        Observation::new(
            "vehicle-aux",
            "comfort_power",
            u8::from(aux.direct_hv_enabled),
            "bool",
            &["osr-aux-power"],
        ),
        Observation::new(
            "vehicle-aux",
            "fault_count",
            aux.state.faults.0.count_ones(),
            "count",
            &["osr-aux-power"],
        ),
        Observation::new(
            "vehicle-hvac",
            "compressor_pct",
            f64::from(hvac.compressor_ppt) / 10.0,
            "%",
            &["osr-hvac", "osr-aux-power"],
        ),
        Observation::new(
            "vehicle-hvac",
            "fan_pct",
            f64::from(hvac.fan_ppt) / 10.0,
            "%",
            &["osr-hvac", "osr-aux-power"],
        ),
        Observation::new(
            "vehicle-hvac",
            "reduced",
            u8::from(hvac.mode == HvacMode::Reduced),
            "bool",
            &["osr-hvac", "osr-aux-power"],
        ),
        Observation::new(
            "vehicle-cbm",
            "health",
            match cbm.sample.worst_health {
                ComponentHealth::Nominal => 0_u8,
                ComponentHealth::Watch => 1,
                ComponentHealth::Service => 2,
            },
            "severity",
            &["osr-cbm-onboard"],
        ),
        Observation::new(
            "vehicle-cbm",
            "brake_remaining_pct",
            f64::from(cbm.sample.brake_pad_remaining_ppt[0]) / 10.0,
            "%",
            &["osr-cbm-onboard"],
        ),
        Observation::new(
            "vehicle-cbm",
            "bearing_vibration_mm_s",
            f64::from(cbm.sample.bearing_vib_ppt[0]) / 1000.0,
            "mm/s",
            &["osr-cbm-onboard"],
        ),
        Observation::new(
            "points",
            "detected_position",
            match points.state.detected {
                DetectedPosition::Unknown => 0_u8,
                DetectedPosition::Normal => 1,
                DetectedPosition::Reverse => 2,
            },
            "position",
            &["osr-wayside-points"],
        ),
        Observation::new(
            "points",
            "detection_unknown",
            u8::from(points.state.detected == DetectedPosition::Unknown),
            "bool",
            &["osr-wayside-points"],
        ),
        Observation::new(
            "points",
            "motor_active",
            u8::from(points.motor != MotorCommand::Stop),
            "bool",
            &["osr-wayside-points"],
        ),
        Observation::new(
            "level-crossing",
            "state",
            match crossing.state.state {
                LcState::Idle => 0_u8,
                LcState::Warning => 1,
                LcState::Closed => 2,
                LcState::Clearing => 3,
                LcState::Faulted => 4,
            },
            "state",
            &["osr-level-crossing"],
        ),
        Observation::new(
            "level-crossing",
            "fault",
            u8::from(crossing.state.state == LcState::Faulted),
            "bool",
            &["osr-level-crossing"],
        ),
        Observation::new(
            "level-crossing",
            "warning_active",
            u8::from(crossing.warning_lights_on),
            "bool",
            &["osr-level-crossing"],
        ),
        Observation::new(
            "faregate",
            "gate_open",
            u8::from(faregate.gate == GateCommand::Open),
            "bool",
            &["osr-afc"],
        ),
        Observation::new(
            "faregate",
            "last_decision",
            match faregate.last_decision {
                None => 0_u8,
                Some(Decision::Grant) => 1,
                Some(Decision::Deny(_)) => 2,
            },
            "decision",
            &["osr-afc"],
        ),
        Observation::new(
            "faregate",
            "grant_count",
            state.faregate_grants as f64,
            "count",
            &["osr-afc"],
        ),
        Observation::new(
            "faregate",
            "denial_count",
            state.faregate_denials as f64,
            "count",
            &["osr-afc"],
        ),
    ];
    let frame = ObservationFrame::simulation(&input.key, input.now_ns, observations);
    frame.validate().map_err(|_| "Invalid supervisory frame")?;
    serde_json::to_value(frame).map_err(|_| "Cannot serialize supervisory frame")
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
        let cross_language_fixture: Value = serde_json::from_str(include_str!(
            "../../../tests/fixtures/operating-bridge.json"
        ))
        .unwrap();
        assert_eq!(nominal, cross_language_fixture);
        assert_eq!(nominal["schema"], osr_supervision_contract::SCHEMA);
        assert_eq!(nominal["authority"], osr_supervision_contract::AUTHORITY);
        let measurement = |frame: &Value, equipment: &str, name: &str| {
            frame["observations"]
                .as_array()
                .unwrap()
                .iter()
                .find(|item| item["equipment_type"] == equipment && item["measurement"] == name)
                .unwrap()["value"]
                .as_f64()
                .unwrap()
        };
        assert_eq!(measurement(&nominal, "vehicle-bms", "trip"), 0.0);
        assert_eq!(measurement(&nominal, "vehicle-hvac", "reduced"), 0.0);
        assert_eq!(measurement(&nominal, "points", "detected_position"), 1.0);
        assert_eq!(measurement(&nominal, "level-crossing", "state"), 0.0);
        assert_eq!(measurement(&nominal, "faregate", "last_decision"), 1.0);
        i.now_ns = 2;
        i.battery_trip = true;
        i.cbm_service = true;
        i.station_fault = true;
        i.points_detection_fault = true;
        i.crossing_motor_fault = true;
        i.faregate_denial = true;
        let fault = evaluate(&i, &mut state).unwrap();
        assert_eq!(measurement(&fault, "vehicle-bms", "trip"), 1.0);
        assert_eq!(measurement(&fault, "vehicle-aux", "comfort_power"), 0.0);
        assert_eq!(measurement(&fault, "vehicle-hvac", "reduced"), 1.0);
        assert_eq!(measurement(&fault, "vehicle-cbm", "health"), 2.0);
        assert_eq!(measurement(&fault, "facilities", "lighting_pct"), 0.0);
        assert_eq!(measurement(&fault, "points", "detected_position"), 0.0);
        assert_eq!(measurement(&fault, "level-crossing", "state"), 4.0);
        assert_eq!(measurement(&fault, "faregate", "last_decision"), 2.0);
        assert_eq!(measurement(&fault, "faregate", "denial_count"), 1.0);
        i.now_ns = 3;
        i.battery_trip = false;
        assert_eq!(
            measurement(&evaluate(&i, &mut state).unwrap(), "vehicle-bms", "trip"),
            1.0
        );
        assert!(evaluate(&i, &mut state).is_err());
        assert_eq!(
            measurement(
                &evaluate(&i, &mut State::default()).unwrap(),
                "vehicle-bms",
                "trip"
            ),
            0.0
        );
    }
}
