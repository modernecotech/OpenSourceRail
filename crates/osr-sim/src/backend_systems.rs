//! Deterministic depot/backend processing of transmitted train telemetry.
//!
//! The shadow consumes only CBM payloads actually released by the T2G radio
//! queue. It runs the real depot work-order evaluator, retains a bounded set
//! of operational metrics in the historian, and evaluates the real analytics
//! statistics over the retained evidence at the end of a run.

use osr_analytics::basic_stats;
use osr_cbm_backend::{
    ingest_sample_in_place, CbmBackendParams, CbmBackendState, Priority, WorkOrder,
};
use osr_cbm_onboard::{CbmSample, ComponentHealth};
use osr_historian::{Historian, Sample};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug)]
pub struct BackendSystemsShadow {
    cbm_state: CbmBackendState,
    cbm_params: CbmBackendParams,
    historian: Historian,
    summary: BackendSystemsSummary,
}

impl Default for BackendSystemsShadow {
    fn default() -> Self {
        Self {
            cbm_state: CbmBackendState::default(),
            cbm_params: CbmBackendParams::default_depot(),
            historian: Historian::default(),
            summary: BackendSystemsSummary::default(),
        }
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct BackendWorkOrderEvidence {
    pub raised_ns: u64,
    pub train_id: u32,
    pub component: String,
    pub component_index: u16,
    pub priority: String,
}

impl From<WorkOrder> for BackendWorkOrderEvidence {
    fn from(order: WorkOrder) -> Self {
        Self {
            raised_ns: order.raised_ns,
            train_id: order.key.train_id,
            component: format!("{:?}", order.key.component),
            component_index: order.key.index,
            priority: format!("{:?}", order.priority),
        }
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct BackendSystemsSummary {
    pub cbm_samples_received: u64,
    pub cbm_components_tracked: u64,
    pub routine_work_orders: u64,
    pub urgent_work_orders: u64,
    pub historian_samples_ingested: u64,
    pub historian_metrics_retained: u32,
    pub analytics_metrics_evaluated: u32,
    pub analytics_samples_evaluated: u64,
    pub work_orders: Vec<BackendWorkOrderEvidence>,
}

/// Ingest one radio-delivered CBM payload into the depot services.
pub fn ingest_cbm_sample(shadow: &mut BackendSystemsShadow, sample: &CbmSample) {
    let orders = ingest_sample_in_place(&mut shadow.cbm_state, sample, &shadow.cbm_params);
    shadow.summary.cbm_samples_received = shadow.summary.cbm_samples_received.saturating_add(1);
    for order in orders {
        match order.priority {
            Priority::Routine => {
                shadow.summary.routine_work_orders =
                    shadow.summary.routine_work_orders.saturating_add(1);
            }
            Priority::Urgent => {
                shadow.summary.urgent_work_orders =
                    shadow.summary.urgent_work_orders.saturating_add(1);
            }
        }
        shadow.summary.work_orders.push(order.into());
    }

    let now = sample.now_ns;
    let train = sample.train_id;
    ingest_metric(
        shadow,
        format!("train.{train}.cbm.health"),
        now,
        health_value(sample.worst_health),
    );
    if let Some(value) = sample.bearing_vib_ppt.iter().max() {
        ingest_metric(
            shadow,
            format!("train.{train}.bearing.max_vib_ppt"),
            now,
            f64::from(*value),
        );
    }
    if let Some(value) = sample.motor_temp_dc.iter().max() {
        ingest_metric(
            shadow,
            format!("train.{train}.motor.max_temp_dc"),
            now,
            f64::from(*value),
        );
    }
    if let Some(value) = sample.brake_pad_remaining_ppt.iter().min() {
        ingest_metric(
            shadow,
            format!("train.{train}.brake_pad.min_remaining_ppt"),
            now,
            f64::from(*value),
        );
    }
    if let Some(value) = sample.wheel_tread_remaining_ppt.iter().min() {
        ingest_metric(
            shadow,
            format!("train.{train}.wheel.min_remaining_ppt"),
            now,
            f64::from(*value),
        );
    }
}

fn ingest_metric(shadow: &mut BackendSystemsShadow, metric: String, timestamp_ns: u64, value: f64) {
    shadow.historian.ingest(
        &metric,
        Sample {
            timestamp_ns,
            value,
        },
    );
    shadow.summary.historian_samples_ingested =
        shadow.summary.historian_samples_ingested.saturating_add(1);
}

const fn health_value(health: ComponentHealth) -> f64 {
    match health {
        ComponentHealth::Nominal => 0.0,
        ComponentHealth::Watch => 1.0,
        ComponentHealth::Service => 2.0,
    }
}

/// Freeze bounded backend and analytics evidence into the simulation result.
#[must_use]
pub fn summarise(shadow: &BackendSystemsShadow) -> BackendSystemsSummary {
    let mut summary = shadow.summary.clone();
    summary.cbm_components_tracked = shadow.cbm_state.components.len() as u64;
    let metrics = shadow.historian.metrics();
    summary.historian_metrics_retained = metrics.len() as u32;
    summary.analytics_metrics_evaluated = metrics.len() as u32;
    summary.analytics_samples_evaluated = metrics
        .iter()
        .map(|metric| basic_stats(&shadow.historian.query(metric, 0, u64::MAX)).count as u64)
        .sum();
    summary
}
