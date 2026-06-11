# RFC 0007 — Hardware Reference Designs

**Status:** Draft v1.1 — planning only, no schematics ship with this RFC
**Date:** 2026-04-22 (v1.1 same day — SoC palette restricted to Raspberry Pi + Radxa)
**Depends on:** [RFC 0005 SBC Software Architecture](0005-sbc-software-architecture.md), [RFC 0006 `osr-tcn` design](0006-osr-tcn-design.md)

## 1. Summary

This RFC fixes the custom-board reference designs for the physical
host classes on which OpenSourceRail software runs — **T-ECU/S**,
**T-ECU/A**, **T-OBS**, **W-SBC**, **S-SBC** — *before* a schematic is
drawn. It picks the SoC, the module form factor, the baseboard
constraints, and the per-board BOM envelope. It does not commit the
schematics; those land as a separate editorial PR once the decisions
below are ratified. For first-article and pilot deployments, the
commodity-module path in [RFC 0019](0019-diy-electronics.md) is the
preferred implementation route and does not require KiCad or gerbers
when no custom PCB is used.

The O-SRV class is commodity server hardware — any x86-64 or ARM64
Linux box that meets the operator's procurement rules. It is out of
scope for this RFC.

Why a planning RFC first: hardware decisions are sticky. A T-ECU/S
reference design outlives three software refreshes and four deployment
generations, because the PCB, the environmental compliance testing,
and the depot spares-and-repairs pipeline all calcify around the choice.
Getting the class selection right costs a session of writing; getting
it wrong costs an order of magnitude more in re-compliance later.

Three non-negotiable constraints shape every decision below:

1. **Local manufacturability.** Every board must be producible on a
   4-layer PCB with 0.15 mm trace/space, 0.3 mm vias, standard SMT
   (0402 minimum passive), and through-hole where rail
   vibration/shock demands it. No micro-vias, no blind/buried vias,
   no 0201 passives, no exotic stackups. These are routine tier-2
   board shops across MENA, sub-Saharan Africa, South and Southeast
   Asia, and Latin America — the target deployment footprint.
2. **Commodity System-on-Module (SoM) first.** Wherever a
   ready-made compute module with the right environmental rating
   exists, we adopt it and design only the baseboard. This reduces
   the domestic engineering burden to a carrier board plus
   enclosure — a fraction of the work of a from-scratch SoC design.
3. **Two-vendor palette — Raspberry Pi and Radxa only.** Raspberry
   Pi supplies the consumer-grade CM5 module and the RP2350 safety
   MCU; Radxa supplies the industrial-temperature CM5 (RK3588S)
   for pole-mount use. Both vendors are available globally at
   predictable prices, document their modules openly, and ship with
   mainline Linux support. This restriction deliberately excludes
   NXP / ST / Rockchip-direct / MilkV / StarFive bring-up paths —
   not because those are technically unfit, but because locking on
   two well-stocked vendors simplifies the domestic procurement and
   spares story for the operator.

## 2. Non-goals

- **Not a full hardware BOM.** This RFC specifies reference choices;
  the per-deployment BOM is owned by the operator and tuned to
  local availability.
- **Not a certification strategy.** EN 50155 / IEC 61373 /
  EN 50121-3-2 compliance testing is in scope for the safety case
  (`osr-safety-case`), not this document.
- **Not a redundancy topology.** The logical redundancy
  (dual T-ECU/S, 3-node W-SBC consensus cluster) is already fixed by
  [RFC 0001](0001-track-state-consensus.md) and
  [RFC 0005 §8](0005-sbc-software-architecture.md). This RFC is about
  one board of each class; stitching them into a consist or a
  wayside cabinet is deployment-level.
- **Not a hard-real-time bus design.** TSN / PTP details are
  [RFC 0006](0006-osr-tcn-design.md). This RFC references those
  choices but does not re-litigate them.

## 3. Common platform choices

These apply to every class below unless overridden.

