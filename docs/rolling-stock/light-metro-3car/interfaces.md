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
| Activation | Electrical lock/unlock from recovery cabinet or OCC command |
| Cut-out / rescue mode | Mechanical unlock handle accessible at ground level |

Every OpenSourceRail consist in every deployment carries the
same coupler — any trainset can rescue any other.

## Station charging connector

| Parameter | Value |
|---|---|
| Primary type | Side-pin conductive connector per RFC 0026 |
| Alternate type | Pantograph-down dock where platform geometry requires it |
| Contact voltage | 1 000 V DC nominal |
| Contact current (charging) | 500–1 000 A station class |
| Actuation | Electro-mechanical (no pneumatic) |
| Location | One train-side connector per car, platform side |
| ATO interface | Extend/retract via the `osr-ato` + `osr-aux-power` pairing on the T-ECU/A |

The station battery buffer supplies the charge pulse. Inter-car
coordination and per-car current limits are handled by `osr-aux-power`.

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
| LIN (local panels) | Twisted pair per ISO 17987 | |
| 24 V DC aux + control | 2.5 mm² × 2 wires | Aux + return |
| 110 V DC backup | 4 mm² × 2 wires | Emergency battery backup |
| Safety loop (emergency brake) | Hardwired pair; normally-closed | Electrically independent of TCN-E |

Connection through the articulation bellows via drag-chain; no
disconnects — this is an intra-consist fixed bus.

## Aux power — station charging dock

The charging interface to the station:

| Parameter | Value |
|---|---|
| Connector | Side-pin primary; pantograph-down alternate |
| Voltage | 1 000 V DC (±10 %) |
| Max current | 500 A continuous; 1 000 A peak at uprated stops |
| Ramp rate | Controlled by `osr-aux-power` soft-start to protect the dock contactor |
| Connector extend / retract signals | From `osr-aux-power` via TCN-E |
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
| `standard-urban` geometry | Yes — 56.6 m consist, 90 m min curve OK, 50 ‰ max grade OK |
| `standard-metro` geometry | Yes — plenty of margin |
| `mainline-mixed` geometry | Yes — meets 25 ‰ max grade (lower than the consist's 5 % capability) |
| `halt` station | Yes — short-platform door select required |
| `standard` station | Yes — 65 m platform |
| `major` station | Yes |
| `interchange` station | Yes |
| `terminal` station | Yes — side-pin dock fits |
| `depot-terminal` station | Yes |

## v2 deliverables (not in v1)

- Coupler electrical connector pinout drawing.
- Station charging dock mechanical envelope (for station civil
  design).
- Gap-filler flap mechanism drawings.
- Antenna radiation-pattern simulations at the consist roof.
