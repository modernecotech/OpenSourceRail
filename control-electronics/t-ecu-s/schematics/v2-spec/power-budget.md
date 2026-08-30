# T-ECU/S v2 — power budget

Every consumer on the baseboard with worst-case current, feeding
the sizing of every rail regulator. Numbers err on the
conservative side: v2 schematic capture multiplies by 1.3×
design margin before selecting parts.

## Input

- **Nominal:** 24 V DC (EN 50155 nominal).
- **Range:** 16.8 – 30 V (EN 50155 wide-input class).
- **Redundant inputs:** J1 and J2, diode-OR'd via two Schottky
  (SBR10U45SP5) in parallel; each line also protected by a
  PolyFuse (TR/300-300-8 or equiv.) rated 3 A hold, 6 A trip.
- **Surge protection:** TVS diode on each input (SM15T28A or
  equiv., 28 V clamping) + common-mode choke for conducted
  emissions compliance.

## Main buck converter

| Param | Value | Source |
|---|---|---|
| IC | TI **LM5164** (low-IQ wide-Vin buck) | RFC 0007 §3 common platform |
| Vout | 5.0 V | |
| Iout max | 2.0 A (datasheet; we'll use ≤ 1.2 A) | |
| Efficiency | ≥ 90 % at 1 A load | |
| Switching frequency | 400 kHz (fixed) | Keeps BOM inductor small |
| Output ripple | < 50 mV p-p at 1 A | |

5 V rail total budget: 1.2 A → 6 W.

## LDO chain downstream of 5 V

| Rail | Regulator | Iout | Consumers |
|---|---|---|---|
| 3.3 V safe A | TI TLV755 (200 mA LDO) | 180 mA | RP2350 A + ATECC608B A + isolator bank |
| 3.3 V safe B | TI TLV755 (200 mA LDO) | 180 mA | RP2350 B + ATECC608B B + isolator bank |
| 3.3 V CM5 IO | TI TPS7A7200 (1.5 A LDO) | 1.0 A | CM5 IO rail + sensor SoMs + GNSS |
| 1.8 V | TI TPS62177 (buck) | 500 mA | CM5 core auxiliary |
| 1.0 V | TI TPS62177 (buck) | 1.5 A | CM5 main core |

The CM5 draws its own core rail internally from 5 V via its
on-SODIMM PMIC — our 1.0 V rail feeds peripherals, not the CM5
core itself. Numbers match RPi's CM5 datasheet footnotes.

Total 5 V draw (sum of LDO inputs + CM5 direct): ~1.2 A.

## Per-consumer breakdown

### Safety MCU channel A (RP2350 A)

| Consumer | Iout | Notes |
|---|---|---|
| RP2350 A VDD_CORE | 80 mA typ., 150 mA peak | Running both M33 cores @ 150 MHz |
| RP2350 A IO | 40 mA | Driving isolators + ATECC608 + ADC |
| ATECC608B A | 2 mA |
| Isolator bank (A-side LEDs) | 40 mA | 8 DIs + 2 tachs × 5 mA |
| **A channel total on 3.3V** | **~180 mA** | Matches TLV755 spec |

B channel is identical by design.

### CM5 peripherals

| Consumer | Iout | Notes |
|---|---|---|
| CM5 IO core | ≤ 500 mA @ 3.3 V | Depends on GPIO utilisation |
| KSZ9031 Ethernet PHY ×2 | 2 × 180 mA = 360 mA @ 3.3 V | RGMII mode |
| GNSS u-blox NEO-F10N | 40 mA |
| NFC PN5180 | 100 mA (peak on RF) |
| CAN-FD PHY ×4 | 4 × 40 mA = 160 mA |
| **CM5 IO rail total** | **~1.0 A** | Matches TPS7A7200 spec |

### Isolators + relay drivers (post-isolator, field side)

| Consumer | Iout | Rail | Notes |
|---|---|---|---|
| 24 V field loop (DI input loop) | 5 mA × 8 = 40 mA | Field 24 V | |
| Relay driver (DO output) | 100 mA × 4 = 400 mA | Field 24 V | When all 4 relays pulled |
| 2oo2 AND relay coil | 150 mA | Field 24 V | Pull-in current |
| **Field 24 V total** | **~600 mA** | Drawn from J1/J2 input directly |

### Worst-case total

- 5 V rail: 1.2 A → 6 W.
- 24 V field: 0.6 A → 14.4 W.
- Total board: ~20 W at worst case.
- With 1.3× margin: ~26 W design target.

The 5 V buck rated 2 A × 5 V = 10 W; headroom 40 % — fits.

## Thermal

At 26 W total dissipation in a conduction-cooled enclosure:

- Buck IC: 1 W at 90 % efficiency. Package TO-263; heat-sink
  to a copper pour ≥ 20 × 20 mm. θ_JA ≤ 40 K/W → rise ≤ 40 K
  above enclosure.
- LDOs: ≤ 500 mW each. Standard copper pour suffices.
- Main heat sources: CM5 SoC (≤ 8 W peak) + TSN PHYs (≤ 1 W each).

At ambient +70 °C EN 50155 OT4 plus 40 K rise = ~110 °C — within
silicon limits (TI TLV755 junction temp rated 125 °C). v2
thermal analysis confirms.

## Inrush

At power-on, the CM5 pulls ~3 A for ≤ 50 ms during its boot.
This exceeds the 2 A steady-state buck rating. Mitigation:

1. Bulk capacitance ≥ 2 200 µF on 5 V rail (holds the
   transient for < 20 ms).
2. Soft-start on buck: TI LM5164 has native 2 ms soft-start.
3. CM5 enable staged 200 ms after the RP2350 pair — by then
   the buck is in regulation.

## Voltage monitoring

Every rail is monitored by the supervisor IC (U95, TI TPS3701):

- 3.3 V safe A — any undervolt → watchdog reset A
- 3.3 V safe B — any undervolt → watchdog reset B
- 3.3 V CM5 IO — undervolt → CM5 reset
- 24 V input — undervolt → external LED indicator + EB relay
  drop (matches RFC 0007 §4.1 composite fail-safe)

## EMC strategy

- Common-mode chokes on 24 V input and every external I/O.
- LC filter per 3.3 V rail entering sensitive analog blocks
  (PT100 frontend).
- EN 50121-3-2 compliance is the v3 deliverable; v2 schematic
  reserves space for all filters so layout doesn't require
  rework.
