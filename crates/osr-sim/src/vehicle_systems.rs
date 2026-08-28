//! Every-tick integration of the trainset's passenger-facing vehicle systems.
//!
//! These are deterministic controller shadows: the aggregate energy model
//! remains authoritative, while the real component crates execute against the
//! same phase, SoC, heading and station state as the service simulation.

use osr_aux_power::{aux_evaluate, AuxInputs, AuxParams, AuxState};
use osr_core::Network;
use osr_door_control::{
    consist_interlock_ok, door_evaluate, DoorAction, DoorInputs, DoorParams, DoorSensors,
    DoorState, DoorStatus,
};
use osr_hvac::{hvac_evaluate, HvacInputs, HvacMode, HvacParams, HvacState};
use osr_lighting::{
    lighting_evaluate, Heading as LightingHeading, LightingInputs, LightingMode, LightingParams,
};
use osr_pis_onboard::{pis_evaluate, AnnouncementKind, PisInputs, PisParams, PisState};
use serde::{Deserialize, Serialize};

use crate::sim::TrainsetSystemsConfig;
use crate::train::{Heading, Train, TrainPhase};

#[derive(Clone, Debug)]
pub struct VehicleSystemsShadow {
    doors: Vec<DoorState>,
    aux: AuxState,
    hvac: HvacState,
    pis: PisState,
    cabin_temp_c: f32,
    summary: VehicleSystemsSummary,
}

