# W-SBC v2 schematic specification

**Status:** RFC 0007 v3 deliverable (partial). Per-board
specification of the wayside SBC per [RFC 0007
§6](../../../../docs/rfcs/0007-control-electronics-reference-designs.md).

## Scope

W-SBC hosts the wayside SIL-4 crates + non-safety energy-site
management:

- `osr-interlocking` — Movement Authority computer (SIL-4).
- `osr-consensus` — Raft log, distributed across 3 W-SBC nodes
  minimum per line.
- `osr-wayside-points` — switch-machine controller (SIL-4).
- `osr-balise` — balise registry + sighting audit (SIL-2).
- `osr-level-crossing` — SIL-4 five-state LX controller.
- `osr-hot-axle-wayside` — SIL-4 HABD at wayside.
- `osr-intrusion-detect` — RFC 0016 wayside intrusion
  evaluator (SIL-4).
- `osr-energy-site` — PV + battery + grid-tie dispatch (SIL-0).

One physical W-SBC may host multiple roles depending on its
location — a junction box near an LX + switch + intrusion pack
runs three SIL-4 crates concurrently.

## SoC

**Radxa CM5 (RK3588S industrial-temp variant)** — Cortex-A76 ×
4 + A55 × 4, 4–16 GB LPDDR5, eMMC on-module. Industrial temp
grade is the important selector — the RPi CM5 BCM2712 is OT3
commercial; the RK3588S-industrial is rated for +85 °C ambient
which is needed for pole-mounted and cabinet-mounted wayside
service in hot climates.

## Architecture

Single-role W-SBC is not 2oo2 at the CPU level; safety redundancy
lives in the **3-node Raft consensus cluster** per line. Any
single W-SBC losing its CPU means the cluster still has quorum.

For safety-critical roles (level-crossing, switch-machine), the
actuator-output stage is still hardware-2oo2 via external relay
stages on the same board: the W-SBC drives both sides of an
external AND-gate exactly like T-ECU/S, even though the
consensus layer provides the cross-CPU redundancy.

## Peripherals (baseboard, selectively populated)

| Peripheral | Qty | Purpose |
|---|---|---|
| TSN Ethernet | 2 | Backbone to adjacent W-SBCs + back-office |
| CAN-FD | 2 | Switch-machine motor drivers, LX barriers |
| Isolated DI | 8 | Fence-line contact sensors, LX inductive loops, SIL-4 switch position |
| Isolated DO | 4 | Relay drives to switch motors + LX barriers |
| 1000BASE-T LIDAR | 1 | ROW-mounted LIDAR (RFC 0016) |
| CAN-FD radar | 1 | ROW-mounted mmWave radar (RFC 0016) |
| MIPI-CSI | 1 | ROW-mounted CCTV camera (optional) |
| GPIO (3.3 V tolerant) | 16 | General I/O — balise triggers, axle-counter inputs |
| PTP PHY | 1 | 1588v2 time sync for consensus cluster |
| M.2 NVMe | 1 | Local log shadow + OTA staging |
| USB-C | 1 | Depot console + OTA |
| 24 V DC input | 2 | Redundant, diode-OR |
| ATECC608B | 1 | Trust anchor — signs SectionIntrusion / SwitchObservation entries |

## Power budget

Depends on populated roles. Bounds:

| Configuration | Sustained | Peak |
|---|---|---|
| Interlocking + consensus only | ~8 W | ~12 W |
| + switch-machine control (one switch) | ~12 W | ~60 W (during throw) |
| + level-crossing control (4 barriers) | ~18 W | ~50 W (during barrier transition) |
| + intrusion-detect (LIDAR + radar + camera) | +14 W | +22 W |
| **Worst-case combined** | **~44 W** | **~90 W** |

Input range 9 – 36 V DC to accommodate both the 24 V wayside
cabinet bus and the 12 V battery-backup mode. An LTC7803 wide-
input buck handles the range.

## Environment

- **Industrial temp:** −40 °C to +85 °C ambient.
- **IP67 enclosure** — pole-mountable; no cabinet required for
  the harsh-climate configuration.
- **EN 50121-4 EMC** compliance for wayside equipment.
- **EN 50125-3** environmental conditions for signalling.
- **Vibration + shock:** IEC 61373 Cat 2 (wayside).
- **Conformal coat:** MG Chemicals 419 before integration.

## Form factor

180 × 130 mm — slightly larger than T-ECU/S to accommodate the
wide 24 V + 12 V PSU and the 8+4 isolated I/O pool. DIN-rail +
pole-mount bracket options. No fans.

## Target BOM

~€340 per board (CM5 ≈ €110 industrial-temp premium, baseboard
≈ €95, I/O isolators ≈ €55, RF + sensor headers ≈ €30, PSU +
passives ≈ €50).

A typical wayside deployment uses three W-SBCs per line as the
minimum Raft quorum; larger networks scale the cluster up as
needed.

## Expected v2-spec file set

- `block-diagram.md` — functional block diagram.
- `power-budget.md` — per-role power profile.
- `pinout-cm5.md` — CM5 SO-DIMM pin assignments.
- `safety-nets.md` — switch-motor + LX actuator safety-critical
  nets with 2oo2 AND-gate relay stages.
- `connector-tables.md` — M12 + terminal-block pinouts.
- `deviations-log.md` — design-review notes.
