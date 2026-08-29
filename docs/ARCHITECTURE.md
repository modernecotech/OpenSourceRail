# OpenSourceRail — Scope & Architecture

**Status:** Current development baseline (2026-08-29)
**Audience:** Engineers, operators, policymakers, and funders evaluating the project.
**Purpose:** Define what OpenSourceRail is, what it is not, and the architectural stance that distinguishes it from existing rail vendor offerings.

---

## 1. Mission

OpenSourceRail is an open reference platform for **designing, testing,
building, and operating urban rail systems**—light metro and urban metro. Its
primary beneficiaries are **developing-world nations** seeking transparent,
locally adaptable alternatives to opaque turnkey planning and integration.
Repository outputs are screening and engineering evidence, not certified or
construction-ready systems.

**Scope is urban transit only.** Intercity passenger, long-distance, and freight/cargo rail are explicitly out of scope. The rationale is focus: urban transit is where the unit of need is highest in target markets, where the duty cycle is most favorable to the catenary-free battery-electric architecture proposed in §4 D7, and where a single reference design generalizes cleanly across many deployments. Freight and intercity have meaningfully different energy, signaling, and rolling-stock profiles that would dilute focus; they may be candidates for sibling projects or a future v2.

The project succeeds when a national railway authority, working with domestic
engineering firms and qualified suppliers, can retain design authority,
localise ordinary fabrication and integration, and limit imported content to
specialist components that cannot yet be sourced or qualified locally.

Target deployment regions — sub-Saharan Africa, MENA, South and Southeast Asia, most of Latin America — share two properties that shape the architecture: they are capital-constrained, and they are high-insolation. Design choices throughout this document treat both as load-bearing assumptions rather than edge cases.

### 1.1 Non-goals

- **Not a standards body.** Where good open standards exist (e.g., GTFS, NeTEx, IEEE 802.1 TSN), adopt them. Where they don't, define minimal project-local interfaces — don't chase ISO ratification.
- **Not a safety certifier or operator of record.** The project will produce artifacts suitable for independent safety assessment, but certification is performed by national authorities and independent assessors. Deployment owners, operators, prime integrators, insurers, and entities in charge of maintenance carry the statutory safety case, liability, and operating approvals.
- **No compatibility layers in the reference core.** Deployment-specific adapters stay outside the shared architecture and are owned by the deployment that needs them.

---

## 2. Design Principles

1. **Commodity hardware, custom software.** Industrial PLCs, proprietary trainbuses, and vendor-specific radios are replaced with commodity SBCs, deterministic Ethernet, and standard radio layers. Value is captured in the software and system integration, which can be produced anywhere.
2. **Appropriate tools with controlled interfaces.** Rust carries the runtime,
   simulation and control core; Python carries GIS, engineering and CAD
   automation; browser applications use pinned web toolchains. Schemas and
   deterministic generators control the boundaries.
3. **Replace and remove.** Superseded reference designs leave the active repository instead of accumulating alternate paths. Every major choice records the concrete advantage of its replacement.
4. **Simulation-first.** No subsystem is considered designed until it runs end-to-end in a shared digital twin. Hardware pilots come after simulation sign-off.
5. **Machine-checkable safety.** Safety arguments are structured (GSN-style), version-controlled, and linked to formal proofs, test evidence, and code. Safety cases regenerate on every commit.
6. **Small, replaceable pieces.** Each subsystem is deployable independently. A country can adopt the dispatching platform without committing to the rolling-stock ECUs, and vice versa.
7. **Defense in depth.** Every wayside node is assumed to be reachable by an adversary. Signed firmware, mutually authenticated links, minimal attack surface, privilege separation at the OS level.

---

## 3. System-of-Systems Map

A rail system is a federation of largely independent subsystems that share a handful of critical interfaces. OpenSourceRail is organized around eight top-level domains:

