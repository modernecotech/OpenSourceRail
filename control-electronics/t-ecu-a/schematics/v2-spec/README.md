# T-ECU/A v2 schematic specification

**Status:** RFC 0007 v3 deliverable (partial). This folder holds
the board-level specification (net list, pinouts, power budget,
connector tables) for the T-ECU/A v2 application-tier ECU per
[RFC 0007 §5](../../../../docs/rfcs/0007-control-electronics-reference-designs.md).

KiCad capture + gerbers + BOM are v3.1, deferred alongside
T-ECU/S and T-OBS.

## Scope

T-ECU/A hosts the SIL-2 + SIL-0 onboard application crates:

- `osr-ato` — Automatic Train Operation (GoA 4 default).
- `osr-tcms` — Train Control and Management System.
- `osr-event-recorder` — black-box circular storage.
- `osr-tcn` — TSN Ethernet trainbus (RFC 0006).
- `osr-t2g` — train-to-ground radio adapter.
- `osr-regen`, `osr-aux-power`, `osr-hvac`, `osr-lighting` —
  comfort + auxiliary systems.
- `osr-pis-onboard` — passenger information displays.
- `osr-hot-axle` — onboard hot-axle-box advisory (SIL-2).
- `osr-cbm-onboard` — condition-based-maintenance telemetry.

## Architecture

Single-redundant at each end: the standard trainset fit carries
two T-ECU/A units, one behind each nose. Unlike T-ECU/S this is
**not** 2oo2: its crates are non-safety-critical. A failure of one
T-ECU/A degrades comfort (HVAC, lighting, PIS) and costs
diagnostics visibility, but the safety chain (T-ECU/S + T-OBS +
brake relay stage) continues to function.

| Block | Qty | Role |
|---|---|---|
| RPi CM5 / Radxa CM5 | 1 | Application processor (4-core A76, 4–16 GB LPDDR4X) |
| TSN Ethernet switch | 1 | 88E6321 — redundant TCN-E A/B |
| CAN-FD transceivers | 2 | HVAC bus + lighting bus (TCAN1462) |
| 5G modem socket | 1 | M.2 Cat.22 — TRG primary |
| LoRa radio | 1 | SX1276 on SPI — TRG backup |
| NVMe slot | 1 | M.2 2280 for event recorder + OTA staging |
| USB-C | 2 | Depot console + diag loader |
| HDMI | 1 | Commissioning display output |
| ATECC608B | 1 | Trust anchor |
| Power input | 1 (redundant) | 24 V DC from aux bus |

## Power budget (target)

| Rail | Voltage | Load | Max power |
|---|---|---|---|
| CM5 core | 5 V | CM5 + RAM under load | ~12 W |
| 3.3 V | 3.3 V | Ethernet PHY + CAN + ATECC | ~2 W |
| 1.8 V | 1.8 V | MIPI + TSN | ~1 W |
| 5G radio | 5 V | M.2 modem at full tx | ~8 W |
| LoRa | 3.3 V | SX1276 tx | ~0.5 W |
| **Total at 24 V in** | — | — | **~28 W peak, ~18 W sustained** |

Natural-convection cooling. Conduction path to DIN rail chassis
for the CM5 heatsink. No fans.

## Environment

- EN 50155 OT4 (-25 °C to +70 °C with +85 °C 10-minute peak).
- IP54 enclosed; DIN-rail mount.
- Conformal coated (MG Chemicals 419).

## Form factor

160 × 100 mm Eurocard — same footprint as T-ECU/S so a cabinet
slot can host either without re-mounting.

## Target BOM

~€220 per board (CM5 ≈ €85, baseboard ≈ €75, radios ≈ €60
volume).

## Expected v2-spec file set

- `block-diagram.md` — functional block diagram.
- `power-budget.md` — rail-by-rail load + headroom.
- `pinout-cm5.md` — CM5 SO-DIMM pin assignments.
- `connector-tables.md` — external M12 + FFC pinouts.
- `deviations-log.md` — design-review notes.

This README provides the summary; individual files fill in
per-block detail as the v2-spec milestone matures.
