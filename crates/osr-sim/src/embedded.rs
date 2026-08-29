//! Deterministic integration of the train application-tier embedded software.
//!
//! The safety and vehicle controller shadows execute their own crates first;
//! this layer consumes those outputs exactly as a T-ECU/A would. It runs the
//! real TCMS roll-up, event recorder, hot-axle monitor, CBM sampler, and T2G
//! radio arbiter for every train on every simulation tick.

use std::collections::VecDeque;

use osr_atp::BrakeCommand;
use osr_cbm_onboard::{cbm_evaluate, CbmInputs, CbmParams, CbmSample, ComponentHealth};
use osr_event_recorder::{EventCategory, EventRecord, EventRecorder};
use osr_hot_axle::{
    hot_axle_evaluate, AxleAlarm, AxleReading, AxleSensor, HotAxleInputs, HotAxleParams,
};
use osr_t2g::{t2g_evaluate, ActiveChannel, T2gInputs, T2gParams, T2gState};
use osr_tcms::{tcms_evaluate, AlarmLevel, ConsistStatus, TcmsInputs};
use osr_traction::InverterState;
use serde::{Deserialize, Serialize};

use crate::fault::FaultEngine;
use crate::onboard::{OnboardShadow, TickReport};
use crate::train::{Train, TrainPhase};
use crate::vehicle_systems::VehicleSystemsTickReport;

const EVENT_RECORDER_CAPACITY: usize = 4_096;
const CBM_PAYLOAD_QUEUE_CAPACITY: usize = 4_096;

/// Stateful application-tier controller stack for one train.
#[derive(Clone, Debug)]
pub struct EmbeddedShadow {
    event_recorder: EventRecorder,
    t2g_state: T2gState,
    cbm_payload_queue: VecDeque<CbmSample>,
    last_tcms_alarm: Option<AlarmLevel>,
    last_channel: Option<ActiveChannel>,
    cbm_params: CbmParams,
    hot_axle_params: HotAxleParams,
    t2g_params: T2gParams,
    summary: PerTrainEmbedded,
}

impl EmbeddedShadow {
    #[must_use]
    pub fn new(train: &Train) -> Self {
        Self {
            event_recorder: EventRecorder::new(EVENT_RECORDER_CAPACITY),
            t2g_state: T2gState::default(),
            cbm_payload_queue: VecDeque::new(),
            last_tcms_alarm: None,
            last_channel: None,
            cbm_params: CbmParams::default_metro(),
            hot_axle_params: HotAxleParams::default_metro(),
            t2g_params: T2gParams::default_metro(),
            summary: PerTrainEmbedded {
                train: train.id.to_string(),
                ..PerTrainEmbedded::default()
            },
        }
    }

    /// Record a movement command that was inhibited by the preceding TCMS
    /// control cycle. Keeping this evidence with the application stack makes
    /// the command/response boundary visible in JSON reports and GUI runs.
    pub(crate) fn record_tcms_departure_inhibit(&mut self) {
        self.summary.tcms_departure_inhibit_ticks =
            self.summary.tcms_departure_inhibit_ticks.saturating_add(1);
    }

    /// Record a section-progress hold commanded by the preceding TCMS cycle.
    pub(crate) fn record_tcms_travel_hold(&mut self) {
        self.summary.tcms_travel_hold_ticks = self.summary.tcms_travel_hold_ticks.saturating_add(1);
    }
}

/// Data produced by one embedded tick for downstream ground services.
#[derive(Clone, Debug)]
pub struct EmbeddedTickReport {
    pub tcms: ConsistStatus,
    /// Oldest queued CBM payload when T2G transmitted this tick.
    pub transmitted_cbm_sample: Option<CbmSample>,
}

/// Per-train evidence retained in [`EmbeddedSummary`].
#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct PerTrainEmbedded {
    pub train: String,
    pub controller_ticks: u64,
    pub tcms_ready_to_move_ticks: u64,
    pub tcms_trip_ticks: u64,
    pub tcms_departure_inhibit_ticks: u64,
    pub tcms_travel_hold_ticks: u64,
    pub event_records_written: u64,
    pub event_records_retained: u64,
    pub event_records_dropped: u64,
    pub cbm_samples: u64,
    pub cbm_watch_flags: u64,
    pub cbm_service_flags: u64,
    pub hot_axle_warning_ticks: u64,
    pub hot_axle_trip_ticks: u64,
    pub t2g_transmissions: u64,
    pub t2g_primary_ticks: u64,
    pub t2g_backup_ticks: u64,
    pub t2g_offline_ticks: u64,
    pub t2g_payloads_dropped: u64,
    pub maximum_t2g_queue_depth: u32,
    pub final_t2g_queue_depth: u32,
    pub final_tcms_alarm: String,
    pub final_t2g_channel: String,
}