For detailed backend, onboard train, station/depot, wayside waypoint,
energy, manufacturing, QA, and maintenance software diagrams, see
[`software-architecture-diagrams.md`](software-architecture-diagrams.md).

```
                         ┌───────────────────────────────────────┐
                         │  D1. Operations & Dispatch (OCC)      │
                         │  - timetable, crew, incident mgmt      │
                         │  - event-sourced state, web UIs        │
                         └───────────────┬───────────────────────┘
                                         │ authoritative ops log
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
    ┌────────────▼──────────┐ ┌──────────▼──────────┐ ┌─────────▼──────────┐
    │ D2. Train Control     │ │ D3. Communications  │ │ D4. Passenger Svcs │
    │  - interlocking       │ │  - train<->wayside  │ │  - fare/ticketing  │
    │  - movement authority │ │  - 5G SA / LoRa mesh│ │  - info displays   │
    │  - T1 safety target   │ │  - TSN wayside bkbn │ │  - announcements   │
    └────────────┬──────────┘ └──────────┬──────────┘ └────────────────────┘
                 │                       │
    ┌────────────▼──────────┐ ┌──────────▼──────────┐
    │ D5. Rolling Stock     │ │ D6. Infrastructure  │
    │  - unified Rust ECUs  │ │  - track monitoring │
    │  - TSN trainbus       │ │  - switch machines  │
    │  - traction/brake/HVAC│ │  - level crossings  │
    └───────────────────────┘ └─────────────────────┘

    ┌───────────────────────┐ ┌─────────────────────┐
    │ D7. Energy            │ │ D8. Depot & Maint.  │
    │  - ROW + station PV   │ │  - CBM telemetry    │
    │  - trackside storage  │ │  - parts/workorders │
    │  - station charging   │ │  - PV+storage μgrid │
    │  - (no catenary)      │ │  - yard automation  │
    └───────────────────────┘ └─────────────────────┘
```

Each domain has a dedicated section below. Interfaces between domains are deliberately narrow and enumerated in §5.

### 3.1 Design And Delivery Control Plane

The [OSR Workbench](workbench/README.md) integrates City Studio, simulation,
OCC training and Ops Core under one origin. It carries city, actor, immutable
revision, approved baseline, simulation run and selected-asset context without
merging authority boundaries:

- City Studio owns planning intent and Git-reviewable revisions;
- GIS, OSR-ALN, IFC4.3, IDS/BCF, CAD, cost and simulation files are generated
  evidence tied to source and tool hashes;
- planning and training views cannot issue live OCC actions;
- live mode does not expose design or simulation controls;
- revision hashes prove identity, not approval; approval history is
  append-only and evidence-referenced.

The [Bonsai civil workflow](civil/bonsai-ifc-workflow.md) is the federation,
inspection, drawing, quantity and 4D review path. OSR project and engineering
rules remain authoritative.

---

## 4. Reference subsystem designs

For each domain, we state (a) the dominant current practice, (b) its problems for our target users, and (c) the OpenSourceRail approach.

### D1. Operations & Dispatch

| | Legacy | OpenSourceRail |
|---|---|---|
| Platform | Proprietary SCADA (Thales ARAMIS, Siemens Vicos, GE Transportation) on Windows | Event-sourced Rust services on Linux SBCs/servers, web-based UIs |
| State model | Periodic polling, opaque internal state, vendor-specific DBs | Append-only operations log (single source of truth), CQRS read models, standard Postgres |
| Observability | Proprietary HMI screens, vendor-locked historians | OpenTelemetry traces + Prometheus + Grafana; historian is just retention on the log |
| Integration | Per-vendor OPC/IEC 60870-5-104 gateways | Typed gRPC/NATS interfaces with OPC UA at the hardware boundary |
| Disaster recovery | Active/passive OCCs with manual cutover | Multi-region event log replication, any dispatcher terminal can fail over to a replica |

**Deprecated:** Windows-based SCADA, proprietary HMIs, per-vendor historians.
**Why this is safe:** Dispatch is non-safety-critical (safety is enforced at D2). The ops platform is free to use modern stacks.

