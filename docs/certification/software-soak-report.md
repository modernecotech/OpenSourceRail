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
| normal | `24301` | **PASS** | 0.200 | 36328.3 | 0 | 0 |
| peak | `24302` | **PASS** | 0.200 | 49460.4 | 0 | 0 |
| degraded | `24303` | **PASS** | 0.200 | 23443.8 | 2 | 0 |
| recovery | `24304` | **PASS** | 0.200 | 27206.6 | 3 | 0 |

## Retained-State Growth

Every final value is checked against the declared bound. A smaller checkpoint value may grow only until that cap is reached.

| Profile | Resource | Halfway | Final | Bound |
|---|---|---:|---:|---:|
| normal | detailed events | 0 | 0 | 0 |
| normal | event-count keys | 8 | 8 | 9 |
| normal | event records | 540672 | 540672 | 540672 |
| normal | T2G payloads | 0 | 0 | 540672 |
| normal | historian metrics | 660 | 660 | 660 |
| normal | historian samples | 2708640 | 3278880 | 8078400 |
| normal | CBM components | 4356 | 4356 | 4356 |
| normal | work orders | 0 | 0 | 4096 |
| normal | compact result bytes | 171643 | 171987 | 2000000 |
| peak | detailed events | 0 | 0 | 0 |
| peak | event-count keys | 6 | 6 | 9 |
| peak | event records | 540672 | 540672 | 540672 |
| peak | T2G payloads | 0 | 0 | 540672 |
| peak | historian metrics | 660 | 660 | 660 |
| peak | historian samples | 2708640 | 3278880 | 8078400 |
| peak | CBM components | 4356 | 4356 | 4356 |
| peak | work orders | 0 | 0 | 4096 |
| peak | compact result bytes | 173108 | 173601 | 2000000 |
| degraded | detailed events | 0 | 0 | 0 |
| degraded | event-count keys | 8 | 8 | 9 |
| degraded | event records | 540672 | 540672 | 540672 |
| degraded | T2G payloads | 540672 | 540672 | 540672 |
| degraded | historian metrics | 0 | 0 | 660 |
| degraded | historian samples | 0 | 0 | 8078400 |
| degraded | CBM components | 0 | 0 | 4356 |
| degraded | work orders | 0 | 0 | 4096 |
| degraded | compact result bytes | 173997 | 174744 | 2000000 |
| recovery | detailed events | 0 | 0 | 0 |
| recovery | event-count keys | 8 | 8 | 9 |
| recovery | event records | 540672 | 540672 | 540672 |
| recovery | T2G payloads | 540672 | 0 | 540672 |
| recovery | historian metrics | 660 | 660 | 660 |
| recovery | historian samples | 13860 | 2866380 | 8078400 |
| recovery | CBM components | 4356 | 4356 | 4356 |
| recovery | work orders | 0 | 4096 | 4096 |
| recovery | compact result bytes | 175369 | 610340 | 2000000 |

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