/// Fleet-wide evidence that the embedded application stack participated in a
/// simulation run. These fields are serialized into CLI JSON and exposed by
/// both GUIs.
#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct EmbeddedSummary {
    pub train_count: u32,
    pub controller_ticks: u64,
    pub tcms_ready_to_move_ticks: u64,
    pub tcms_trip_ticks: u64,
    pub tcms_departure_inhibit_ticks: u64,
    pub tcms_travel_hold_ticks: u64,
    pub event_records_written: u64,
    pub event_records_retained: u64,
    pub event_records_dropped: u64,
    pub cbm_samples: u64,
    pub cbm_watch_flags: u64,
    pub cbm_service_flags: u64,
    pub hot_axle_warning_ticks: u64,
    pub hot_axle_trip_ticks: u64,
    pub t2g_transmissions: u64,
    pub t2g_primary_ticks: u64,
    pub t2g_backup_ticks: u64,
    pub t2g_offline_ticks: u64,
    pub t2g_payloads_dropped: u64,
    pub maximum_t2g_queue_depth: u32,
    pub final_t2g_queue_depth: u64,
    pub per_train: Vec<PerTrainEmbedded>,
}

/// Execute one deterministic T-ECU/A tick.
#[allow(clippy::too_many_arguments)]
pub fn embedded_tick(
    shadow: &mut EmbeddedShadow,
    train: &Train,
    onboard: &OnboardShadow,
    onboard_report: Option<&TickReport>,
    vehicle: &VehicleSystemsTickReport,
    faults: &FaultEngine,
    ambient_c: f32,
    sim_time_s: u32,
) -> EmbeddedTickReport {
    let now_ns = u64::from(sim_time_s).saturating_mul(1_000_000_000);
    let (section_id, at_station, speed_mmps) = match train.phase {
        TrainPhase::Traveling { section, .. } => {
            (Some(section.0 as u32), false, onboard.kin.speed_mmps)
        }
        TrainPhase::Dwelling { .. } | TrainPhase::AwaitingDispatch { .. } => (None, true, 0),
    };

    let hot_axle = hot_axle_evaluate(
        &HotAxleInputs {
            now_ns,
            ambient_dc: (ambient_c * 10.0).round() as i16,
            axles: axle_readings(train, faults.hot_axle_overheat_for(train.id), ambient_c),
        },
        &shadow.hot_axle_params,
    );

    let emergency = onboard_report.map(|report| report.brake.emergency_sources);
    let tcms = tcms_evaluate(&TcmsInputs {
        now_ns,
        speed_mmps,
        section_id,
        at_station,
        atp_emergency: onboard_report.is_some_and(|report| report.atp.is_emergency()),
        fire_emergency: emergency.is_some_and(|sources| sources.fire),
        derailment_emergency: emergency.is_some_and(|sources| sources.derailment),
        remote_assist_emergency: emergency.is_some_and(|sources| sources.remote_assist),
        obstacle_emergency: emergency.is_some_and(|sources| sources.obstacle),
        doors_interlock_ok: vehicle.doors_interlock_ok,
        bms_contactor_closed: matches!(
            onboard.bms_state.contactor,
            osr_bms::ContactorState::Closed
        ),
        traction_inverter_enabled: matches!(
            onboard.traction_state.inverter,
            InverterState::Running
        ),
        bms_alarm: bms_alarm(onboard.bms_state.alarm),
        traction_alarm: if onboard.traction_state.faults.any() {
            AlarmLevel::Trip
        } else {
            AlarmLevel::Nominal
        },
        fire_alarm: if onboard.fire_state.emergency_latched {
            AlarmLevel::Trip
        } else if onboard.fire_state.latched_tripped.any() {
            AlarmLevel::Warning
        } else {
            AlarmLevel::Nominal
        },
        derailment_alarm: if onboard.derailment_state.latched_tripped {
            AlarmLevel::Trip
        } else {
            AlarmLevel::Nominal
        },
        hot_axle_alarm: hot_axle_alarm(hot_axle.worst_alarm),
        hvac_alarm: if vehicle.hvac_reduced {
            AlarmLevel::Warning
        } else {
            AlarmLevel::Nominal
        },
        comfort_alarm: if vehicle.aux_load_shed_active {
            AlarmLevel::Warning
        } else {
            AlarmLevel::Nominal
        },
        door_alarm: if !vehicle.doors_interlock_ok && !at_station {
            AlarmLevel::Trip
        } else {
            AlarmLevel::Nominal
        },
        soc_ppt: (train.soc.clamp(0.0, 1.0) * 1_000.0).round() as u16,
        v24_rail_enabled: vehicle.v24_rail_enabled,
        v110_rail_enabled: vehicle.v110_rail_enabled,
        direct_hv_enabled: vehicle.direct_hv_enabled,
    });

    record_embedded_events(
        shadow,
        now_ns,
        section_id,
        speed_mmps,
        onboard_report,
        &tcms,
        vehicle,
    );

    // CBM uses service-life-linked nominal inputs. A declared degradation
    // fault drives every component over its service threshold, allowing the
    // full sampler → T2G → OCC evidence path to be exercised.
    let cbm = cbm_evaluate(
        &cbm_inputs(
            train,
            now_ns,
            faults.cbm_degradation_for(train.id),
            ambient_c,
        ),
        &shadow.cbm_params,
    );
    shadow.summary.cbm_samples = shadow.summary.cbm_samples.saturating_add(1);
    for flag in &cbm.flags {
        match flag.health {
            ComponentHealth::Nominal => {}
            ComponentHealth::Watch => {
                shadow.summary.cbm_watch_flags = shadow.summary.cbm_watch_flags.saturating_add(1);
            }
            ComponentHealth::Service => {
                shadow.summary.cbm_service_flags =
                    shadow.summary.cbm_service_flags.saturating_add(1);
            }
        }
    }
    if cbm.sample.worst_health != ComponentHealth::Nominal {
        shadow.event_recorder.record(
            EventRecord::new(now_ns, EventCategory::Diagnostic, 0xCB0)
                .with_values(i64::from(cbm.flags.len() as u32), 0),
        );
    }

    // TCMS aggregates at 1 Hz while CBM ground telemetry is sampled at 0.5 Hz.
    // Queue the real payload so radio outages preserve ordering and recovery
    // drains the original samples instead of substituting the latest value.
    if sim_time_s % 2 == 0 {
        if shadow.cbm_payload_queue.len() >= CBM_PAYLOAD_QUEUE_CAPACITY {
            shadow.cbm_payload_queue.pop_front();
            shadow.summary.t2g_payloads_dropped =
                shadow.summary.t2g_payloads_dropped.saturating_add(1);
        }
        shadow.cbm_payload_queue.push_back(cbm.sample.clone());
    }
    let queued_payloads = shadow.cbm_payload_queue.len().min(u32::MAX as usize) as u32;
    let t2g = t2g_evaluate(
        &shadow.t2g_state,
        &T2gInputs {
            now_ns,
            primary_signal: if faults.t2g_primary_offline_for(train.id)
                || faults.t2g_all_offline_for(train.id)
            {
                0
            } else {
                80
            },
            backup_signal: if faults.t2g_all_offline_for(train.id) {
                0
            } else {
                55
            },
            queued_payloads,
            emergency_priority: tcms.any_emergency,
        },
        &shadow.t2g_params,
    );
    shadow.t2g_state = t2g.state;
    let transmitted_cbm_sample = if t2g.transmit_now {
        shadow.cbm_payload_queue.pop_front()
    } else {
        None
    };
    debug_assert_eq!(
        shadow.cbm_payload_queue.len().min(u32::MAX as usize) as u32,
        t2g.queue_remaining
    );
    if t2g.transmit_now {
        shadow.summary.t2g_transmissions = shadow.summary.t2g_transmissions.saturating_add(1);
    }
    match t2g.active {
        ActiveChannel::Primary => {
            shadow.summary.t2g_primary_ticks = shadow.summary.t2g_primary_ticks.saturating_add(1);
        }
        ActiveChannel::Backup => {
            shadow.summary.t2g_backup_ticks = shadow.summary.t2g_backup_ticks.saturating_add(1);
        }
        ActiveChannel::Offline => {
            shadow.summary.t2g_offline_ticks = shadow.summary.t2g_offline_ticks.saturating_add(1);
        }
    }
    if shadow.last_channel != Some(t2g.active) {
        shadow.event_recorder.record(
            EventRecord::new(now_ns, EventCategory::Diagnostic, 0x720)
                .with_values(channel_code(t2g.active), i64::from(t2g.queue_remaining)),
        );
        shadow.last_channel = Some(t2g.active);
    }

    shadow.summary.controller_ticks = shadow.summary.controller_ticks.saturating_add(1);
    if tcms.ready_to_move {
        shadow.summary.tcms_ready_to_move_ticks =
            shadow.summary.tcms_ready_to_move_ticks.saturating_add(1);
    }
    if tcms.worst_alarm == AlarmLevel::Trip {
        shadow.summary.tcms_trip_ticks = shadow.summary.tcms_trip_ticks.saturating_add(1);
    }
    match hot_axle.worst_alarm {
        AxleAlarm::Nominal => {}
        AxleAlarm::Warning => {
            shadow.summary.hot_axle_warning_ticks =
                shadow.summary.hot_axle_warning_ticks.saturating_add(1);
        }
        AxleAlarm::Trip => {
            shadow.summary.hot_axle_trip_ticks =
                shadow.summary.hot_axle_trip_ticks.saturating_add(1);
        }
    }
    shadow.summary.maximum_t2g_queue_depth = shadow
        .summary
        .maximum_t2g_queue_depth
        .max(t2g.queue_remaining);
    shadow.summary.final_t2g_queue_depth = t2g.queue_remaining;
    shadow.summary.final_tcms_alarm = format!("{:?}", tcms.worst_alarm);
    shadow.summary.final_t2g_channel = format!("{:?}", t2g.active);
    shadow.summary.event_records_written = shadow.event_recorder.total_written();
    shadow.summary.event_records_retained = shadow.event_recorder.len() as u64;
    shadow.summary.event_records_dropped = shadow.event_recorder.dropped();

    EmbeddedTickReport {
        tcms,
        transmitted_cbm_sample,
    }
}