### D2. Train Control (Interlocking, ATP, ATO)

This is the heart of the safety argument and receives the most design attention.

| | Legacy | OpenSourceRail |
|---|---|---|
| Block model | **Fixed block** (track circuits, axle counters) or vendor **CBTC moving block** | **Software-defined moving block** via distributed consensus across wayside nodes + self-reporting trains |
| Interlocking | Relay panels or proprietary PLC-based (Simis, Smartlock) at $55k–$550k/site | SIL-4-target Rust interlocking on redundant RISC-V SBCs at <$5k/site; formally verified with Kani/Creusot |
| Position | Track circuits + balises (Eurobalise) | Sensor fusion: GNSS + IMU + wheel odometry + low-cost UWB/beacon fixes at switches and platforms |
| Movement authority | Centralized zone controller issues MA to trains | Distributed Raft-style log holds authoritative track state; each train computes its own MA, cross-validated by two independent wayside nodes |
| Certification path | Per-vendor SIL-4 case, years to re-certify | Open formal models + continuously regenerated safety-case evidence, assessed per deployment |

**Excluded from the reference architecture:** Track circuits as primary train detection, centralized zone controllers, and relay interlockings.
**Why this is novel:** "Rail as a distributed system." Existing CBTC vendors use centralized zone controllers because their software isn't trusted to run distributed consensus correctly; a formally verified Rust implementation of a restricted consensus protocol (fixed membership, no dynamic reconfiguration in the hot path) changes that calculus.
**Key risk:** regulators, insurers, and procurement authorities need more than a technical artifact. A Git repository cannot carry the safety certificate or product liability for a railway. Mitigation: publish the formal model early, solicit review from independent safety assessors, and start with deployable non-safety subsystems, yard/test-track trials, and segregated-ROW pilots before any full metro deployment.

### D3. Communications

| | Legacy | OpenSourceRail |
|---|---|---|
| Mainline radio | GSM-R (sunsetting ~2030), FRMCS over dedicated 5G | Public 5G SA with slicing where available; private 5G on n77/n78 or CBRS where not |
| Backup/telemetry | Dedicated leaky-feeder or TETRA | **LoRa mesh** for low-bandwidth safety telemetry (MA updates, position reports) — cheap, long-range, carrier-independent |
| Wayside backbone | Vendor-specific fiber rings, proprietary timing | Ethernet + **TSN (IEEE 802.1)** for determinism; PTP (1588) for time sync |
| Station/passenger | Per-vendor WiFi controllers | WiFi HaLow (802.11ah) for IoT/telemetry, standard WiFi 6 for passenger access |
| Security | Often weak (GSM-R has known weaknesses) | mTLS everywhere, Noise Protocol Framework on LoRa link, signed firmware on every radio |

**Deprecated:** GSM-R, TETRA for rail, proprietary fiber timing protocols.
**Why LoRa for safety telemetry?** Safety messages are small (<100 bytes) and infrequent (~1 Hz per train). LoRa gives 5–15 km line-of-sight range at sub-$10 BOM, so a mesh of wayside LoRa gateways provides coverage redundancy at negligible cost compared to a primary 5G link.

### D4. Passenger Services

| | Legacy | OpenSourceRail |
|---|---|---|
| Fare media | Smart cards (MIFARE, Calypso) with per-operator infrastructure | **Account-based ticketing**: mobile money (M-Pesa, UPI, etc.) + QR + optional NFC, validated via signed short-TTL tokens offline-capable |
| Ticket vending | Dedicated TVMs at $22k+/unit | SBC-based TVMs with commodity barcode scanner + contactless reader; <$1k/unit; most passengers use phones and don't need a TVM at all |
| Info displays | Proprietary LCD controllers with custom protocols | SBC + standard HDMI + minimal Rust display agent subscribing to the ops event stream |
| Announcements | Per-station PA controllers, manual voicing | Text-to-speech from the same event stream, multilingual by default; human override for incidents |

