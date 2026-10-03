# RFC 0019 — DIY plug-and-play electronics

**Status:** accepted prototype integration path; hardware and operational qualification open.
**Review:** 3 October 2026 — corrects the April candidate wiring and price assumptions.
**Amends:** [RFC 0007](0007-control-electronics-reference-designs.md).

## 1. Purpose

Commodity modules provide a useful bench and first-article integration path for T-ECU/S, T-ECU/A, T-OBS, W-SBC and S-SBC. A custom PCB is optional for a bench prototype. The accepted path does not release a railway control assembly, a safety integrity level, a complete BOM or a bootable target image.

The detailed [host requirements](../../control-electronics/diy-assembly/README.md), [reference integration source](../../control-electronics/reference-integration.json) and [release checklist](../../control-electronics/release-checklist.md) control the current design stage. Exact supplier, pin, power and environment data must be frozen and tested before an operator can use the hardware.

## 2. Host classes

| Host | Bench reference | Integration work still required |
|---|---|---|
| T-ECU/S | Dual evaluator channels and optional application carrier | External bus controllers, separately protected power/watchdogs, output feedback and real field-input mapping |
| T-ECU/A | CM5-compatible application carrier | Peripheral/modem compatibility, protected power, network/radio and thermal design |
| T-OBS | Dual evaluators, application carrier and sensor candidates | Sensor/harness choice, corrected startup power, timed ingress and measured fault/coverage tests |
| W-SBC | Commodity wayside controller | Cabinet mains/DC/UPS, earthing, field I/O, output and resource-control qualification |
| S-SBC | Commodity station controller | Station services, UPS, network, AFC/PIS/SCADA and degraded-operation design |

## 3. Candidate components and corrected interfaces

Exact order codes, lifecycle, alternates and prices remain unverified in the historical candidate catalogue. Use vendor documentation and a complete board/harness BOM before ordering.

| Earlier assumption | Required correction |
|---|---|
| CM5/CM5IO codes SC1124/SC1125 released as exact selections | Freeze actual memory/storage/carrier variant and vendor order code |
| USB isolator for SPI or two Pico USB-device endpoints | Directionally correct isolated SPI with controller/peripheral roles and separate supplies |
| Native Pico CAN-FD or Ethernet/RMII | External controllers/transceivers and measured bus/deadline budget |
| TPS3701 heartbeat watchdog | Voltage detector only; separate external heartbeat watchdog functions |
| HDR-60-24 powers 5/12 V from a 24 V onboard bus | AC/high-voltage DC input to 24 V output; protected onboard DC/DC branches required |
| ADS1115 captures HC-SR04 digital echo | Timer/PIO capture with voltage conversion; raw piezo requires excitation/receiver AFE |
| Murata raw piezo labelled rail-grade plug-in replacement | Candidate-specific driver, lifecycle and environmental qualification; no rail-grade claim |
| HAP USB/Gigabit/12 V PoE interface | TX uses 100BASE-TX; T1 uses 100BASE-T1; vendor 9–18 V supply/cable separately |
| Relay board proves 2oo2 safety | Bench simulated load only; driver/contact feedback, welded faults and common-cause analysis required |

The CM5 carrier alone has a 25 W input envelope. The T-OBS bench candidate calculation allocates 71.5 W simultaneous output and 99.31 W input capacity with efficiency/margin, selecting a 100 W reference envelope. This is sizing rather than measured sustained consumption; no fuse or converter part is thereby qualified. Exact power and thermal behaviour must be tested on the selected revision.

## 4. Procurement and cost

The former DIY/custom price comparison and host subtotals are withdrawn as complete assembly comparisons. They omitted DC/DC conversion, watchdogs, output feedback, external controllers, harness/connectors, enclosure thermal provisions and qualification. A low-price module does not price the installed system. Keep unknown costs open and reconcile a quoted complete BOM against the city allowance before changing CAPEX or finance.

The [Baghdad detailed register](../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/detail/README.md) allocates reference quantities and Iraqi integration routes for the six-car fleet. These are nested engineering requirements, not additional purchases on top of complete priced assemblies or live ERP Items.

## 5. Assembly and evidence

1. Freeze host/board revision, vendor interfaces, exposed/package pins and supported peripheral resources.
2. Complete load, inrush, protection, isolation, thermal and EMC calculations.
3. Issue a cavity-by-cavity harness, terminal/wire list, enclosure and simulated-load output truth table.
4. Build and inspect a bench unit; measure voltage domains, boot/default outputs, power loss, heartbeat failures, peer faults and contact feedback.
5. Bind actual HAL/drivers, protocol/configuration and signed image to the revision; test stale data, timing, environmental exposure and recovery.
6. Close the appropriate release checklist and independent assessment before any field or train actuation.

[Production SD images remain absent](../../control-electronics/diy-assembly/sd-card-images.md). Software/library tests, the same MCU silicon or a relay schematic do not prove qualified hardware independence. Do not connect a bench assembly to real brake/traction actuators as a result of this RFC.