| Aspect | Choice | Rationale |
|---|---|---|
| **PCB** | 4-layer FR-4, 0.15 mm trace/space, 0.3 mm min via | Routine at tier-2 fabs worldwide. |
| **Passives** | 0402 minimum | SMT-line friendly, hand-rework possible. |
| **Connectors** | M12 for field I/O, board-to-board for modules | M12 is the rail industry standard for trackside and consist wiring (EN 50467). |
| **Isolation** | 1.5 kV galvanic on every external I/O | EN 50155 demands it for rolling stock; W-SBC gains the same treatment for consistency. |
| **Power input** | 24 V DC nominal, 16.8–30 V range | EN 50155 wide-input class. On trains this comes from the battery bus via `osr-aux-power`. At wayside sites it comes from the site supply. |
| **Power sequencing** | TI LM5164 buck → 5 V → per-rail LDO | Single widely-stocked part, no exotic controllers. |
| **Firmware storage** | eMMC (on-module) + external SPI-NOR for boot | eMMC is the reference OS filesystem; SPI-NOR holds the measured-boot root. |
| **Trust anchor** | Microchip ATECC608 or NXP A1006 SE | Either is commodity, EN 50155 rated, well-documented. ATECC608 is our baseline because ed25519 support is native. |

## 4. Class T-ECU/S — Train Safety Kernel

**Role:** Hosts the SIL-4 crates — `osr-atp`, `osr-odometry`,
`osr-traction` (MCU bring-up), `osr-bms`, `osr-brake`,
`osr-door-control`, `osr-vigilance`, `osr-fire-safety`,
`osr-derailment`. One primary + one hot-standby per consist.

**Environment:** EN 50155 OT4 (−40…+85 °C), IEC 61373 Cat 1 Class B
vibration + shock, EN 50121-3-2 EMC.

### 4.1 Safety architecture — 2oo2 composite fail-safe

The safety case is anchored in *diverse redundancy between two
independent microcontrollers*, not in a single silicon vendor's
lockstep claim. Each T-ECU/S board carries **two Raspberry Pi
RP2350 MCUs** wired in a 2-out-of-2 voting arrangement:

```text
   sensors ──┬─► RP2350 #A ──► result_A ─┐
             │                           ├─► 2oo2 vote ─► actuator
             └─► RP2350 #B ──► result_B ─┘     (HW relay)
                    ▲                              │
                    │ cross-check (SPI, 10 kHz) ◄──┘
                    │         mismatch ─► BOTH chips halt,
                    │                      hardware watchdog
                    │                      drops brake relay.
```

- Both chips receive the same raw sensor inputs on electrically
  separate pins.
- Both chips execute identical Rust `no_std` code (Hubris or a
  bespoke bounded scheduler).
- Each tick they exchange their computed safety decisions over a
  dedicated SPI link and compare byte-for-byte.
- The final actuator-drive output is produced by a hardware AND of
  both chips' drive lines through an external 2oo2 relay network.
  A single chip can only *permit* motion; it cannot command it
  alone.
- On disagreement, both chips set themselves to fail-safe (drive
  lines open) and a downstream hardware watchdog asserts the
  emergency brake relay directly.

This is the "composite fail-safe" pattern that EN 50129 appendix D
blesses for SIL-4. Because the two chips are physically identical
(not lockstep within one die), a single-event upset or silicon
defect affects at most one of them — the other still votes the
actuator into the safe state. Identical-software redundancy
handles random hardware faults; RFC 0004's Kani + proptest coverage
handles systematic software faults.

### 4.2 SoC picks

