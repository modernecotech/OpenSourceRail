# Deterministic Software Resilience Report

> In-process design evidence only. Hardware, filesystem, network, clock, HIL and independent-assessment evidence remain required.

- Result: **PASS**
- Deterministic seed: `24301`
- Fault/recovery actions: **34**
- Fail-restrictive safety proposal rejections: **3**
- Runtime invariant failures: **0**

## Checked Boundaries

- node crash, stable-state restart and post-heal convergence;
- asymmetric message loss, bounded delay, partition and healing;
- atomic checkpoint behavior under disk-full and partial writes;
- fail-closed rejection of corrupted, truncated, wrong-node and inconsistent stable state;
- clock-offset, time-source and telemetry health gating for safety proposals; and
- election, log-matching, leader-completeness, state-machine and fail-restrictive consensus invariants after every action.

## Trace

| Step | Action | Outcome | Leader | Commit | Safe inputs |
|---:|---|---|---|---:|---|
| 0 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 0 | yes |
| 1 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 0 | yes |
| 2 | `Propose { value: [98, 97, 115, 101, 108, 105, 110, 101], category: Advisory }` | `proposed` | N0 | 0 | yes |
| 3 | `Checkpoint { node: NodeId(2) }` | `checkpoint-committed` | N0 | 0 | yes |
| 4 | `Delay { node: NodeId(2), ticks: 3 }` | `delay-scheduled` | N0 | 0 | yes |
| 5 | `DropFrom { node: NodeId(1), enabled: true }` | `asymmetric-egress-updated` | N0 | 0 | yes |
| 6 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 0 | yes |
| 7 | `Heal { node: NodeId(1) }` | `healed` | N0 | 0 | yes |
| 8 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 1 | yes |
| 9 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 1 | yes |
| 10 | `DiskFull { node: NodeId(0) }` | `checkpoint-rejected-disk-full` | N0 | 1 | yes |
| 11 | `PartialWrite { node: NodeId(1), bytes: 7 }` | `checkpoint-rejected-partial-write` | N0 | 1 | yes |
| 12 | `Checkpoint { node: NodeId(2) }` | `checkpoint-committed` | N0 | 1 | yes |
| 13 | `Crash { node: NodeId(2) }` | `crashed` | N0 | 1 | yes |
| 14 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 1 | yes |
| 15 | `Restart { node: NodeId(2) }` | `restarted` | N0 | 1 | yes |
| 16 | `Telemetry { available: false }` | `telemetry-updated` | N0 | 1 | no |
| 17 | `Propose { value: [116, 101, 108, 101, 109, 101, 116, 114, 121, 45, 114, 101, 106, 101, 99, 116, 101, 100], category: Safety }` | `rejected-fail-restrictive` | N0 | 1 | no |
| 18 | `Telemetry { available: true }` | `telemetry-updated` | N0 | 1 | yes |
| 19 | `ClockOffset { offset_ns: 8000000000 }` | `clock-offset-updated` | N0 | 1 | no |
| 20 | `Propose { value: [99, 108, 111, 99, 107, 45, 114, 101, 106, 101, 99, 116, 101, 100], category: Safety }` | `rejected-fail-restrictive` | N0 | 1 | no |
| 21 | `ClockOffset { offset_ns: 0 }` | `clock-offset-updated` | N0 | 1 | yes |
| 22 | `TimeSource { available: false }` | `time-source-updated` | N0 | 1 | no |
| 23 | `Propose { value: [116, 105, 109, 101, 45, 115, 111, 117, 114, 99, 101, 45, 114, 101, 106, 101, 99, 116, 101, 100], category: Safety }` | `rejected-fail-restrictive` | N0 | 1 | no |
| 24 | `TimeSource { available: true }` | `time-source-updated` | N0 | 1 | yes |
| 25 | `Partition { node: NodeId(0) }` | `partitioned` | N0 | 1 | yes |
| 26 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 1 | yes |
| 27 | `Tick { duration_ns: 100000000 }` | `ticked` | N0 | 1 | yes |
| 28 | `Heal { node: NodeId(0) }` | `healed` | N0 | 1 | yes |
| 29 | `Tick { duration_ns: 100000000 }` | `ticked` | none | 1 | yes |
| 30 | `Tick { duration_ns: 100000000 }` | `ticked` | none | 1 | yes |
| 31 | `Checkpoint { node: NodeId(0) }` | `checkpoint-committed` | none | 1 | yes |
| 32 | `Checkpoint { node: NodeId(1) }` | `checkpoint-committed` | none | 1 | yes |
| 33 | `Checkpoint { node: NodeId(2) }` | `checkpoint-committed` | none | 1 | yes |

## Remaining Release Evidence

Repeat these cases on the selected storage, processor, RTOS/OS, production transport and clock sources. Add power-cut injection, storage endurance, WCET/resource measurements, long-duration soak, signed binary/update evidence and independent review before release.
