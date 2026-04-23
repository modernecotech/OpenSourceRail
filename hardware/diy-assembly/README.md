# DIY plug-and-play assembly — RFC 0019

**Audience:** anyone building an OSR deployment without access
to a PCB-fabrication chain — a municipal authority in a
developing-nation target market, a pilot-scale integrator, a
community project, a university lab building a first-article
board before committing to silicon.

**Outcome after following this cookbook:** every OSR host class
(T-ECU/S, T-ECU/A, T-OBS, W-SBC, S-SBC) running on commodity
modules in DIN-rail enclosures, wired through terminal blocks,
booted off a prepared SD card. No KiCad, no soldering iron,
no hot-air station.

## Contents

- **[`parts-catalogue.md`](parts-catalogue.md)** — every part
  name + SKU + price + distributor used across the five host
  classes.
- **[`tooling.md`](tooling.md)** — the four tools the whole
  build takes (screwdriver, wire cutter/stripper, ferrule
  crimper, micro-HDMI cable for commissioning).
- **[`sd-card-images.md`](sd-card-images.md)** — how to build
  and flash the per-host-class SD-card image (v0.2 will ship
  pre-built images; v0.1 you build from the workspace).
- **[`safety-case-amendment.md`](safety-case-amendment.md)** —
  the three paragraphs to add to the deployment's safety case
  explaining why the DIY integration preserves the RFC 0015 /
  RFC 0016 SIL-4 arguments.

Per-host-class BOMs and wiring maps live under each host
class's folder:

- [`hardware/t-ecu-s/diy-assembly/`](../t-ecu-s/diy-assembly/)
- [`hardware/t-ecu-a/diy-assembly/`](../t-ecu-a/diy-assembly/)
- [`hardware/t-obs/diy-assembly/`](../t-obs/diy-assembly/)
- [`hardware/w-sbc/diy-assembly/`](../w-sbc/diy-assembly/)
- [`hardware/s-sbc/diy-assembly/`](../s-sbc/diy-assembly/)

## Assembly order (any host class)

1. **Prepare the SD card** (~15 min) per
   [`sd-card-images.md`](sd-card-images.md).
2. **Snap enclosure + DIN rail** (~5 min). Each host class
   uses a 25–35 mm DIN-rail mount.
3. **Install compute modules** into the enclosure: RPi
   Pico 2 × 2 (for SIL-4 classes) + CM5 on its IO Board.
   Friction-fit and captive thumbscrews.
4. **Attach HATs** — 40-pin GPIO headers are keyed. Each
   HAT's screws + standoffs secure it.
5. **Wire terminal blocks** per the per-class wiring map.
   Use ferrules on stranded wire; no tinning.
6. **Cable the cross-check SPI** (SIL-4 classes only) via
   the Adafruit USB isolator between the two Pico 2 boards.
7. **Power on.** LEDs on each board confirm self-test pass.
8. **Run `osr-selftest`** — CLI tool on the CM5; exercises
   each crate's health check and reports pass/fail.
9. **Stamp the commissioning log** with the unit's
   unique-id hash + self-test output. This becomes the
   EN 50129 per-unit evidence record.

Total per-unit assembly time: ~90 minutes for an experienced
tech, ~3 hours for a first-time builder.

## Per-trainset total

A light-metro-3car trainset needs:

- **2 × T-ECU/S** (one per cab end) — ~3 hours each
- **2 × T-ECU/A** (one per cab end) — ~2 hours each
- **2 × T-OBS** (nose cowl, each end) — ~3 hours each

**Total: ~16 labour-hours per trainset** of electronics
assembly. A two-person team on a workbench produces one
trainset's electronics in a working day.

## Per-section wayside

A 1-km `standard-urban` section with intrusion-detect
instrumentation needs:

- **1 × W-SBC** at the trackside junction box — ~3 hours
- **Up to 5 × LIDAR pole mounts** (200 m spacing) — plug
  Ethernet + 12 V in, no assembly beyond the housing
- **1 × radar** per 500 m
- **Fence-line sensor run** — civil-scope installation

**Total W-SBC + sensor plug-up per 1-km section:** half a day
per pole, ~1 day per section.

## Licence note

Every commercial SKU referenced in the BOMs is sold under its
vendor's own terms. The OSR project's references to these
SKUs are purely informational — we're telling you what to
buy, not distributing the parts. The deployment partner is
responsible for procurement and their respective vendor
relationships.