fn record_embedded_events(
    shadow: &mut EmbeddedShadow,
    now_ns: u64,
    section_id: Option<u32>,
    speed_mmps: i32,
    onboard_report: Option<&TickReport>,
    tcms: &ConsistStatus,
    vehicle: &VehicleSystemsTickReport,
) {
    shadow.event_recorder.record(
        EventRecord::new(now_ns, EventCategory::Position, 1).with_values(
            i64::from(speed_mmps),
            i64::from(section_id.unwrap_or_default()),
        ),
    );
    if let Some(report) = onboard_report {
        if !matches!(report.brake.command, BrakeCommand::Release) {
            let effort = match report.brake.command {
                BrakeCommand::Release => 0,
                BrakeCommand::Service(value) => i64::from(value),
                BrakeCommand::Emergency => 1_000,
            };
            shadow.event_recorder.record(
                EventRecord::new(now_ns, EventCategory::BrakeCommand, 1)
                    .with_values(effort, i64::from(report.brake.friction_effort_ppt)),
            );
        }
    }
    if shadow.last_tcms_alarm != Some(tcms.worst_alarm) {
        shadow.event_recorder.record(
            EventRecord::new(now_ns, EventCategory::Diagnostic, 0x7C0)
                .with_values(alarm_code(tcms.worst_alarm), i64::from(tcms.ready_to_move)),
        );
        shadow.last_tcms_alarm = Some(tcms.worst_alarm);
    }
    if vehicle.pis_announcement {
        shadow
            .event_recorder
            .record(EventRecord::new(now_ns, EventCategory::Comfort, 1));
    }
}

