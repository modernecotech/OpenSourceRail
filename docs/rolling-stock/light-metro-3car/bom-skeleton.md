# Procurement BOM skeleton — `light-metro-3car`

This is the **source-identified parts list** a fabricator uses to
price the consist. Parts split three ways:

- **SOURCE** — commodity off-the-shelf. Mouser / Digi-Key / LCSC
  line available; no engineering work required.
- **MAKE** — fabricator produces in-house. Single-supplier tender.
- **BID** — multi-supplier tender. The deployment's procurement
  office runs the bid.

Costs are BASE USD volume-100. Country cost factor from
[`lib/templates/country-costs.toml`](../../../lib/templates/country-costs.toml)
scales them per deployment.

## Body + interior

| Line | Desc | Qty per consist | Source | Base USD | Notes |
|---|---|---|---|---|---|
| B1 | Aluminium extrusion OSR-A1 (120×60 box) | 500 m | MAKE | 7 500 | Local mill |
| B2 | Aluminium extrusion OSR-A2 (80×40 box) | 600 m | MAKE | 6 000 | Local mill |
| B3 | Aluminium extrusion OSR-A3 (200×40 C) | 120 m | MAKE | 2 400 | |
| B4 | Aluminium extrusion OSR-A4 (100×100 sq) | 40 m | MAKE | 1 200 | Corner posts |
| B5 | Aluminium skin 5083 (6 mm, sheet) | 400 m² | SOURCE | 16 000 | |
| B6 | Aluminium deck sheet (6 mm) | 180 m² | SOURCE | 7 200 | |
| B7 | End bulkhead pressing (6 mm alu) | 2 | MAKE | 8 000 | |
| B8 | Articulation joint, Hübner RTS-B40 | 2 | BID | 90 000 | Or local equivalent |
| B9 | Laminated safety-glass window (900×1200) | 36 | SOURCE | 18 000 | |
| B10 | IFE type-4 plug door (or equiv.) | 24 | BID | 144 000 | |
| B11 | Vinyl floor covering (EN 45545 R5) | 270 m² | SOURCE | 10 800 | |
| B12 | Seat, longitudinal bench (EN 45545 R7) | 60 | SOURCE | 18 000 | |
| B13 | Grab rail + stanchion (anodised) | 80 m | MAKE | 8 000 | |
| B14 | Interior LED strip lighting | 260 m | SOURCE | 5 200 | |
| B15 | Exterior LED marker + head / taillight | 8 | SOURCE | 3 200 | |
| B16 | Paint + 2K urethane topcoat | set | SOURCE | 6 000 | |
| B17 | Conformal coat for interior electronics | set | SOURCE | 2 000 | |
| **Body + interior subtotal** | | | | **353 500** | |

## Bogies (6 per consist)

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| G1 | Welded bogie frame (powered) | 3 | MAKE | 60 000 | EN 15085 CL1 |
| G2 | Welded bogie frame (trailer) | 3 | MAKE | 54 000 | |
| G3 | Wheelset monobloc (RFC 0022, S1002) | 12 | BID | 144 000 | |
| G4 | Axle bearing box (SKF / FAG) | 24 | SOURCE | 48 000 | |
| G5 | Primary chevron spring | 24 | SOURCE | 12 000 | |
| G6 | Secondary spring / air spring | 12 | SOURCE | 7 200 | |
| G7 | Secondary damper | 12 | SOURCE | 14 400 | |
| G8 | Brake disc | 12 | SOURCE | 12 000 | |
| G9 | Electromagnetic brake caliper | 24 | BID | 72 000 | |
| G10 | Park-brake spring assembly | 24 | SOURCE | 9 600 | |
| G11 | Centre-pin ring bearing + PTFE slider | 6 | SOURCE | 12 000 | |
| G12 | Yaw-restraint link + bushes | 12 | SOURCE | 6 000 | |
| G13 | Cable-guide + centre-pin assembly | 6 | MAKE | 9 000 | |
| G14 | Wheel-tach (quadrature encoder) | 12 | SOURCE | 6 000 | |
| G15 | Axle bearing temp sensor | 24 | SOURCE | 4 800 | |
| **Bogies subtotal** | | | | **240 500** | |

