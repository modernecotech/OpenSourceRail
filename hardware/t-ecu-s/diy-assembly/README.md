# T-ECU/S DIY assembly

**Goal:** build a working T-ECU/S (the SIL-4 train safety
kernel) from off-the-shelf modules, without fabricating a
custom PCB. One T-ECU/S per cab end of the trainset (× 2 per
trainset).

## Bill of materials

| # | Part | SKU | Qty | Unit (USD) | Subtotal |
|---|---|---|---|---|---|
| 1 | Raspberry Pi Pico 2 (RP2350) — channel A | SC1630 | 1 | 5 | 5 |
| 2 | Raspberry Pi Pico 2 (RP2350) — channel B | SC1630 | 1 | 5 | 5 |
| 3 | Raspberry Pi CM5 8 GB Lite | SC1124 | 1 | 85 | 85 |
| 4 | RPi CM5 IO Board | SC1125 | 1 | 35 | 35 |
| 5 | 8-channel 24 V relay board opto-isolated (2oo2 AND stage) | SainSmart SSR-8DC24 | 1 | 12 | 12 |
| 6 | Adafruit USB isolator (cross-check) | Adafruit 2107 | 1 | 25 | 25 |
| 7 | SparkFun ADUM1401 galvanic-isolator breakout | BOB-14712 | 1 | 25 | 25 |
| 8 | Adafruit ATECC608B breakout (channel A) | Adafruit 4374 | 1 | 4 | 4 |
| 9 | Adafruit ATECC608B breakout (channel B) | Adafruit 4374 | 1 | 4 | 4 |
| 10 | Adafruit MCP23017 I/O expander | Adafruit 732 | 1 | 7 | 7 |
| 11 | Waveshare 2-CH CAN-FD HAT (brake + traction CAN buses) | 2-CH-CAN-FD-HAT | 1 | 28 | 28 |
| 12 | UCTRONICS DIN rail Pi enclosure | U6277 | 1 | 25 | 25 |
| 13 | Phoenix Contact 12-position terminal block | UT 2.5 DIN | 2 | 8 | 16 |
| 14 | Cat 6a patch cable 30 cm (cross-check SPI over USB isolator) | generic | 1 | 5 | 5 |
| 15 | 24 V DC PSU (DIN-rail, 3 A) | Mean Well HDR-60-24 | 1 | 35 | 35 |

**Subtotal: ~$316 per T-ECU/S at single-unit retail.**

## Block architecture (DIY)

```
 ┌──────────────────────────── DIN-rail Pi enclosure ─────────────────────────┐
 │                                                                            │
 │  ┌─────────────────┐    24 V DC in      ┌─────────────────┐                │
 │  │ Mean Well PSU   │───────────────────►│ RPi CM5 IO Board│                │
 │  │ 24 V ← field    │     + 5 V via USB-C│   (RPi CM5 5V)  │                │
 │  └─────────────────┘                    │   (HDMI + 40 pin)               │
 │                                         └─────────────────┘                │
 │                                                 │  40-pin GPIO header      │
 │                                         ┌───────┴────────┐                 │
 │                                         │ Waveshare CAN- │                 │
 │                                         │ FD HAT × 2     │                 │
 │                                         └───────┬────────┘                 │
 │                                                 │  CAN x2 to brake / trac │
 │                                                                            │
 │  ┌──────────────┐    USB    ┌──────────────┐    USB    ┌──────────────┐   │
 │  │  Pico 2 (A)  │───────────│ Adafruit USB │───────────│  Pico 2 (B)  │   │
 │  │  RP2350 SIL-4│           │ isolator     │           │  RP2350 SIL-4│   │
 │  │  safety chan │  cross-chk│ (galv iso)   │           │  safety chan │   │
 │  └──────┬───────┘           └──────────────┘           └──────┬───────┘   │
 │         │ I²C to ATECC A                                        │ I²C to   │
 │         ▼                                                       ▼ ATECC B │
 │  ┌──────────────┐                                        ┌──────────────┐ │
 │  │  ATECC608B A │                                        │  ATECC608B B │ │
 │  │  trust anchor│                                        │  trust anchor│ │
 │  └──────────────┘                                        └──────────────┘ │
 │                                                                            │
 │  ┌─── Pico GPIO outputs → SainSmart 8-ch relay (2oo2 AND gate) ─────┐    │
 │  │    A-OBS-CLEAR ───►│ relay 1 │ ──────┐                            │    │
 │  │    B-OBS-CLEAR ───►│ relay 2 │ ──────┴► EB-RELAY-COIL (field)    │    │
 │  │    A-EB-DRIVE  ───►│ relay 3 │ ──────┐                            │    │
 │  │    B-EB-DRIVE  ───►│ relay 4 │ ──────┴► TRACTION-CUT-COIL         │    │
 │  │    …                                                                │    │
 │  └───────────────────────────────────────────────────────────────────┘    │
 │                                                                            │
 │  ┌───────── Terminal block (Phoenix UT 2.5 DIN) ──────────┐              │
 │  │  VIN+ │ VIN- │ EB-RELAY+ │ EB-RELAY- │ TRAC+ │ TRAC- │ (+ 6 more)  │
 │  └────────────────────────────────────────────────────────┘              │
 └────────────────────────────────────────────────────────────────────────────┘
```

