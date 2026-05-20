# T-ECU/A — Train Application

**Role:** Host for the SIL-2 / SIL-0 onboard crates —
[`osr-ato`](../../crates/osr-ato/), [`osr-tcms`](../../crates/osr-tcms/),
[`osr-dmi`](../../crates/osr-dmi/), [`osr-pis-onboard`](../../crates/osr-pis-onboard/),
[`osr-hvac`](../../crates/osr-hvac/), [`osr-lighting`](../../crates/osr-lighting/),
[`osr-aux-power`](../../crates/osr-aux-power/),
[`osr-event-recorder`](../../crates/osr-event-recorder/),
[`osr-regen`](../../crates/osr-regen/), [`osr-hot-axle`](../../crates/osr-hot-axle/),
[`osr-cbm-onboard`](../../crates/osr-cbm-onboard/),
[`osr-t2g`](../../crates/osr-t2g/), [`osr-tcn`](../../crates/osr-tcn/).

Canonical `light-metro-3car` fit: **2 boards per trainset**, one in
the A-end electronics cabinet and one in the B-end electronics
cabinet. T-ECU/A is single-redundant and non-safety; the T-ECU/S +
T-OBS safety chain continues without it.

**Environment:** EN 50155 OT4, single-redundant.

## SoC

Raspberry Pi **CM5** (BCM2712, Cortex-A76 4-core, 4–16 GB LPDDR4X,
eMMC on-module) on a custom baseboard. **Radxa CM5** (RK3588S) is
the pin-compatible drop-in via the same SO-DIMM footprint — only
the device-tree blob changes. Operators may source whichever module
is locally stocked.

See [RFC 0007 §5](../../docs/rfcs/0007-hardware-reference-designs.md#5-class-t-ecua-train-application).

## Peripherals

| Peripheral | Qty | Purpose |
|---|---|---|
| TSN Ethernet | 2 | TCN-E A/B |
| CAN-FD | 2 | HVAC + lighting |
| USB-C host+device | 2 | Depot console + diag loader |
| HDMI | 1 | DMI touchscreen |
| USB 2.0 | 2 | DMI touch, PIS display |
| M.2 2280 NVMe | 1 | Event recorder + OTA staging |
| M.2 2230 Cat.22 5G | 1 | TRG-1 primary radio |
| LoRa SX1276 on SPI | 1 | TRG-2 backup radio |
| SPI bridge to T-ECU/S | 1 | One-way feed from the safety board |
| ATECC608B SE | 1 | Trust anchor |

## Form factor

160 × 100 mm Eurocard (same DIN slot as T-ECU/S). Heatsink → enclosure
conduction cooling, no fans.

## Target BOM

~€220 per board (CM5 ≈ €85, baseboard ≈ €75, radios ≈ €60).
The consist-level procurement quantity is tracked in
[`../rolling-stock-integration.md`](../rolling-stock-integration.md)
and line E2 of the rolling-stock BOM.

## Status

- `schematics/v2-spec/` — board-level v2 specification overview and
  block diagram.
- `gerbers/` — pending KiCad layout release.
- `bom/` — pending board BOM release.

DIY bring-up on a stock RPi CM5 IO Board + Waveshare M.2 HAT +
generic Cat.22 5G M.2 module validates peripheral enumeration before
the custom baseboard is drawn.
