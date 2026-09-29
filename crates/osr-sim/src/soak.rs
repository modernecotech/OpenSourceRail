//! Deterministic multi-day simulator soak profiles and logical resource bounds.
//!
//! The soak deliberately measures retained application state rather than host
//! RSS. Allocator, linker and runner differences make RSS unsuitable for a
//! reproducible acceptance gate; the structures below are the state that can
//! grow as simulated time advances.

use serde::{Deserialize, Serialize};

use crate::backend_systems::WORK_ORDER_EVIDENCE_CAPACITY;
use crate::embedded::{CBM_PAYLOAD_QUEUE_CAPACITY, EVENT_RECORDER_CAPACITY};
use crate::fault::{Fault, FaultKind, FaultScope, TrainFaultScope};
use crate::scenario_file::canonical_samawah_scenario;
use crate::sim::{run_with_event_recording, RuntimeConfig, ScenarioConfig, SimResult};

pub const FAST_DAYS: u32 = 2;
// Five seconds is deliberately not an integer multiple of the 0.5 Hz CBM
// sampling period. Alternating sample/send ticks preserve the production
// model's spare upload bandwidth, so a recovered radio can drain its backlog.
pub const FAST_TIME_STEP_S: u32 = 5;
pub const FULL_DAYS: u32 = 7;
pub const FULL_TIME_STEP_S: u32 = 5;
const COMPONENTS_PER_CAR: u64 = 11;
const MAX_COMPACT_RESULT_BYTES: u64 = 2_000_000;

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum SoakProfile {
    Normal,
    Peak,
    Degraded,
    Recovery,
}

impl SoakProfile {
    pub const ALL: [Self; 4] = [Self::Normal, Self::Peak, Self::Degraded, Self::Recovery];

    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Normal => "normal",
            Self::Peak => "peak",
            Self::Degraded => "degraded",
            Self::Recovery => "recovery",
        }
    }

    #[must_use]
    pub const fn seed(self) -> u64 {
        match self {
            Self::Normal => 24_301,
            Self::Peak => 24_302,
            Self::Degraded => 24_303,
            Self::Recovery => 24_304,
        }
    }
}

#[derive(Copy, Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct SoakConfig {
    pub days: u32,
    pub time_step_s: u32,
}

impl SoakConfig {
    #[must_use]
    pub const fn fast() -> Self {
        Self {
            days: FAST_DAYS,
            time_step_s: FAST_TIME_STEP_S,
        }
    }

    #[must_use]
    pub const fn full() -> Self {
        Self {
            days: FULL_DAYS,
            time_step_s: FULL_TIME_STEP_S,
        }
    }

    #[must_use]
    pub const fn duration_s(self) -> u32 {
        self.days.saturating_mul(86_400)
    }

