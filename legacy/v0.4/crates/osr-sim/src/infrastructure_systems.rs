//! Deterministic station and wayside controller integration.
//!
//! Station shadows run the real PSD, station-PIS, and SCADA evaluators.
//! Wayside shadows convert scenario intrusion faults into sensor frames, run
//! the real SIL-4 detector, and return only verdict changes for the consensus
//! log. No switch, crossing, fare-gate, or vendor asset is invented when it is
//! absent from the scenario model.

use std::collections::BTreeMap;

use osr_core::{Network, SectionId, Station, StationId};
use osr_interlocking::IntrusionState;
use osr_intrusion_detect::{
    evaluate as intrusion_evaluate, IntrusionParams, IntrusionVerdict, LidarReturn,
    WaysideSensorFrame,
};
use osr_pis_station::{
    pis_station_evaluate, AudioCue, Direction as PisDirection, PendingArrival, PisStationInputs,
    PisStationParams, PisStationState,
};
use osr_psd::{
    psd_evaluate, PsdCommand, PsdInputs, PsdPanelStatus, PsdParams, PsdSensors, PsdState,
};
use osr_station_scada::{
    station_scada_evaluate, CctvNvrStatus, EscalatorDirection, EscalatorStatus, LiftStatus,
    LightingZoneStatus, StationHealth, StationHvacStatus, StationScadaInputs, StationScadaParams,
};
use serde::{Deserialize, Serialize};

use crate::fault::FaultEngine;
use crate::train::{Heading, Train, TrainPhase};
use crate::vehicle_systems::VehicleSystemsTickReport;

const PSD_PANEL_COUNT: usize = 12;

#[derive(Clone, Debug)]
pub struct StationSystemsShadow {
    station_id: StationId,
    station_name: String,
    psd: PsdState,
    pis: PisStationState,
    psd_params: PsdParams,
    pis_params: PisStationParams,
    scada_params: StationScadaParams,
    summary: PerStationSystems,
}

impl StationSystemsShadow {
    #[must_use]
    pub fn new(station: &Station) -> Self {
        Self {
            station_id: station.id,
            station_name: station.name.clone(),
            psd: PsdState::initial(PSD_PANEL_COUNT),
            pis: PisStationState::default(),
            psd_params: PsdParams::default_station(),
            pis_params: PisStationParams::default_metro(),
            scada_params: StationScadaParams::default_metro(),
            summary: PerStationSystems {
                station_id: station.id.to_string(),
                station_name: station.name.clone(),
                ..PerStationSystems::default()
            },
        }
    }
}

#[derive(Clone, Debug)]
pub struct WaysideSystemsShadow {
    last_verdict: BTreeMap<SectionId, IntrusionState>,
    params: IntrusionParams,
    summary: WaysideSystemsSummary,
}

