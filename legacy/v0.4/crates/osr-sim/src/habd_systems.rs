//! Deterministic integration of physical wayside hot-axle detectors.
//!
//! Detector sites are explicit scenario assets. Each site may observe one or
//! both directional tracks. A trip latches a stop order until a scheduled,
//! identified inspection reset is accepted after the injected overheat clears.

use std::collections::{BTreeMap, BTreeSet};

use osr_core::{SectionId, TrainId};
use osr_hot_axle_wayside::{
    habd_evaluate, AxleReading, HabdAction, HabdInputs, HabdParams, HwAlarmLevel,
};
use serde::{Deserialize, Serialize};

use crate::fault::FaultEngine;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HabdDetectorConfig {
    pub id: String,
    pub track_positions: Vec<HabdTrackPosition>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct HabdTrackPosition {
    pub section: SectionId,
    pub offset_mm: u64,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HabdResetAction {
    pub at_sim_s: u32,
    pub train: TrainId,
    pub authorised_by: String,
    pub inspection_reference: String,
}

#[derive(Clone, Copy, Debug)]
pub struct HabdTrainPosition {
    pub train: TrainId,
    pub section: SectionId,
    pub offset_mm: u64,
    pub axle_count: u32,
}

#[derive(Clone, Debug)]
pub struct HabdSystemsShadow {
    detectors: Vec<HabdDetectorConfig>,
    params: HabdParams,
    last_train_positions: BTreeMap<TrainId, (SectionId, u64)>,
    active_stop_orders: BTreeMap<TrainId, HabdStopOrder>,
    active_speed_restrictions: BTreeMap<TrainId, HabdSpeedRestriction>,
    applied_resets: BTreeSet<usize>,
    summary: HabdSystemsSummary,
}

impl HabdSystemsShadow {
    #[must_use]
    pub fn new(detectors: &[HabdDetectorConfig]) -> Self {
        Self {
            detectors: detectors.to_vec(),
            params: HabdParams::default_metro(),
            last_train_positions: BTreeMap::new(),
            active_stop_orders: BTreeMap::new(),
            active_speed_restrictions: BTreeMap::new(),
            applied_resets: BTreeSet::new(),
            summary: HabdSystemsSummary {
                detector_count: detectors.len().min(u32::MAX as usize) as u32,
                track_position_count: detectors
                    .iter()
                    .map(|detector| detector.track_positions.len() as u64)
                    .sum(),
                ..HabdSystemsSummary::default()
            },
        }
    }

    #[must_use]
    pub fn stop_active_for(&self, train: TrainId) -> bool {
        self.active_stop_orders.contains_key(&train)
    }

    #[must_use]
    pub fn speed_limit_mps_for(&self, train: TrainId) -> Option<f32> {
        self.active_speed_restrictions
            .get(&train)
            .map(|restriction| restriction.limit_mmps as f32 / 1_000.0)
    }

    pub fn record_stop_hold(&mut self) {
        self.summary.stop_hold_ticks = self.summary.stop_hold_ticks.saturating_add(1);
    }

    pub fn record_speed_restriction_tick(&mut self, actual_speed_mps: f32) {
        self.summary.speed_restriction_ticks =
            self.summary.speed_restriction_ticks.saturating_add(1);
        let speed_mmps = (actual_speed_mps.max(0.0) * 1_000.0).round() as u32;
        self.summary.maximum_restricted_speed_mmps =
            self.summary.maximum_restricted_speed_mmps.max(speed_mmps);
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct HabdStopOrder {
    pub train: String,
    pub detector: String,
    pub section: String,
    pub axle_index: u8,
    pub peak_temperature_dc: i16,
    pub issued_at_sim_s: u32,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct HabdSpeedRestriction {
    pub train: String,
    pub detector: String,
    pub section: String,
    pub axle_index: u8,
    pub peak_temperature_dc: i16,
    pub limit_mmps: i32,
    pub issued_at_sim_s: u32,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct HabdSpeedRestrictionClearRecord {
    pub train: String,
    pub detector: String,
    pub cleared_at_sim_s: u32,
    pub decision: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct HabdSystemsSummary {
    pub detector_count: u32,
    pub track_position_count: u64,
    pub passages_evaluated: u64,
    pub nominal_passages: u64,
    pub warning_passages: u64,
    pub trip_passages: u64,
    pub speed_restrictions_issued: u64,
    pub speed_restriction_ticks: u64,
    pub maximum_restricted_speed_mmps: u32,
    pub speed_restrictions_cleared: u64,
    pub stop_orders_issued: u64,
    pub stop_hold_ticks: u64,
    pub reset_actions_accepted: u64,
    pub reset_actions_rejected: u64,
    pub reset_records: Vec<HabdResetRecord>,
    pub speed_restriction_clear_records: Vec<HabdSpeedRestrictionClearRecord>,
    pub active_speed_restrictions: Vec<HabdSpeedRestriction>,
    pub active_stop_orders: Vec<HabdStopOrder>,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct HabdResetRecord {
    pub at_sim_s: u32,
    pub train: String,
    pub authorised_by: String,
    pub inspection_reference: String,
    pub accepted: bool,
    pub decision: String,
}

/// Apply due inspection resets before movement is evaluated for this tick.
/// A reset is rejected while the train's overheat input remains active or if
/// there is no matching latched stop order.
pub fn apply_due_resets(
    shadow: &mut HabdSystemsShadow,
    resets: &[HabdResetAction],
    faults: &FaultEngine,
    sim_time_s: u32,
) {
    for (index, reset) in resets.iter().enumerate() {
        if reset.at_sim_s != sim_time_s || !shadow.applied_resets.insert(index) {
            continue;
        }
        let overheat_active = faults.habd_overheat_for(reset.train);
        let had_stop_order = shadow.active_stop_orders.contains_key(&reset.train);
        let accepted = !overheat_active && shadow.active_stop_orders.remove(&reset.train).is_some();
        if accepted {
            shadow.summary.reset_actions_accepted =
                shadow.summary.reset_actions_accepted.saturating_add(1);
        } else {
            shadow.summary.reset_actions_rejected =
                shadow.summary.reset_actions_rejected.saturating_add(1);
        }
        shadow.summary.reset_records.push(HabdResetRecord {
            at_sim_s: sim_time_s,
            train: reset.train.to_string(),
            authorised_by: reset.authorised_by.clone(),
            inspection_reference: reset.inspection_reference.clone(),
            accepted,
            decision: if accepted {
                "released-after-inspection".to_string()
            } else if overheat_active {
                "rejected-overheat-active".to_string()
            } else if !had_stop_order {
                "rejected-no-active-stop-order".to_string()
            } else {
                "rejected".to_string()
            },
        });
    }
}

/// Evaluate detector sites crossed during this tick.
pub fn habd_tick(
    shadow: &mut HabdSystemsShadow,
    positions: &[HabdTrainPosition],
    faults: &FaultEngine,
    ambient_c: f32,
    sim_time_s: u32,
) {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let ambient_dc = (ambient_c * 10.0).round() as i16;
    for position in positions {
        let previous_offset = shadow
            .last_train_positions
            .get(&position.train)
            .filter(|(section, _)| *section == position.section)
            .map_or(0, |(_, offset)| *offset);
        for detector in &shadow.detectors {
            for track_position in detector
                .track_positions
                .iter()
                .filter(|track| track.section == position.section)
            {
                if track_position.offset_mm <= previous_offset
                    || track_position.offset_mm > position.offset_mm
                {
                    continue;
                }
                let axle_count = position.axle_count.min(u32::from(u8::MAX) + 1);
                let peak_dc = if faults.habd_overheat_for(position.train) {
                    1_100
                } else if faults.habd_warning_for(position.train) {
                    800
                } else {
                    ambient_dc.saturating_add(100)
                };
                let axles: Vec<AxleReading> = (0..axle_count)
                    .map(|axle| AxleReading {
                        axle_index: axle as u8,
                        peak_dc,
                    })
                    .collect();
                let output = habd_evaluate(
                    &HabdInputs {
                        now_ns,
                        train_id: position.train.0.min(u64::from(u32::MAX)) as u32,
                        section_id: position.section.0.min(u64::from(u32::MAX)) as u32,
                        ambient_dc,
                        axles: &axles,
                    },
                    &shadow.params,
                );
                shadow.summary.passages_evaluated =
                    shadow.summary.passages_evaluated.saturating_add(1);
                match output.alarm {
                    HwAlarmLevel::Nominal => {
                        shadow.summary.nominal_passages =
                            shadow.summary.nominal_passages.saturating_add(1);
                    }
                    HwAlarmLevel::Warning => {
                        shadow.summary.warning_passages =
                            shadow.summary.warning_passages.saturating_add(1);
                    }
                    HwAlarmLevel::Trip => {
                        shadow.summary.trip_passages =
                            shadow.summary.trip_passages.saturating_add(1);
                    }
                }
                match output.action {
                    HabdAction::Nominal => {}
                    HabdAction::SpeedRestriction { limit_mmps, .. } => {
                        if !shadow
                            .active_speed_restrictions
                            .contains_key(&position.train)
                        {
                            shadow.summary.speed_restrictions_issued =
                                shadow.summary.speed_restrictions_issued.saturating_add(1);
                            shadow.active_speed_restrictions.insert(
                                position.train,
                                HabdSpeedRestriction {
                                    train: position.train.to_string(),
                                    detector: detector.id.clone(),
                                    section: position.section.to_string(),
                                    axle_index: output.worst_axle_index.unwrap_or_default(),
                                    peak_temperature_dc: output.worst_peak_dc.unwrap_or_default(),
                                    limit_mmps,
                                    issued_at_sim_s: sim_time_s,
                                },
                            );
                        }
                    }
                    HabdAction::StopOrder { .. } => {
                        if !shadow.active_stop_orders.contains_key(&position.train) {
                            shadow.summary.stop_orders_issued =
                                shadow.summary.stop_orders_issued.saturating_add(1);
                            shadow.active_stop_orders.insert(
                                position.train,
                                HabdStopOrder {
                                    train: position.train.to_string(),
                                    detector: detector.id.clone(),
                                    section: position.section.to_string(),
                                    axle_index: output.worst_axle_index.unwrap_or_default(),
                                    peak_temperature_dc: output.worst_peak_dc.unwrap_or_default(),
                                    issued_at_sim_s: sim_time_s,
                                },
                            );
                        }
                    }
                }
            }
        }
        shadow
            .last_train_positions
            .insert(position.train, (position.section, position.offset_mm));
    }
}

/// Clear a warning restriction only after its train leaves the detector's
/// section and enters the next station domain.
pub fn clear_completed_speed_restrictions(
    shadow: &mut HabdSystemsShadow,
    positions: &[HabdTrainPosition],
    sim_time_s: u32,
) {
    let completed: Vec<TrainId> = shadow
        .active_speed_restrictions
        .iter()
        .filter_map(|(train, restriction)| {
            (!positions.iter().any(|position| {
                position.train == *train && position.section.to_string() == restriction.section
            }))
            .then_some(*train)
        })
        .collect();
    for train in completed {
        if let Some(restriction) = shadow.active_speed_restrictions.remove(&train) {
            shadow.summary.speed_restrictions_cleared =
                shadow.summary.speed_restrictions_cleared.saturating_add(1);
            shadow
                .summary
                .speed_restriction_clear_records
                .push(HabdSpeedRestrictionClearRecord {
                    train: restriction.train,
                    detector: restriction.detector,
                    cleared_at_sim_s: sim_time_s,
                    decision: "cleared-at-next-station".to_string(),
                });
        }
    }
}

#[must_use]
pub fn summarise(shadow: &HabdSystemsShadow) -> HabdSystemsSummary {
    let mut summary = shadow.summary.clone();
    summary.active_speed_restrictions =
        shadow.active_speed_restrictions.values().cloned().collect();
    summary.active_stop_orders = shadow.active_stop_orders.values().cloned().collect();
    summary
}
