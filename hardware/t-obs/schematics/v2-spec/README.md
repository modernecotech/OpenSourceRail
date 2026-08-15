# T-OBS v2 schematic specification

**Status:** v2 board-level specification. KiCad capture, gerbers,
and board BOM are the next release artifacts.

## Scope

This folder holds the board-level spec (net list, pinouts,
power budget, safety-net routing rules) for the **T-OBS v2**
obstacle-detection ECU per [RFC 0015
§5.2](../../../../docs/rfcs/0015-driverless-operation.md) and
[RFC 0007 §5.5](../../../../docs/rfcs/0007-hardware-reference-designs.md).

Canonical `light-metro-3car` fit is **2 T-OBS modules per
trainset**, one behind each cabless nose cowl. The consist quantity
is mirrored in [`../../../rolling-stock-integration.md`](../../../rolling-stock-integration.md)
and BOM line E18.

## Expected file set

Mirroring the T-ECU/S v2 template:

- `block-diagram.md` — functional block diagram.
- `power-budget.md` — rail-by-rail current draw + headroom.
- `pinout-rp2350.md` — safety MCU A+B pins.
- `connector-tables.md` — external connector pinouts.
- `safety-nets.md` — safety-critical net list with clearance
  + routing rules.

## Next release artifacts

The KiCad capture should create the downstream `v2-kicad` folder,
gerbers under `hardware/t-obs/gerbers/v2-rev-A/`, and a board BOM
under `hardware/t-obs/bom/v2-rev-A.csv`. Any schematic/layout
deviation from this spec should be logged beside those release
artifacts.