impl WaysideSystemsShadow {
    #[must_use]
    pub fn new(network: &Network) -> Self {
        Self {
            last_verdict: network
                .sections
                .keys()
                .copied()
                .map(|section| (section, IntrusionState::Clear))
                .collect(),
            params: IntrusionParams::default(),
            summary: WaysideSystemsSummary {
                section_count: network.sections.len() as u32,
                ..WaysideSystemsSummary::default()
            },
        }
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct PerStationSystems {
    pub station_id: String,
    pub station_name: String,
    pub controller_ticks: u64,
    pub psd_panel_evaluations: u64,
    pub psd_open_ticks: u64,
    pub psd_obstruction_ticks: u64,
    pub psd_fault_ticks: u64,
    pub pis_board_entries: u64,
    pub pis_announcements: u64,
    pub scada_warning_ticks: u64,
    pub scada_degraded_ticks: u64,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct StationSystemsSummary {
    pub station_count: u32,
    pub controller_ticks: u64,
    pub psd_panel_evaluations: u64,
    pub psd_open_ticks: u64,
    pub psd_obstruction_ticks: u64,
    pub psd_fault_ticks: u64,
    pub pis_board_entries: u64,
    pub pis_announcements: u64,
    pub scada_warning_ticks: u64,
    pub scada_degraded_ticks: u64,
    pub per_station: Vec<PerStationSystems>,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct WaysideSystemsSummary {
    pub section_count: u32,
    pub detector_ticks: u64,
    pub clear_ticks: u64,
    pub unknown_ticks: u64,
    pub present_ticks: u64,
    pub verdict_transitions: u64,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct InfrastructureSystemsSummary {
    pub stations: StationSystemsSummary,
    pub wayside: WaysideSystemsSummary,
}

/// Run one station controller cycle using the actual train-door result and
/// deterministic ETA data from the service simulation.
pub fn station_systems_tick(
    shadow: &mut StationSystemsShadow,
    trains: &[Train],
    vehicle_reports: &[VehicleSystemsTickReport],
    faults: &FaultEngine,
    sim_time_s: u32,
) {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let berthed_train = trains.iter().enumerate().find(|(_, train)| {
        matches!(
            train.phase,
            TrainPhase::Dwelling { station, .. } if station == shadow.station_id
        )
    });
    let train_at_platform = berthed_train.is_some();
    let train_doors_open = berthed_train.is_some_and(|(index, _)| {
        vehicle_reports
            .get(index)
            .is_some_and(|report| !report.doors_interlock_ok)
    });
    let obstructed = faults.psd_obstructed_at(shadow.station_id);
    let sensors = vec![
        PsdSensors {
            closed_limit: !train_doors_open && !obstructed,
            open_limit: train_doors_open,
            motor_current_ma: if obstructed { 5_000 } else { 0 },
            obstruction_detected: obstructed,
        };
        PSD_PANEL_COUNT
    ];
    let psd = psd_evaluate(
        &shadow.psd,
        &PsdInputs {
            now_ns,
            train_at_platform,
            // A stopped and geometrically berthed train supplies the approach
            // interlock; the current door-open state is the separate input.
            train_interlock_ok: train_at_platform,
            train_doors_open_or_opening: train_doors_open,
            occ_commanded: if train_at_platform {
                PsdCommand::Open
            } else {
                PsdCommand::Close
            },
            emergency_stop: false,
            panels: &sensors,
        },
        &shadow.psd_params,
    );
    shadow.psd = psd.state;

    let arrivals = pending_arrivals(shadow.station_id, trains);
    let pis = pis_station_evaluate(
        &shadow.pis,
        &PisStationInputs {
            now_ns,
            pending_arrivals: &arrivals,
            emergency_code: None,
            operator_banner: None,
        },
        &shadow.pis_params,
    );
    shadow.pis = pis.state;

    let scada_failed = faults.station_scada_failed_at(shadow.station_id);
    let escalators = vec![
        EscalatorStatus {
            commanded: EscalatorDirection::Up,
            running: if scada_failed {
                EscalatorDirection::Stop
            } else {
                EscalatorDirection::Up
            },
            faulted: scada_failed,
            overload: false,
            estop: false,
        };
        2
    ];
    let lifts = vec![LiftStatus {
        current_floor: 0,
        requested_floor: 0,
        door_open: false,
        faulted: scada_failed,
    }];
    let lighting = vec![
        LightingZoneStatus {
            enabled: true,
            dim_ppt: 1_000,
            faulted: false,
        };
        4
    ];
    let escalator_commands = vec![None; escalators.len()];
    let lift_calls = vec![None; lifts.len()];
    let scada = station_scada_evaluate(
        &StationScadaInputs {
            now_ns,
            emergency_stop: false,
            escalators: &escalators,
            lifts: &lifts,
            lighting_zones: &lighting,
            hvac: StationHvacStatus {
                setpoint_dc: 230,
                faulted: scada_failed,
            },
            cctv: CctvNvrStatus {
                online: !scada_failed,
                free_storage_ppt: if scada_failed { 0 } else { 500 },
                channels_offline: u8::from(scada_failed),
            },
            escalator_commands: &escalator_commands,
            lift_calls: &lift_calls,
        },
        &shadow.scada_params,
    );

    shadow.summary.controller_ticks = shadow.summary.controller_ticks.saturating_add(1);
    shadow.summary.psd_panel_evaluations = shadow
        .summary
        .psd_panel_evaluations
        .saturating_add(PSD_PANEL_COUNT as u64);
    if !psd.panel_statuses.is_empty()
        && psd
            .panel_statuses
            .iter()
            .all(|status| matches!(status, PsdPanelStatus::Open))
    {
        shadow.summary.psd_open_ticks = shadow.summary.psd_open_ticks.saturating_add(1);
    }
    if psd.any_obstructed {
        shadow.summary.psd_obstruction_ticks =
            shadow.summary.psd_obstruction_ticks.saturating_add(1);
    }
    if psd.any_faulted {
        shadow.summary.psd_fault_ticks = shadow.summary.psd_fault_ticks.saturating_add(1);
    }
    shadow.summary.pis_board_entries = shadow
        .summary
        .pis_board_entries
        .saturating_add(pis.board.len() as u64);
    if !matches!(pis.audio_cue, AudioCue::None) {
        shadow.summary.pis_announcements = shadow.summary.pis_announcements.saturating_add(1);
    }
    match scada.health {
        StationHealth::Nominal => {}
        StationHealth::Warning => {
            shadow.summary.scada_warning_ticks =
                shadow.summary.scada_warning_ticks.saturating_add(1);
        }
        StationHealth::Degraded => {
            shadow.summary.scada_degraded_ticks =
                shadow.summary.scada_degraded_ticks.saturating_add(1);
        }
    }
}

fn pending_arrivals(station_id: StationId, trains: &[Train]) -> Vec<PendingArrival> {
    trains
        .iter()
        .filter_map(|train| match train.phase {
            TrainPhase::Traveling {
                to_station,
                remaining_s,
                ..
            } if to_station == station_id => Some(PendingArrival {
                train_id: train.id.0.min(u64::from(u32::MAX)) as u32,
                line_id: (train.line_index + 1).min(u32::MAX as usize) as u32,
                direction: match train.heading {
                    Heading::Forward => PisDirection::Forward,
                    Heading::Reverse => PisDirection::Reverse,
                },
                eta_s: remaining_s.max(0.0).ceil() as u32,
                approaching: remaining_s <= 60.0,
            }),
            _ => None,
        })
        .collect()
}

/// Evaluate every configured section and return only consensus-log changes.
#[must_use]
pub fn wayside_systems_tick(
    shadow: &mut WaysideSystemsShadow,
    network: &Network,
    faults: &FaultEngine,
    sim_time_s: u32,
) -> Vec<(SectionId, IntrusionState)> {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let mut transitions = Vec::new();
    for section in network.sections.keys().copied() {
        let requested = faults.intrusion_state_for(section);
        let mut frame = WaysideSensorFrame::clear();
        match requested {
            IntrusionState::Clear => {}
            IntrusionState::Unknown => frame.lidar_offline = true,
            IntrusionState::Present => {
                frame.lidar[0] = Some(LidarReturn {
                    longitudinal_mm: 1_000,
                    lateral_mm: 0,
                });
            }
        }
        let outcome = intrusion_evaluate(&frame, now_ns, &shadow.params);
        let verdict = match outcome.verdict {
            IntrusionVerdict::Clear => IntrusionState::Clear,
            IntrusionVerdict::Unknown => IntrusionState::Unknown,
            IntrusionVerdict::Present => IntrusionState::Present,
        };
        shadow.summary.detector_ticks = shadow.summary.detector_ticks.saturating_add(1);
        match verdict {
            IntrusionState::Clear => {
                shadow.summary.clear_ticks = shadow.summary.clear_ticks.saturating_add(1);
            }
            IntrusionState::Unknown => {
                shadow.summary.unknown_ticks = shadow.summary.unknown_ticks.saturating_add(1);
            }
            IntrusionState::Present => {
                shadow.summary.present_ticks = shadow.summary.present_ticks.saturating_add(1);
            }
        }
        if shadow.last_verdict.get(&section).copied() != Some(verdict) {
            shadow.last_verdict.insert(section, verdict);
            shadow.summary.verdict_transitions =
                shadow.summary.verdict_transitions.saturating_add(1);
            transitions.push((section, verdict));
        }
    }
    transitions
}

#[must_use]
pub fn summarise(
    station_shadows: &[StationSystemsShadow],
    wayside: &WaysideSystemsShadow,
) -> InfrastructureSystemsSummary {
    let mut stations = StationSystemsSummary {
        station_count: station_shadows.len() as u32,
        ..StationSystemsSummary::default()
    };
    for shadow in station_shadows {
        debug_assert_eq!(shadow.station_id.to_string(), shadow.summary.station_id);
        debug_assert_eq!(shadow.station_name, shadow.summary.station_name);
        let item = shadow.summary.clone();
        stations.controller_ticks = stations
            .controller_ticks
            .saturating_add(item.controller_ticks);
        stations.psd_panel_evaluations = stations
            .psd_panel_evaluations
            .saturating_add(item.psd_panel_evaluations);
        stations.psd_open_ticks = stations.psd_open_ticks.saturating_add(item.psd_open_ticks);
        stations.psd_obstruction_ticks = stations
            .psd_obstruction_ticks
            .saturating_add(item.psd_obstruction_ticks);
        stations.psd_fault_ticks = stations
            .psd_fault_ticks
            .saturating_add(item.psd_fault_ticks);
        stations.pis_board_entries = stations
            .pis_board_entries
            .saturating_add(item.pis_board_entries);
        stations.pis_announcements = stations
            .pis_announcements
            .saturating_add(item.pis_announcements);
        stations.scada_warning_ticks = stations
            .scada_warning_ticks
            .saturating_add(item.scada_warning_ticks);
        stations.scada_degraded_ticks = stations
            .scada_degraded_ticks
            .saturating_add(item.scada_degraded_ticks);
        stations.per_station.push(item);
    }
    InfrastructureSystemsSummary {
        stations,
        wayside: wayside.summary.clone(),
    }
}