- **Safety MCU (×2 per board):** Raspberry Pi **RP2350**.
  Dual Cortex-M33 plus dual Hazard3 RISC-V in the same die (software
  selects one pair at boot), 520 KB SRAM, 150 MHz. Arm TrustZone-M
  for secure boot, hardware random number generator, and a single
  signed ROM loader. Published datasheet, globally available through
  the Raspberry Pi channel and every major distributor. Per-chip
  price ≈ €1 in 1k volume.

  Why RP2350 for safety — fit against the mission:
  - Tiny, stable silicon with a 5-year announced support window
    from Raspberry Pi. Matches the ≥ 20-year service life of the
    rolling stock better than most MCU vendors' SKUs.
  - Dual instruction-set option (Arm M33 or RISC-V Hazard3) means
    a second diverse implementation is available by re-selecting
    the ISA pair at boot — a future v2 refinement of the 2oo2
    pattern can go to true *ISA-diverse* 2oo2 without changing
    the BOM.
  - Available in QFN-56 (0.4 mm pitch) — hand-solderable under a
    loupe, trivial on any SMT line.

- **Application processor (×1 per board):** Raspberry Pi **CM5**.
  Handles TCN-E, logging, OTA, diagnostics, and hosts the event
  recorder. Runs mainline Linux. **The app processor is never on
  the safety path** — it subscribes to a one-way SPI feed from the
  safety MCUs and cannot preempt their decisions.

### 4.3 Peripherals (baseboard)

| Peripheral | Qty | Purpose |
|---|---|---|
| CAN-FD | 4 | Door, brake, traction, BMS buses (two CAN-FDs per RP2350, identical) |
| TSN Ethernet (on CM5 + external PHY KSZ9031) | 2 | TCN-E (A + B, redundant paths per RFC 0006) |
| Isolated DI | 8 | Emergency plunger, cab door switches, depot enable, deadman handle (each routed to *both* RP2350s) |
| Isolated DO | 4 | Emergency brake relay, traction cut relay, park brake solenoid, fire-suppression trigger (via 2oo2 relay network) |
| Tachometer inputs | 2 | Wheel encoders (quadrature, 5–24 V, each read by both RP2350s) |
| IMU | 1 | Bosch BMI088 6-axis (derailment + odometry) — read by both RP2350s via separate SPI chip-selects |
| GNSS | 1 | u-blox NEO-F10N over UART to CM5 |
| Balise reader | 1 | PN5180 NFC front-end over SPI (passive HF balise per RFC 0003) |
| Thermistors | 4 | Battery bay, traction bay, HVAC plenum, enclosure ambient |
| ATECC608B SE | 2 | One per RP2350 — trust anchor for signed firmware + cross-check keys |

Every input reaches both RP2350s on physically separate pins;
every output is AND-gated through the external 2oo2 relay stage.

### 4.4 Target BOM (volume 100+)

| Item | Unit cost (€) | Per board |
|---|---|---|
| RP2350 × 2 | 1.10 | 2.20 |
| Raspberry Pi CM5 (4 GB) | 85 | 85 |
| Baseboard (4-layer, 160 × 100 mm) | 40 | 40 |
| CAN-FD transceivers × 4 | 3 | 12 |
| Ethernet PHYs + mags | 12 | 12 |
| Isolated DI / DO (ADUM + discrete drivers) | 35 | 35 |
| BMI088 IMU + NEO-F10N GNSS + PN5180 | 45 | 45 |
| ATECC608B × 2, passives, connectors, power | 45 | 45 |
| **Total** | — | **~€280** |

Two per consist = **€560 per trainset** for the safety-kernel layer.
Well below the €900 previously budgeted on the NXP-centric plan;
the RPi-family modules drive the cost down.

### 4.5 Form factor

160 × 100 mm Eurocard, DIN-rail mountable in the cab cabinet.
Conduction-cooled to the DIN rail; no fans. Conformal coated
(MG Chemicals 419) before integration. Sealed to IP54.

## 5. Class T-ECU/A — Train Application

**Role:** Hosts SIL-2 / SIL-0 app-tier crates — `osr-ato`,
`osr-tcms`, `osr-dmi`, `osr-pis-onboard`, `osr-hvac`,
`osr-lighting`, `osr-aux-power`, `osr-event-recorder`,
`osr-regen`, `osr-hot-axle`, `osr-cbm-onboard`, `osr-t2g`.

**Environment:** EN 50155 OT4, single-redundant (two units per
consist is standard but a single unit is tolerable for non-safety
functions).

