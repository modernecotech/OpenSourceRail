# T-ECU/S v2 — block diagram

```
     ┌──────────────────────────────────────────────────────────┐
     │                    24 V DC input (×2 redundant)           │
     │         TI LM5164 buck → 5V → LDO chain → per-rail        │
     │  3.3V safe (A+B), 3.3V app (CM5), 1.8V, 1.0V (SoC cores)  │
     └──────────────────────────────────────────────────────────┘
                       │        │         │
                       ▼        ▼         ▼
                   ┌────────┐ ┌────────┐ ┌─────────┐
                   │RP2350 A│ │RP2350 B│ │ RPi CM5 │
                   │(safety)│ │(safety)│ │(app)    │
                   └────────┘ └────────┘ └─────────┘
                        │          │         │
           ┌────────────┼──────────┼─────────┤
           │            │          │         │
           ▼            │          │         │
     ┌───────┐          │          │         │
     │ATECC  │          │          │         │     1x ATECC608B
     │608B A │ ← A-SPI ─┤          │         │      per RP2350.
     └───────┘          │          │         │
                        │          │         │
     ┌───────┐          │          │         │
     │ATECC  │ ← B-SPI ─┼──────────┤         │
     │608B B │          │          │         │
     └───────┘          │          │         │
                        │          │         │
                    cross-check SPI (A-SPI1 ↔ B-SPI1) @ 1 MHz
                    ─────────────────▶◀─────────────────
                        │          │         │
                     ┌──┴──────────┴───┐     │
                     │   2oo2 AND gate │◀────┼── both must agree
                     │   (HW relay)    │     │   to drive actuator
                     └─────────┬───────┘     │
                               │             │
                               ▼             │
                 EB relay drive + traction-cut  │
                                               │
     ┌────── shared field inputs ──────┐      │
     │   ADuM galvanic isolator banks  │──────┘ feed both A+B
     │   (each input → separate A/B pins)
     └──────────────────────────────────┘
                     ▲
                     │  isolated DI (x8) + DO (x4) + tach (x2)
                     │  CAN-FD (x4) + TSN Ethernet (x2) + IMU
                     │  GNSS + NFC balise + PT100 (x4)
                     │
                ┌────┴─────┐
                │   Field   │
                │   (M12)   │
                └───────────┘
```

## Block inventory

| Block | Ref | Purpose |
|---|---|---|
| Power input (×2) | `J1`, `J2` | 24 V DC redundant supply; diode-OR + PolyFuse |
| Main buck | `U1` | TI LM5164, 24→5V, 2 A |
| LDOs | `U2`..`U6` | 5→3.3V safe A, 5→3.3V safe B, 5→3.3V CM5 IO, 5→1.8V, 3.3→1.0V |
| RP2350 A | `U10` | Safety MCU channel A |
| RP2350 B | `U11` | Safety MCU channel B (identical footprint + power) |
| CM5 SODIMM slot | `CN1` | Application processor, non-safety |
| ATECC608B A | `U20` | Trust anchor for channel A |
| ATECC608B B | `U21` | Trust anchor for channel B |
| Cross-check isolator | `U30` | ADuM1401 digital isolator on the A↔B SPI |
| 2oo2 AND relay stage | `K1`, `K2` | Two SPDT relays wired in series on each safety output |
| Field-input isolator bank | `U40`..`U47` | ADuM3190 per input (8 DIs + 2 tachs) |
| Field-output driver bank | `U50`..`U53` | Isolated HSS (high-side switch) + relay driver per output (4 DOs) |
| IMU | `U60` | Bosch BMI088 via both A-SPI0 + B-SPI0 (separate CS) |
| GNSS | `U61` | u-blox NEO-F10N, UART to CM5 only |
| NFC balise reader | `U62` | PN5180 via CM5's SPI |
| Ethernet PHYs (×2) | `U70`, `U71` | KSZ9031 + KSZ9031 (TSN-capable RGMII) |
| CAN-FD PHYs (×4) | `U80`..`U83` | MCP2562FD per bus |
| PT100 frontend (×4) | `U90`..`U93` | MAX31865 per channel, A-SPI2 + B-SPI2 |
| Supervisor / reset | `U95` | TI TPS3701 watchdog — trips EB if both RP2350s hang |

## Net classification (for stackup + routing rules)

| Class | Nets | Notes |
|---|---|---|
| **Safety-critical** | EB relay drive A, EB relay drive B, 2oo2 AND out, watchdog reset | No high-speed neighbour, separation ≥ 1.5 mm to other classes |
| **Cross-check SPI** | A-SPI1 CLK/MOSI/MISO/CS (galvanic-isolated) | Controlled-impedance, ≤ 10 cm total length |
| **Field-isolated** | 24 V field inputs / outputs (post-isolator side) | Different return; no short to logic ground |
| **High-speed digital** | TSN RGMII, CM5 PCIe, CM5 SDIO | Controlled-impedance 50 Ω single-ended, 100 Ω diff |
| **Low-speed digital** | SPI / I²C / UART to sensors | Standard routing |
| **Analog** | PT100 bridge | Guard-ring + Kelvin sense where needed |
| **Power** | 24 V, 5 V, 3.3 V rails | Plane-based; decouple per IC datasheet |

## Stackup

4-layer:
1. **Top** — signal + components
2. **GND plane** (solid pour)
3. **Split power plane** (5 V / 3.3V-safe-A / 3.3V-safe-B / 3.3V-CM5 / 1.8V / 1.0V)
4. **Bottom** — signal + some components

Controlled-impedance nets (RGMII, PCIe, SDIO, cross-check SPI)
are routed on Top / Bottom referenced to the GND plane at Layer 2.

## What the v2 schematic must produce

The KiCad schematic that gets drawn from this doc should have
**one sheet per block** from the inventory above, plus a top-
level sheet showing only the block-to-block net summary. No
single sheet exceeds A3 at 1:1 scale — deliberate simplicity
for reviewability.