    #[must_use]
    pub const fn checkpoint_s(self) -> u32 {
        self.duration_s() / 2
    }
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct ResourceSnapshot {
    pub detailed_events_retained: u64,
    pub event_count_keys: u64,
    pub event_records_retained: u64,
    pub t2g_payloads_retained: u64,
    pub historian_metrics_retained: u64,
    pub historian_samples_retained: u64,
    pub cbm_components_tracked: u64,
    pub work_orders_retained: u64,
    pub compact_result_bytes: u64,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct ResourceBounds {
    pub detailed_events_retained: u64,
    pub event_count_keys: u64,
    pub event_records_retained: u64,
    pub t2g_payloads_retained: u64,
    pub historian_metrics_retained: u64,
    pub historian_samples_retained: u64,
    pub cbm_components_tracked: u64,
    pub work_orders_retained: u64,
    pub compact_result_bytes: u64,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SoakProfileReport {
    pub profile: SoakProfile,
    pub seed: u64,
    pub checkpoint_sim_s: u32,
    pub final_sim_s: u32,
    pub checkpoint: ResourceSnapshot,
    pub final_state: ResourceSnapshot,
    pub bounds: ResourceBounds,
    pub minimum_train_soc: f32,
    pub total_train_km: f64,
    pub faults_fired: u64,
    pub invariant_failures: u64,
    pub assertions: Vec<String>,
    pub failures: Vec<String>,
    pub passed: bool,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct SoakReport {
    pub schema: String,
    pub evidence_class: String,
    pub configuration: SoakConfig,
    pub profiles: Vec<SoakProfileReport>,
    pub passed: bool,
    pub remaining_release_evidence: Vec<String>,
}

#[must_use]
pub fn run_suite(configuration: SoakConfig) -> SoakReport {
    assert!(
        configuration.days >= 2,
        "soak must span at least two simulated days"
    );
    assert!(
        configuration.time_step_s > 0,
        "soak time step must be positive"
    );
    let profiles = SoakProfile::ALL
        .into_iter()
        .map(|profile| run_profile(profile, configuration))
        .collect::<Vec<_>>();
    let passed = profiles.iter().all(|profile| profile.passed);
    SoakReport {
        schema: "osr-software-soak/1".into(),
        evidence_class: "deterministic-software-design-evidence-not-hardware-qualification".into(),
        configuration,
        profiles,
        passed,
        remaining_release_evidence: vec![
            "selected-target WCET, stack and heap measurement".into(),
            "wall-clock endurance and storage wear on production hardware".into(),
            "power-cut, network and clock HIL with production transports".into(),
            "independent safety assessment and authority acceptance".into(),
        ],
    }
}

fn run_profile(profile: SoakProfile, configuration: SoakConfig) -> SoakProfileReport {
    let final_s = configuration.duration_s();
    let checkpoint_s = configuration.checkpoint_s();
    let final_scenario = scenario_for(profile, final_s);
    // Both executions use the same complete manifest. The shorter execution
    // is therefore a true prefix checkpoint, including the same absolute
    // fault/recovery times, rather than a separately scaled scenario.
    let checkpoint_scenario = final_scenario.clone();
    let checkpoint_result = run_with_event_recording(
        &checkpoint_scenario,
        &runtime(checkpoint_s, configuration.time_step_s),
        false,
    );
    let final_result = run_with_event_recording(
        &final_scenario,
        &runtime(final_s, configuration.time_step_s),
        false,
    );
    let train_count = final_result.embedded.train_count as u64;
    let consist_cars = u64::from(final_scenario.consist.car_count);
    let metric_bound = train_count.saturating_mul(5);
    let component_bound = train_count
        .saturating_mul(consist_cars)
        .saturating_mul(COMPONENTS_PER_CAR);
    let historian = osr_historian::HistorianParams::default_metro();
    let bounds = ResourceBounds {
        detailed_events_retained: 0,
        event_count_keys: 9,
        event_records_retained: train_count.saturating_mul(EVENT_RECORDER_CAPACITY as u64),
        t2g_payloads_retained: train_count.saturating_mul(CBM_PAYLOAD_QUEUE_CAPACITY as u64),
        historian_metrics_retained: metric_bound,
        historian_samples_retained: metric_bound.saturating_mul(
            historian
                .raw_capacity
                .saturating_add(historian.decimated_capacity) as u64,
        ),
        cbm_components_tracked: component_bound,
        work_orders_retained: WORK_ORDER_EVIDENCE_CAPACITY as u64,
        compact_result_bytes: MAX_COMPACT_RESULT_BYTES,
    };
    let checkpoint = snapshot(&checkpoint_result);
    let final_state = snapshot(&final_result);
    let minimum_train_soc = final_result
        .per_train_final_soc
        .iter()
        .map(|(_, _, _, minimum)| *minimum)
        .fold(1.0_f32, f32::min);
    let mut assertions = vec![
        "detailed event retention disabled while aggregate counts remain available".into(),
        "event recorder and T2G queues stay within fixed per-train capacities".into(),
        "historian raw and decimated tiers stay within fixed per-metric capacities".into(),
        "CBM component state and detailed work-order evidence stay within explicit capacities"
            .into(),
        "every generated work order is represented by retained or dropped-record accounting".into(),
        "compact result payload stays within the deterministic evidence envelope".into(),
        "operating reserve and simulator invariants remain satisfied".into(),
    ];
    let mut failures = resource_failures(&checkpoint, &bounds)
        .into_iter()
        .map(|failure| format!("checkpoint: {failure}"))
        .collect::<Vec<_>>();
    failures.extend(resource_failures(&final_state, &bounds));
    for (label, result) in [("checkpoint", &checkpoint_result), ("final", &final_result)] {
        let generated = result
            .backend_systems
            .routine_work_orders
            .saturating_add(result.backend_systems.urgent_work_orders);
        let accounted = result
            .backend_systems
            .work_orders
            .len()
            .try_into()
            .unwrap_or(u64::MAX);
        let accounted = accounted.saturating_add(result.backend_systems.work_order_records_dropped);
        if generated != accounted {
            failures.push(format!(
                "{label}: {generated} generated work orders but {accounted} retained/dropped records"
            ));
        }
    }
    if !final_result.invariant_violations.is_empty() {
        failures.push(format!(
            "{} simulator invariant failures",
            final_result.invariant_violations.len()
        ));
    }
    if minimum_train_soc < 0.20 {
        failures.push(format!(
            "minimum train SoC {minimum_train_soc:.3} below 0.20 reserve"
        ));
    }
    if final_result.total_train_km <= 0.0 {
        failures.push("fleet accumulated no distance".into());
    }
    profile_assertions(
        profile,
        &checkpoint_result,
        &final_result,
        &mut assertions,
        &mut failures,
    );
    // The final snapshot may grow from the checkpoint, but no retained field
    // may cross its explicit bound. This detects time-dependent leaks without
    // requiring allocator-specific process measurements.
    assertions
        .push("checkpoint-to-final retained-state growth remains inside every declared cap".into());
    let passed = failures.is_empty();
    SoakProfileReport {
        profile,
        seed: profile.seed(),
        checkpoint_sim_s: checkpoint_s,
        final_sim_s: final_s,
        checkpoint,
        final_state,
        bounds,
        minimum_train_soc,
        total_train_km: final_result.total_train_km,
        faults_fired: final_result.faults_fired.len() as u64,
        invariant_failures: final_result.invariant_violations.len() as u64,
        assertions,
        failures,
        passed,
    }
}

fn runtime(duration_s: u32, time_step_s: u32) -> RuntimeConfig {
    RuntimeConfig {
        duration_s,
        time_step_s,
        status_every_s: 0,
        csv_out: None,
        csv_every_s: 60,
        // The direct MA derived state is bounded. Consensus restart/storage
        // behavior has a separate deterministic harness and report; its audit
        // journal needs deployment-specific retention/compaction policy.
        ma_check_every_s: 0,
    }
}

fn scenario_for(profile: SoakProfile, duration_s: u32) -> ScenarioConfig {
    let mut scenario = canonical_samawah_scenario();
    scenario.name = format!("Samawah {} software soak", profile.name());
    match profile {
        SoakProfile::Normal => {}
        SoakProfile::Peak => {
            for fleet in &mut scenario.fleets {
                for window in &mut fleet.schedule.windows {
                    window.headway_s = window.headway_s.min(180);
                }
            }
        }
        SoakProfile::Degraded => {
            scenario.faults.extend([
                Fault {
                    name: "soak-radio-blackout".into(),
                    from_sim_s: 0,
                    to_sim_s: duration_s,
                    kind: FaultKind::T2gAllOffline {
                        scope: TrainFaultScope::All,
                    },
                },
                Fault {
                    name: "soak-grid-outage".into(),
                    from_sim_s: deterministic_offset(SoakProfile::Degraded.seed(), duration_s / 8),
                    to_sim_s: duration_s,
                    kind: FaultKind::GridOutage {
                        scope: FaultScope::All,
                    },
                },
            ]);
        }
        SoakProfile::Recovery => {
            let recovery_at = duration_s.saturating_mul(3) / 5;
            let fault_at = deterministic_offset(SoakProfile::Recovery.seed(), duration_s / 10);
            scenario.faults.extend([
                Fault {
                    name: "soak-recovering-radio-blackout".into(),
                    from_sim_s: fault_at,
                    to_sim_s: recovery_at,
                    kind: FaultKind::T2gAllOffline {
                        scope: TrainFaultScope::All,
                    },
                },
                Fault {
                    name: "soak-recovering-grid-outage".into(),
                    from_sim_s: fault_at,
                    to_sim_s: recovery_at,
                    kind: FaultKind::GridOutage {
                        scope: FaultScope::All,
                    },
                },
                Fault {
                    name: "soak-recovering-cbm-degradation".into(),
                    from_sim_s: fault_at,
                    to_sim_s: recovery_at,
                    kind: FaultKind::CbmDegradation {
                        scope: TrainFaultScope::All,
                    },
                },
            ]);
        }
    }
    scenario
}

const fn deterministic_offset(seed: u64, span_s: u32) -> u32 {
    if span_s == 0 {
        0
    } else {
        let mixed = seed ^ (seed << 13) ^ (seed >> 7) ^ (seed << 17);
        (mixed % span_s as u64) as u32
    }
}

fn snapshot(result: &SimResult) -> ResourceSnapshot {
    ResourceSnapshot {
        detailed_events_retained: result.events.len() as u64,
        event_count_keys: result.event_counts.len() as u64,
        event_records_retained: result.embedded.event_records_retained,
        t2g_payloads_retained: result.embedded.final_t2g_queue_depth,
        historian_metrics_retained: u64::from(result.backend_systems.historian_metrics_retained),
        historian_samples_retained: result.backend_systems.analytics_samples_evaluated,
        cbm_components_tracked: result.backend_systems.cbm_components_tracked,
        work_orders_retained: result.backend_systems.work_orders.len() as u64,
        compact_result_bytes: serde_json::to_vec(result)
            .expect("simulation result must serialize")
            .len() as u64,
    }
}

fn resource_failures(snapshot: &ResourceSnapshot, bounds: &ResourceBounds) -> Vec<String> {
    let checks = [
        (
            "detailed events",
            snapshot.detailed_events_retained,
            bounds.detailed_events_retained,
        ),
        (
            "event-count keys",
            snapshot.event_count_keys,
            bounds.event_count_keys,
        ),
        (
            "event records",
            snapshot.event_records_retained,
            bounds.event_records_retained,
        ),
        (
            "T2G payloads",
            snapshot.t2g_payloads_retained,
            bounds.t2g_payloads_retained,
        ),
        (
            "historian metrics",
            snapshot.historian_metrics_retained,
            bounds.historian_metrics_retained,
        ),
        (
            "historian samples",
            snapshot.historian_samples_retained,
            bounds.historian_samples_retained,
        ),
        (
            "CBM components",
            snapshot.cbm_components_tracked,
            bounds.cbm_components_tracked,
        ),
        (
            "work orders",
            snapshot.work_orders_retained,
            bounds.work_orders_retained,
        ),
        (
            "compact result bytes",
            snapshot.compact_result_bytes,
            bounds.compact_result_bytes,
        ),
    ];
    checks
        .into_iter()
        .filter(|(_, actual, bound)| actual > bound)
        .map(|(name, actual, bound)| format!("{name} retained {actual}, bound {bound}"))
        .collect()
}

fn profile_assertions(
    profile: SoakProfile,
    checkpoint: &SimResult,
    final_result: &SimResult,
    assertions: &mut Vec<String>,
    failures: &mut Vec<String>,
) {
    match profile {
        SoakProfile::Normal => {
            assertions.push(
                "normal service completes repeated service/stabling cycles without injected faults"
                    .into(),
            );
            if !final_result.faults_fired.is_empty() {
                failures.push("normal profile unexpectedly fired a fault".into());
            }
            if final_result.total_train_km <= checkpoint.total_train_km {
                failures.push(
                    "normal profile accumulated no additional fleet distance after checkpoint"
                        .into(),
                );
            }
        }
        SoakProfile::Peak => {
            assertions.push(
                "peak profile uses three-minute-or-better published headways and continues accumulating fleet distance after the checkpoint".into(),
            );
            if final_result.total_train_km <= checkpoint.total_train_km {
                failures.push(
                    "peak profile accumulated no additional fleet distance after checkpoint".into(),
                );
            }
        }
        SoakProfile::Degraded => {
            assertions.push("continuous radio loss saturates, but never exceeds, the bounded store-and-forward queue".into());
            if final_result.embedded.maximum_t2g_queue_depth != CBM_PAYLOAD_QUEUE_CAPACITY as u32
                || final_result.embedded.final_t2g_queue_depth
                    != final_result.embedded.train_count as u64 * CBM_PAYLOAD_QUEUE_CAPACITY as u64
                || final_result.embedded.t2g_payloads_dropped == 0
                || final_result.faults_fired.len() != 2
            {
                failures.push(
                    "degraded profile did not exercise bounded T2G saturation and drop accounting"
                        .into(),
                );
            }
        }
        SoakProfile::Recovery => {
            assertions.push("radio/grid/CBM degradation clears and queued telemetry drains before the final checkpoint".into());
            if final_result.embedded.maximum_t2g_queue_depth != CBM_PAYLOAD_QUEUE_CAPACITY as u32
                || final_result.embedded.final_t2g_queue_depth != 0
                || final_result.embedded.t2g_payloads_dropped == 0
                || final_result.backend_systems.urgent_work_orders == 0
                || final_result.faults_fired.len() != 3
            {
                failures.push("recovery profile did not saturate, recover, drain and process degraded telemetry".into());
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deterministic_offsets_stay_in_span() {
        for profile in SoakProfile::ALL {
            assert!(deterministic_offset(profile.seed(), 10_000) < 10_000);
        }
    }

    #[test]
    fn compact_snapshot_enforces_all_declared_bounds() {
        let snapshot = ResourceSnapshot {
            detailed_events_retained: 1,
            ..ResourceSnapshot::default()
        };
        let bounds = ResourceBounds {
            detailed_events_retained: 0,
            event_count_keys: 0,
            event_records_retained: 0,
            t2g_payloads_retained: 0,
            historian_metrics_retained: 0,
            historian_samples_retained: 0,
            cbm_components_tracked: 0,
            work_orders_retained: 0,
            compact_result_bytes: 0,
        };
        assert_eq!(resource_failures(&snapshot, &bounds).len(), 1);
    }
}