**SoC baseline:** Raspberry Pi **Compute Module 5** (BCM2712,
Cortex-A76 4-core, 4–16 GB LPDDR4X, eMMC on-module). RPi CM-class is
the obvious commodity module — wide availability, mature Linux
support, global stock, SO-DIMM-style connector.

Alternative drop-in: **Radxa CM5** (RK3588S — Cortex-A76 + A55
big.LITTLE on the same SO-DIMM footprint). Radxa's module is
pin-compatible with our baseboard; the only code delta is the
device-tree blob. Operators can source whichever is locally
available at procurement time.

**Peripherals (baseboard):**

| Peripheral | Qty | Purpose |
|---|---|---|
| TSN Ethernet | 2 | TCN-E A/B (redundant) |
| CAN-FD | 2 | HVAC + lighting buses |
| USB-C (host + device) | 2 | Depot console + diag loader |
| HDMI | 1 | DMI touchscreen output |
| USB 2.0 | 2 | DMI touch, PIS display |
| M.2 2280 NVMe | 1 | Event recorder ring buffer + OTA staging |
| M.2 2230 Cat.22 5G | 1 | TRG-1 (primary ground radio) |
| LoRa SX1276 on SPI | 1 | TRG-2 (backup ground radio) |
| CCA-B2B to T-ECU/S | 1 | Mailbox bridge to the safety side |
| ATECC608 SE | 1 | Trust anchor |

**Target BOM:** €220 per board (CM5 module ≈ €85, baseboard ≈ €75,
radios ≈ €60 volume).

**Form factor:** 160 × 100 mm Eurocard, same DIN mount as T-ECU/S so a
cabinet can accept either without re-designing the slot.

## 5.5 Class T-OBS — Train Obstacle-Detection ECU

**Role:** Hosts the SIL-4 `osr-obstacle-detect` evaluator per
[RFC 0015 §5.2](0015-driverless-operation.md). Fuses the nose-
cone sensor suite (ultrasonic × 4, LIDAR, mmWave radar, stereo
camera) into an `ObstacleVerdict` bus message consumed by the
T-ECU/S 2oo2 AND-gate relay stage.

**Two modules per trainset** — one at each nose. Only the
leading module is active for a given direction of travel; the
trailing module self-tests continuously and publishes an
`Inactive` status.

**Environment:** EN 50155 OT4, dual-redundant (both nose-end
modules duplicate the safety evaluator; either can drive the
brake chain).

**Architecture:** mirrors T-ECU/S: **two Raspberry Pi RP2350**
safety MCUs running the `osr-obstacle-detect` evaluator in a
2oo2 cross-check plus a **Raspberry Pi CM5** application
processor for sensor fusion, classifier inference, and the
non-safety data path. The safety-critical verdict is produced
*inside* the RP2350 pair; the CM5 supplies pre-processed
detection lists but cannot emit a `Clear` on its own.

**Peripherals (baseboard):**

| Peripheral | Qty | Purpose |
|---|---|---|
| Ultrasonic transceivers (40 kHz, 200 µs drive, 10-bit ADC) | 4 | Close-range safety belt per RFC 0015 §5.1 |
| CAN-FD to mmWave radar (TI AWR1843 or eq.) | 1 | All-weather long-range |
| 1000BASE-T Ethernet to LIDAR (Livox HAP / Tele / RoboSense M1) | 1 | Mid-range 3D primary |
| MIPI-CSI to stereo camera pair (IMX477 / IMX219) | 2 | Classification |
| TSN Ethernet | 2 | TCN-E A/B back to T-ECU/S + T-ECU/A |
| CCA-B2B to T-ECU/S | 1 | Direct brake-demand line (2oo2 AND-gate stage) |
| ATECC608 SE | 1 | Trust anchor (shared with T-ECU/S) |

**Power budget:** ~18 W under full load (LIDAR dominates at
~12 W); 24 V DC in with the same EN 50155 isolation as the rest
of the cab.

