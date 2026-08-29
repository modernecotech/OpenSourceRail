//! Explicit point-machine and level-crossing controller integration.
//!
//! Assets are never inferred from plain track. Generated scenarios carry the
//! switches declared by the city design; level crossings execute only when
//! explicitly listed. This keeps grade-separated networks honest.

use osr_core::{Network, SectionId, StationId};
use osr_level_crossing::{
    lc_evaluate, BarrierCommand, BarrierSensors, LcInputs, LcParams, LcState, LcStatePersistent,
};
use osr_wayside_points::{
    switch_evaluate, CommandedPosition, DetectedPosition, MotorCommand, RawSensor, SwitchInputs,
    SwitchParams, SwitchState,
};
use serde::{Deserialize, Serialize};

use crate::train::{Heading, Train, TrainPhase};

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SwitchAssetConfig {
    pub id: String,
    pub station: StationId,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct LevelCrossingAssetConfig {
    pub id: String,
    /// Both directed sections through the same physical crossing.
    pub sections: Vec<SectionId>,
}

#[derive(Clone, Debug)]
struct SwitchAssetShadow {
    config: SwitchAssetConfig,
    state: SwitchState,
}

#[derive(Clone, Debug)]
struct LevelCrossingAssetShadow {
    config: LevelCrossingAssetConfig,
    state: LcStatePersistent,
    barrier_command: BarrierCommand,
    was_approaching_or_occupied: bool,
}

#[derive(Clone, Debug, Default)]
pub struct WaysideAssetSystemsShadow {
    switches: Vec<SwitchAssetShadow>,
    crossings: Vec<LevelCrossingAssetShadow>,
    summary: WaysideAssetSystemsSummary,
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct WaysideAssetSystemsSummary {
    pub switch_count: u32,
    pub switch_controller_ticks: u64,
    pub switch_observations: u64,
    pub switch_fault_ticks: u64,
    pub crossing_count: u32,
    pub crossing_controller_ticks: u64,
    pub crossing_warning_ticks: u64,
    pub crossing_closed_ticks: u64,
    pub crossing_fault_ticks: u64,
}

impl WaysideAssetSystemsShadow {
    #[must_use]
    pub fn new(switches: &[SwitchAssetConfig], crossings: &[LevelCrossingAssetConfig]) -> Self {
        Self {
            switches: switches
                .iter()
                .cloned()
                .map(|config| SwitchAssetShadow {
                    config,
                    state: SwitchState::default(),
                })
                .collect(),
            crossings: crossings
                .iter()
                .cloned()
                .map(|config| LevelCrossingAssetShadow {
                    config,
                    state: LcStatePersistent::default(),
                    barrier_command: BarrierCommand::Hold,
                    was_approaching_or_occupied: false,
                })
                .collect(),
            summary: WaysideAssetSystemsSummary {
                switch_count: switches.len().min(u32::MAX as usize) as u32,
                crossing_count: crossings.len().min(u32::MAX as usize) as u32,
                ..WaysideAssetSystemsSummary::default()
            },
        }
    }

    /// Fail-restrictive pre-entry predicate used by the movement gate.
    #[must_use]
    pub fn entry_safe(&self, station: StationId, section: SectionId) -> bool {
        let switches_safe = self
            .switches
            .iter()
            .filter(|asset| asset.config.station == station)
            .all(|asset| {
                asset.state.detected == DetectedPosition::Normal
                    && asset.state.commanded == Some(CommandedPosition::Normal)
                    && asset.state.motor == MotorCommand::Stop
                    && asset.state.fault_reason.is_none()
            });
        let crossings_safe = self
            .crossings
            .iter()
            .filter(|asset| asset.config.sections.contains(&section))
            .all(|asset| asset.state.state == LcState::Closed);
        switches_safe && crossings_safe
    }
}

pub fn wayside_asset_systems_tick(
    shadow: &mut WaysideAssetSystemsShadow,
    trains: &[Train],
    network: &Network,
    sim_time_s: u32,
) {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    for asset in &mut shadow.switches {
        let output = switch_evaluate(
            &asset.state,
            &SwitchInputs {
                now_ns,
                sensor_a: RawSensor::ReadNormal,
                sensor_b: RawSensor::ReadNormal,
                commanded: Some(CommandedPosition::Normal),
                motor_over_temp: false,
                motor_drive_fault: false,
            },
            &SwitchParams::typical(),
        );
        shadow.summary.switch_controller_ticks =
            shadow.summary.switch_controller_ticks.saturating_add(1);
        if output.publish_observation.is_some() {
            shadow.summary.switch_observations =
                shadow.summary.switch_observations.saturating_add(1);
        }
        if output.state.fault_reason.is_some() {
            shadow.summary.switch_fault_ticks = shadow.summary.switch_fault_ticks.saturating_add(1);
        }
        asset.state = output.state;
    }

    for asset in &mut shadow.crossings {
        let active = trains
            .iter()
            .any(|train| train_approaches_any(train, network, &asset.config.sections));
        let train_cleared = asset.was_approaching_or_occupied && !active;
        let barriers = match asset.barrier_command {
            BarrierCommand::Lower => BarrierSensors {
                fully_up: false,
                fully_down: true,
                motor_fault: false,
            },
            BarrierCommand::Raise | BarrierCommand::Hold
                if asset.state.state == LcState::Clearing =>
            {
                BarrierSensors::default()
            }
            _ if matches!(asset.state.state, LcState::Warning | LcState::Closed) => {
                BarrierSensors {
                    fully_up: false,
                    fully_down: true,
                    motor_fault: false,
                }
            }
            _ => BarrierSensors::default(),
        };
        let output = lc_evaluate(
            &asset.state,
            &LcInputs {
                now_ns,
                train_approaching: active,
                train_cleared,
                barrier_a: barriers,
                barrier_b: barriers,
                manual_emergency_lower: false,
                manual_reset: false,
            },
            &LcParams::default_metro(),
        );
        shadow.summary.crossing_controller_ticks =
            shadow.summary.crossing_controller_ticks.saturating_add(1);
        match output.state.state {
            LcState::Warning => {
                shadow.summary.crossing_warning_ticks =
                    shadow.summary.crossing_warning_ticks.saturating_add(1);
            }
            LcState::Closed => {
                shadow.summary.crossing_closed_ticks =
                    shadow.summary.crossing_closed_ticks.saturating_add(1);
            }
            LcState::Faulted => {
                shadow.summary.crossing_fault_ticks =
                    shadow.summary.crossing_fault_ticks.saturating_add(1);
            }
            LcState::Idle | LcState::Clearing => {}
        }
        asset.state = output.state;
        asset.barrier_command = output.barrier_command;
        asset.was_approaching_or_occupied = active;
    }
}

fn train_approaches_any(train: &Train, network: &Network, sections: &[SectionId]) -> bool {
    if let TrainPhase::Traveling { section, .. } = train.phase {
        return sections.contains(&section);
    }
    let station = match train.phase {
        TrainPhase::AwaitingDispatch { station } | TrainPhase::Dwelling { station, .. } => station,
        TrainPhase::Traveling { .. } => unreachable!(),
    };
    let line = &network.lines[train.line_index];
    let Some(index) = line
        .stations
        .iter()
        .position(|candidate| *candidate == station)
    else {
        return false;
    };
    let next = match train.heading {
        Heading::Forward if index + 1 < line.forward_sections.len() + 1 => {
            line.forward_sections.get(index).copied()
        }
        Heading::Reverse if index > 0 => line.reverse_sections.get(index - 1).copied(),
        Heading::Forward if line.is_ring => line.forward_sections.last().copied(),
        Heading::Reverse if line.is_ring => line.reverse_sections.last().copied(),
        Heading::Forward | Heading::Reverse => None,
    };
    next.is_some_and(|section| sections.contains(&section))
}

#[must_use]
pub fn summarise(shadow: &WaysideAssetSystemsShadow) -> WaysideAssetSystemsSummary {
    shadow.summary.clone()
}
