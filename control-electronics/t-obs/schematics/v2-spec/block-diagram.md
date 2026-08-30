# T-OBS v2 — block diagram

Two modules per trainset, one behind each nose-cone panel. Each
module mirrors the T-ECU/S safety-kernel architecture (2 ×
RP2350 + RPi CM5 in a 2oo2 composite fail-safe arrangement)
and adds the obstacle-detection sensor front-ends.

```
 ┌─────────────────────────────────────────────────────────────────┐
 │           24 V DC input (from trainset aux bus, ×2 redundant)   │
 │    LM5164 buck → 5V → LDO chain → per-rail (safety A+B, app)    │
 │    3.3V safe (A+B), 3.3V app (CM5), 1.8V, 1.0V, 12V (LIDAR)     │
 └─────────────────────────────────────────────────────────────────┘
                         │         │          │          │
                         ▼         ▼          ▼          ▼
                    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
                    │RP2350 A│ │RP2350 B│ │ RPi CM5│ │LIDAR   │
                    │(safety)│ │(safety)│ │ (app)  │ │ 12V    │
                    └────────┘ └────────┘ └────────┘ └────────┘
                         │          │         │
       ┌─────────────────┤          │         │
       │                 │          │         │
       │          cross-check SPI @ 1 MHz     │
       │          (A-SPI1 ↔ B-SPI1)            │
       │                 │          │         │
       │             ┌───┴──────────┴───┐     │
       │             │  2oo2 AND gate    │◀───┼── both must agree to
       │             │  (HW relay K1)    │    │   drive brake-demand
       │             └────────┬──────────┘    │
       │                      │                │
       │                      ▼                │
       │         TSN Ethernet out → T-ECU/S    │
       │        (brake-demand, verdict frame)  │
       │                                       │
   ┌───┴──────── sensor front-ends ───────┐   │
   │                                       │   │
   │  ┌─── 4× ultrasonic (40 kHz) ───┐    │   │
   │  │  MAX14970 drive + AD7091     │    │   │
   │  │  TOF timer in RP2350 A+B     │    │   │
   │  │  Analog echo → ADC per chan  │    │   │
   │  └──────────────────────────────┘    │   │
   │                                       │   │
   │  ┌─── mmWave radar (CAN-FD) ───┐     │   │
   │  │  TI AWR1843 @ 77 GHz         │     │   │
   │  │  TCAN1462 transceiver        │     │   │
   │  │  Detection list → RP2350 A   │     │   │
   │  │                 → RP2350 B   │     │   │
   │  │                 → CM5 (log)  │     │   │
   │  └──────────────────────────────┘     │   │
   │                                       │   │
   │  ┌─── LIDAR (1000BASE-T) ───┐         │   │
   │  │  Livox / RoboSense /       │         │   │
   │  │  Leishen class; 12V PoE-    │         │   │
   │  │  class or 12V barrel        │         │   │
   │  │  Point cloud → CM5          │         │   │
   │  │  Detections → RP2350 A+B    │         │   │
   │  └────────────────────────────┘         │   │
   │                                       │   │
   │  ┌─── stereo camera (MIPI-CSI) ─┐      │   │
   │  │  IMX477 or IMX219 pair       │      │   │
   │  │  MIPI-CSI → CM5 (classifier) │      │   │
   │  │  Classifier result → A+B     │      │   │
   │  └──────────────────────────────┘     │   │
   │                                       │   │
   └───────────────────────────────────────┘   │
                                               │
   ┌────── ATECC608B A + B ───────┐            │
   │  Trust anchors, one per       │            │
   │  RP2350; share key material   │            │
   │  with paired T-ECU/S          │            │
   └───────────────────────────────┘            │
                                               │
   ┌────── debug / OTA ──────┐                 │
   │  USB-C console (CM5)    │                 │
   │  JTAG (A + B)           │◀────────────────┘
   │  TSN A/B (redundant)    │
   └─────────────────────────┘
```

## Block inventory

| Block | Ref | Purpose |
|---|---|---|
| Power input (×2) | `J1`, `J2` | 24 V DC redundant supply from trainset aux bus |
| Main buck | `U1` | TI LM5164, 24 → 5 V, 4 A (extra headroom vs T-ECU/S for LIDAR + radar) |
| 12 V rail | `U2` | LM5017, 24 → 12 V, 2 A — LIDAR power |
| LDO chain — safety A | `U3..U5` | 3.3 V_A, 1.8 V_A, 1.0 V_A for RP2350 A + ADC A + ATECC A |
| LDO chain — safety B | `U6..U8` | 3.3 V_B, 1.8 V_B, 1.0 V_B for RP2350 B + ADC B + ATECC B |
| LDO chain — app | `U9..U10` | 3.3 V_app, 1.8 V_app for CM5 + camera |
| RP2350 A | `U11` | Safety MCU A — primary obstacle-detect evaluator |
| RP2350 B | `U12` | Safety MCU B — cross-check evaluator |
| RPi CM5 | `U13` | Sensor-fusion + classifier + non-safety logging |
| ATECC608B A | `U14` | Trust anchor A (shared with T-ECU/S key book) |
| ATECC608B B | `U15` | Trust anchor B |
| Ultrasonic AFE ×4 | `U16..U19` | MAX14970 drive + AD7091 ADC per channel |
| Radar transceiver | `U20` | TCAN1462 CAN-FD transceiver to AWR1843 |
| LIDAR PHY | `U21` | 1000BASE-T KSZ9031 to CM5 + RP2350 detection loop |
| Camera bridge | `U22` | MIPI-CSI-2 hub (2 × IMX-series to CM5) |
| 2oo2 AND relay | `K1` | Passive AND gate — both A + B must agree for brake-demand output |
| TSN Ethernet switch | `U23` | 88E6321 — TSN A/B out to T-ECU/S |
| Debug USB-C | `J3` | CM5 console + firmware OTA |
| JTAG headers | `J4`, `J5` | Cortex-M33 SWD on RP2350 A + B |

## Safety architecture note

The **obstacle-detection verdict is produced on the RP2350 A+B
pair** — not on the CM5. CM5 supplies pre-processed detection
lists (ultrasonic envelope-detected peaks, radar target list,
LIDAR clustered returns, camera classification) but cannot emit
a `Clear` on its own. This keeps the SIL-4 path on silicon that
supports `no_std` Rust, no heap, no interrupts outside the
scheduler — and a known failure-mode inventory.

The **2oo2 AND gate** is the same passive-relay design as
T-ECU/S §safety-nets. Both RP2350 channels must drive their
side of the gate to the "Clear" state to release the brake-
demand line to T-ECU/S. Any single-channel fault → brake-demand
asserted → T-ECU/S commands EB via its own 2oo2 stage.
