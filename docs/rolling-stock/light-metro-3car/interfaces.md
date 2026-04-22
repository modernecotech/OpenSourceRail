# Interfaces — `light-metro-3car`

The interfaces this trainset exposes to the outside world. Every
interface is pinned to a commodity standard; no bespoke
connectors.

## Coupler

| Parameter | Value |
|---|---|
| Type | Scharfenberg Type 10 automatic |
| Vertical coupling compatibility | Any Scharfenberg-family consist at 720 mm coupler face height |
| Mechanical strength | 1 000 kN static tensile |
| Electric coupler | 128 pins: 24 V DC aux, CAN-FD (2 pairs), Ethernet (TSN 1 Gbps), emergency-brake loop, video (MIPI over fibre) |
| Pneumatic coupler | **None.** No pneumatic brake / air-horn compressed-air coupling. |
| Activation | Electrical lock/unlock from cab DMI |
| Cut-out / rescue mode | Mechanical unlock handle accessible at ground level |

Every OpenSourceRail consist in every deployment carries the
same coupler — any trainset can rescue any other.

## Pantograph

| Parameter | Value |
|---|---|
| Type | Single-arm PZ-series (Stemmann, Faiveley, or local equiv.) |
| Contact voltage | 1 500 V DC |
| Contact current (charging) | 400 A @ 1 500 V = 600 kW |
| Raise/lower | Electro-mechanical (no pneumatic) |
| Contact strip | Pure-carbon with copper insert |
| Location | Roof-mounted, one per driving car (Car A, Car C) |
| Height when lowered | Within 3 800 mm UIC 505-1 envelope |
| Height when raised | 5 400 mm (at a 1 500 V DC overhead dock) |
| ATO interface | Raise/lower via the `osr-ato` + `osr-aux-power` pairing on the T-ECU/A |

Only one pantograph is raised at a time (the one on the
currently-charging car). Inter-car coordination is handled by
`osr-aux-power`.

## Platform gap

Per [RFC 0010 §4.4](../../rfcs/0010-station-design-standard.md#44-edge-treatment):

| Parameter | Value |
|---|---|
| Horizontal gap (straight platform, door-to-sill) | ≤ 75 mm (target 40 mm with retractable skirt) |
| Horizontal gap (curved platform at 90 m radius) | ≤ 110 mm with 80 mm gap-filler flap |
| Vertical gap (floor-to-platform) | ≤ 50 mm |
| Door sill retractable skirt | 40 mm, electrically actuated at dwell-open |
| Door sill gap-filler flap | 80 mm, drops on PSD-open signal at curved platforms (identified per-deployment) |

Gap-filler flap is a simple solenoid-driven plate — no pneumatic,
no gear train. Failure mode: flap stuck up → `osr-door-control`
blocks door-open; failure flap stuck down → visual inspection at
depot next cycle.

## TCN-E connector (intra-consist, via articulation)

Standard Ethernet + power bundle through each articulation joint:

| Signal | Cable | Notes |
|---|---|---|
| TCN-E port A | Cat 6 RJ45, TSN-capable | Per RFC 0006 §4; single-ring backbone |
| TCN-E port B | Cat 6 RJ45, TSN-capable | Redundant ring |
| CAN-FD (doors + HVAC) | Twisted pair per ISO 11898 | |
| LIN (cab panels) | Twisted pair per ISO 17987 | |
| 24 V DC aux + control | 2.5 mm² × 2 wires | Aux + return |
| 110 V DC backup | 4 mm² × 2 wires | Emergency battery backup |
| Safety loop (emergency brake) | Hardwired pair; normally-closed | Electrically independent of TCN-E |

Connection through the articulation bellows via drag-chain; no
disconnects — this is an intra-consist fixed bus.

## Aux power — 1 500 V DC pantograph dock

The charging interface to the station:

| Parameter | Value |
|---|---|
| Connector | Overhead conductor bar (OCS) at terminal dock |
| Voltage | 1 500 V DC (±10 %) |
| Max current | 400 A continuous; 600 A peak (< 30 s) |
| Ramp rate | Controlled by `osr-aux-power` soft-start to protect the dock contactor |
| Pantograph up / down signals | From `osr-aux-power` via TCN-E |
| Isolation | Dock-side mechanical isolator; electrical monitoring via `osr-energy-site` |

Full RFC 0002 energy-sizing compatibility.

## Emergency door release (external)

- Each exterior door has an external unlock per EN 14752.
- Mechanical; no electronics on the external side.
- Engages only when trainset speed ≤ 5 km/h OR on emergency-
  brake trip (latched state).

## Ground-radio (external antennas)

| Antenna | Location | Band | Notes |
|---|---|---|---|
| TRG-1 5G main | Car A roof | n77 / n78 / CBRS | |
| TRG-1 5G diversity | Car C roof | Same band | MIMO pair |
| TRG-2 LoRa | Car B roof centre | 868 MHz (EU) / 915 MHz (US/MEA) | |
| GNSS | Car A roof + Car C roof | L1/L2 | |
| Public-safety (optional) | Car A roof | 700 MHz | Per-deployment |

All antennas use a single-type N-male to RP-SMA termination, no
bespoke sockets.

## Mass & structure compatibility matrix

Rolling-stock × track-geometry × station-archetype compatibility
per RFCs 0008 §4 / 0009 §10 / 0010 §12:

| Compatible with | Reason |
|---|---|
| `heritage-tram` geometry | No — gauge 1 000 mm variant required (build order) |
| `standard-urban` geometry | Yes — 65 m consist, 90 m min curve OK, 50 ‰ max grade OK |
| `standard-metro` geometry | Yes — plenty of margin |
| `mainline-mixed` geometry | Yes — meets 25 ‰ max grade (lower than the consist's 5 % capability) |
| `halt` station | Yes — 71 m platform (65 consist + 6 clearance) |
| `standard` station | Yes — 75 m platform |
| `major` station | Yes |
| `interchange` station | Yes |
| `terminal` station | Yes — pantograph dock fits |
| `depot-terminal` station | Yes |

## v2 deliverables (not in v1)

- Coupler electrical connector pinout drawing.
- Pantograph dock mechanical envelope (for terminal civil
  design).
- Gap-filler flap mechanism drawings.
- Antenna radiation-pattern simulations at the consist roof.