**Deprecated:** Closed-loop smart card systems, dedicated TVMs as the primary sales channel.
**Why account-based first:** Most target markets have leapfrogged cards via mobile money. Investing in a smart card ecosystem now is a decade-long dead end.

### D5. Rolling Stock

| | Legacy | OpenSourceRail |
|---|---|---|
| Trainbus | MVB + WTB (IEC 61375), proprietary silicon, decades-old | **TSN Ethernet** (IEEE 802.1 Qbv/Qcc) over standard copper/fiber — off-the-shelf switches, deterministic traffic |
| ECU diversity | 20–50 ECUs from different vendors, different RTOSes, different toolchains | Single **reference ECU hardware** (RISC-V or ARM SoC + CAN-FD + TSN Ethernet PHY). Different "apps" (traction control, door control, HVAC, PIS) as Rust binaries on identical hardware |
| OS | Mix of VxWorks, QNX, proprietary | **Hubris** (or seL4) on safety-critical ECUs; Linux on infotainment |
| Energy source | Pantograph/shoe drawing from catenary/3rd rail; diesel genset on non-electrified lines | **800 V-class onboard LFP.** Three 225 kWh gross car packs on the promoted three-car train; automated conductive station charging; no continuous catenary. |
| Traction drive | Proprietary VVVF inverters from rail Tier-1s | Six supplier-neutral heavy-commercial-vehicle-class PMSM/controller sets on the promoted train, qualified against an OSR interface control document |
| Diagnostics | Per-vendor tools, per-train service laptops | Unified OpenTelemetry export to depot; any maintainer with a browser can inspect any train |

**Deprecated:** MVB/WTB, per-vendor ECUs, VxWorks/QNX dependence, pantograph-as-primary-energy-source, diesel-genset rolling stock.
**Why a single reference ECU:** Two trains of the same class today contain dozens of subtly different PCBs from a supply chain deeply entangled with specific Tier-1s. One reference board (manufactured anywhere with basic SMT capability) for all non-traction-power functions collapses the supply chain dramatically.
**Why onboard battery instead of continuous electrification:** See D7 for the full argument. Each reference car carries one 225 kWh gross LFP pack in fire-resistant under-seat compartments, for 675 kWh gross across the three-car train.

### D6. Infrastructure Monitoring

| | Legacy | OpenSourceRail |
|---|---|---|
| Track geometry | Dedicated measurement trains, quarterly runs | Continuous CBM: every service train carries a low-cost IMU + acoustic package; data fused server-side |
| Switch machines | Proprietary motor controllers with point-detection contacts | Commodity BLDC + SBC controller, dual redundant position sensors, reports to the train-control consensus log |
| Level crossings | Standalone controllers, minimal integration | Same SBC platform as interlocking; crossings are just wayside nodes in the consensus network |
| Bridge/tunnel | Periodic manual inspection | Distributed vibration/strain sensors over LoRa, anomaly detection in the ops platform |

**Deprecated:** Dedicated measurement trains as the primary data source, isolated crossing controllers.

### D7. Energy — Solar Generation, Trackside Storage, Battery Traction

This domain departs most sharply from legacy rail. OpenSourceRail systems are **catenary-free by default**, powered by solar PV deployed on railway-owned land with battery storage buffering the mismatch between generation and train demand.

