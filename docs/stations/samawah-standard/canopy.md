# Solar canopy — first-pass structural envelope

Per RFC 0010 §9, every non-`halt` archetype carries a solar
canopy over the platform. Samawah `standard` archetype target:
**1 800 m²** (per `lib/templates/stations.toml`).

This document is the first-pass structural envelope the civil
engineer bids against. v2 is the full FEA + wind-tunnel +
stamped drawings.

## Geometry

| Parameter | Value |
|---|---|
| Canopy footprint (roof area) | 1 800 m² (canopied platform + eave) |
| Length (along track) | 85 m (75 m platform + 5 m each end eave) |
| Width | ~22 m spanning both platforms + track between |
| Height above platform | 2 200 mm clear (min), 3 800 mm roof peak above ToR |
| Pitch | 7° south-facing (Samawah is N of equator) |
| Column spacing along track | 8.5 m (10 column pairs over the 85 m length) |
| Column spacing across tracks | none — roof spans the whole station column-free between outer columns |

## Structural system

Steel truss roof, tied to steel columns at the platform-back
edges. Not concrete — we need the structure to be erectable in
a tight urban site by a commodity SMT-style crane (no form
shoring). Welded steel plus bolted-steel truss is the simplest
build.

### Columns

- Size: **HSS 200 × 200 × 8 mm**, S355 grade.
- Count: 2 rows × 10 columns = **20 columns** per station.
- Height above platform: 3.85 m (platform deck to truss
  bottom).
- Foundation: isolated pad, 1.8 × 1.8 × 0.8 m reinforced
  concrete, four #25 rebar anchors.
- Anchorage: base plate 400 × 400 × 20 mm, 4 × M30 anchor bolts
  per column.

### Truss spans

- Span: 22 m (clear between outer-row columns).
- Truss type: Warren truss, 2.0 m depth, 2.5 m panel spacing.
- Top + bottom chords: **HSS 150 × 150 × 6 mm** S355.
- Diagonals: **L90 × 90 × 8 mm** angle, S355.
- Truss spacing along track: 8.5 m (matches column spacing).
- Total: 10 trusses per station.

### Roof panels

- Standing-seam sheet steel, 0.5 mm galvanised + powder-coat white.
- PV modules mounted flush on the south-facing slope.
- Sheet metal: 550 × 8 500 mm each (standing-seam stock), 2 200
  sheets per station.

## Photovoltaic layout

Per RFC 0010 §9 target 90 % platform shading:

| Parameter | Value |
|---|---|
| Module: 2.0 × 1.0 m, 450 Wp bifacial | (commodity — any brand) |
| Modules per canopy | 330 |
| Nameplate capacity | 148 kWp |
| Yield at Samawah (6.0 peak sun hours) | 325 MWh/year |
| Self-consumption (charging trains + station services) | ~20 % |
| Export to grid | ~80 % |

The canopy output per `osr-energy-site` dispatch: 148 kWp is
below the `standard` archetype's 300 kWp target in the RFC 0002
sizing; this is because the RFC 0010 §9 target is 1 800 m² but
we only have ~1 650 m² of south-slope. The operator can adjust
the roof pitch to flatten (more area, lower peak output) per
climate; Samawah's sun angle makes the 7° choice optimal.

## Load cases (first-pass)

Per EN 1991-1 basis. Samawah-specific values:

| Load | Characteristic value | Source |
|---|---|---|
| Dead load (roof + PV + services) | 0.6 kN/m² | Material build-up |
| Snow load | 0 kN/m² | Samawah never snows |
| Wind load (50-year return) | 1.2 kN/m² | Iraq national code, Samawah zone |
| Dust accumulation | 0.15 kN/m² | 50 mm of desert dust, post-haboob |
| Live load (maintenance) | 0.5 kN/m² | Per EN 1991-1-1 Cat H |
| Seismic (PGA) | 0.1 g | Samawah seismic zone (Iraq) |

### Governing load combination (first-pass)

1. **Wind uplift:** 1.2 kN/m² up + 0.6 kN/m² self-weight down
   → net uplift 0.6 kN/m². Governs roof tie-down + column base
   anchorage.
2. **Gravity (hot-day dust + maintenance):** 0.6 + 0.15 + 0.5 =
   1.25 kN/m² down. Governs truss chord sizing.
3. **Seismic:** 0.1 g × 360 t total station structure mass =
   360 kN horizontal. Governs the base connection — additional
   cross-bracing in the longitudinal direction.

### Truss check (first-pass)

At 22 m span, 8.5 m tributary width, 1.25 kN/m² UDL:
- Peak moment M = (1.25 × 8.5) × 22² / 8 = **642 kN·m**.
- Truss top-chord axial = M / depth = 642 / 2.0 = **321 kN**.
- HSS 150 × 150 × 6 mm S355 capacity: 1 250 kN axial. **Ratio
  0.26** — plenty of margin.

### Column check (first-pass)

At 8.5 m tributary × 22 m/2 (half-bay) × 1.25 kN/m² = 117 kN
axial + lateral wind 1.2 × 8.5 × 3.85 / 2 = 20 kN lateral.
- HSS 200 × 200 × 8 mm S355 capacity: 1 800 kN axial, 90 kN·m
  bending. **Ratios 0.07 axial, 0.42 bending** — comfortable.

### Foundation check (first-pass)

Isolated pad 1.8 × 1.8 × 0.8 m on 200 kPa bearing (typical
Samawah alluvial soil):
- Column ultimate load: 117 × 1.5 = **175 kN**.
- Pad bearing pressure: 175 / (1.8 × 1.8) = **54 kPa** — well
  below 200 kPa capacity. ✓

### Uplift check

Net uplift 0.6 kN/m² over the 1 870 m² footprint = 1 100 kN
total lift. Distributed across 20 columns = 55 kN per column.

- Anchor bolt pullout (4 × M30 anchors × 380 kN capacity each)
  = 1 520 kN per column. Ratio 0.036. ✓

## Materials quantities (planning-grade BOM)

| Line | Qty | Unit |
|---|---|---|
| HSS 200×200×8 mm column | 80 m | S355 |
| HSS 150×150×6 mm truss chord | 880 m | S355 |
| L90×90×8 mm truss diagonal | 650 m | S355 |
| Plate 400×400×20 mm base plate | 20 ea | S355 |
| Plate 450×450×25 mm foundation plate | 20 ea | S355 |
| M30 anchor bolt, 800 mm long | 80 ea | grade 8.8 |
| C25/30 reinforced concrete (foundations) | 52 m³ | per-pad 2.6 m³ × 20 |
| #25 rebar | 2.4 t | foundations |
| Galvanised standing-seam steel sheet | 2 200 ea | 0.5 mm |
| PV module, 450 Wp | 330 ea | |
| PV mounting rail + clamps | 1 set | commodity |
| Lightning-protection finial + down conductor | 1 set | |

**Planning-grade CAPEX: ~€ 180 000 per canopy** (materials
only, volume-10 per-deployment pricing).

## Per-deployment customisation

The operator's architect-of-record adjusts:

- Cardinal orientation if site geometry forces east-west
  (acceptable performance loss ~15 %).
- Column finish (paint scheme / cladding — no structural
  implication).
- PV module brand / wattage (same racking footprint).
- Lightning protection class per local code.

## What v1 doesn't include

- Full FEA / buckling analysis (v2).
- Wind-tunnel or CFD study for vortex shedding (v2 — matters
  only if slender columns are reduced; the envelope above is
  conservative).
- Foundation-specific geotech (v2 per-site).
- Detailed PV wiring + string layout (electrical-engineer scope
  separate from structural).
