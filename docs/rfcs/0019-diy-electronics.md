# RFC 0019 — DIY plug-and-play electronics

**Status:** accepted · 2026-04-23.
**Authors:** OSR project.
**Amends:** [RFC 0007](0007-hardware-reference-designs.md) (hardware
palette). **Complements:** [CHANGELOG.md](../../CHANGELOG.md).

## 1. Purpose

The RFC 0007 v2-spec boards (T-ECU/S, T-ECU/A, T-OBS, W-SBC,
S-SBC) assume a custom PCB captured in KiCad and fabricated
somewhere in the target deployment footprint. That's fine for
volume production, but it is a real barrier for:

- A **pilot deployment** that needs five trainsets, not fifty —
  the NRE of designing + fabricating custom boards dominates
  the total cost.
- A **developing-nation DIY operator** — a city authority in
  (say) the Sahel that wants to run its own metro but doesn't
  have a PCB-design in-house capability.
- **Early academic / community prototypes** that need to run
  the safety chain on commodity hardware before investing in
  silicon.

This RFC defines a **DIY plug-and-play electronics path** for
all five host classes using commercially-available modules
(Raspberry Pi Foundation boards, commodity HATs, off-the-shelf
relay + sensor breakouts). **No custom PCB required for any
host class.** Wiring is terminal-block + ribbon cable; the
assembly-time tool is a screwdriver.

The trade-off is higher per-unit cost (roughly 1.5–2× the custom-
PCB BOM at volume) and slightly larger enclosure footprint. For
pilot deployments that's the right trade — the 10× saving on NRE
dominates.

## 2. Design principles

1. **Off-the-shelf only.** Every component has a public SKU at
   ≥ 2 global distributors (Mouser / DigiKey / Adafruit /
   SparkFun / Waveshare / AliExpress-commodity).
2. **No soldering required** on the assembly path. Every
   connection is a terminal block, ribbon header, or
   USB/Ethernet cable.
3. **DIN-rail mounting** for every enclosed unit. Off-the-shelf
   DIN-rail Pi cases + sensor-module housings.
4. **Single-SD-card boot** for every compute module. The OSR
   project ships a pre-built SD-card image per host class —
   flash, insert, power, done.
5. **Safety architecture preserved.** 2oo2 composite fail-safe
   (two RP2350 + CM5) is kept; we just use commodity **Pi
   Pico 2** boards (which carry the same RP2350 silicon as a
   custom design) instead of an RP2350 on a custom PCB.
6. **Same software.** The RFC 0015 / RFC 0016 / RFC 0005 crate
   map runs unchanged; only the board-level integration is
   commodity-module-based.

## 3. Host-class mapping — custom vs DIY

| Host class | v2-spec custom PCB | DIY plug-and-play |
|---|---|---|
| T-ECU/S | Custom 160 × 100 mm 4-layer with 2× RP2350 + CM5 | 2× Raspberry Pi Pico 2 boards + RPi CM5 on official IO Board + relay HAT |
| T-ECU/A | Custom 160 × 100 mm with CM5 + radios | RPi CM5 IO Board + CAN HAT + 5G HAT + LoRa HAT |
| T-OBS | Custom 180 × 120 mm with 2× RP2350 + CM5 + sensor front-ends | 2× Pi Pico 2 + RPi CM5 IO Board + ultrasonic breakouts + Livox LIDAR USB + TI radar eval board |
| W-SBC | Custom 180 × 130 mm industrial-temp Radxa | Radxa CM5 IO Board + isolated DI/DO HAT + CAN HAT + intrusion-sensor modules |
| S-SBC | Already commodity (RPi CM5 on IO Board) | **No change — S-SBC is already DIY by design.** |

The custom path stays the recommended v2+ track for volume
production. The DIY path is the recommended first-article /
pilot track for any new deployment.

## 4. Core component catalogue

All pricing in USD, 2026 indicative retail. SKUs verified to
exist with two or more global distributors.

### 4.1 Compute modules (universal across host classes)

| Module | Role | SKU / source | Price |
|---|---|---|---|
| Raspberry Pi Pico 2 | RP2350 safety MCU (2 per SIL-4 board) | Official Raspberry Pi Foundation, SC1630 | $5 |
| Raspberry Pi CM5 (8 GB Lite) | Application / sensor-fusion SoC | Official RPi Foundation, SC1124 | $85 |
| Raspberry Pi CM5 IO Board | Carrier exposing full CM5 interface | Official RPi Foundation, SC1125 | $35 |
| Radxa CM5 (RK3588S, industrial-temp) | Wayside SoC on industrial temp | Radxa store SKU `rock-cm5-industrial` | $110 |
| Radxa CM5 IO Board | Carrier for Radxa CM5 | Radxa store SKU `rock-cm5-io` | $40 |

