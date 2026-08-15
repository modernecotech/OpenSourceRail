# T-OBS DIY assembly

**Goal:** build the nose-cone obstacle-detection ECU (RFC 0015)
from off-the-shelf modules. One T-OBS per trainset nose × 2
per trainset (each end is identical).

## Bill of materials

| # | Part | SKU | Qty | Unit (USD) | Subtotal |
|---|---|---|---|---|---|
| 1 | Raspberry Pi Pico 2 — channel A | SC1630 | 1 | 5 | 5 |
| 2 | Raspberry Pi Pico 2 — channel B | SC1630 | 1 | 5 | 5 |
| 3 | Raspberry Pi CM5 8 GB Lite | SC1124 | 1 | 85 | 85 |
| 4 | RPi CM5 IO Board | SC1125 | 1 | 35 | 35 |
| 5 | 8-channel 24 V relay board (2oo2 AND for brake-demand to T-ECU/S) | SSR-8DC24 | 1 | 12 | 12 |
| 6 | Adafruit USB isolator (cross-check) | Adafruit 2107 | 1 | 25 | 25 |
| 7 | Adafruit ATECC608B × 2 | Adafruit 4374 | 2 | 4 | 8 |
| 8 | Adafruit ADS1115 ADC × 2 (4 ultrasonic channels × 2 redundant banks) | Adafruit 1085 | 2 | 15 | 30 |
| 9 | HC-SR04 ultrasonic transceivers (dev grade) × 4 | commodity | 4 | 2 | 8 |
|   | — or Murata MA40H1S-R (production) × 4 | MA40H1S-R | 4 | 25 | 100 |
| 10 | TI AWR1843BOOST 77 GHz radar eval board | AWR1843BOOST | 1 | 500 | 500 |
| 11 | Livox HAP solid-state LIDAR (USB-C + Ethernet) | LIVOX-HAP | 1 | 1 500 | 1 500 |
| 12 | RPi Camera Module 3 (stereo pair) | SC0872 | 2 | 35 | 70 |
| 13 | ArduCam stereo bracket | B0203 | 1 | 18 | 18 |
| 14 | Waveshare CAN-FD HAT (radar CAN bus to Pico + CM5) | 2-CH-CAN-FD-HAT | 1 | 28 | 28 |
| 15 | UCTRONICS DIN rail Pi enclosure | U6277 | 1 | 25 | 25 |
| 16 | Mean Well 24 V DIN-rail PSU | HDR-60-24 | 1 | 35 | 35 |
| 17 | Terminal block, Phoenix UT 2.5 DIN | UT 2.5 DIN | 2 | 8 | 16 |
| 18 | Cat 6a 1 m patch (CM5 → LIDAR) | generic | 1 | 5 | 5 |

**Subtotal (dev-grade ultrasonic): ~$2 410 per T-OBS.**
**Subtotal (production Murata ultrasonic): ~$2 500.**

Sensors dominate the cost; compute + integration is ~$200 of
it.

## Block architecture

```
 ┌─ Nose-cone cavity (RF-transparent panel facing forward) ──────────┐
 │                                                                    │
 │   ┌─ HC-SR04 (or Murata MA40H1S-R) ×4 ──┐                          │
 │   │   mounted UL, UR, LL, LR quadrants   │ analog echoes           │
 │   │   3-wire each: VCC / GND / ECHO      │─────────┐               │
 │   └───────────────────────────────────────┘         │               │
 │                                                      ▼               │
 │   ┌──────────────┐   I²C   ┌────────────┐                          │
 │   │ ADS1115 A    │◄────────┤ Pico 2 A   │                          │
 │   │ (4-ch ADC)   │         │ GP2/GP3    │                          │
 │   └──────────────┘         └─────┬──────┘                          │
 │                                   │ GP29 → OBS_CLEAR_A              │
 │                                   │                                  │
 │   ┌──────────────┐   I²C   ┌────────────┐                          │
 │   │ ADS1115 B    │◄────────┤ Pico 2 B   │                          │
 │   │ (redundant)  │         │ (cross)    │                          │
 │   └──────────────┘         └─────┬──────┘                          │
 │                                   │ GP29 → OBS_CLEAR_B              │
 │                                                                     │
 │   ┌─ Cross-check via Adafruit USB isolator ──────────────┐          │
 │   │   Pico A USB-C ──── iso ──── Pico B USB-C             │          │
 │   └────────────────────────────────────────────────────────┘          │
 │                                                                     │
 │   ┌─ SainSmart 8-ch relay (2oo2 AND to T-ECU/S) ──┐                  │
 │   │  OBS_CLEAR_A ──►│ rel 1 │                     │                  │
 │   │  OBS_CLEAR_B ──►│ rel 2 │  series → T-ECU/S   │                  │
 │   └───────────────────────────────────────────────┘                  │
 │                                                                     │
 │   ┌─ TI AWR1843BOOST (radar) ──────────────┐                        │
 │   │  USB-C config · CAN-FD detections       │──── Waveshare CAN HAT │
 │   │  mounted on nose-centre                 │──── RPi CM5 I/O Board │
 │   └─────────────────────────────────────────┘                        │
 │                                                                     │
 │   ┌─ Livox HAP LIDAR ─────────────────────┐                         │
 │   │  Ethernet (1000BASE-T) + 12 V power   │──── Cat 6a to CM5       │
 │   │  mounted on nose-centre (above radar) │   IO Board LAN port     │
 │   └────────────────────────────────────────┘                         │
 │                                                                     │
 │   ┌─ Stereo camera pair ────┐                                       │
 │   │  RPi Cam Module 3 × 2   │── MIPI-CSI ── CM5 IO Board             │
 │   │  500 mm baseline        │                                       │
 │   └─────────────────────────┘                                       │
 └────────────────────────────────────────────────────────────────────┘

 ┌─ Inside train-body DIN rail cabinet ──────────────────────────────┐
 │                                                                    │
 │   Mean Well HDR-60-24 PSU: 24 V DC → 5 V (CM5) + 12 V (LIDAR)     │
 │   RPi CM5 IO Board: runs osr-obstacle-detect (sensor fusion)      │
 │   CAN-FD HAT: radar bus                                             │
 │   Terminal block: output to T-ECU/S brake-demand                    │
 └────────────────────────────────────────────────────────────────────┘
```