**Target BOM:** $850 per board module, dominated by the LIDAR
unit (~$550 for a Livox-class sensor in volume) + mmWave radar
(~$550 / $275 volume) + stereo camera pair (~$165) + baseboard
plus 2× RP2350 + CM5 (~$240 per the T-ECU/A BOM). Trainset total
(2 modules): **~$1 700 per consist**, well below the ~$150 k
cab capex removed.

**Form factor:** 180 × 120 mm Eurocard — slightly larger than
T-ECU/S to accommodate the four ultrasonic analog front-ends.
Mounted behind the RF-transparent nose panel; cooling is
ambient-air natural convection.

**Detailed v2 spec:** scaffold at
[`hardware/t-obs/schematics/v2-spec/`](../../hardware/t-obs/schematics/v2-spec/)
follows the T-ECU/S v2 template (block diagram, power budget,
pinouts, connector table, safety-net routing rules). KiCad
capture is v3 per §11 rollout.

## 6. Class W-SBC — Wayside

**Role:** Hosts `osr-consensus`, `osr-interlocking`,
`osr-wayside-points`, `osr-level-crossing`, `osr-hot-axle-wayside`,
`osr-balise` (reader side), `osr-energy-site`. Deployed in
pole-mounted IP67 cabinets along the corridor and at each junction.

**Environment:** IEC 60529 IP67, EN 50121-4 EMC, −40…+70 °C,
pole-mount vibration profile.

**SoC baseline:** **Radxa CM5** (RK3588S — Cortex-A76 4-core +
Cortex-A55 4-core big.LITTLE, 4/8/16 GB LPDDR4X, eMMC on-module).
Radxa offers the industrial-temperature variant of the CM5 (−20…+85 °C
grade) which matches the IP67-cabinet thermal envelope; the
consumer-grade module is the drop-in for mild-climate deployments.

Rationale:
- Same SO-DIMM connector as the Raspberry Pi CM5, so a baseboard
  built around Radxa CM5 also accepts RPi CM5 (with the device
  tree recompiled). One carrier design, two module options.
- RK3588S is widely second-sourced (Rockchip is one of the few
  merchant SoC vendors with strong domestic semiconductor
  availability across the target regions).
- RK3588S ships with mainline Linux kernel support; Debian and
  Yocto both build without vendor forks.
- For safety-role wayside (interlocking + consensus), the A55
  little cluster is pinned to the safety partition and runs Hubris
  or seL4; the A76 big cluster carries non-safety services
  (telemetry, diagnostics) under PREEMPT_RT Linux. The two
  clusters share the memory controller but are scheduled on
  separate cores with cache-partitioning hints from the kernel.
- For non-safety sites (balise reader, energy site) the same
  module runs Debian straight-through.

