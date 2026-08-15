# T-ECU/S — Train Safety Kernel

**Role:** Host for the SIL-4 onboard crates — [`osr-atp`](../../crates/osr-atp/),
[`osr-odometry`](../../crates/osr-odometry/), [`osr-brake`](../../crates/osr-brake/),
[`osr-bms`](../../crates/osr-bms/),
[`osr-fire-safety`](../../crates/osr-fire-safety/),
[`osr-derailment`](../../crates/osr-derailment/),
[`osr-door-control`](../../crates/osr-door-control/),
[`osr-traction`](../../crates/osr-traction/) (MCU bring-up only).

Canonical `light-metro-3car` fit: **2 boards per trainset**, one in
the A-end electronics cabinet and one in the B-end electronics
cabinet. The train-level role is one primary + one hot-standby per
consist; neither unit depends on a driver cab being present.

**Environment:** EN 50155 OT4 (−40…+85 °C), IEC 61373 Cat 1 Class B,
EN 50121-3-2 EMC.

## 2-out-of-2 composite fail-safe

Each T-ECU/S board carries **two Raspberry Pi RP2350 MCUs** in a
2oo2 voting arrangement. Both chips receive the same sensor inputs
on separate pins, both run identical Rust `no_std` code, both
outputs are AND-gated through an external 2oo2 relay network. Each
tick they cross-check their computed safety decisions over SPI; on
mismatch, both chips fail-safe open and a hardware watchdog asserts
the emergency brake relay directly.

See [RFC 0007 §4.1](../../docs/rfcs/0007-hardware-reference-designs.md#41-safety-architecture--2oo2-composite-fail-safe)
for the rationale against a single-vendor lockstep MCU.

## SoC picks

- **Safety MCU × 2:** Raspberry Pi **RP2350**. Dual Cortex-M33 +
  dual Hazard3 RISC-V in the same die, 520 KB SRAM, 150 MHz,
  TrustZone-M, HW RNG. ~€1.10 in 1k volume. QFN-56 0.4 mm pitch —
  routine SMT.
- **App processor × 1:** Raspberry Pi **CM5** (BCM2712). Hosts
  TCN-E, logging, OTA, event recorder — never on the safety path.
  Subscribes to a one-way SPI feed from the RP2350 pair.

## Peripherals

| Peripheral | Qty | Purpose |
|---|---|---|
| CAN-FD | 4 | Door, brake, traction, BMS (each on both RP2350s) |
| TSN Ethernet (CM5 + KSZ9031 PHY) | 2 | TCN-E A/B |
| Isolated DI | 8 | Plunger, cab, depot enable, deadman (routed to both RP2350s) |
| Isolated DO | 4 | EB relay, traction cut, park, fire (via 2oo2 relay stage) |
| Tach inputs (quadrature 5–24 V) | 2 | Wheel encoders (both RP2350s) |
| Bosch BMI088 IMU | 1 | Derailment + odometry, SPI (both RP2350s) |
| u-blox NEO-F10N GNSS | 1 | UART to CM5 |
| PN5180 NFC balise reader | 1 | SPI to CM5 |
| PT100 thermistors | 4 | Battery, traction, HVAC, ambient |
| Microchip ATECC608B SE | 2 | Trust anchor per RP2350 |

## Form factor

160 × 100 mm Eurocard, DIN-rail mount, conduction-cooled. No fans.
Conformal-coated (MG Chemicals 419) before integration. IP54.

## Target BOM (volume 100+)

~€280 per board. Two boards per trainset = €560 for the safety
kernel layer. The consist-level procurement quantity is tracked in
[`../rolling-stock-integration.md`](../rolling-stock-integration.md)
and line E1 of the rolling-stock BOM.

## Status

- Pilot / DIY track: [`diy-assembly/`](diy-assembly/) uses two
  Raspberry Pi Pico 2 boards (each carrying one RP2350) in a 2oo2
  test jig, plus a stock RPi CM5 IO Board for the app processor.
  Boots `osr-atp` + `osr-brake` + `osr-odometry` + the SPI
  cross-check harness. Integration evidence is still pending.
- Custom-board track: `schematics/v2-spec/` is the board-level v2
  specification: block diagram, power budget, connector tables,
  CM5/RP2350 pinouts, and safety-net rules. `gerbers/` and `bom/`
  remain pending until a KiCad layout and board BOM are released.