fn axle_readings(train: &Train, overheat: bool, ambient_c: f32) -> Vec<AxleReading> {
    let axle_count = train.consist.car_count.saturating_mul(4) as usize;
    let nominal_dc = (ambient_c * 10.0).round() as i16 + 100;
    let temp_dc = if overheat { 1_100 } else { nominal_dc };
    vec![
        AxleReading {
            sensor_a: AxleSensor {
                temp_dc,
                valid: true,
            },
            sensor_b: AxleSensor {
                temp_dc,
                valid: true,
            },
        };
        axle_count
    ]
}

fn cbm_inputs(train: &Train, now_ns: u64, degraded: bool, ambient_c: f32) -> CbmInputs {
    let cars = train.consist.car_count as usize;
    let axles = cars.saturating_mul(4);
    let motors = cars.saturating_mul(2);
    let service_life_loss = (train.odometer_km / 2_000.0).floor().clamp(0.0, 850.0) as u16;
    CbmInputs {
        now_ns,
        train_id: train.id.0.min(u64::from(u32::MAX)) as u32,
        bearing_vib_ppt: vec![if degraded { 8_000 } else { 1_000 }; axles],
        motor_temp_dc: vec![
            if degraded {
                1_700
            } else {
                (ambient_c * 10.0).round() as i16 + 250
            };
            motors
        ],
        brake_pad_remaining_ppt: vec![
            if degraded {
                100
            } else {
                1_000_u16.saturating_sub(service_life_loss)
            };
            cars
        ],
        wheel_tread_remaining_ppt: vec![
            if degraded {
                100
            } else {
                1_000_u16.saturating_sub(service_life_loss / 2)
            };
            axles
        ],
    }
}