Why not the RPi CM5 for wayside too: Raspberry Pi publishes a
narrower industrial-temp range than Radxa (commercial
0…+50 °C vs Radxa's industrial +85 °C upper). Pole-mount cabinets
in MENA / sub-Saharan routes routinely hit cabinet internals
above +60 °C at midday; Radxa's variant has the margin.

**Peripherals (baseboard, one SKU fits all wayside roles):**

| Peripheral | Qty | Purpose |
|---|---|---|
| TSN Ethernet | 2 | WAY-E A/B (redundant) |
| RS-485 | 4 | Switch-machine motor drive, level-crossing barrier, HABD sensor bus, balise reader I/F |
| Isolated DI | 8 | Switch end-of-travel sensors (A+B), crossing strike detectors, field-fault inputs |
| Isolated DO | 4 | Motor directional contactors, crossing barrier lift/drop |
| 4-wire PT100 | 4 | Hot-axle IR temperature measurement |
| 802.11ax AP | 1 | Depot maintenance console only; disabled in revenue service by default |
| Dual 24 V DC-in | 2 | Primary + backup site supplies |
| ATECC608 SE | 1 | Trust anchor |

The same baseboard populates selectively: a switch site leaves the
PT100s unpopulated; a HABD site leaves the switch-driver DOs
unpopulated. One SKU, one spares stock, one support burden — the
simplicity bet pays off in the depot.

**Target BOM:** €280 per board, €550 with IP67 enclosure and
mounting hardware.

**Form factor:** 120 × 80 mm, inside a DIN-rail-mountable aluminium
extrusion with IP67 M12 penetrations. Conduction-cooled to the
enclosure.

## 7. Class S-SBC — Station / Depot

**Role:** Hosts `osr-psd`, `osr-pis-station`, `osr-station-scada`,
`osr-afc`, `osr-tvm`. Deployed indoors; no rail-industry environmental
rating required.

**SoC baseline:** Raspberry Pi **CM5** on a commodity carrier (e.g.
Waveshare CM5-IO). No custom baseboard needed — the station
enclosure carries the I/O. This explicitly deviates from the other
classes; indoor environments don't require the custom engineering.

**Peripherals (commodity carrier):**

- 2 × Gigabit Ethernet (one to station LAN, one to PSD/gate network)
- 4 × USB 3.0 for QR scanner, NFC reader, receipt printer, TVM bill
  acceptor
- HDMI for the passenger-facing display
- USB-C console
- ATECC608 on a small add-on board (I²C)

**Target BOM:** €130 per complete station-role SBC, including the
CM5 and the add-on SE board.

## 8. Manufacturing envelope

Every reference PCB respects these constraints so that a tier-2 fab
in any target region can produce it:

| Constraint | Value | Source |
|---|---|---|
| Layer count | 4 | Lowest yield-loss tier. |
| Trace / space | 0.15 mm / 0.15 mm | Routine at tier-2 fabs (6 mil). |
| Minimum via | 0.3 mm drilled, 0.55 mm annular ring | No micro-vias. |
| Aspect ratio | ≤ 8:1 | Standard. |
| Min hole-to-pad | 0.2 mm | Standard. |
| Passive minimum | 0402 | Hand-reworkable, SMT-line friendly. |
| BGA | ≤ 0.8 mm pitch, escape on 4 layers | CM5 module uses 0.65 mm BGA internally but exposes a SO-DIMM connector — no direct BGA escape needed on our baseboards. |
| SMT line min width | 10 mm component edge-to-edge | Fits on any SMT line with ≥ 0.5 m conveyor. |
| Conformal coating | Acrylic (MG Chemicals 419) | Single-can hand coating acceptable for low volume; dip-coat line at high volume. |

**Nothing on the BOM requires any restricted-export component.** Every
part is a catalog item at Mouser/Digi-Key/LCSC. Local second-source
is identified for every component in the Phase 3 procurement RFC
(out of scope for this doc).

## 9. Reliability envelope

| Class | MTBF target | MDBF target | Notes |
|---|---|---|---|
| T-ECU/S | ≥ 200 000 h | ≥ 500 000 km | Safety role — bigger than the rest. Figure taken from EN 50126 for on-vehicle SIL-4 nodes. |
| T-ECU/A | ≥ 100 000 h | ≥ 200 000 km | Single-redundant; failure is a comfort / diagnostic issue, not a safety issue. |
| W-SBC | ≥ 150 000 h | n/a | Ten years of unattended pole-mount operation is the minimum acceptable. |
| S-SBC | ≥ 50 000 h | n/a | Indoor environment; consumer-grade components acceptable. |

Derating rules per Telcordia SR-332 Issue 4: thermal derate all
active devices to ≤ 80 % of rated junction temperature at worst-case
ambient plus 10 °C margin.

## 10. Pitfalls and decisions

These were flagged during planning — they're recorded here so the
implementation session doesn't rediscover them.

- **Two RP2350s on T-ECU/S, not one safety MCU with internal
  lockstep.** Rule 3.3 of RFC 0005 requires SIL-4 code not to
  depend on SIL-2 code at runtime. Internal lockstep on a single
  die is a single-vendor claim; two physically-separate RP2350s
  cross-checking over an external SPI link are independently
  verifiable. The €2.20 BOM cost for two chips is trivial; the
  cross-domain auditability is worth orders of magnitude more in
  the safety case. Future v2 can move one of the two RP2350s to
  its Hazard3 RISC-V cores for genuine ISA-diverse redundancy
  without a BOM change.
- **RPi CM5 for consumer-grade hosts, Radxa CM5 for
  industrial-grade hosts.** T-ECU/A and S-SBC use RPi CM5; W-SBC
  uses Radxa CM5 for its wider industrial temp range. Both are
  SO-DIMM compatible, so a baseboard designed for either accepts
  the other with a device-tree swap. Operators in mild climates
  can single-source RPi CM5; operators in hot climates spec
  Radxa CM5 everywhere if they'd rather single-source the other
  way. The palette is two vendors only, by policy.
- **No custom ASICs.** An OpenSourceRail-branded silicon die is
  explicitly out of scope for v1 and v2. The cost is borne by
  accepting some commodity-module markup; the benefit is zero
  ASIC design NRE and a three-year faster path to first deployment.
- **No NXP / ST / MilkV / StarFive on the BOM.** Earlier drafts
  of this RFC used NXP S32K344 + i.MX 93 for the safety board and
  MilkV Jupiter for wayside. The two-vendor-only restriction
  (§3 constraint 3) replaced those with the RPi + Radxa palette
  above. The previous choices were technically sound; the new
  palette trades a small amount of safety-MCU certifiability for
  dramatic procurement simplicity and a tighter alignment with
  the two vendors' multi-year support commitments.
- **Conformal coating is mandatory.** Rail environments are humid,
  dusty, and occasionally sprayed. Every production board ships
  coated; lab samples for development use are coated *before*
  integration testing, not after, to catch solder-mask defects
  early.
- **No fans.** Fan bearings are a top-quartile failure mode in
  trackside equipment. Every reference design is conduction-cooled
  to its enclosure. Thermal headroom is the binding constraint, not
  CPU performance.
- **Isolation on every external I/O.** Digital I/O that leaves the
  board crosses a galvanic barrier. This is an EMC + safety bet:
  one lightning surge at the wayside must not take out a pole-mount
  W-SBC via an unpowered sensor line.

## 11. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | Bring-up board for each class on vendor dev kits (RPi CM5 dev kit, Radxa CM5 dev kit, Raspberry Pi Pico 2 — which carries the RP2350) — validate software boots and all peripherals enumerate. Runbook procedures committed at [`docs/hardware/bring-up/`](../hardware/bring-up/) (done 2026-04-22) | — |
| **v2** ✅ (spec) | Board-level specifications for every host class: T-ECU/S at [`hardware/t-ecu-s/schematics/v2-spec/`](../../hardware/t-ecu-s/schematics/v2-spec/) (done 2026-04-22), T-OBS at [`hardware/t-obs/schematics/v2-spec/`](../../hardware/t-obs/schematics/v2-spec/) (done 2026-04-22), T-ECU/A at [`hardware/t-ecu-a/schematics/v2-spec/`](../../hardware/t-ecu-a/schematics/v2-spec/), W-SBC at [`hardware/w-sbc/schematics/v2-spec/`](../../hardware/w-sbc/schematics/v2-spec/), S-SBC at [`hardware/s-sbc/schematics/v2-spec/`](../../hardware/s-sbc/schematics/v2-spec/) (all done 2026-04-23). Each covers block diagram, power budget, connector tables, and (for SIL-4 boards) safety-nets. KiCad capture + gerbers + BOM are custom-board deliverables under CERN-OHL-S v2, not prerequisites for an RFC 0019 pilot build. | v1 |
| **v3** | Compliance-test campaign for T-ECU/S (EN 50155 OT4, IEC 61373 Cat 1B, EN 50121-3-2) on one v2 prototype | v2 |
| **v4** | Quantity-100 procurement package published — canonical BOM with Mouser / Digi-Key / LCSC lines, pick-and-place + stencil files, assembly drawings | v2 |
| **v5** | First-article approval by the Samawah reference operator (or equivalent pilot) | v4, RFC 0003 |

**This RFC's v0 deliverable is only the plan.** Every later phase is
a dedicated piece of work owned by the hardware working group. The
session that implements v1 starts by ordering three dev kits —
Raspberry Pi Pico 2 (RP2350), Raspberry Pi CM5 IO Board, and Radxa
CM5 IO Board — and boots the relevant Rust crates on each: the
onboard safety stack on a pair of Pico 2 boards, the onboard app
stack on RPi CM5, and `osr-consensus` + `osr-interlocking` +
`osr-wayside-points` on Radxa CM5. The sim already runs every crate
without hardware, so the bring-up is a migration, not a redesign.

## 12. Relationship to existing work

- **Software stays unchanged.** Every crate in `crates/` is designed
  to be hardware-agnostic Rust. The reference designs here are the
  first *physical* host; a second or third SoC family is additive,
  not breaking, so long as it exposes the same TCN-E / CAN-FD / GPIO
  surface specified in §§4–7.
- **`hardware/` directory.** The top-level directory now carries one
  subdirectory per class, board-level v2 specifications where
  available, RFC 0019 DIY assembly docs, and an explicit
  [`hardware/release-checklist.md`](../../hardware/release-checklist.md)
  with separate pilot-integration and custom-board fabrication gates.
  A class is only pilot-ready after the integration gate is closed, and
  only fabrication-ready after the custom-board gate is closed.
- **Licensing.** All hardware designs under CERN-OHL-S v2 per
  [ARCHITECTURE.md §9](../ARCHITECTURE.md#9-roadmap). Documentation
  (this RFC) under CC-BY-SA 4.0. Firmware ports of existing crates
  keep their Apache-2.0 origin.

## 13. Open questions

1. **Does the 2oo2 RP2350 pattern need an independent
   type-approval?** Unlike internal lockstep silicon, the 2oo2
   claim is a system-level argument that lives in the safety case.
   Our line is that an operator runs per-deployment type approval
   on the full T-ECU/S board anyway; the silicon-level
   certificate becomes a building block of the board certificate.
   Open: does this match EN 50129 appendix D's expectations for
   diverse redundancy? Resolve during v3 compliance-test planning.
2. **ISA-diverse 2oo2 — when does it land?** RP2350 can boot either
   Arm M33 or Hazard3 RISC-V. Running the two chips on different
   ISAs (identical Rust source, two different codegen back-ends)
   strengthens the diversity argument against common-mode compiler
   bugs. Not a v1 goal; track for v2 after the baseline 2oo2 is
   in service.
3. **Which balise protocol?** RFC 0003 proposed passive 27 MHz
   transponders; the safety board's footprint reserves a PN5180 NFC
   front-end (13.56 MHz) for now. Committing the passive-balise
   frequency band is a deployment-level choice — different
   operators have different RFID-spectrum allocations.
4. **How does the energy-site W-SBC physically interface to the
   PV inverter and BESS?** Modbus-TCP over an isolated Ethernet
   segment is the RFC 0002 v1 assumption; the same 4-port wayside
   baseboard already has it.
5. **Repairability requirement.** Should the target markets demand
   a specific MTTR (mean time to repair) at the field level? A
   5-minute module swap is the baseline the DIN-rail + M12
   strategy enables; whether that's sufficient for a country's
   availability SLA is a per-deployment conversation.

## 14. Done criteria

- [x] Every class's SoC and SoM pick is justified (§§4–7)
- [x] One baseboard per class, with a peripheral count (§§4–7)
- [x] Manufacturing envelope fits a tier-2 fab (§8)
- [x] Reliability targets allocated per class (§9)
- [x] Pitfalls and alternatives captured (§10)
- [x] Rollout ordered and scoped (§11)
- [x] Relationship to existing software + licensing named (§12)

The next session picks up at **v1 — bring-up boards on vendor
carriers**. The expected sequence is (a) order the three dev kits,
(b) bring up the Rust stack on each, (c) validate peripherals against
this RFC's §§4–7, (d) file v1 deliverable as a `hardware/` folder
update.