| | Legacy | OpenSourceRail |
|---|---|---|
| Traction energy delivery | Overhead catenary (25 kV AC / 1.5–3 kV DC) or third rail, fed from grid substations every 2–5 km | **No catenary.** Onboard battery traction; recharged at stations/depots from trackside storage (see D5). |
| Primary generation | Grid purchase at fixed tariff; dedicated traction substations | **Solar PV on** (a) platform/station canopies, (b) depot roofs, (c) right-of-way along track (vertical bifacial + between-rail panels) |
| Energy buffering | Typically none — instantaneous draw from grid | Repeatable **500 kWh stationary-LFP modules** at stations, quantity proved by the timetable/energy model |
| Grid interface | High-power traction substations, often dedicated feeders | Smaller grid-tie inverters that *import* when PV + storage are insufficient and *export* surplus where regulations allow |
| Chemistry preference | N/A (no storage) | **LFP reference chemistry** onboard and wayside; no NMC in the baseline |
| Charging interface | Continuous pantograph/shoe contact along entire route | **500 kW automated conductive side contact** at station dwells; terminals use the same cabinet for longer |
| Regeneration | Often wasted in resistor banks | Fully recaptured to onboard battery and exported to trackside storage during platform charging |
| Control | Centralized SCADA | Per-site Rust controller + PV-storage-charge optimizer driven by the ops timetable (D1); autonomous on sub-second timescales |

**Deprecated by default in the reference architecture:** overhead catenary, third rail, dedicated traction substations, resistor-brake dissipation, centralized thyristor rectifiers, diesel gensets on non-electrified lines.

#### 7.1 Why catenary-free

- **Capex.** Catenary + support structures + paralleling posts cost $1–3M/km. Eliminating that is the single largest capex reduction available on a greenfield rail project.
- **Opex and workforce.** OCS maintenance requires specialized crews (live-line work, night possessions). Battery + station-charging infrastructure is maintainable by general electricians and renewable-energy technicians — skills that are more transferable and more widely available in target economies.
- **Copper theft.** Overhead copper is a persistent operational hazard in many developing markets. Trackside infrastructure in hardened cabinets is a much harder target.
- **Phased deployment.** Non-electrified lines become usable the day rolling stock arrives, with no "electrification project" preceding revenue service.
- **Operational resilience.** A single catenary fault halts every train on the section; a distributed storage+generation network degrades gracefully — trains can reach the next charging station on reserve capacity.

#### 7.2 Why solar-along-ROW

- Railways own long, linear, already-cleared strips of land with predictable sun exposure. The real estate is effectively free.
- Generation is co-located with load. Losses and transmission infrastructure are minimal.
- Three complementary PV deployment patterns (pilots exist for each):
  1. **Platform and station canopies** — straightforward, aesthetically acceptable, dual-use as weather protection.
  2. **Vertical bifacial PV along ROW boundaries** — doubles as property fence; captures morning/evening sun at different angles than horizontal panels (smoother daily generation curve).
  3. **Between-rail / on-sleeper PV** (Sun-Ways-style) — highest area utilization but must tolerate train passage and ballast tamping; treat as Phase 4+ after basic patterns prove out.
- First-order math at 5 peak sun-hours, 3 m usable PV width per track-km, 200 W/m² module density: ≈3 MWh/day per track-km. A light metro trainset consumes on the order of 3–5 kWh/car-km. A modestly loaded 3-car service at 20 round-trips/day consumes ≈180–300 kWh/day/km. That makes self-powered operation a plausible screening target across many OSR regions, but not a guarantee. The generated energy model must survive local solar, dust, temperature, grid, export-tariff, charger, storage, and timetable studies before a deployment claims net-positive operation. Grid import covers monsoon/cloudy stretches and overnight draw on trackside storage; grid export monetizes midday surplus where regulations allow.

#### 7.3 LFP and the 800 V-class DC system

[RFC 0021](rfcs/0021-battery-traction.md) is the controlling
energy architecture. The promoted three-car train retains 675 kWh gross /
540 kWh routinely usable capacity, split into three independently serviceable
225 kWh LFP car packs. The pack is 650–700 V nominal, with its exact cell
count and upper SOC voltage constrained by controller transient margin.

