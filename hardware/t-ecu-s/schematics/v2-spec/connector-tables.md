# T-ECU/S v2 — connector pinouts

Every external connector on the baseboard, pin-by-pin.
Populating all connectors exactly as below means the v2
hardware plugs directly into the Samawah reference wiring
harness without per-site adaptation.

## J1, J2 — 24 V DC inputs

Connector: **Phoenix Contact MCVW 1.5/2-G-3.5** (2-pin screw-
cage, 3.5 mm pitch).

| Pin | Function |
|---|---|
| 1 | +24 V DC |
| 2 | 0 V (DC return) |

Both J1 and J2 identical; diode-OR'd inside the board. Operator
connects J1 = primary battery bus, J2 = backup battery bus.

## J10 — Debug UART (RP2350 A + B + CM5)

Connector: **2×5 2.54 mm pitch IDC**.

| Pin | Function |
|---|---|
| 1 | GND |
| 2 | RP2350 A UART TX (to host) |
| 3 | RP2350 A UART RX (from host) |
| 4 | GND |
| 5 | RP2350 B UART TX |
| 6 | RP2350 B UART RX |
| 7 | GND |
| 8 | CM5 UART TX (serial console) |
| 9 | CM5 UART RX |
| 10 | 3.3 V (bench power; 100 mA max) |

Used only at depot for bench debug; not populated at revenue.

## J11 — SWD for RP2350 A + B

Connector: **2×5 1.27 mm pitch (Cortex Debug Connector)**.

Two separate J11A and J11B connectors, one per RP2350.
Standard Cortex-M SWD pinout — off-the-shelf debugger cable.

## J20 — CM5 USB-C device

Standard USB-C receptacle. CM5's USB2 port 0 in device mode.
Used for `rpiboot` flashing + serial console fallback.

## J21, J22 — TSN Ethernet (TCN-E A + B)

Connector: **Rosenberger HSD-4 connector (or M12 X-coded for
field use)**.

HSD layout:

| Pin | Signal | Notes |
|---|---|---|
| 1 | TX+ | 1000BASE-T pair 0 + |
| 2 | TX– | pair 0 – |
| 3 | RX+ | pair 1 + |
| 4 | RX– | pair 1 – |
| 5 | BI-C+ | pair 2 + |
| 6 | BI-C– | pair 2 – |
| 7 | BI-D+ | pair 3 + |
| 8 | BI-D– | pair 3 – |

Shield tied to chassis GND through a 1 nF / 10 MΩ AC-coupled
shield bond (EN 50121-3-2 best practice).

**M12 X-coded alternative:** for field-harness compatibility,
populate M12 receptacles instead of HSD — same signal layout,
X-coded Cat 6A pinout. Per-deployment decision.

## J30..J33 — CAN-FD buses (4×)

Connector: **M12 A-coded 5-pin**.

| Pin | Signal |
|---|---|
| 1 | CAN-FD H |
| 2 | CAN-FD L |
| 3 | GND |
| 4 | Shield (chassis) |
| 5 | 12 V DC (for powering a remote CAN node at ≤ 200 mA) |

120 Ω termination switchable on-board per bus (0 Ω jumper on
populate; each bus is either terminated or not based on
network topology).

## J40..J47 — Isolated DIs (8×)

Connector: **M12 A-coded 5-pin**.

| Pin | Signal |
|---|---|
| 1 | Loop + (field side) — normally driven by a remote sensor or switch |
| 2 | Loop – |
| 3 | Shield |
| 4 | NC |
| 5 | NC |

Loop current 5 mA nominal; field-side voltage 24 V. An open
loop (sensor unpowered) reads as logic 0 on both RP2350 DIs.

## J50..J53 — Isolated DOs (4×, through 2oo2 AND stage)

Connector: **M12 A-coded 5-pin**, pigtail to dry contact.

| Pin | Signal |
|---|---|
| 1 | Common (shared between NO + NC) |
| 2 | Normally Open (relay-active = closed) |
| 3 | Normally Closed (relay-active = open) |
| 4 | Shield |
| 5 | NC |

Contact rating: 2 A at 30 VDC. For higher load, driver drives
an external contactor.

The 2oo2 AND stage lives between the RP2350 driver and the M12
connector — both A+B channels must command the same state,
otherwise the output stays inactive.

## J60, J61 — Tachometer inputs (2×)

Connector: **M12 A-coded 5-pin**.

| Pin | Signal |
|---|---|
| 1 | Channel A pulse (quadrature) |
| 2 | Channel B pulse (quadrature) |
| 3 | GND |
| 4 | +24 V DC (for powering the tacho encoder) |
| 5 | Shield |

Both channels land on both RP2350s after galvanic isolation.

## J70 — GNSS antenna

Connector: **SMA receptacle**.

Active antenna with 3.3 V bias fed from u-blox NEO-F10N.
Routed to CM5-side GNSS module (not safety-critical — GNSS is
one of the three position sources `osr-odometry` fuses, not
the only one).

## J71 — NFC balise antenna

Connector: **2×4 2.54 mm pitch header**.

Matched loop antenna for 13.56 MHz. Coil details per the
PN5180 datasheet's reference design; geometry customised to
fit the T-ECU/S enclosure's underside (where the balise reader
points toward the track).

## J80..J83 — PT100 inputs (4×)

Connector: **M12 A-coded 8-pin (for 4-wire PT100)**.

| Pin | Signal |
|---|---|
| 1 | IOUT+ (current source out) |
| 2 | IOUT– |
| 3 | V+ (sense) |
| 4 | V– |
| 5 | NC |
| 6 | NC |
| 7 | Shield |
| 8 | GND |

4-wire RTD compensates for cable resistance — necessary for the
mid-range (−40..+150 °C) precision needed on battery-bay and
traction-bay temp.

## Summary connector count

| Type | Count |
|---|---|
| 24 V DC screw-cage | 2 |
| IDC debug | 1 |
| Cortex Debug | 2 |
| USB-C | 1 |
| HSD / M12 X-coded Ethernet | 2 |
| M12 A-coded 5-pin (CAN, DI, DO, tach) | 18 |
| M12 A-coded 8-pin (PT100) | 4 |
| SMA / antenna | 2 |
| 2×4 antenna header | 1 |
| **Total** | **33 connectors** |

Cabinet wiring harness has 33 mating plugs. Worker-installable
in the field with M12 pre-crimped pigtails.
