# Deterministic Multi-Day Software Soak Report

> Software design evidence only. This accelerated simulation is not target-hardware endurance, WCET evidence, certification, or permission to operate.

- Result: **PASS**
- Duration: **2 simulated days per profile**
- Fixed simulation step: **5 seconds**
- Profiles: normal, peak, degraded and recovery
- Growth measure: retained logical state at the halfway and final checkpoints

## Profile Results

| Profile | Seed | Result | Min SoC | Train-km | Faults | Invariant failures |
|---|---:|---|---:|---:|---:|---:|
| normal | `24301` | **PASS** | 0.200 | 34871.0 | 0 | 0 |
| peak | `24302` | **PASS** | 0.200 | 44893.7 | 0 | 0 |
| degraded | `24303` | **PASS** | 0.200 | 22048.0 | 2 | 0 |
| recovery | `24304` | **PASS** | 0.200 | 25191.0 | 3 | 0 |

## Retained-State Growth

Every final value is checked against the declared bound. A smaller checkpoint value may grow only until that cap is reached.

| Profile | Resource | Halfway | Final | Bound |
|---|---|---:|---:|---:|
| normal | detailed events | 0 | 0 | 0 |
| normal | event-count keys | 8 | 8 | 9 |
| normal | event records | 544768 | 544768 | 544768 |
| normal | T2G payloads | 0 | 0 | 544768 |
| normal | historian metrics | 665 | 665 | 665 |
| normal | historian samples | 2729160 | 3303720 | 8139600 |
| normal | CBM components | 4389 | 4389 | 4389 |
| normal | work orders | 0 | 0 | 4096 |
| normal | compact result bytes | 153697 | 154123 | 2000000 |
| peak | detailed events | 0 | 0 | 0 |
| peak | event-count keys | 6 | 6 | 9 |
| peak | event records | 544768 | 544768 | 544768 |
| peak | T2G payloads | 0 | 0 | 544768 |
| peak | historian metrics | 665 | 665 | 665 |
| peak | historian samples | 2729160 | 3303720 | 8139600 |
| peak | CBM components | 4389 | 4389 | 4389 |
| peak | work orders | 0 | 0 | 4096 |
| peak | compact result bytes | 155050 | 155596 | 2000000 |
| degraded | detailed events | 0 | 0 | 0 |
| degraded | event-count keys | 8 | 8 | 9 |
| degraded | event records | 544768 | 544768 | 544768 |
| degraded | T2G payloads | 544768 | 544768 | 544768 |
| degraded | historian metrics | 0 | 0 | 665 |
| degraded | historian samples | 0 | 0 | 8139600 |
| degraded | CBM components | 0 | 0 | 4389 |
| degraded | work orders | 0 | 0 | 4096 |
| degraded | compact result bytes | 155937 | 156557 | 2000000 |
| recovery | detailed events | 0 | 0 | 0 |
| recovery | event-count keys | 8 | 8 | 9 |
| recovery | event records | 544768 | 544768 | 544768 |
| recovery | T2G payloads | 544768 | 0 | 544768 |
| recovery | historian metrics | 665 | 665 | 665 |
| recovery | historian samples | 13965 | 2888095 | 8139600 |
| recovery | CBM components | 4389 | 4389 | 4389 |
| recovery | work orders | 0 | 4096 | 4096 |
| recovery | compact result bytes | 157099 | 592168 | 2000000 |

## Assertions

### normal

- PASS — detailed event retention disabled while aggregate counts remain available
- PASS — event recorder and T2G queues stay within fixed per-train capacities
- PASS — historian raw and decimated tiers stay within fixed per-metric capacities
- PASS — CBM component state and detailed work-order evidence stay within explicit capacities
- PASS — every generated work order is represented by retained or dropped-record accounting
- PASS — compact result payload stays within the deterministic evidence envelope
- PASS — operating reserve and simulator invariants remain satisfied
- PASS — normal service completes repeated service/stabling cycles without injected faults
- PASS — checkpoint-to-final retained-state growth remains inside every declared cap

### peak

- PASS — detailed event retention disabled while aggregate counts remain available
- PASS — event recorder and T2G queues stay within fixed per-train capacities
- PASS — historian raw and decimated tiers stay within fixed per-metric capacities
- PASS — CBM component state and detailed work-order evidence stay within explicit capacities
- PASS — every generated work order is represented by retained or dropped-record accounting
- PASS — compact result payload stays within the deterministic evidence envelope
- PASS — operating reserve and simulator invariants remain satisfied
- PASS — peak profile uses three-minute-or-better published headways and continues accumulating fleet distance after the checkpoint
- PASS — checkpoint-to-final retained-state growth remains inside every declared cap

### degraded

- PASS — detailed event retention disabled while aggregate counts remain available
- PASS — event recorder and T2G queues stay within fixed per-train capacities
- PASS — historian raw and decimated tiers stay within fixed per-metric capacities
- PASS — CBM component state and detailed work-order evidence stay within explicit capacities
- PASS — every generated work order is represented by retained or dropped-record accounting
- PASS — compact result payload stays within the deterministic evidence envelope
- PASS — operating reserve and simulator invariants remain satisfied
- PASS — continuous radio loss saturates, but never exceeds, the bounded store-and-forward queue
- PASS — checkpoint-to-final retained-state growth remains inside every declared cap

### recovery

- PASS — detailed event retention disabled while aggregate counts remain available
- PASS — event recorder and T2G queues stay within fixed per-train capacities
- PASS — historian raw and decimated tiers stay within fixed per-metric capacities
- PASS — CBM component state and detailed work-order evidence stay within explicit capacities
- PASS — every generated work order is represented by retained or dropped-record accounting
- PASS — compact result payload stays within the deterministic evidence envelope
- PASS — operating reserve and simulator invariants remain satisfied
- PASS — radio/grid/CBM degradation clears and queued telemetry drains before the final checkpoint
- PASS — checkpoint-to-final retained-state growth remains inside every declared cap

## Remaining Release Evidence

- selected-target WCET, stack and heap measurement
- wall-clock endurance and storage wear on production hardware
- power-cut, network and clock HIL with production transports
- independent safety assessment and authority acceptance