Stations use the same chemistry in commodity stationary modules: one 500 kWh
gross module is the starting normal-station design, and the simulation may add
integer modules where timetable, solar, grid, or degraded-service evidence
requires them. In the three-car reference, one 500 kW DC/DC cabinet is shared
between platform contacts. Four-car high-throughput deployments repeat that
complete storage/cabinet/contact module three times and six-car deployments
four times; the converter design itself is unchanged and the generator
carries every module in CAPEX.
This choice prioritizes mature, high-volume heavy-vehicle and stationary-
storage supply chains. LFP is the sole repository battery chemistry; NMC and
other chemistries are outside the reference design.

#### 7.4 Scope fit

This architecture is tuned for urban transit duty cycles: short runs, frequent stops, predictable daily service patterns, and fleet sizes in the low tens of trainsets. Within that envelope the catenary-free + solar model is a credible default to test, not a universal replacement for electrification. Heavy freight and long-distance intercity service have meaningfully different energy profiles and are explicitly out of scope (§1); this section does not attempt to cover them.

#### 7.5 Interfaces

New or modified cross-domain interfaces:

- **I9 (Charging Dispatch):** D1 ops informs D7 which trains are due at which charging sites and when, so trackside storage can pre-charge buffers.
- **I10 (Energy Telemetry):** D5 trains report state-of-charge and predicted arrival SoC to D1/D7; D1 can re-plan around a low-SoC unit the way it would re-plan around a delayed one.
- **I11 (Grid Tie):** D7 sites speak standard grid-interface protocols (IEEE 2030.5 / Sunspec Modbus) to the local utility.

These are additions to §5 and will be formalized in `crates/osr-core/proto/energy.proto`.

### D8. Depot & Maintenance

| | Legacy | OpenSourceRail |
|---|---|---|
| Work orders | SAP PM or proprietary EAM | Rust service on the same event-sourced platform; integrated with train telemetry |
| CBM | Optional, bolt-on, per-vendor | First-class; every ECU streams condition data continuously |
| Yard automation | Manual | Same train-control stack, restricted to yard speeds; useful proving ground |
| Energy | Grid-fed charging (where electric at all), diesel refueling | **Depot PV+LFP-storage microgrid:** rooftop solar, repeated stationary modules, overnight low-C balancing, and grid import for shortfalls. |

---

## 5. Cross-Domain Interfaces

OpenSourceRail defines a minimal set of typed interfaces between domains. Everything else is internal to the owning domain.

| # | Interface | Producers | Consumers | Transport | Format |
|---|---|---|---|---|---|
| I1 | **Track State Log** | D2 interlockings | D1 ops, D5 trains | Raft-replicated, gRPC streaming | Protobuf schema `track_state.proto` |
| I2 | **Movement Authority** | D2 | D5 trains | mTLS gRPC over D3 radio | `movement_authority.proto` |
| I3 | **Train Position Report** | D5 trains | D2 | mTLS gRPC or LoRa (primary/backup) | `position_report.proto` |
| I4 | **Ops Event Stream** | D1 | D4, D6, D8 | NATS JetStream or Kafka-compatible | CloudEvents JSON |
| I5 | **Telemetry** | all ECUs/wayside | D1, D8 | OpenTelemetry OTLP | OTLP standard |
| I6 | **Passenger-facing schedule** | D1 | public | GTFS-RT + GTFS static | GTFS standard |
| I7 | **Fare Token** | D4 issuing service | D4 validators | Offline-verifiable JWT variant | RFC 8392 CWT |
| I8 | **Traction Setpoints** | D7 controller | charging / inverter hardware | OPC UA | standard |
| I9 | **Charging Dispatch** | D1 ops | D7 station charging sites | NATS JetStream | `charging_dispatch.proto` |
| I10 | **Energy Telemetry** | D5 trains, D7 sites | D1 ops, D8 depot | OpenTelemetry OTLP | OTLP standard |
| I11 | **Grid Tie** | D7 sites | local utility | IEEE 2030.5 / Sunspec Modbus | standard |

Only I1–I3 are safety-critical. Everything else can fail without loss of safe operation (degraded service only). **I9/I10 failure** degrades energy planning but does not affect train control — trains carry enough reserve to reach the next charging site without active dispatch.