impl VehicleSystemsShadow {
    #[must_use]
    pub fn new(train: &Train, config: &TrainsetSystemsConfig, ambient_c: f32) -> Self {
        let door_count = train
            .consist
            .car_count
            .saturating_mul(config.door_cassettes_per_car) as usize;
        Self {
            doors: vec![DoorState::default(); door_count],
            aux: AuxState::default(),
            hvac: HvacState::default(),
            pis: PisState::default(),
            cabin_temp_c: ambient_c,
            summary: VehicleSystemsSummary::default(),
        }
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct VehicleSystemsSummary {
    pub train_count: u32,
    pub controller_ticks: u64,
    pub door_controller_evaluations: u64,
    pub doors_open_evaluations: u64,
    pub door_interlock_violations: u64,
    pub aux_power_controller_ticks: u64,
    pub aux_load_shed_ticks: u64,
    pub hvac_controller_ticks: u64,
    pub hvac_cooling_ticks: u64,
    pub hvac_heating_ticks: u64,
    pub hvac_reduced_ticks: u64,
    pub lighting_controller_ticks: u64,
    pub main_light_module_ticks: u64,
    pub emergency_light_module_ticks: u64,
    pub door_threshold_light_module_ticks: u64,
    pub pis_controller_ticks: u64,
    pub pis_announcements: u64,
    pub mechanical_configuration: TrainsetSystemsConfig,
}

/// Current outputs handed to the embedded TCMS integration layer. Keeping
/// this small prevents the simulator from reconstructing controller state.
#[derive(Copy, Clone, Debug, Default)]
pub struct VehicleSystemsTickReport {
    pub doors_interlock_ok: bool,
    pub v24_rail_enabled: bool,
    pub v110_rail_enabled: bool,
    pub direct_hv_enabled: bool,
    pub aux_load_shed_active: bool,
    pub hvac_reduced: bool,
    pub pis_announcement: bool,
}

/// Execute all passenger-facing controllers for one train and simulation tick.
pub fn vehicle_systems_tick(
    shadow: &mut VehicleSystemsShadow,
    train: &Train,
    network: &Network,
    config: &TrainsetSystemsConfig,
    ambient_c: f32,
    sim_time_s: u32,
    dt_s: f32,
) -> VehicleSystemsTickReport {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let (station_id, distance_to_stop_mm, at_station, speed_mmps, door_action) =
        phase_inputs(train, network);

    let aux_out = aux_evaluate(
        &shadow.aux,
        &AuxInputs {
            now_ns,
            pack_soc_ppt: (train.soc.clamp(0.0, 1.0) * 1000.0).round() as u16,
            pack_contactor_closed: true,
            v24_over_temp: false,
            v110_over_temp: false,
            direct_hv_over_temp: false,
            v24_drive_fault: false,
            v110_drive_fault: false,
            direct_hv_drive_fault: false,
            v24_enable_request: true,
            v110_enable_request: true,
            direct_hv_enable_request: true,
        },
        &AuxParams::light_metro_default(),
    );
    shadow.aux = aux_out.state;

    let door_sensors = if at_station {
        DoorSensors {
            closed_limit: false,
            lock_sensor: false,
            open_limit: true,
            motor_current_ma: 0,
            obstruction_detected: false,
        }
    } else {
        DoorSensors {
            closed_limit: true,
            lock_sensor: true,
            open_limit: false,
            motor_current_ma: 0,
            obstruction_detected: false,
        }
    };
    let mut door_outputs = Vec::with_capacity(shadow.doors.len());
    for state in &mut shadow.doors {
        let output = door_evaluate(
            state,
            &DoorInputs {
                now_ns,
                speed_mmps,
                at_station,
                commanded: door_action,
                emergency_unlock: false,
                sensors: door_sensors,
            },
            &DoorParams::light_metro_default(),
        );
        *state = output.state;
        if output.status == DoorStatus::Open {
            shadow.summary.doors_open_evaluations += 1;
        }
        door_outputs.push(output);
    }
    if matches!(train.phase, TrainPhase::Traveling { .. }) && !consist_interlock_ok(&door_outputs) {
        shadow.summary.door_interlock_violations += 1;
    }

    let hvac_out = hvac_evaluate(
        &shadow.hvac,
        &HvacInputs {
            now_ns,
            dt_ns: (dt_s.max(0.0) * 1_000_000_000.0).round() as u64,
            cabin_temp_dc: (shadow.cabin_temp_c * 10.0).round() as i16,
            ambient_temp_dc: (ambient_c * 10.0).round() as i16,
            setpoint_dc: 230,
            direct_hv_enabled: aux_out.direct_hv_enabled,
            hvac_enable_request: true,
        },
        &HvacParams::light_metro_default(),
    );
    shadow.hvac = hvac_out.state;
    // Compact deterministic thermal response. Energy is not debited here:
    // HVAC and auxiliaries are already included in kWh/car-km.
    let ambient_leak = (ambient_c - shadow.cabin_temp_c) * 0.0005 * dt_s;
    let active_change = (f32::from(hvac_out.heater_ppt) - f32::from(hvac_out.compressor_ppt))
        / 1000.0
        * 0.015
        * dt_s;
    shadow.cabin_temp_c = (shadow.cabin_temp_c + ambient_leak + active_change).clamp(-20.0, 70.0);

    let _lighting_out = lighting_evaluate(
        &LightingInputs {
            now_ns,
            mode_request: LightingMode::Normal,
            v110_rail_enabled: aux_out.v110_enabled,
            v24_rail_enabled: aux_out.v24_enabled,
            emergency_unlock: false,
            heading: match train.heading {
                Heading::Forward => LightingHeading::Forward,
                Heading::Reverse => LightingHeading::Reverse,
            },
            ambient_lux: None,
        },
        &LightingParams::light_metro_default(),
    );

    let pis_out = pis_evaluate(
        &shadow.pis,
        &PisInputs {
            now_ns,
            speed_mmps,
            station_id,
            distance_to_stop_mm,
            at_station,
            emergency_broadcast: None,
            v110_rail_enabled: aux_out.v110_enabled,
            v24_rail_enabled: aux_out.v24_enabled,
        },
        &PisParams::light_metro_default(),
    );
    shadow.pis = pis_out.state;

    let cars = u64::from(train.consist.car_count);
    shadow.summary.controller_ticks += 1;
    shadow.summary.door_controller_evaluations += shadow.doors.len() as u64;
    shadow.summary.aux_power_controller_ticks += 1;
    shadow.summary.hvac_controller_ticks += 1;
    shadow.summary.lighting_controller_ticks += 1;
    shadow.summary.pis_controller_ticks += 1;
    shadow.summary.main_light_module_ticks += cars * u64::from(config.main_light_modules_per_car);
    shadow.summary.emergency_light_module_ticks +=
        cars * u64::from(config.emergency_light_modules_per_car);
    shadow.summary.door_threshold_light_module_ticks +=
        cars * u64::from(config.door_threshold_light_modules_per_car);
    if aux_out.load_shed_active {
        shadow.summary.aux_load_shed_ticks += 1;
    }
    match hvac_out.mode {
        HvacMode::Cooling => shadow.summary.hvac_cooling_ticks += 1,
        HvacMode::Heating => shadow.summary.hvac_heating_ticks += 1,
        HvacMode::Reduced => shadow.summary.hvac_reduced_ticks += 1,
        HvacMode::Off | HvacMode::Ventilating => {}
    }
    if pis_out.audio_announcement != AnnouncementKind::None {
        shadow.summary.pis_announcements += 1;
    }

    VehicleSystemsTickReport {
        doors_interlock_ok: consist_interlock_ok(&door_outputs),
        v24_rail_enabled: aux_out.v24_enabled,
        v110_rail_enabled: aux_out.v110_enabled,
        direct_hv_enabled: aux_out.direct_hv_enabled,
        aux_load_shed_active: aux_out.load_shed_active,
        hvac_reduced: hvac_out.mode == HvacMode::Reduced,
        pis_announcement: pis_out.audio_announcement != AnnouncementKind::None,
    }
}

fn phase_inputs(
    train: &Train,
    network: &Network,
) -> (Option<u32>, Option<i64>, bool, i32, DoorAction) {
    match train.phase {
        TrainPhase::Dwelling { station, .. } => {
            (Some(station.0 as u32), Some(0), true, 0, DoorAction::Open)
        }
        TrainPhase::AwaitingDispatch { station } => {
            (Some(station.0 as u32), Some(0), false, 0, DoorAction::Close)
        }
        TrainPhase::Traveling {
            section,
            to_station,
            total_travel_s,
            remaining_s,
            ..
        } => {
            let fraction = if total_travel_s > 0.0 {
                (remaining_s / total_travel_s).clamp(0.0, 1.0)
            } else {
                0.0
            };
            let distance =
                (network.section(section).length_mm as f64 * f64::from(fraction)).round() as i64;
            (
                Some(to_station.0 as u32),
                Some(distance),
                false,
                15_000,
                DoorAction::Close,
            )
        }
    }
}

#[must_use]
pub fn summarise(
    shadows: &[VehicleSystemsShadow],
    config: &TrainsetSystemsConfig,
    car_count: u32,
) -> VehicleSystemsSummary {
    let mut total = VehicleSystemsSummary {
        train_count: shadows.len() as u32,
        mechanical_configuration: config.clone(),
        ..VehicleSystemsSummary::default()
    };
    for shadow in shadows {
        let summary = &shadow.summary;
        total.controller_ticks += summary.controller_ticks;
        total.door_controller_evaluations += summary.door_controller_evaluations;
        total.doors_open_evaluations += summary.doors_open_evaluations;
        total.door_interlock_violations += summary.door_interlock_violations;
        total.aux_power_controller_ticks += summary.aux_power_controller_ticks;
        total.aux_load_shed_ticks += summary.aux_load_shed_ticks;
        total.hvac_controller_ticks += summary.hvac_controller_ticks;
        total.hvac_cooling_ticks += summary.hvac_cooling_ticks;
        total.hvac_heating_ticks += summary.hvac_heating_ticks;
        total.hvac_reduced_ticks += summary.hvac_reduced_ticks;
        total.lighting_controller_ticks += summary.lighting_controller_ticks;
        total.main_light_module_ticks += summary.main_light_module_ticks;
        total.emergency_light_module_ticks += summary.emergency_light_module_ticks;
        total.door_threshold_light_module_ticks += summary.door_threshold_light_module_ticks;
        total.pis_controller_ticks += summary.pis_controller_ticks;
        total.pis_announcements += summary.pis_announcements;
    }
    debug_assert_eq!(
        total.door_controller_evaluations,
        total.controller_ticks * u64::from(car_count) * u64::from(config.door_cassettes_per_car)
    );
    total
}

#[cfg(test)]
mod tests {
    use super::*;
    use osr_core::{ConsistDescriptor, TrainId};

    fn train(phase: TrainPhase) -> Train {
        Train {
            id: TrainId::new(1),
            line_index: 0,
            consist: ConsistDescriptor::reference_3car(),
            energy_kwh_per_car_km: 2.4,
            heading: Heading::Forward,
            phase,
            soc: 0.95,
            odometer_km: 0.0,
            energy_consumed_kwh: 0.0,
            energy_charged_kwh: 0.0,
            energy_roof_pv_kwh: 0.0,
            min_soc_seen: 0.95,
        }
    }

    #[test]
    fn dwelling_opens_every_physical_door_cassette() {
        let config = TrainsetSystemsConfig::default();
        let tr = train(TrainPhase::Dwelling {
            station: osr_core::StationId::new(1),
            remaining_s: 20.0,
            depot_service_remaining_s: 0.0,
            energy_added_kwh: 0.0,
        });
        let mut shadow = VehicleSystemsShadow::new(&tr, &config, 28.0);
        let network = Network::default();
        vehicle_systems_tick(&mut shadow, &tr, &network, &config, 28.0, 0, 1.0);
        assert_eq!(shadow.summary.door_controller_evaluations, 12);
        assert_eq!(shadow.summary.doors_open_evaluations, 12);
        assert_eq!(shadow.summary.door_interlock_violations, 0);
    }
}
