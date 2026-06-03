# T-OBS — Train Obstacle Detection

**Role:** Nose-mounted obstacle-detection ECU for cabless GoA 4
operation. Each module fuses ultrasonic transducers, solid-state
LIDAR, mmWave radar, and a stereo camera pair, then sends a
fail-restrictive brake-demand/verdict interface to T-ECU/S.

Canonical `light-metro-3car` fit: **2 modules per trainset**, one
behind the A-end nose cowl and one behind the B-end nose cowl. The
matching mechanical envelope is `trainset-tobs-sensor-pack.png` and
`mechanical-py/src/osr_mech/rolling_stock/systems.py`.

## Architecture

T-OBS mirrors the T-ECU/S safety pattern: two RP2350 safety channels
cross-check each other, while a CM5 performs non-safety sensor
pre-processing and logging. The RP2350 pair owns the final
obstacle-detection safety verdict.

See:

- [`schematics/v2-spec/`](schematics/v2-spec/) for the board-level v2
  schematic specification.
- [`diy-assembly/`](diy-assembly/) for the off-the-shelf first-article
  build.
- [`../rolling-stock-integration.md`](../rolling-stock-integration.md)
  for trainset quantities and BOM alignment.

## Target BOM

The custom-board target is carried by the rolling-stock procurement
BOM as line E18. The DIY first article is sensor-dominated and costs
about `$2.4k` per T-OBS module at single-unit retail.

## Status

- `schematics/v2-spec/` — board-level v2 specification.
- `gerbers/` — empty until KiCad layout is released.
- `bom/` — empty until the v2 board BOM is released.