### 4.2 Communications HATs

| Module | Role | SKU / source | Price |
|---|---|---|---|
| Waveshare 2-CH CAN-FD HAT | CAN-FD × 2 (HVAC + lighting buses) | Waveshare `2-CH-CAN-FD-HAT` | $28 |
| Waveshare SX1262 LoRa HAT | LoRa TRG-2 backup radio | Waveshare `SX1262-LoRa-HAT` | $18 |
| Quectel RM500Q-GL M.2 5G modem | TRG-1 primary radio | DigiKey `RM500Q-GL` | $80 |
| GL.iNet GL-MT3000 Wi-Fi/Cellular router | 5G + LTE aggregation for OCC backhaul | Amazon / Alibaba | $130 |

### 4.3 I/O modules (SIL-4 actuator path)

| Module | Role | SKU / source | Price |
|---|---|---|---|
| 8-channel 24 V relay board, opto-isolated | 2oo2 AND-gate relay stage (EB, traction-cut) | SainSmart `SSR-8DC24` / Seeed Grove | $12 |
| ADS1115 16-bit ADC breakout | Ultrasonic analog echo capture | Adafruit #1085 | $15 |
| MCP23017 I²C 16-bit I/O expander | Digital I/O for field inputs | Adafruit #732 | $7 |
| ADUM1411 / ADUM1401 isolator breakout | 4-channel digital galvanic isolation | SparkFun `BOB-14712` | $25 |
| ATECC608B Adafruit breakout | Ed25519 trust anchor (RFC 0017) | Adafruit #4374 | $4 |
| Adafruit USB isolator | Galvanic separation on 2oo2 cross-check path | Adafruit #2107 | $25 |

### 4.4 Obstacle-detect sensors (RFC 0015)

| Module | Role | SKU / source | Price |
|---|---|---|---|
| HC-SR04 ultrasonic transceiver (dev) | Prototype-grade ultrasonic (×4 per nose) | Amazon / AliExpress commodity | $2 each |
| Murata MA40H1S-R (production) | Rail-grade 40 kHz transducer | Mouser `MA40H1S-R` | $25 each |
| TI AWR1843BOOST | 77 GHz mmWave radar eval board | TI ti.com / Mouser | $500 |
| Livox HAP | Solid-state LIDAR | Livox direct | $1 500 |
| Raspberry Pi Camera Module 3 (×2) | Stereo forward-view | Official RPi SC0872 | $35 each |

### 4.5 Wayside-intrusion sensors (RFC 0016)

| Module | Role | SKU / source | Price |
|---|---|---|---|
| Senstar FlexZone fence-line sensor | Perimeter breach detection | Senstar-authorised dealer | $300 / 100 m |
| Livox Mid-360 | ROW LIDAR (per 200 m) | Livox direct | $900 |
| TI AWR1843BOOST | ROW radar (per 500 m) | TI Mouser | $500 |
| 4 K IP camera + Coral TPU | CCTV + AI classifier | Reolink / Dahua + Coral USB | $250 + $60 |

### 4.6 Enclosures + mechanical

| Module | Role | SKU / source | Price |
|---|---|---|---|
| DIN rail Pi 5 / CM5 DIN rail enclosure | Safe-kernel cabinet mount | UCTRONICS `U6277` | $25 |
| Radxa CM5 industrial DIN enclosure | Wayside IP67 pole-mount | Radxa store | $45 |
| Terminal block strip, 12-position 24 V | Field wiring | Phoenix Contact / DigiKey | $8 |
| Cat 6a patch cables assorted | TSN + LAN | Amazon commodity | $5 each |

## 5. Total-cost comparison

| Host class | v2-spec custom (€, volume) | DIY plug-and-play (USD, single-unit retail) | Notes |
|---|---|---|---|
| T-ECU/S | €280 | ~$240 | DIY cheaper at n=1; custom wins at n ≥ 50 |
| T-ECU/A | €220 | ~$300 | Official IO Board + HATs; close to parity |
| T-OBS | €780 + sensors | ~$2 300 | Sensors dominate; commodity vs custom makes little difference |
| W-SBC | €340 | ~$350 | Parity |
| S-SBC | €150 | ~$150 | Already commodity |
| **Per-trainset (T-ECU/S × 2 + T-ECU/A × 2 + T-OBS × 2)** | **~€2 560** | **~$5 680** | DIY path doubles the per-trainset capex — still <5 % of rolling-stock total |