fn bms_alarm(value: osr_bms::AlarmLevel) -> AlarmLevel {
    match value {
        osr_bms::AlarmLevel::Nominal => AlarmLevel::Nominal,
        osr_bms::AlarmLevel::Warning => AlarmLevel::Warning,
        osr_bms::AlarmLevel::Trip => AlarmLevel::Trip,
    }
}

fn hot_axle_alarm(value: AxleAlarm) -> AlarmLevel {
    match value {
        AxleAlarm::Nominal => AlarmLevel::Nominal,
        AxleAlarm::Warning => AlarmLevel::Warning,
        AxleAlarm::Trip => AlarmLevel::Trip,
    }
}

const fn alarm_code(value: AlarmLevel) -> i64 {
    match value {
        AlarmLevel::Nominal => 0,
        AlarmLevel::Warning => 1,
        AlarmLevel::Trip => 2,
    }
}

const fn channel_code(value: ActiveChannel) -> i64 {
    match value {
        ActiveChannel::Primary => 1,
        ActiveChannel::Backup => 2,
        ActiveChannel::Offline => 0,
    }
}

#[must_use]
pub fn summarise(shadows: &[EmbeddedShadow]) -> EmbeddedSummary {
    let mut total = EmbeddedSummary {
        train_count: shadows.len() as u32,
        ..EmbeddedSummary::default()
    };
    for shadow in shadows {
        let item = shadow.summary.clone();
        total.controller_ticks = total.controller_ticks.saturating_add(item.controller_ticks);
        total.tcms_ready_to_move_ticks = total
            .tcms_ready_to_move_ticks
            .saturating_add(item.tcms_ready_to_move_ticks);
        total.tcms_trip_ticks = total.tcms_trip_ticks.saturating_add(item.tcms_trip_ticks);
        total.tcms_departure_inhibit_ticks = total
            .tcms_departure_inhibit_ticks
            .saturating_add(item.tcms_departure_inhibit_ticks);
        total.tcms_travel_hold_ticks = total
            .tcms_travel_hold_ticks
            .saturating_add(item.tcms_travel_hold_ticks);
        total.event_records_written = total
            .event_records_written
            .saturating_add(item.event_records_written);
        total.event_records_retained = total
            .event_records_retained
            .saturating_add(item.event_records_retained);
        total.event_records_dropped = total
            .event_records_dropped
            .saturating_add(item.event_records_dropped);
        total.cbm_samples = total.cbm_samples.saturating_add(item.cbm_samples);
        total.cbm_watch_flags = total.cbm_watch_flags.saturating_add(item.cbm_watch_flags);
        total.cbm_service_flags = total
            .cbm_service_flags
            .saturating_add(item.cbm_service_flags);
        total.hot_axle_warning_ticks = total
            .hot_axle_warning_ticks
            .saturating_add(item.hot_axle_warning_ticks);
        total.hot_axle_trip_ticks = total
            .hot_axle_trip_ticks
            .saturating_add(item.hot_axle_trip_ticks);
        total.t2g_transmissions = total
            .t2g_transmissions
            .saturating_add(item.t2g_transmissions);
        total.t2g_primary_ticks = total
            .t2g_primary_ticks
            .saturating_add(item.t2g_primary_ticks);
        total.t2g_backup_ticks = total.t2g_backup_ticks.saturating_add(item.t2g_backup_ticks);
        total.t2g_offline_ticks = total
            .t2g_offline_ticks
            .saturating_add(item.t2g_offline_ticks);
        total.t2g_payloads_dropped = total
            .t2g_payloads_dropped
            .saturating_add(item.t2g_payloads_dropped);
        total.maximum_t2g_queue_depth = total
            .maximum_t2g_queue_depth
            .max(item.maximum_t2g_queue_depth);
        total.final_t2g_queue_depth = total
            .final_t2g_queue_depth
            .saturating_add(u64::from(item.final_t2g_queue_depth));
        total.per_train.push(item);
    }
    total
}
