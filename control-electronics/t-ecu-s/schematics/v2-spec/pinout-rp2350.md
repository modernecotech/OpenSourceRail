# T-ECU/S v2 — RP2350 pin allocation (per channel)

Both RP2350 A (U10) and RP2350 B (U11) share an identical
pinout — this is the 2oo2 composite fail-safe requirement.

RP2350 package: QFN-60, GPIO0..GPIO29 + 3 system pins.

## Allocation

| Pin | Function | Direction | Notes |
|---|---|---|---|
| GPIO0 | CAN0 CAN-FD TX | OUT | to MCP2562FD #1 |
| GPIO1 | CAN0 CAN-FD RX | IN | from MCP2562FD #1 |
| GPIO2 | CAN0 STB (standby) | OUT | |
| GPIO3 | CAN1 CAN-FD TX | OUT | to MCP2562FD #2 |
| GPIO4 | CAN1 CAN-FD RX | IN | |
| GPIO5 | CAN1 STB | OUT | |
| GPIO6 | SPI0 CLK — IMU (BMI088 A/B CS) | OUT | shared field input |
| GPIO7 | SPI0 MOSI — IMU | OUT | |
| GPIO8 | SPI0 MISO — IMU | IN | |
| GPIO9 | SPI0 CS — IMU A (on RP2350 A) / IMU B (on RP2350 B) | OUT | Separate CS so each RP2350 reads independent samples from the same IMU |
| GPIO10 | SPI1 CLK — cross-check link | OUT/IN | Isolated via ADuM1401 |
| GPIO11 | SPI1 MOSI — cross-check | OUT/IN | |
| GPIO12 | SPI1 MISO — cross-check | IN/OUT | |
| GPIO13 | SPI1 CS — cross-check (A drives CS to B, and vice versa; HW-arbitrated master/slave) | OUT/IN | |
| GPIO14 | SPI2 CLK — ATECC608B + PT100 ×4 | OUT | MAX31865 × 4 + ATECC608B |
| GPIO15 | SPI2 MOSI — ATECC608B + PT100 | OUT | |
| GPIO16 | SPI2 MISO — ATECC608B + PT100 | IN | |
| GPIO17 | SPI2 CS — ATECC608B | OUT | |
| GPIO18 | SPI2 CS — PT100 1 | OUT | Battery-bay temp |
| GPIO19 | SPI2 CS — PT100 2 | OUT | Traction-bay temp |
| GPIO20 | SPI2 CS — PT100 3 | OUT | HVAC-plenum temp |
| GPIO21 | SPI2 CS — PT100 4 | OUT | Enclosure ambient |
| GPIO22 | Isolated DI 1 (from ADuM-isolator A side) | IN | Emergency plunger |
| GPIO23 | Isolated DI 2 | IN | Deadman handle |
| GPIO24 | Isolated DI 3 | IN | Cab-door switch A |
| GPIO25 | Isolated DI 4 | IN | Cab-door switch B |
| GPIO26 | Isolated DI 5 | IN | Depot enable |
| GPIO27 | Isolated DI 6 | IN | Park-brake request |
| GPIO28 | Isolated DI 7 | IN | Fire-suppress manual |
| GPIO29 | Isolated DI 8 | IN | Coupler-electric handshake |

**Note:** all 8 DIs land on both RP2350 A and RP2350 B pins —
the ADuM isolator bank has A-side + B-side outputs for every
input.

## Peripherals not on GPIO (dedicated pins)

| Pin name | Function | Notes |
|---|---|---|
| PIO0[0..3] | Tachometer-1 quadrature | 4-pin PIO state machine for quad decode |
| PIO0[4..7] | Tachometer-2 quadrature | |
| UART0 TX/RX | Debug console to external USB-UART | Shared A+B via header J10 (selector jumper) |

Tachometer inputs use RP2350's PIO engine — one of the few
places where a fixed-function peripheral is insufficient for
full rail tachometer decoding at 50 kHz pulse rates.

## Outputs to the 2oo2 AND stage

The four "safety outputs" go to the external 2oo2 relay stage
(K1 / K2):

| Net | Driven by | Destination |
|---|---|---|
| `EB_DRIVE_A` | RP2350 A | 2oo2 AND stage input A, then to EB relay K1 |
| `EB_DRIVE_B` | RP2350 B | 2oo2 AND stage input B, then to EB relay K1 |
| `TRACTION_CUT_A` | RP2350 A | 2oo2 AND stage → traction-cut relay K2 |
| `TRACTION_CUT_B` | RP2350 B | 2oo2 AND stage → traction-cut relay K2 |
| `PARK_DRIVE_A` | RP2350 A | separate relay, single-channel (park brake is fail-safe-apply so no 2oo2 needed) |
| `PARK_DRIVE_B` | RP2350 B | separate relay, single-channel (redundant for availability) |
| `FIRE_SUPPRESS_A` | RP2350 A | 2oo2 → fire suppression trigger |
| `FIRE_SUPPRESS_B` | RP2350 B | 2oo2 → fire suppression trigger |

The "safety output driver" per channel is a high-side switch
(NCV8202 or equiv.) with thermal shutdown and over-current
detection; the supervisor IC monitors its status pin.

## Pin planning notes for the PCB designer

- Every cross-channel signal (`*_A` vs `*_B`) must route with
  ≥ 1.5 mm separation to avoid capacitive coupling from one
  channel to the other.
- The cross-check SPI is the one exception — it's *intentionally*
  routed A ↔ B but through the ADuM1401 galvanic isolator, so
  the physical routing goes A-side → isolator → B-side.
- All four CAN buses use differential signalling; route the
  diff pair with matched length at the 7 mm pair-offset rule.
- Decouple every RP2350 VDD pin with 100 nF + 10 µF ceramic.

## What this file does NOT specify

- Exact package variants (QFN vs BGA — QFN standard).
- Trace widths (layout EEE — follow class rules in
  `block-diagram.md` §Net classification).
- Crystal oscillator (both RP2350s use their internal ROSC — no
  external crystal required for this application).
