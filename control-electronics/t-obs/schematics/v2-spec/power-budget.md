# T-OBS v2 — power budget

Each T-OBS module is fed from the trainset auxiliary bus at
24 V DC (dual-redundant inputs, diode-OR + PolyFuse). The
module's total load sits under 20 W — well below the 40 W
per-module budget allocated in the T-ECU/A auxiliary power
draw in [RFC 0003](../../../../docs/rfcs/0003-samawah-reference-deployment.md)
§4.5.

## Per-rail inventory

| Rail | Voltage | Max current | Max power | Load |
|---|---|---|---|---|
| Safety 3.3 V A | 3.30 V | 0.35 A | 1.16 W | RP2350 A + ATECC A + ADC A bank + ultrasonic AFE bias A |
| Safety 3.3 V B | 3.30 V | 0.35 A | 1.16 W | RP2350 B + ATECC B + ADC B bank + ultrasonic AFE bias B |
| Safety 1.8 V A | 1.80 V | 0.20 A | 0.36 W | RP2350 A I/O + ADC A ref |
| Safety 1.8 V B | 1.80 V | 0.20 A | 0.36 W | RP2350 B I/O + ADC B ref |
| Safety 1.0 V A | 1.00 V | 0.45 A | 0.45 W | RP2350 A core |
| Safety 1.0 V B | 1.00 V | 0.45 A | 0.45 W | RP2350 B core |
| App 3.3 V | 3.30 V | 0.60 A | 1.98 W | CM5 peripheral, camera I/O |
| App 1.8 V | 1.80 V | 0.40 A | 0.72 W | MIPI-CSI bridge, LIDAR PHY |
| CM5 core | 5.00 V | 1.80 A | 9.00 W | RPi CM5 BCM2712 at classifier load (sustained) |
| 12 V (LIDAR) | 12.00 V | 1.00 A | 12.00 W | Livox-class LIDAR peak |
| 5 V (radar) | 5.00 V | 0.30 A | 1.50 W | TI AWR1843 sensor module |
| **Subtotal (24 V)** | — | — | **≈ 29 W peak** | Includes ~11 % regulator loss |
| **Sustained average** | — | — | **≈ 18 W** | LIDAR + radar + classifier under normal running |

## Thermal

- **No active cooling.** Natural convection behind the nose
  panel — ambient air at up to 55 °C inside the nose-cone
  cavity is the worst-case design point.
- **Peak junction temperatures** at 55 °C ambient: RP2350 ≤
  85 °C, CM5 SoC ≤ 95 °C (thermal throttling starts at 85 °C
  but is acceptable since obstacle-detection evaluates on the
  RP2350 pair, not CM5).
- **LIDAR unit** has its own housing with vendor-specified
  thermal envelope; mounting bracket conducts its heat to the
  nose-panel skin.

## Surge + transient

- 24 V input protected by 40 V TVS + 1 A PolyFuse per input leg.
- EFT/burst IEC 61000-4-4 Level 4 (4 kV) and surge IEC 61000-4-5
  Level 3 (2 kV line-to-line) — same as T-ECU/S, re-using its
  TVS diode network.
- Startup in-rush limited by NTC thermistor; steady-state input
  current ≤ 1.3 A at 24 V nominal (≈ 31 W VBUS with all the
  regulator losses).

## EMC

Sensors are EMC-noisy by design (radar + LIDAR switching). The
baseboard runs:

- Shielded MIPI-CSI flex to the stereo cameras (≤ 150 mm).
- CAN-FD and 1000BASE-T via common-mode chokes before the
  connector.
- Ultrasonic AFE traces routed on inner layer with GND sandwich
  to avoid coupling into the RP2350 pair.

## Fault-state power

On a safety-relevant fault (EB asserted via the 2oo2 stage):

- The 12 V LIDAR rail and 5 V radar rail remain powered — we
  want the sensors still reporting during the brake sequence
  so the event recorder captures what was seen.
- CM5 continues to run (non-safety logging).
- RP2350 A+B enter a persistent `Emergency` verdict loop;
  brake-demand line stays asserted until depot recovery
  command via the locked keyswitch (RFC 0015 §8.2).
