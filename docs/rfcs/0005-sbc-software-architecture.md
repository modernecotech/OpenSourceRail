# RFC 0005 — SBC Software Architecture

**Status:** Implemented software baseline; production transport/hardware evidence remains
**Date:** 2026-04-21
**Depends on:** [RFC 0001 Track State Consensus](0001-track-state-consensus.md), [RFC 0004 `osr-interlocking` Plan](0004-osr-interlocking-plan.md)
**Supersedes for repo layout:** [ARCHITECTURE.md §6.3](../ARCHITECTURE.md#63-repository-layout-proposed)

## 1. Summary

This RFC enumerates the Rust crates that run on OpenSourceRail hardware —
onboard train ECUs, wayside SBCs, station and depot controllers, and the
OCC back-office — and fixes their boundaries, buses, SIL tiers, and
rollout order *before* the first of them is written.

The workspace now implements the crate map below. `osr-sim` connects the
onboard safety, vehicle, TCMS, recorder, CBM, hot-axle, and T2G evaluators, plus
station PSD/PIS/SCADA and wayside intrusion detection, then carries CBM through
T2G into the depot backend, historian, and analytics. A TCMS trip inhibits
dispatch or section progress on the following one-second control cycle.
Explicit physical HABDs run the trackside evaluator, cap warning-band trains
until the next station, and latch stop orders until a named post-inspection
reset is accepted. This is all timestamped by a real
`osr-ptp` state machine that acquires the simulator's deterministic shared
clock. This is integration evidence, not certification or production
hardware-I/O evidence.

Without a map, those crates would grow ad hoc, buses would be redesigned
repeatedly, SIL boundaries would be fuzzy, and the safety case would be
rebuilt from scratch several times. This document is the map.

The crate map remains the architectural contract. Implemented links are
tracked by `lib/simulation-component-coverage.toml`; hardware and production
transport evidence remains governed by the later RFCs and release checklists.

## 2. Non-goals

- Not a hardware reference design. Schematics, BOMs, and ratings are the
  domain of [RFC 0007](0007-control-electronics-reference-designs.md) and the
  [`control-electronics/`](../../control-electronics/) directory. This RFC specifies *which
  software targets which hardware class*, not what that hardware looks
  like.
- Not a formal safety case. SIL targets here are *allocations*, not
  claims. The evidence that a crate meets its allocation is produced per
  crate (cf. [RFC 0004 §7](0004-osr-interlocking-plan.md#7-safety-case-anchors)
  for the interlocking pattern).
- Not a commitment to build every crate listed. Items beyond Phase 2 of
  §11 are placeholders; inclusion here is architectural scoping, not a
  roadmap promise.
- Not a redefinition of domains D1–D8 in
  [ARCHITECTURE.md §3](../ARCHITECTURE.md#3-system-of-systems-map).
  Domains are kept; this RFC decomposes each domain into crates.

## 3. Design context

### 3.1 Hardware classes

Five hardware classes host OpenSourceRail software. Every crate is
tagged with the class(es) it targets. The reference designs for
each class — SoC, peripherals, baseboard, manufacturability — are
in [RFC 0007](0007-control-electronics-reference-designs.md).

| Class | Acronym | Environment | Typical SoC | Reference OS |
|---|---|---|---|---|
| Train ECU — safety kernel | **T-ECU/S** | EN 50155, −25…+70 °C, vibration, dual-redundant | RISC-V (MilkV Jupiter-class) or ARM Cortex-R52 | Hubris or seL4, `no_std` |
| Train ECU — app | **T-ECU/A** | EN 50155, single-redundant | ARM64 (CM5-class) | PREEMPT_RT Linux |
| Wayside SBC | **W-SBC** | IP67 cabinet, −40…+70 °C, dual-PSU | RISC-V or ARM64 | Hubris (safety) / Debian (non-safety) |
| Station / depot SBC | **S-SBC** | indoor/sheltered, commodity | ARM64 | Debian or Yocto |
| Ops server | **O-SRV** | datacenter / colo | x86-64 or ARM64 | Debian |

T-ECU/S and W-SBC (safety role) are the hosts for the SIL-4 tier;
everything else is SIL-2 or lower. The safety kernel binaries stay small
(cf. [ARCHITECTURE.md §6.1](../ARCHITECTURE.md#61-software-tiers),
"< 50k LoC per binary") by design.

### 3.2 Buses

| Bus | Standard | Role | Determinism |
|---|---|---|---|
| **TCN-E** | IEC 61375-2-3 (Ethernet TRDP) on IEEE 802.1 Qbv TSN | On-train backbone | Hard real-time |
| **CAN-FD** | ISO 11898-1 | Short-haul ECU sub-segments (door, brake panel, lighting) | Soft real-time |
| **LIN** | ISO 17987 | Low-cost switch/sensor strings (cab panels, exterior lighting) | Best effort |
| **TRG-1** | Public 5G SA with slicing, or private 5G on n77/n78/CBRS | Train-to-ground primary | Statistical |
| **TRG-2** | LoRa mesh per [ARCHITECTURE.md §D3](../ARCHITECTURE.md#d3-communications) | Train-to-ground backup for safety telemetry | Statistical, short messages |
| **WAY-E** | Ethernet + TSN + PTP (IEEE 1588) | Wayside backbone | Hard real-time |
| **NATS-JS** | NATS JetStream over TLS | Ops event stream, non-safety | Best effort |
| **gRPC/mTLS** | HTTP/2 + TLS 1.3 | Control-plane RPC between wayside nodes and the OCC | Best effort |

All onboard publishers and subscribers use TCN-E topics.

### 3.3 SIL allocation rules

Three rules govern where each crate falls:

1. **Anything that can command or suppress a brake application is SIL-4.**
   This is the traditional rail safety partition and we adopt it.
2. **Anything whose failure can cause a train to exceed its Movement
   Authority is SIL-4.** (Consequence of rule 1 via ATP.)
3. **Anything else is SIL-2 or SIL-0.** SIL-2 for systems that can cause
   operational disruption but not injury (e.g. door control *opening*,
   traction control *limiting*); SIL-0 for passenger-experience systems
   (PIS, lighting, HVAC comfort) where failure degrades comfort only.

Door *closing* interlock and wheel-slide protection sit in SIL-4 under
rule 1. Door *opening* sits in SIL-2 because failing to open is not a
safety hazard — it is a service disruption.

## 4. Crate inventory

Thirty-five crates across the eight domains. Each row shows the owning
domain, the crate name, the hardware class it targets, the SIL
allocation, and a one-line scope. Within each domain crates are ordered
roughly by build dependency.

### 4.1 D2 — Train control (onboard)

These crates live on the train and are the direct consumers of the
`osr-interlocking` MA output. All four SIL-4 crates here must share the
same toolchain pin and formal-methods harness discipline as the
interlocking crate.

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-atp** | T-ECU/S | 4 | Onboard ATP. Receives MA from `osr-interlocking`, computes a time-based speed envelope from the braking curve, commands emergency brake on violation. Pure function of `(MA, consist, position, speed, now)`; no I/O in the core. |
| **osr-ato** | T-ECU/A | 2 | Automatic Train Operation. Generates traction and service-brake setpoints inside the envelope `osr-atp` permits. Station-stopping, energy-optimal driving, dwell management. GoA 4 unattended operation is the only supported profile per [RFC 0015](0015-driverless-operation.md). |
| **osr-odometry** | T-ECU/S | 4 | Sensor fusion: wheel tachometers + IMU + GNSS + balise fixes → train head/tail position and confidence. Feeds `osr-atp` and emits `TrainPositionReport` entries. |
| **osr-obstacle-detect** | **T-OBS** | **4** | **NEW (RFC 0015 v1, 2026-04-22):** onboard obstacle detection for GoA 4. Fuses ultrasonic + LIDAR + mmWave radar + stereo camera into an `ObstacleVerdict` per tick (Clear / CrawlOnly / EmergencyBrake). Five SIL-4 properties O1–O5 with Kani harnesses + proptest coverage. Substitutes for the driver's eyes in the unattended-operation safety case. |
| **osr-tcms** | T-ECU/A | 2 | Train Management System. Aggregates ECU state onto TCN-E; records the event recorder stream; publishes passenger PIS status. Non-safety *subscribers*; does **not** mediate between `osr-atp` and the brake. |
| **osr-event-recorder** | T-ECU/A | 2 | Onboard "black box". Crash-survivable circular storage of TCN-E traffic at a deterministic sample rate. Feeds incident investigation. |

### 4.2 D5 — Rolling stock ECUs

Actuators and comfort systems. Traction, brake, BMS, and door-closing
interlock are SIL-4; everything else is SIL-2 or SIL-0.

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-traction** | T-ECU/S | 4 | Field-oriented control for the RFC 0021 commercial-vehicle PMSM/controller channel; torque command from `osr-ato`; anti-slip; anti-slide. |
| **osr-bms** | T-ECU/S | 4 | LFP battery management. Cell balancing, SoC/SoH estimation, thermal limits, contactor control, off-gas/fire isolation, and cell-out derating. Exposes pack state to `osr-ato` for energy-optimal driving. |
| **osr-brake** | T-ECU/S | 4 | EP brake controller. Blends regen (commanded via `osr-traction`) with friction brake; integrates WSP (wheel-slide protection); parking brake; emergency brake. Primary consumer of `osr-atp`'s brake-apply command. |
| **osr-regen** | T-ECU/A | 2 | Regen arbitration. Decides whether excess regen current goes to the pack (via BMS), to trackside storage (via pantograph at charging pads, when contacted), or to a dump resistor. Not SIL-4 because `osr-brake` can always apply friction brake if regen is refused. |
| **osr-aux-power** | T-ECU/A | 2 | Isolated 24 V and 110 V DC conversion plus direct-HV comfort-branch control. Load-shed logic under low SoC. |
| **osr-door-control** | T-ECU/S | 4 | Door controller. Closing-interlock above 5 km/h is SIL-4 (rule 1 in §3.3); opening is SIL-2 but lives in the same crate to keep the interlock logic colocated. Obstacle detection via motor current + dedicated sensor. |
| **osr-hvac** | T-ECU/A | 0 | HVAC control loops. Climate setpoint (20–24 °C) per [RFC 0003](0003-samawah-reference-deployment.md) hot-climate uplift. Publishes thermal state to `osr-tcms`. Failure degrades comfort. |
| **osr-lighting** | T-ECU/A | 0 | Interior and exterior lighting, emergency egress lighting, headlight/taillight PWM. Emergency-lighting battery backup is handled at hardware level; this crate only drives the normal-mode controller. |
| **osr-pis-onboard** | T-ECU/A | 0 | Passenger Information System — onboard displays, audio announcements, next-station logic. Consumes the ops event stream through `osr-t2g`. |

### 4.3 D5 — Onboard safety monitors

Detect conditions that require an emergency brake application
independently of ATP. All SIL-4.

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-fire-safety** | T-ECU/S | 4 | Aspirating smoke detection + suppression activation in battery bay, traction bay, HVAC plenum. Emergency brake + passenger alert on detection. |
| **osr-derailment** | T-ECU/S | 4 | Lateral accelerometer + tilt sensor. Threshold-based trigger for emergency brake per EN 50159 envelopes. |
| **osr-hot-axle** | T-ECU/A | 2 | Onboard axle-bearing temperature monitoring. Not SIL-4 because wayside HABD provides the primary trip; onboard detection is backup and maintenance-signalling. |

### 4.4 D5 — Condition-based maintenance (onboard)

Not safety-critical; streams telemetry to the depot for offline analysis.

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-cbm-onboard** | T-ECU/A | 0 | Continuous monitoring of bearing vibration, brake pad wear, motor temperature, wheel profile (accelerometer-based), pantograph state if present. Streams to `osr-cbm-backend` over TRG. |

### 4.5 D3 — Communications

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-tcn** | T-ECU/* | 2 | TCN-E (IEC 61375-2-3) stack. Topic-addressed pub/sub over TSN Ethernet. Shared by every onboard crate that speaks on the bus. |
| **osr-t2g** | T-ECU/A | 2 | Train-to-ground link abstraction. Multipath over 5G (TRG-1) and LoRa (TRG-2); mTLS on both; Noise Protocol for LoRa. Exposes a simple `send(topic, bytes)` / subscribe interface to the rest of the train. |
| **osr-ptp** | T-ECU/* & W-SBC | 2 | PTP (IEEE 1588) time sync for TSN determinism. Wrapped into the TCN stack but broken out as a separate crate because the wayside uses the same code. |

### 4.6 D6 — Wayside infrastructure

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-wayside-points** | W-SBC | 4 | Power switch (point) machine controller. Commodity BLDC motor driver + dual redundant position sensors. Publishes `SwitchObservation` entries to the consensus log; accepts `SwitchCommand` entries. |
| **osr-balise** | W-SBC | 2 | Balise/transponder reader. Provides position fixes at fixed points (platform edges, switches) for `osr-odometry` to consume. Passive balises preferred; active balises used only where a data payload is needed. |
| **osr-level-crossing** | W-SBC | 4 | Level-crossing controller. Same SBC family as the interlocking; crossings are consensus-log participants. |
| **osr-hot-axle-wayside** | W-SBC | 4 | Wayside Hot Axle Box Detector (HABD). IR sensor array reads bearing temperatures on passing trains; publishes a speed-restriction entry or a stop-order if thresholds exceeded. |
| **osr-consensus** | W-SBC & O-SRV | 4 | Raft implementation of the SMRaft spec (see [`engineering/assurance/formal/tla/SMRaft.tla`](../../engineering/assurance/formal/tla/SMRaft.tla)). Maintains the track-state log consumed by `osr-interlocking`. Separate crate because every safety-critical wayside node hosts a replica. |

### 4.7 D4 — Passenger services

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-psd** | S-SBC | 2 | Platform Screen Door controller. Synchronises with train-side `osr-door-control`; reports state to the OCC. Failure-to-open is a service failure; failure-to-close in presence of a passenger is a safety issue and that interlock lives in hardware. |
| **osr-afc** | S-SBC | 0 | Automatic Fare Collection gate firmware. QR + NFC + account-based tokens per [I7 in ARCHITECTURE.md §5](../ARCHITECTURE.md#5-cross-domain-interfaces). |
| **osr-tvm** | S-SBC | 0 | Ticket Vending Machine firmware. Commodity barcode scanner + contactless reader; accepts mobile-money QR and cash where applicable. |
| **osr-pis-station** | S-SBC | 0 | Station PIS — next-arrival displays, PA, emergency announcements. Consumes the ops event stream directly. |
| **osr-station-scada** | S-SBC | 2 | Station SCADA — escalators, lifts, HVAC, lighting, CCTV NVR integration. Monitoring-only for SIL-rated station subsystems; vendor safety systems remain self-contained, this crate only observes them. |

### 4.8 D1 & D8 — Ops, depot, backend

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-occ** | O-SRV | 2 | Operations Control Centre. Fleet roster, incident management, dispatch holds, timetable editor and ATS (Automatic Train Supervision). Its deterministic core runs in `osr-sim`; the production event stream remains the deployment boundary. |
| **osr-historian** | O-SRV | 0 | Time-series ingest + retention. Prometheus remote-write + a typed Parquet archive for audit. |
| **osr-analytics** | O-SRV | 0 | KPIs (MDBF, availability, kWh/km, regen %, occupancy heatmaps). Consumes the historian; produces Grafana-compatible datasets and monthly PDF reports. |
| **osr-cbm-backend** | O-SRV | 0 | Depot-side analysis of `osr-cbm-onboard` telemetry. Predictive-maintenance triggers, work-order generation. |
| **osr-afc-backoffice** | O-SRV | 0 | Fare settlement, revenue reconciliation, MaaS API, fraud detection. |
| **osr-energy-site** | W-SBC | 2 | Per-site PV, stationary LFP, 500 kW DC/DC and grid-tie controller per [RFC 0002](0002-energy-sizing.md). |

### 4.9 Cross-cutting support crates

| Crate | Class | SIL | Scope |
|---|---|---|---|
| **osr-proto** | all | n/a | Generated types for the protobuf schemas in [`crates/osr-core/proto/`](../../crates/osr-core/proto/). Pulled out of `osr-core` once `osr-consensus` demands the wire format. |
| **osr-crypto** | all | 2 | Thin wrapper around RustCrypto primitives and `rustls` configured for IEC 62443-4-2 conformance. Every safety-relevant network node links this crate rather than rolling its own TLS/KEM usage. |
| **osr-safety-case** ✅ | tooling | n/a | GSN (Goal Structuring Notation) compiler. TOML claim files in, rendered safety case out. CI fails if the case no longer closes. Starter case under [`docs/safety-case/gsn/`](../safety-case/gsn/) — 11 goals / 3 strategies / 14 solutions, all linked to real evidence in-tree. |

## 5. Dependency graph

Build dependencies flow bottom-up; SIL-4 crates sit at the bottom so
they have no dependencies on higher-SIL crates (a SIL-4 crate must not
link SIL-0 code).

```
SIL-4   osr-core ─── osr-interlocking ─── osr-consensus
          │             │   │
          ▼             │   ▼
         osr-odometry   │   osr-wayside-points
          │             │   osr-level-crossing
          ▼             │   osr-hot-axle-wayside
         osr-atp ───────┤
          │             │
          ▼             ▼
         osr-brake    osr-traction    osr-bms
         osr-door-control
         osr-fire-safety osr-derailment

SIL-2   osr-tcn   osr-t2g   osr-ptp   osr-crypto
         │         │
         ▼         ▼
        osr-tcms  osr-ato  osr-regen
        osr-aux-power  osr-hot-axle  osr-event-recorder
        osr-psd  osr-station-scada  osr-energy-site
        osr-occ

SIL-0   osr-hvac  osr-lighting  osr-pis-onboard  osr-pis-station
        osr-afc  osr-tvm  osr-historian  osr-analytics
        osr-cbm-onboard  osr-cbm-backend  osr-afc-backoffice
```

The binding rule: a crate at tier N must not `[dependencies]` any crate
at tier >N. This is enforced by a `cargo-deny` policy added in the
first implementation PR (RFC 0006).

## 6. Interface contracts

Five on-train interfaces and four train-to-ground interfaces. Each is
defined by a message schema in `crates/osr-proto/` (new location —
moved out of `osr-core` in Phase 2a, see §11).

### 6.1 On-train

| # | Topic | Producer | Consumers | Rate | Size |
|---|---|---|---|---|---|
| O1 | `osr.train.ma` | `osr-atp` (mirror of `osr-interlocking` output) | `osr-ato`, `osr-event-recorder` | On change, ≤ 1 Hz | ~200 B |
| O2 | `osr.train.position` | `osr-odometry` | `osr-tcms` → TRG; `osr-atp` (internal) | 10 Hz | ~80 B |
| O3 | `osr.train.setpoint` | `osr-ato` | `osr-traction`, `osr-brake` | 50 Hz | ~30 B |
| O4 | `osr.train.brake_apply` | `osr-atp`, `osr-fire-safety`, `osr-derailment`, `osr-passenger-assist`, `osr-obstacle-detect` | `osr-brake` | On event | ~20 B |
| O5 | `osr.train.telemetry.*` | every crate | `osr-tcms` → TRG | 1–10 Hz | variable |

O4 is safety-critical. It is a *union* of commands from every SIL-4
monitor; the brake crate applies the emergency brake if *any*
subscriber asserts it. This is the single point where safety
partitioning is enforced on the train; all other interfaces are for
coordination, not safety.

### 6.2 Train-to-ground

| # | Topic | Producer | Consumers | Transport | Cadence |
|---|---|---|---|---|---|
| G1 | `TrainPositionReport` (log entry) | `osr-odometry` via `osr-t2g` | `osr-consensus` | TRG-1 primary, TRG-2 fallback | 1 Hz |
| G2 | Movement Authority subscription | `osr-interlocking` at wayside | `osr-atp` onboard | TRG-1 + TRG-2 replicated | On change |
| G3 | Ops event stream | `osr-occ` | `osr-pis-onboard`, `osr-tcms` | TRG-1 | As produced |
| G4 | Telemetry + CBM stream | `osr-tcms`, `osr-cbm-onboard` | `osr-historian`, `osr-cbm-backend` | TRG-1 | 1–10 Hz |

G1 and G2 are safety-critical. G2 is replicated on both radios; onboard
`osr-atp` uses the most recent valid MA from either path. Loss of both
paths for more than `MA_VALIDITY_WINDOW_NS` (3 s) forces fail-restrictive
behaviour per [RFC 0001](0001-track-state-consensus.md).

## 7. SIL-4 coding standard

Every SIL-4 crate in §4 follows the conventions established for
`osr-interlocking` (RFC 0004 §3):

- `#![forbid(unsafe_code)]` at crate root.
- Integer-only units in the hot path: millimetres, millimetres-per-second,
  nanoseconds, parts-per-thousand for SoC. No floats on the safety path.
- No allocator calls in the control loop. Pre-allocated buffers, bounded
  collections, `heapless`/`SmallVec` where dynamic sizing is genuinely
  needed.
- All public API types `Debug + Clone + PartialEq` for test ergonomics.
- `no_std` compatible by default. Tests that need `std` are gated
  behind a `std` feature.
- Kani harnesses live under `crates/<name>/harnesses/`, one file per
  named property, bounded by the same small-model sizes used in
  `osr-interlocking`.
- Proptests live under `crates/<name>/tests/` and run in CI unbounded.
- Every SIL-4 crate pins the same Rust toolchain version
  (`rust-toolchain.toml` at workspace root).

SIL-2 crates follow the same standard *except* for Kani (encouraged but
not mandatory) and `no_std` (optional).

SIL-0 crates follow ordinary Rust idiomatic style; the goal there is
velocity.

## 8. Deployment topology

This is the target electronics/software partition, not an approved hardware
installation. SBC names in this RFC are development candidates. The
[pilot signalling profile](../certification/pilot-signalling-profile.md) keeps
OSR wayside control in shadow/supervised operation behind independent
occupancy detection and a separately qualified safety channel until its staged
assessment gates close.

One trainset hosts: two redundant T-ECU/S units (primary + hot spare,
running `osr-atp`, `osr-odometry`, `osr-traction`, `osr-brake`,
`osr-bms`, `osr-door-control`, `osr-fire-safety`,
`osr-derailment`), and one or more T-ECU/A units (running `osr-ato`,
`osr-tcms`, `osr-pis-onboard`, `osr-hvac`, `osr-lighting`,
`osr-event-recorder`, `osr-aux-power`, `osr-regen`, `osr-cbm-onboard`,
`osr-hot-axle`, `osr-t2g`).

One wayside site (a station, a switch, or a level crossing) hosts: one
to three W-SBCs running the relevant subset of `osr-wayside-points`,
`osr-level-crossing`, `osr-balise`, `osr-hot-axle-wayside`, plus
`osr-consensus` and `osr-interlocking` on sites that are safety
participants. Non-safety stations also host `osr-energy-site` if the
station has PV and storage.

One station hosts: one S-SBC for `osr-psd`, one to four for `osr-pis-station`,
`osr-station-scada`, and as many as needed for `osr-afc` and `osr-tvm`.

The OCC hosts: `osr-occ`, `osr-historian`, `osr-analytics`,
`osr-cbm-backend`, `osr-afc-backoffice`, and a replica of
`osr-consensus`.

## 9. Cybersecurity posture

Per [ARCHITECTURE.md §8](../ARCHITECTURE.md#8-security-posture) and
IEC 62443-4-2 / TS 50701:

- Every TCN-E and WAY-E node holds a unique key pair provisioned at
  commissioning; no shared credentials.
- All inter-node traffic is mTLS (gRPC) or Noise-protected (LoRa).
  `osr-crypto` is the only TLS-configuring crate.
- Network segmentation on the wayside: safety plane (consensus,
  interlocking, points) is physically separated from operational plane
  (SCADA, telemetry) and the passenger plane (Wi-Fi, PIS). The three
  planes meet only at `osr-occ`, across audited gateways.
- Signed firmware everywhere; measured boot on T-ECU/S and W-SBC.
- The safety plane is considered air-gapped from the public internet in
  normal operation; updates are staged and pushed manually via a
  cleanroom.

## 10. Reference boundary

The reference stack uses TCN-E over TSN, the two ECU hardware classes in
§4, onboard odometry plus the shared track-state log, OTLP condition
monitoring, and account-based fare collection. Deployment-specific adapters
are outside this crate map.

## 11. Rollout order

Five phases, chosen to front-load the safety-critical onboard stack
while allowing non-safety passenger-facing work to proceed in parallel
once the safety partition is firm.

### Phase 2a — Onboard safety partition (starts immediately)

Prerequisite: RFC 0004 M1+M2 are done; M3 (Kani) can run in parallel.

1. **`osr-atp`** — RFC 0006, this week. First SBC crate. Consumes
   `MovementAuthority` from `osr-interlocking`, produces brake-apply
   commands. Pure function + integration stub for simulator-in-the-loop.
2. **`osr-odometry`** — RFC 0007. Sensor-fusion kernel; emits
   `TrainPositionReport` entries.
3. **`osr-brake`** — RFC 0008. EP brake blending + WSP.

### Phase 2b — Onboard traction partition

5. **`osr-bms`** — LFP pack management and fire-isolation interface.
6. **`osr-traction`** — VVVF firmware against a SPICE-simulated
   inverter first, hardware second.
7. **`osr-ato`** — consumes ATP envelope, drives traction + service
   brake within it.

### Phase 2c — On-train bus and non-safety app layer

8. **`osr-tcn`**, **`osr-ptp`** — bus stack.
9. **`osr-tcms`**, **`osr-event-recorder`**.
10. **`osr-door-control`**, **`osr-hvac`**, **`osr-lighting`**,
    **`osr-aux-power`**, **`osr-pis-onboard`**.
11. **`osr-t2g`** — radio abstraction (5G SA SIM emulated first).
12. **`osr-fire-safety`**, **`osr-derailment`**, **`osr-hot-axle`**,
    **`osr-regen`**, **`osr-cbm-onboard`**.

### Phase 2d — Wayside and consensus

13. **`osr-consensus`** — Raft against the TLA+ spec.
14. **`osr-wayside-points`**, **`osr-level-crossing`**,
    **`osr-balise`**, **`osr-hot-axle-wayside`**.
    The simulator derives one stable passive-balise record per directed
    section, audits each crossing through `osr-balise`, and passes only valid
    fixes into the real `osr-odometry` evaluator.
15. **`osr-energy-site`** (already scoped in RFC 0002; crate created here).

### Phase 2e — Stations and back-office

16. **`osr-psd`**, **`osr-pis-station`**, **`osr-station-scada`**.
17. **`osr-afc`**, **`osr-tvm`**, **`osr-afc-backoffice`**.
    The simulator executes the complete signed-token and settlement path as a
    representative station workload, including signature-tamper denial and
    fraud-rate evidence; it does not treat that workload as demand forecast.
18. **`osr-occ`**, **`osr-historian`**, **`osr-analytics`**,
    **`osr-cbm-backend`**.

### Phase 3 — Hardware integration (overlapping)

Hardware-in-the-loop bench for each SIL-4 crate as it lands.
Full-system HIL with simulator-driven wayside + real T-ECU by end of
Phase 2c.

## 12. Relationship to existing work

- [`osr-interlocking`](../../crates/osr-interlocking/) is the *producer*
  of MAs; `osr-atp` (Phase 2a, crate 1) is the *first real consumer*.
  The two crates share no mutable state; `osr-atp` treats MAs as
  immutable inputs.
- [`osr-sim`](../../crates/osr-sim/) remains the digital twin. In
  Phase 2a, `osr-atp` runs inside the simulator against `osr-sim`'s
  kinematics, consuming MAs derived from consensus log entries via
  `osr-interlocking`. Station and intrusion controllers also run against
  deterministic physical/sensor shadows; hardware remains a separate gate.
- [`osr-core`](../../crates/osr-core/) stays as it is; the protobuf
  types migrate into a new `osr-proto` crate when `osr-consensus`
  lands (Phase 2d) so that cross-language consumers (the Python
  reference interpreter, future tooling) can link the schema without
  linking domain logic.
- [`engineering/assurance/formal/tla/SMRaft.tla`](../../engineering/assurance/formal/tla/SMRaft.tla) is the spec
  that `osr-consensus` implements. The TLA+ work is already done; only
  the Rust refinement is pending.

## 13. Pitfalls and decisions

- **Two T-ECU/S units, not three.** Standard SIL-4 practice is
  triple-modular redundancy. We adopt dual-redundant ("composite
  fail-safe") because the consensus layer provides a third opinion at
  the system level — any disagreement between the two onboard ECUs
  falls back to the wayside-authoritative MA. This is a design bet;
  validated in the safety case per deployment.
- **Regen is not SIL-4.** Rule 1 in §3.3 might be read as forcing it,
  but the brake crate can always substitute friction brake; regen
  refusing to accept current is an energy-efficiency issue, not a
  safety one. Listed here so the allocation is auditable.
- **Door opening is SIL-2, closing is SIL-4.** Same crate. This bifurcation
  is the one place where a single crate spans two SIL tiers. The
  alternative — splitting the crate — leaves the interlock logic
  divided between two binaries, which is worse. The crate's internal
  partitioning (separate tasks under Hubris) is the mitigation.
- **`osr-tcn` is SIL-2, not SIL-4.** Justification: the bus is a
  shared mechanism; the safety argument lives in the *payload* crates
  (atp, brake, bms, etc.) which validate every message. A corrupted
  frame fails validation and is discarded; a missing frame triggers
  fail-restrictive timeouts in the consumer. TCN-E itself does not
  need SIL-4 treatment.
- **SIL-4 crates must not depend on SIL-2 code at runtime.** `osr-atp`
  cannot `use osr_tcn`. Instead, the TCN plumbing delivers MA bytes
  to a memory-mapped region that `osr-atp` reads; any error in that
  delivery manifests as MA expiry, which `osr-atp` handles safely.
  This pattern is consistent across every SIL-4 crate.
- **OS choice per tier is deferred.** Hubris vs. seL4 for T1 remains
  open ([ARCHITECTURE.md §10 open question 3](../ARCHITECTURE.md#10-open-questions)).
  SIL-4 crates are written to be OS-agnostic `no_std` libraries; a
  thin OS-specific task wrapper lives outside the crate.
- **Cybersecurity is not a crate.** It is a set of invariants enforced
  by `osr-crypto` plus configuration discipline plus the measured-boot
  hardware stack. A single "osr-cyber" crate would be an anti-pattern.

## 14. Open questions

1. **Crate naming: hyphens or underscores in the wire-topic namespace?**
   The topics in §6 use dotted names (`osr.train.ma`); crate names use
   hyphens. The mapping is unambiguous but warrants a one-line style
   rule in the contribution guide.
2. **Does `osr-atp` own the envelope math or delegate to a companion
   `osr-brake-model` crate?** Leaning toward owning it; the braking
   curve is already in `osr-core::consist::BrakingCurve`. Revisit if
   the curve model needs to support non-trivial consists (articulated,
   heterogeneous).
3. **Pantograph monitoring.** If a deployment instance adds
   opportunity-charging pads, a `osr-pantograph` crate is needed. Not
   in §4 because pads are Phase 4+ (post-Samawah baseline).
4. **Wayside relay interlocking retrofit shim.** Some brownfield
   pilots may need to bridge to an existing relay plant. Shim crate
   or per-deployment tooling? Deferred to first retrofit engagement.
5. **Hot-axle threshold tuning.** Value varies by bearing vendor and
   ambient. Parameterised in TOML config; default per
   [RFC 0003](0003-samawah-reference-deployment.md) climate envelope.
6. **Repository layout change.** The [ARCHITECTURE.md §6.3 tree](../ARCHITECTURE.md#63-repository-layout-proposed)
   is superseded by §4 here (more crates, cleaner domain split). A
   follow-up editorial PR updates ARCHITECTURE.md to point at this RFC
   for the crate list.

## 15. Done criteria

- [x] Every hardware class tagged (§3.1)
- [x] Every bus named and standardised (§3.2)
- [x] SIL allocation rules explicit (§3.3)
- [x] All thirty-five crates enumerated with owner-domain, class, SIL, scope (§4)
- [x] Dependency graph closed under the "no higher-SIL-on-lower" rule (§5)
- [x] On-train and train-to-ground interface contracts defined (§6)
- [x] SIL-4 coding standard carried forward from RFC 0004 (§7)
- [x] Deployment topology stated (§8)
- [x] Cybersecurity posture linked to ARCHITECTURE.md §8 (§9)
- [x] Reference boundary stated (§10)
- [x] Rollout order fixed (§11)
- [x] Pitfalls and open questions captured (§13, §14)

The next session picks up at **Phase 2a, crate 1 — `osr-atp`** (RFC 0006).