---

## 6. Platform Stack

### 6.1 Software tiers

| Tier | Examples | OS | Rust flavor | Constraints |
|---|---|---|---|---|
| **T1 — Safety kernel** | Interlocking, ATP, door safety | Hubris or seL4 | `no_std`, RTIC | SIL-4 target; formally verified; < 50k LoC per binary |
| **T2 — Safety-adjacent** | Train ECU apps, substation control | Hubris or PREEMPT_RT Linux | `no_std` or minimal std | SIL-2 target; strict coding standard; full test coverage |
| **T3 — Supervisory** | Dispatching, ops services, telemetry collectors | Linux (Debian or Yocto) | `tokio` std | High availability; not safety-critical |
| **T4 — UX/Back-office** | Dispatcher web UI, passenger apps, EAM | Linux / browser | `axum`/`leptos` Rust, TypeScript at edges | Standard web security practices |

### 6.2 Reference hardware

- **Wayside SBC (W-SBC):** RISC-V (e.g., MilkV Jupiter-class) or ARM64 (e.g., Raspberry Pi CM5 carrier), dual Ethernet, CAN-FD, hardware RoT (TPM 2.0 or OpenTitan). Deployed in ruggedized enclosures; runs T1/T2.
- **Train ECU (T-ECU):** Same SoC family as W-SBC, EN 50155 environmental ratings, TSN Ethernet PHY, CAN-FD, isolated I/O modules.
- **Ops server (O-SRV):** Commodity x86 or ARM64 server, Debian, standard datacenter gear. T3/T4.

Reference hardware has two implementation tracks under
[`hardware/`](../hardware/). The first-pilot track is the
[RFC 0019](rfcs/0019-diy-electronics.md) COTS/SBC assembly path:
commodity compute modules, sensor boards, relay modules, power
supplies, terminal blocks, DIN-rail enclosures, prepared firmware
images, wiring/harness maps, and bench evidence. It does not require
KiCad or gerbers when no custom PCB is used. The volume-production
track is the [RFC 0007](rfcs/0007-hardware-reference-designs.md)
custom-board path: OSR-specific carrier, power, safety-I/O, or
sensor-interface boards captured as schematics, BOMs, layouts, and
Gerbers. Custom boards must remain manufacturable by a 4-layer PCB fab
with 0.15 mm trace/space and 0.3 mm vias — routine at tier-2 fabs
across the target deployment footprint.

### 6.3 Repository layout

The canonical runtime-component map is in
[RFC 0005](rfcs/0005-sbc-software-architecture.md); the complete implemented
inventory is checked by [simulation software coverage](simulation-software-coverage.md).

```
OpenSourceRail/
├── projects/                  # City Studio inputs and immutable revisions
├── designs/                   # Generated city/national packages
├── crates/                    # Runtime, simulation, control and browser apps
├── design-py/                 # GIS and city engineering sidecars
├── mechanical-py/             # Parametric rolling-stock/civil CAD
├── engineering/               # IFC, schemas and engineering evidence
├── hardware/                  # Host roles and bring-up/integration evidence
├── formal/                    # Formal models and checks
└── docs/                      # Shared decisions, operations and assurance
```

---

## 7. Safety & Certification Strategy

OpenSourceRail targets the EN 50126/50128/50129 and IEC 61508 framework because that is what national safety authorities will recognize. Until a deployment-specific assessor and authority accept the evidence, SIL wording in this repository means target assurance class and hazard allocation, not certification. The approach is:

1. **Formal models first.** Signaling logic is expressed in a formal model (Kani, Creusot, or TLA+ where appropriate) before implementation. The Rust implementation is proven to refine the model.
2. **Small safety kernel.** T1 binaries are aggressively minimized. Everything that can be pushed out of the safety kernel is.
3. **Diversity by construction.** Two independent Rust implementations of each T1 function, compiled with different toolchain configurations, cross-check each other on redundant hardware. This is cheaper than the traditional "different language + different team" because the second implementation is constrained by the same formal model.
4. **Machine-checkable safety case.** Safety arguments are written in GSN (Goal Structuring Notation) serialized as TOML, with claim → evidence links resolving to code commits, proof artifacts, and test results. CI regenerates the case on every merge; a safety case that no longer closes blocks the release.
5. **Independent assessment.** The project produces artifacts. Certification is performed per-deployment by the national authority's chosen ISA, with the owner/operator and prime integrator carrying the accepted safety case, insurance, and liability. Reference safety cases from pilot deployments are published to compound assessor familiarity across countries.

---

## 8. Security Posture

- **Zero trust on the wayside network.** Every node authenticates every peer (mTLS, mutually verified certificates rooted in a project-operated PKI per deployment).
- **Signed firmware, measured boot.** TPM-backed attestation; update rollback via A/B partitions.
- **Privilege separation at OS level.** Hubris's "task" model gives hardware-enforced isolation; on Linux, systemd + seccomp + namespaces.
- **No default credentials, ever.** Commissioning generates unique per-device keys.
- **Auditable by construction.** Every safety-relevant event is in the append-only log; tampering is detectable.

---

## 9. Roadmap

Implemented software, design and evidence capabilities are summarised in the
[root feature table](../README.md#feature-highlights). Remaining work is
maintained once in [ROADMAP.md](ROADMAP.md) and the domain release checklists.
Calendar predictions are deliberately excluded until an owner, funded work
package and external evidence route exist.

---

## 10. Open Questions

The controlling open questions are deployment evidence rather than missing
marketing claims:

1. Which eligible operator, university, integrator and independent assessor
   will govern the first bounded pilot?
2. Which supplier modules, host hardware and secure deployment transports pass
   the required qualification and lifecycle evidence?
3. Which surveyed alignment, ground, utility, climate, demand and fire data
   replace the planning assumptions for that pilot?
4. Which national rules determine homologation, cyber approval, accessibility,
   grid connection, battery end-of-life and operating responsibility?
5. Which public, research or development-finance route funds each evidence
   stage without treating screening outputs as an investment approval?

Detailed gaps are tracked in the certification, civil, rolling-stock,
hardware and operations release checklists linked from [ROADMAP.md](ROADMAP.md).

---

## 11. Architecture Reading Order

Start with the root [Find Your Way](../README.md#find-your-way) table. For a
deeper architecture review, continue in this order:

1. This document.
2. [`docs/GLOSSARY.md`](GLOSSARY.md) — rail-domain terms for software engineers and vice versa.
3. [`docs/rfcs/0001-track-state-consensus.md`](rfcs/0001-track-state-consensus.md) — the distributed track-state log design.
4. [`docs/rfcs/0002-energy-sizing.md`](rfcs/0002-energy-sizing.md) — quantitative sizing for the catenary-free, solar-first energy architecture.
5. [`docs/rfcs/0003-samawah-reference-deployment.md`](rfcs/0003-samawah-reference-deployment.md) - Samawah context, pilot rationale, and risks; generated city numbers live under `designs/west-asia/Iraq/Samawah/`.
6. [`docs/rfcs/0004-osr-interlocking-plan.md`](rfcs/0004-osr-interlocking-plan.md) — implementation plan for the Rust SIL-4 MA computer.
7. [`docs/rfcs/0005-sbc-software-architecture.md`](rfcs/0005-sbc-software-architecture.md) — canonical SBC software architecture + crate map.
8. [`crates/osr-core/proto/track_state.proto`](../crates/osr-core/proto/track_state.proto) — the interface definitions.
9. [`formal/tla/SMRaft.tla`](../formal/tla/SMRaft.tla) — TLA+ spec of the consensus protocol.

---

*This document is a living architecture brief. Material changes go through RFCs in `docs/rfcs/`; editorial changes can be PRs directly.*