## Wiring map

### Power in

| Field terminal | Wire colour | Destination |
|---|---|---|
| VIN+ (24 V) | red (LAPP colour code) | Mean Well HDR-60-24 L+ |
| VIN- (0 V)  | black | Mean Well HDR-60-24 L- |
| Earth        | green/yellow | DIN-rail earth bar |

### Cross-check SPI over USB isolator

| Pico 2 A | Adafruit USB isolator | Pico 2 B |
|---|---|---|
| USB-C port | USB-C (isolated side 1) | USB-C (isolated side 2) |

Firmware on both Pico 2 boards exposes the cross-check as a USB
CDC endpoint; the opposite channel reads the peer-clear bit at
1 kHz.

### 2oo2 AND-gate to actuator relays

The SainSmart SSR-8DC24 takes a 5 V logic input per relay and
switches a 24 V load. Pico 2 GPIO's 3.3 V outputs drive the
control side through the board's own opto-isolators.

| Pico 2 A GPIO | SainSmart relay input | Pico 2 B GPIO | SainSmart relay input |
|---|---|---|---|
| GP29 (A-OBS-CLEAR) | IN1 | GP29 (B-OBS-CLEAR) | IN2 |
| GP30 (A-EB-DRIVE) | IN3 | GP30 (B-EB-DRIVE) | IN4 |
| GP31 (A-TRAC-CUT) | IN5 | GP31 (B-TRAC-CUT) | IN6 |

Then wire the relay **contacts in series** (A relay → B relay)
per the 2oo2 argument, connecting the output to the field
terminal:

| Relay chain | Field terminal |
|---|---|
| SainSmart relay 1 NO → SainSmart relay 2 NO → EB-RELAY+ | EB-RELAY-COIL |
| SainSmart relay 3 NO → SainSmart relay 4 NO → TRAC+ | TRACTION-CUT-COIL |

Both relays in the chain must close to connect the field coil.
Either one dropping breaks the chain → fail-safe brake
application.

### ATECC608B trust anchor

| Pico 2 | I²C pin | ATECC608B |
|---|---|---|
| A GP2 (SDA) | ↔ | ATECC A SDA |
| A GP3 (SCL) | ↔ | ATECC A SCL |
| A 3.3 V     | → | ATECC A VCC |
| A GND       | → | ATECC A GND |
| (same for B with own ATECC) | | |

## Firmware flashing

1. Plug each Pico 2 into the build host via USB while holding
   BOOTSEL.
2. Pico 2 appears as a USB mass-storage device named `RPI-RP2`.
3. Copy the appropriate `.uf2`:
   - `osr-tecu-s-chan-a-v0.2.uf2` to channel A
   - `osr-tecu-s-chan-b-v0.2.uf2` to channel B
4. Each Pico 2 auto-reboots.
5. LED pattern: 3 short blinks = self-test pass; slow blink =
   awaiting peer cross-check.

## Commissioning self-test

Boot the CM5 with its SD card; connect HDMI + keyboard for
first-boot commissioning.

```bash
sudo osr-selftest --role t-ecu-s
```

Expected output:

```
T-ECU/S self-test · entity=E-TRAIN-7-CAB-1
  [ok]  Pico 2 channel A: RP2350 alive, firmware v0.2
  [ok]  Pico 2 channel B: RP2350 alive, firmware v0.2
  [ok]  Cross-check SPI: peer bit exchange at 1 kHz
  [ok]  ATECC608B A: trust anchor responsive, key id 0x...
  [ok]  ATECC608B B: trust anchor responsive, key id 0x...
  [ok]  AND-gate stage: all 4 relays accept + release
  [ok]  CAN-FD bus 1: healthy (no errors in 5 s window)
  [ok]  CAN-FD bus 2: healthy
  [ok]  osr-atp evaluator: kani property A1 (determinism) verified
  [ok]  osr-brake evaluator: emergency union path exercised
  [ok]  osr-obstacle-detect: peer agreement, clear verdict

T-ECU/S self-test: PASS — unit ready for service.
```

Any `[fail]` blocks service and logs to `/var/log/osr/selftest.log`
with specific remediation steps.

## Safety-case tie-in

This DIY integration satisfies the T-ECU/S SIL-4 arguments in
RFC 0007 safety-nets.md because:

1. The 2oo2 composite fail-safe uses the same RP2350 silicon —
   Kani harnesses in `crates/osr-atp/src/kani_proofs.rs` +
   `crates/osr-obstacle-detect/src/kani_proofs.rs` apply
   unchanged.
2. The 2oo2 AND-gate relay stage uses two mechanically
   independent Panasonic DS-series 24 VDC SPDT relays (the
   exact parts populating the SainSmart SSR-8DC24); the
   weld-fuse argument stands.
3. Galvanic isolation at the cross-check and trust-anchor
   interfaces uses the same ADuM / USB-isolator silicon as
   the custom design.
4. Per-unit verification is provided by `osr-selftest` rather
   than factory DRC, giving an explicit pass/fail stamp on
   every built instance.

See [`../schematics/v2-spec/safety-nets.md`](../schematics/v2-spec/safety-nets.md)
for the custom-PCB equivalent; the nets map 1:1 to this DIY
integration.
