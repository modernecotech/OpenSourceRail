# S-SBC v2 schematic specification

**Status:** RFC 0007 v3 deliverable. Specification for the
station / depot SBC per [RFC 0007 §7](../../../../docs/rfcs/0007-control-electronics-reference-designs.md).

## Scope

S-SBC hosts the station-tier and depot-tier crates, all SIL-2
or SIL-0 — station operation is not safety-critical because
passenger safety on the platform is delegated to PSDs (SIL-4
hardware at the door itself) + station-staff supervision per
RFC 0013 T2, with the interlocking handling train-side safety
autonomously.

- `osr-psd` — PSD controller (SIL-2 logic; the SIL-4 mechanical
  interlock is inside each PSD unit).
- `osr-station-scada` — station SCADA / HMI.
- `osr-pis-station` — passenger-information displays.
- `osr-afc` — automatic fare collection logic.
- `osr-tvm` — ticket-vending-machine controller.
- `osr-historian` — metric ring-buffer storage (when station
  hosts a regional historian).
- `osr-cbm-backend` — deployment-side CBM for depot-adjacent
  S-SBCs.

At depots, the S-SBC also hosts the depot-automation crate that
orchestrates overnight trainset movements (stall allocation,
charging-pad assignment, pre-service brake tests).

## SoC

**Raspberry Pi Compute Module 5 (BCM2712)** on a commodity
carrier — no custom baseboard required.

- 4-core Cortex-A76, 4–16 GB LPDDR4X.
- eMMC on-module.
- Wide availability, mature Linux, broad spares pool in target
  deployment markets.

S-SBC stays on the RPi CM5 (not Radxa RK3588S industrial) because
station cabinets are temperature-controlled — the commercial OT3
temperature grade is sufficient indoors. For outdoor TVMs in
extreme climates, deploy a Radxa CM5 drop-in replacement under
the same carrier pinout (§3.2 of RFC 0007).

## Architecture

Non-safety, non-redundant per station. Typical station carries
**one S-SBC** with cold-spare kept at the depot. If a station's
S-SBC fails:

- PSDs lock open (fail-safe for passenger egress) per
  `osr-psd`'s PSD-controller contract.
- Fare gates default to open (paid-area unlocked).
- PIS displays show the emergency-only banner.
- OCC dispatches a maintainer per RFC 0013 T5 ticket.

Recovery is swap-in of the cold spare (5–15 minute task per
RFC 0013 M5 depot procedure).

## Peripherals (commodity carrier)

| Peripheral | Qty | Purpose |
|---|---|---|
| Gigabit Ethernet | 2 | Backhaul to W-SBC + OCC; station-local PIS LAN |
| USB 3.0 | 4 | TVMs, fare gates, PSD console |
| HDMI | 2 | Station-master console + PIS display (small stations) |
| MIPI-CSI | 2 | Station-monitoring cameras |
| microSD | 1 | Boot image (eMMC is primary) |
| ATECC608B (optional) | 1 | Trust anchor for station-originated consensus entries (e.g., PSD-state) |
| 12/24 V DC input | 1 | Either building DC or adapter from 230 VAC mains |

## Power budget

| Rail | Voltage | Max power |
|---|---|---|
| CM5 core + RAM | 5 V | ~10 W |
| USB downstream (TVM, gates) | 5 V | ~8 W (at 2 × TVM idle) |
| Camera MIPI-CSI | 3.3 V | ~1 W |
| Fans, lights | 12 V | deployment-specific |
| **Baseboard total** | — | **~20 W sustained** |

Cooling: natural-convection in a temperature-controlled station
equipment room. Fan-forced air in TVM outdoor kiosks.

## Environment

- Typical: indoor station equipment room, 0–45 °C.
- Outdoor TVM: −10 to +55 °C with sun-shield; consider Radxa
  drop-in for the RK3588S industrial-temp variant if local
  climate is harsher than that.
- IP43 for indoor cabinet, IP65 for outdoor TVM.

## Form factor

Commodity off-the-shelf RPi CM5 IO Board (official Raspberry Pi
carrier) is sufficient for most deployments. A custom low-cost
carrier is v3.1 if a particular deployment wants a single
integrated SKU.

## Target BOM

~€150 per board total (CM5 ≈ €85 + commodity carrier ≈ €65).

## Expected v2-spec file set

- `block-diagram.md` — functional block diagram.
- `power-budget.md` — station + depot power profile.
- `connector-tables.md` — HMI + PIS + fare-gate connector
  pinouts.
- `deviations-log.md` — design-review notes.

No safety-nets.md because S-SBC does not drive any SIL-4
actuator — the PSD SIL-4 interlock is inside the PSD hardware,
not on this board.
