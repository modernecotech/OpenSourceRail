//! Deterministic restart, storage, communications and time-source fault harness.
//!
//! This is intentionally in-process: it makes safety/recovery traces cheap and
//! reproducible in CI. Deployment HIL still has to repeat the scenarios on the
//! selected processors, storage, network and clocks.

use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

use crate::durable::{RestoreError, StableStore, StoreError, WriteFault};
use crate::invariants;
use crate::{Category, Cluster, Config, LogIndex, NodeId};

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum FaultAction {
    Tick { duration_ns: u64 },
    Propose { value: Vec<u8>, category: Category },
    Crash { node: NodeId },
    Restart { node: NodeId },
    Partition { node: NodeId },
    Heal { node: NodeId },
    DropFrom { node: NodeId, enabled: bool },
    DropTo { node: NodeId, enabled: bool },
    Delay { node: NodeId, ticks: u32 },
    ClockOffset { offset_ns: i64 },
    TimeSource { available: bool },
    Telemetry { available: bool },
    Checkpoint { node: NodeId },
    DiskFull { node: NodeId },
    PartialWrite { node: NodeId, bytes: usize },
    CorruptStableByte { node: NodeId, offset: usize },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct TraceRow {
    pub step: usize,
    pub action: FaultAction,
    pub leader: Option<NodeId>,
    pub maximum_commit_index: LogIndex,
    pub safe_state: bool,
    pub outcome: String,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct FaultReport {
    pub seed: u64,
    pub passed: bool,
    pub invariant_failures: Vec<String>,
    pub alarms: BTreeSet<String>,
    pub trace: Vec<TraceRow>,
}

#[derive(Debug)]
pub struct FaultHarness {
    pub cluster: Cluster,
    configurations: BTreeMap<NodeId, Config>,
    stable: BTreeMap<NodeId, StableStore>,
    delayed: BTreeMap<NodeId, u32>,
    clock_offset_ns: i64,
    maximum_clock_offset_ns: u64,
    time_source_available: bool,
    telemetry_available: bool,
    alarms: BTreeSet<String>,
}

impl FaultHarness {
    #[must_use]
    pub fn new(nodes: u16, election_timeout_ns: u64) -> Self {
        let cluster = Cluster::new(nodes, election_timeout_ns);
        let configurations = cluster
            .nodes
            .iter()
            .map(|(id, node)| (*id, node.config.clone()))
            .collect();
        let stable = cluster
            .nodes
            .iter()
            .map(|(id, node)| (*id, StableStore::from_node(node)))
            .collect();
        Self {
            cluster,
            configurations,
            stable,
            delayed: BTreeMap::new(),
            clock_offset_ns: 0,
            maximum_clock_offset_ns: 5_000_000_000,
            time_source_available: true,
            telemetry_available: true,
            alarms: BTreeSet::new(),
        }
    }

    #[must_use]
    pub fn safe_state(&self) -> bool {
        self.time_source_available
            && self.telemetry_available
            && self.clock_offset_ns.unsigned_abs() <= self.maximum_clock_offset_ns
    }

    #[must_use]
    pub fn alarms(&self) -> &BTreeSet<String> {
        &self.alarms
    }

    pub fn run(&mut self, seed: u64, actions: &[FaultAction]) -> FaultReport {
        let mut failures = Vec::new();
        let mut trace = Vec::with_capacity(actions.len());
        for (step, action) in actions.iter().cloned().enumerate() {
            let outcome = self.apply(&action);
            if let Err(error) = invariants::check_all(&self.cluster) {
                failures.push(format!("step {step}: {error}"));
            }
            let maximum_commit_index = self
                .cluster
                .nodes
                .values()
                .map(|node| node.commit_index)
                .max()
                .unwrap_or_default();
            trace.push(TraceRow {
                step,
                action,
                leader: self.cluster.leader(),
                maximum_commit_index,
                safe_state: self.safe_state(),
                outcome,
            });
        }
        FaultReport {
            seed,
            passed: failures.is_empty(),
            invariant_failures: failures,
            alarms: self.alarms.clone(),
            trace,
        }
    }

    fn apply(&mut self, action: &FaultAction) -> String {
        match action {
            FaultAction::Tick { duration_ns } => {
                self.cluster.tick(*duration_ns);
                let delayed_ids: Vec<_> = self.delayed.keys().copied().collect();
                for id in delayed_ids {
                    let remaining = self.delayed.get_mut(&id).expect("known delayed node");
                    *remaining = remaining.saturating_sub(1);
                    if *remaining == 0 {
                        self.delayed.remove(&id);
                        self.cluster.policy.partitioned.remove(&id);
                    }
                }
                "ticked".into()
            }
            FaultAction::Propose { value, category } => {
                if *category == Category::Safety && !self.safe_state() {
                    self.alarms
                        .insert("safety-proposal-rejected-unhealthy-inputs".into());
                    return "rejected-fail-restrictive".into();
                }
                let Some(leader) = self.cluster.leader() else {
                    return "rejected-no-leader".into();
                };
                self.cluster.propose(leader, value.clone(), *category);
                "proposed".into()
            }
            FaultAction::Crash { node } => {
                if self.cluster.nodes.remove(node).is_some() {
                    self.cluster.inbox.entry(*node).or_default().clear();
                    self.alarms.insert(format!("node-{}-offline", node.0));
                    "crashed".into()
                } else {
                    "already-offline".into()
                }
            }
            FaultAction::Restart { node } => {
                let Some(config) = self.configurations.get(node).cloned() else {
                    return "rejected-unknown-node".into();
                };
                let result = self
                    .stable
                    .get(node)
                    .ok_or(RestoreError::Truncated)
                    .and_then(|store| store.restore(config, self.cluster.now_ns));
                match result {
                    Ok(restored) => {
                        self.cluster.nodes.insert(*node, restored);
                        self.cluster.inbox.entry(*node).or_default().clear();
                        self.alarms.remove(&format!("node-{}-offline", node.0));
                        "restarted".into()
                    }
                    Err(error) => {
                        self.alarms
                            .insert(format!("node-{}-restore-rejected-{error:?}", node.0));
                        "restore-rejected".into()
                    }
                }
            }
            FaultAction::Partition { node } => {
                self.cluster.policy.partitioned.insert(*node);
                "partitioned".into()
            }
            FaultAction::Heal { node } => {
                self.cluster.policy.partitioned.remove(node);
                self.cluster.policy.drop_from.remove(node);
                self.cluster.policy.drop_to.remove(node);
                self.delayed.remove(node);
                "healed".into()
            }
            FaultAction::DropFrom { node, enabled } => {
                set_membership(&mut self.cluster.policy.drop_from, *node, *enabled);
                "asymmetric-egress-updated".into()
            }
            FaultAction::DropTo { node, enabled } => {
                set_membership(&mut self.cluster.policy.drop_to, *node, *enabled);
                "asymmetric-ingress-updated".into()
            }
            FaultAction::Delay { node, ticks } => {
                self.cluster.policy.partitioned.insert(*node);
                self.delayed.insert(*node, (*ticks).max(1));
                "delay-scheduled".into()
            }
            FaultAction::ClockOffset { offset_ns } => {
                self.clock_offset_ns = *offset_ns;
                if !self.safe_state() {
                    self.alarms.insert("clock-unhealthy".into());
                } else {
                    self.alarms.remove("clock-unhealthy");
                }
                "clock-offset-updated".into()
            }
            FaultAction::TimeSource { available } => {
                self.time_source_available = *available;
                set_alarm(&mut self.alarms, "time-source-unavailable", !available);
                "time-source-updated".into()
            }
            FaultAction::Telemetry { available } => {
                self.telemetry_available = *available;
                set_alarm(&mut self.alarms, "telemetry-unavailable", !available);
                "telemetry-updated".into()
            }
            FaultAction::Checkpoint { node } => self.checkpoint(*node, WriteFault::None),
            FaultAction::DiskFull { node } => self.checkpoint(*node, WriteFault::DiskFull),
            FaultAction::PartialWrite { node, bytes } => {
                self.checkpoint(*node, WriteFault::PartialWrite(*bytes))
            }
            FaultAction::CorruptStableByte { node, offset } => {
                if self
                    .stable
                    .get_mut(node)
                    .is_some_and(|store| store.corrupt_byte(*offset))
                {
                    "stable-state-corrupted".into()
                } else {
                    "corruption-offset-rejected".into()
                }
            }
        }
    }

    fn checkpoint(&mut self, node: NodeId, fault: WriteFault) -> String {
        let Some(active) = self.cluster.nodes.get(&node) else {
            return "checkpoint-rejected-node-offline".into();
        };
        let store = self.stable.entry(node).or_default();
        match store.save(active, fault) {
            Ok(()) => "checkpoint-committed".into(),
            Err(StoreError::DiskFull) => {
                self.alarms.insert(format!("node-{}-disk-full", node.0));
                "checkpoint-rejected-disk-full".into()
            }
            Err(StoreError::PartialWrite) => {
                self.alarms.insert(format!("node-{}-partial-write", node.0));
                "checkpoint-rejected-partial-write".into()
            }
        }
    }
}

fn set_membership(values: &mut BTreeSet<NodeId>, value: NodeId, enabled: bool) {
    if enabled {
        values.insert(value);
    } else {
        values.remove(&value);
    }
}

fn set_alarm(alarms: &mut BTreeSet<String>, alarm: &str, enabled: bool) {
    if enabled {
        alarms.insert(alarm.into());
    } else {
        alarms.remove(alarm);
    }
}