## Traction + power

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| T1 | PMSM axle motor (180 / 320 kW) | 6 | BID | 180 000 | |
| T2 | Reduction gear (single-stage 6.5:1) | 6 | BID | 42 000 | |
| T3 | SiC inverter (360 / 600 kW) | 3 | BID | 105 000 | Wolfspeed or equiv. |
| T4 | Cold-plate + chiller for traction | 3 | SOURCE | 27 000 | |
| T5 | Na-ion under-seat pack (120 kWh usable) | 3 | BID | 43 200 | CATL / HiNa / etc |
| T6 | BMS electronics (pack-level) | 3 | BID | 18 000 | |
| T7 | Pack cooling plate set | 3 | SOURCE | 6 000 | |
| T8 | Under-seat aluminium module enclosure set | 3 | MAKE | 12 000 | |
| T9 | Aspirating smoke detector (battery + traction bay) | 6 | SOURCE | 18 000 | |
| T10 | Fire suppression (aerosol, auto-discharge) | 6 | SOURCE | 24 000 | |
| T11 | HV contactor + bus bar set | 3 | SOURCE | 24 000 | |
| T12 | Station charging side-pin connector | 3 | SOURCE | 45 000 | Pantograph-down alternate per site |
| T13 | Aux inverter (400 V / 110 V / 24 V) | 3 | SOURCE | 66 000 | |
| T14 | HVAC unit (20 kW each, per car) | 3 | SOURCE | 45 000 | |
| T15 | Regen dump resistor (roof-mount) | 1 | SOURCE | 3 500 | |
| **Traction + power subtotal** | | | | **540 500** | |

## Electronics + safety

| Line | Desc | Qty | Source | Base USD | Notes |
|---|---|---|---|---|---|
| E1 | T-ECU/S board (2× RP2350 + CM5) | 2 | BID | 2 500 | Custom baseboard per RFC 0007 §4 |
| E2 | T-ECU/A board (CM5) | 1 | BID | 1 500 | Per RFC 0007 §5 |
| E3 | ADIS16505 IMU (or BMI088) | 2 | SOURCE | 1 000 | |
| E4 | u-blox NEO-F10N GNSS | 2 | SOURCE | 600 | |
| E5 | PN5180 NFC balise reader | 1 | SOURCE | 200 | |
| E6 | ATECC608B SE chip (on T-ECU/S + T-ECU/A carriers) | 3 | SOURCE | 30 | |
| E7 | Cat.22 5G M.2 module | 1 | SOURCE | 500 | |
| E8 | LoRa SX1276 breakout | 1 | SOURCE | 60 | |
| E9 | NVMe SSD 256 GB (event recorder) | 1 | SOURCE | 60 | |
| E10 | 10.1" touchscreen DMI (per cab) | 2 | SOURCE | 800 | |
| E11 | Cab master-controller (combined) | 2 | BID | 6 000 | |
| E12 | Emergency plunger (hardwired) | 2 | SOURCE | 400 | |
| E13 | Deadman handle + sensor | 2 | SOURCE | 500 | |
| E14 | PIS display (exterior + interior) | 8 | SOURCE | 6 400 | |
| E15 | CCTV camera (forward + door-sill + in-car) | 20 | SOURCE | 6 000 | |
| E16 | 2oo2 relay stage (per safety output) | 4 | SOURCE | 1 200 | |
| E17 | Cable harness (pre-terminated, per car) | 3 | MAKE | 30 000 | |
| **Electronics + safety subtotal** | | | | **57 750** | |

## Consist total

| Bucket | Subtotal (USD) |
|---|---|
| Body + interior | 353 500 |
| Bogies | 240 500 |
| Traction + power | 540 500 |
| Electronics + safety | 57 750 |
| **Total direct-material consist** | **1 192 250** |

Labour (shop weld, assembly, commissioning) adds ~35 %: ~420 000
USD.

**Planning-grade per-consist cost (volume 100): ~1.6 M USD.**

For comparison, legacy-vendor light-metro trainsets in the target
regions typically land 4–6 M USD each — the OSR design's
commodity-module + no-pneumatic bets deliver a ~3× cost reduction
at scale.

## Per-deployment customisation

The operator's own procurement office fills in:

- Livery paint scheme (B16).
- Seat fabric colour (B12).
- TRG-1 5G carrier SIM spec (per-country mobile network).
- Public-safety radio band (E-: not in base BOM).
- Pantograph dock voltage if a non-1500 V DC dock is used (out
  of scope upstream).

## v2 deliverables (not in v1)

- Supplier shortlist per BID line with qualification criteria.
- Lead-time analysis per SOURCE / MAKE / BID.
- Risk log: single-source parts + mitigation.
- Weight budget with per-line tare contribution + final target
  vs actual.
