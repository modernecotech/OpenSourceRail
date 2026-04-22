# T-OBS v2 schematic specification

**Status:** RFC 0015 v3 deliverable — scaffold only. Full spec
lands with the T-OBS v2 milestone (alongside KiCad capture for
T-ECU/S and W-SBC at RFC 0007 v3).

## Scope

This folder holds the board-level spec (net list, pinouts,
power budget, safety-net routing rules) for the **T-OBS v2**
obstacle-detection ECU per [RFC 0015
§5.2](../../../../docs/rfcs/0015-driverless-operation.md) and
[RFC 0007 §5.5](../../../../docs/rfcs/0007-hardware-reference-designs.md).

## Expected file set

Mirroring the T-ECU/S v2 template:

- `block-diagram.md` — functional block diagram.
- `power-budget.md` — rail-by-rail current draw + headroom.
- `pinout-rp2350-a.md` + `pinout-rp2350-b.md` — safety MCU
  pins.
- `pinout-cm5.md` — application processor pins.
- `connector-tables.md` — external connector pinouts.
- `safety-nets.md` — safety-critical net list with clearance
  + routing rules.
- `sensor-interfaces.md` — per-sensor interface spec
  (ultrasonic AFE, radar CAN-FD, LIDAR 1000BASE-T, camera MIPI-
  CSI).
- `deviations-log.md` — DRC + manual checks for the board
  revision.

## v3 rollout

Per RFC 0015 §11 v3: this folder fills in concurrently with the
T-ECU/S v2 KiCad capture, since the two boards share the 2×
RP2350 + CM5 architecture and most of the safety-nets pattern.
The obstacle-detect adds sensor-front-end circuitry (analog
ultrasonic, LIDAR Ethernet, radar CAN-FD) that T-ECU/S does not
carry.
