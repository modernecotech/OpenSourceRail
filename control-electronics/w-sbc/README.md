# W-SBC — Wayside

**Role:** Host for [`osr-consensus`](../../crates/osr-consensus/),
[`osr-interlocking`](../../crates/osr-interlocking/),
[`osr-wayside-points`](../../crates/osr-wayside-points/),
[`osr-level-crossing`](../../crates/osr-level-crossing/),
[`osr-hot-axle-wayside`](../../crates/osr-hot-axle-wayside/),
[`osr-balise`](../../crates/osr-balise/) (reader side),
[`osr-energy-site`](../../crates/osr-energy-site/).

Deployed in pole-mounted IP67 cabinets along the corridor and at
junctions.

**Environment:** IP67, EN 50121-4 EMC, −40…+70 °C.

## SoC

**Radxa CM5** (RK3588S — Cortex-A76 4-core + Cortex-A55 4-core
big.LITTLE, 4/8/16 GB LPDDR4X, eMMC on-module) on a custom
baseboard. Radxa's **industrial-temperature** variant (−20…+85 °C
rated) is the baseline; pole-mount cabinets in hot climates
routinely hit +60 °C internal, so the extra margin over the
consumer-grade CM5 matters.

Raspberry Pi CM5 is the pin-compatible drop-in on the same SO-DIMM
slot for mild-climate deployments.

For safety-related wayside logic, the CM5 hosts application, diagnostics and
communications only. A separately qualified controller owns field proving,
watchdogs and fail-safe actuator outputs; see the
[selection gate](../safety-controller-selection.md). Core pinning or a
separation kernel on a shared SBC is defence in depth, not a SIL-4 boundary.
Non-safety sites (balise-only, energy-site) run Debian
straight-through.

See [RFC 0007 §6](../../docs/rfcs/0007-control-electronics-reference-designs.md#6-class-w-sbc-wayside).

## Peripherals — one SKU fits every wayside role

| Peripheral | Qty | Role |
|---|---|---|
| TSN Ethernet | 2 | WAY-E A/B |
| RS-485 | 4 | Switch motor, crossing barrier, HABD bus, balise reader |
| Isolated DI | 8 | Switch end-of-travel (A+B), strike detectors, field faults |
| Isolated DO | 4 | Motor direction contactors, barrier lift/drop |
| 4-wire PT100 | 4 | Hot-axle IR temperature |
| 802.11ax AP | 1 | Depot maintenance (disabled in service) |
| Dual 24 V DC-in | 2 | Primary + backup site supplies |
| ATECC608B SE | 1 | Trust anchor |

Selective population per role — switch site leaves PT100 inputs
unpopulated, HABD site leaves motor-direction DOs unpopulated. One
SKU, one spares stock.

## Form factor

120 × 80 mm PCB inside an IP67 aluminium extrusion with M12
penetrations. Conduction-cooled.

## Target BOM

~€280 per board, ~€550 with enclosure + mounting hardware.

## Status

- Pilot / DIY track: [`diy-assembly/`](diy-assembly/) uses the Radxa
  CM5 IO Board + a SparkFun RS-485 breakout to validate the
  `osr-consensus` + `osr-interlocking` + `osr-wayside-points` stack
  on a real RK3588S module. Integration evidence is still pending.
- Custom-board track: `schematics/v2-spec/` is the board-level v2
  specification overview and block diagram. `gerbers/` and `bom/`
  remain pending until a KiCad layout and board BOM are released.