## Sensor placement in the nose cowl

Per RFC 0015 §5.1, the four ultrasonic transducers are
arranged in a quadrant:

| Transducer | Mount | Aim |
|---|---|---|
| `US_UL` (upper-left)  | Top-left of nose cowl | 10° above horizontal, left of centre |
| `US_UR` (upper-right) | Top-right of nose cowl | 10° above, right of centre |
| `US_LL` (lower-left)  | Bottom-left | 5° below horizontal, left of centre |
| `US_LR` (lower-right) | Bottom-right | 5° below, right of centre |

The radar + LIDAR go centre-mounted with the LIDAR above the
radar (LIDAR's 12° vertical FoV clears the radar's housing).
Stereo cameras are below both, 500 mm apart for triangulation.

## Wiring — safety-primary path

Each ultrasonic transducer has ECHO and DRIVE lines routed **twice**
— once to channel A's ADS1115, once to channel B's ADS1115.
This gives the SIL-4 safety-primary channel redundancy that
RFC 0015 §5.2 calls for. The HC-SR04 / MA40H1S-R's echo pin
simply fans out into two parallel ADC inputs; a single
transducer failure appears on both channels simultaneously
which is the correct fail-restrictive behaviour.

| Transducer pin | Channel A | Channel B |
|---|---|---|
| ECHO (open-collector) | ADS1115-A A0 | ADS1115-B A0 |
| DRIVE (PWM from Pico) | Pico A GP10 | Pico B GP10 |
| VCC | 5 V bus | 5 V bus |
| GND | GND | GND |

## Firmware + SD card

Two `.uf2`:

- `osr-tobs-chan-a-v0.2.uf2` on Pico A (evaluates O1..O5, drives
  OBS_CLEAR_A, does cross-check with B over USB).
- `osr-tobs-chan-b-v0.2.uf2` on Pico B (same, swapped role).

CM5 SD card: `osr-t-obs-v0.2.img.xz` — carries the
`osr-obstacle-detect` sensor-fusion module that reads the LIDAR
point cloud + radar detection list over Ethernet / CAN-FD,
preprocesses, and forwards the result to both Picos for the
final safety-primary evaluation.

## Commissioning self-test

```bash
sudo osr-selftest --role t-obs
```

Exercises every sensor in turn and validates O1–O5 against a
known-safe baseline plus a calibration target (a reflective
post placed at 5 m) for LIDAR + radar.

## Cost-reduction notes

- **Dev-grade ultrasonic (HC-SR04) is fine for bench / test
  deployments.** Do NOT deploy to revenue service without
  swapping to Murata MA40H1S-R or equivalent — HC-SR04's
  temperature compensation is poor outside lab conditions and
  the RFC 0015 safety case is built against the Murata
  spec's MTBF.
- **LIDAR is the biggest line item.** For a demonstration /
  classroom deployment you can drop the LIDAR and run
  ultrasonic-only below 40 km/h per RFC 0015 O4a, saving
  $1 500 per T-OBS and capping mainline speed to 40 km/h.
  Not permitted for revenue service.
- **Stereo cameras are optional.** RFC 0015 §5.1.1 makes the
  camera classifier a severity-escalation input only, not a
  safety-primary. A deployment that omits it gets lower
  false-positive rejection on windblown-debris obstacles but
  the same safety envelope.