The doubling is the NRE trade-off — you pay 2× per unit but
0× up-front design. For a 5-trainset pilot the custom-PCB NRE
(≈ €150 k for 4-layer design + fab setup across 5 SKUs) swamps
the per-unit premium. The break-even is roughly 30 trainsets.

## 6. Assembly path

Per host class, the DIY assembly is:

1. **Flash the SD card.** OSR ships a per-class image (native
   Rust binary + OS + pre-loaded feature flags). Documented
   at [`hardware/diy-assembly/sd-card-images.md`](../../hardware/diy-assembly/sd-card-images.md).
2. **Snap modules onto DIN rail.** Pi + CM5 IO Board + HATs all
   fit standard DIN-rail enclosures.
3. **Screw terminal blocks to field I/O.** Every field-side
   connection is a labelled screw terminal. Wiring map per
   host class at `hardware/<class>/diy-assembly/wiring-map.md`.
4. **Power up.** 24 V DC in. Boot time ~ 15 s. LEDs on each
   Pico indicate 2oo2 self-test pass. CM5 boots Rust + the
   RFC 0005 crate image for its role.
5. **Verify.** Run `osr-selftest` (Rust CLI tool, ships with
   the image) which exercises every crate's health-check and
   reports pass/fail per function.

No KiCad, no soldering iron, no hot-air station, no custom
fabrication step.

## 7. Safety-case implications

The DIY path does **not** weaken the SIL-4 safety case:

- **2oo2 composite fail-safe** is preserved — two commodity
  Pi Pico 2 boards carry the same RP2350 silicon that the
  custom T-ECU/S v2 spec uses; the Kani harnesses + proptests
  run unchanged.
- **2oo2 AND-gate relay stage** — the custom board's
  hardware relay pattern maps 1:1 onto an opto-isolated relay
  HAT (SainSmart SSR-8DC24). Each relay's contacts are
  mechanically independent; the DIY wiring through the HAT
  preserves the weld-fuse argument.
- **Galvanic isolation** — the ADuM isolator breakouts
  (SparkFun BOB-14712) carry the same ADuM1401 silicon; trace
  length through the breakout is actually shorter than a
  custom board in many cases.
- **Trust anchors** — the Adafruit ATECC608B breakout is the
  identical chip, different enclosure.

The safety argument from EN 50129 § clause applies to the
**silicon + logic**, not to the board-level layout. The DIY
path uses the same silicon; the argument carries.

What the DIY path *does* require is a per-unit bring-up test
(`osr-selftest` per §6.5) to establish that the specific
bolt-together instance is functional. For custom boards the
factory DRC + flying-probe check substitutes; DIY builders run
`osr-selftest` at commissioning.

## 8. Documentation deliverables

Under `hardware/`:

- **[`diy-assembly/`](../../hardware/diy-assembly/)** — top-
  level cookbook: parts catalogue, assembly order, tooling,
  SD-card build.
- **`<class>/diy-bom.md`** — per-host-class specific BOM with
  SKU + price + distributor + wiring map.
- **SD-card images** — signed pre-built images are a v0.2 hardening
  deliverable. Until they ship, the builder flashes the reference
  Raspberry Pi OS image and installs the relevant OSR crate binaries
  from the workspace.

## 9. Rollout

| Phase | Deliverable | Dependencies |
|---|---|---|
| **v0** | This RFC ratified | — |
| **v1** ✅ | Per-host-class DIY BOM tables + top-level assembly cookbook (done 2026-04-23) | v0 |
| **v2** | Pre-built per-class SD-card images, signed + checksummed + hosted | v1 |
| **v3** | Field-validation report from a first external DIY build | v2 |
| **v4** | Retrofit path for upgrading a DIY build to the custom-PCB v2 spec (swap boards without re-certifying software) | v2, RFC 0007 |

## 10. Relationship to RFC 0007

RFC 0007 remains the authoritative board-level spec — its
net list, safety-net rules, and power budgets are what every
implementation (custom or DIY) must satisfy. This RFC is the
**alternate integration path**; it does not supersede the custom
spec. v2+ commercial deployments may transition from DIY to
custom PCB as volumes justify; the software stack runs
unchanged either way.

## 11. What this RFC does NOT include

- **Mass-market consumer Raspberry Pi distributions** — this
  path is for deployment partners and authorised system
  integrators, not general enthusiasts. Rail safety is not a
  weekend-project target.
- **Certification for novel sensor combinations** — every
  SKU in §4 is covered by the existing RFC 0015 / 0016 safety
  case. Substituting a new sensor family requires a safety-
  case amendment.
- **Warranty or support** — the OSR project provides designs,
  not commercial support. Deployment-partner scope.
