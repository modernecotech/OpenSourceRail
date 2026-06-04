# mechanical-py — parametric mechanical + civil + station catalogue

Every piece of the OpenSourceRail physical catalogue — rails, sleepers,
U-girders, station canopies, turnout kits, depot doors, solar mounts —
is expressed as a parametric Python CAD assembly.

## Design philosophy

The whole catalogue is biased toward **prefabrication and bolt-together
assembly**. Every design choice in this package is made against three
criteria, in order:

1. **Eliminate on-site structural engineering.** The deployment partner's
   civil engineer should never have to redesign a structural member.
   Everything is cataloged with published load envelopes; the engineer's
   job is to pick a kit size, not to draw a new one.

2. **Eliminate on-site welding and wet concrete.** Hot-dip galvanised
   bolted steel + precast concrete is the default. The only on-site
   concrete is pad footings. The only on-site welding is the continuous-
   welded rail (CWR), which is already standard practice.

3. **Ship flat, erect fast.** Every assembly is dimensioned so one
   standard lorry (13.6 m flatbed × 2.48 m × 2.65 m height) can take
   a meaningful erection package. A `standard` station canopy is two
   lorry-loads of steel + roof panels; erection is 3–5 days with a
   small crew and a 30 t crawler crane.

## What's in scope

| Module | Components |
|---|---|
| `osr_mech.track` | Rail profile (54E1 / 60E1), precast mono-block sleeper, Pandrol-style fastener, assembled track panel |
| `osr_mech.civil` | Precast U-girder for elevated spans (RFC 0011), precast pad footing, precast L-unit platform edge |
| `osr_mech.station` | Steel portal-frame bay, multi-bay canopy assembly, solar-roof panel, signage + lighting mast |
| `osr_mech.rolling_stock` | Car body, bogie components, trainset assemblies, sensor cowl, couplers, articulation, doors, batteries, traction/electronics envelopes, T-OBS sensor pack, fit-out envelopes |
| `osr_mech.cad_templates` | Fabrication templates plus supplier-neutral COTS fixture envelopes |

The current CAD is an envelope and design-review package, not a
homologated production drawing set. It now includes COTS-inspired
fixture geometry, rolling-stock systems, and sheet-metal/chassis
templates. Remaining v0.2 production-detail work is supplier-exact
SKUs, weld maps, tolerance stacks, FEA-ready brackets, harness clamp
locations, and controlled 2D manufacturing drawings.

Supplier-neutral fixture models intentionally remain generic until a
procurement freeze. A selected SKU closes the CAD gap only when its
datasheet envelope, mounting keep-outs, service-removal path, and
revision are captured in the parametric source and matching drawing
register.

## Parametric inputs

Every component takes its parameters from the RFC-level choices the
operator has already made in `design.toml`:

- **Rolling-stock family** → platform length → canopy bay count.
- **Track-geometry preset** → rail profile + sleeper spacing.
- **Station archetype** → bay count + facility mast count.
- **Civil class** (at-grade / elevated / bridge) → U-girder span
  + pier spacing or ballast depth.

So `design.toml` drives both the Rust planning pipeline *and* the
mechanical catalogue. One source of truth for the whole deployment.

## Canonical Source

The Python CAD source files under [`src/osr_mech/`](src/osr_mech/) are
the design basis. Tracked FreeCAD `.FCStd` files under
[`catalog/freecad/`](catalog/freecad/) are the compact assembly-review
artifacts. Neutral CAD exports are local-only scratch files when a
supplier specifically asks for them.

Key rolling-stock source entry points:

| Source | Scope |
|---|---|
| [`src/osr_mech/rolling_stock/trainset.py`](src/osr_mech/rolling_stock/trainset.py) | Trainset family assembly and motorisation |
| [`src/osr_mech/rolling_stock/car_body.py`](src/osr_mech/rolling_stock/car_body.py) | Concept-aligned layered car body: structure, exterior, interior, HVAC ducts, LV/data, HV/PV, thermal/fire routes |
| [`src/osr_mech/rolling_stock/sensor_cowl.py`](src/osr_mech/rolling_stock/sensor_cowl.py) | Large glass end cowl and T-OBS nose envelope |
| [`src/osr_mech/rolling_stock/systems.py`](src/osr_mech/rolling_stock/systems.py) | Doors, batteries, couplers, electronics, charging, sensor packs |
| [`src/osr_mech/rolling_stock/bogie/`](src/osr_mech/rolling_stock/bogie/) | Powered and trailer bogie components |
| [`src/osr_mech/cad_templates/rolling_stock.py`](src/osr_mech/cad_templates/rolling_stock.py) | Chassis/body sheet-metal templates |

## Usage

```bash
# One-time: install the package in editable mode.
pip install -e .[test]

# Build a FreeCAD review assembly.
# The launcher uses native FreeCADCmd or the FreeCAD Flatpak and handles
# FreeCAD's script argument quirks.
scripts/freecad_trainset.sh --family light-metro-3car

# Build chassis/bogie and full-body FreeCAD documents with assembled
# and disassembled/exploded review states, plus geometry-check markdown.
scripts/freecad_assembly_review.sh

# Run first-pass FreeCAD/CalculiX screening FEA beam models and
# solver-result PNGs for chassis, bogie, and body load cases.
scripts/freecad_fea.sh

# Capture FreeCAD GUI screenshots from the review/FEA documents.
# Uses Xvfb automatically when available and refreshes the stable
# docs/screenshots/freecad/ latest image set.
scripts/freecad_screenshots.sh

```

## Testing

`pytest` validates volumes, masses, overall footprints, and solar-roof
area against the published numbers in the RFCs. A geometry test that
regresses mass outside ± 1 % fails — the RFC needs updating or the
model needs fixing, but the two can't silently diverge.

## Handoff to structural engineering

The tracked handoff package is the Python source, FreeCAD `.FCStd`
review assemblies, screenshots, and design notes. A deployment partner
can generate local neutral CAD exports from the same source if their
toolchain requires them, but those exports are not committed because
they are bulky and reproducible.

The published load envelopes (in the component docstrings) are
conservative — every kit is sized for the worst of:

- EN 1991-2 rail loading (LM71 × α = 0.83 for light metro).
- Eurocode 8 seismic (PGA 0.3 g, which covers most of the target
  deployment footprint from MENA through South Asia).
- Wind: 50 m/s basic wind speed (typhoon-class).
- Thermal: ΔT = 70 K for steel, 35 K for concrete.

Deployment sites with harsher envelopes need a beefed-up variant; we'd
rather add a "heavy" SKU than weaken the standard.

## FreeCAD assembly bridge

`osr_mech.freecad_trainset` builds a structured FreeCAD document
directly from the parametric source geometry. The resulting `.FCStd`
file is a review and handoff assembly: parts are grouped as car bodies,
bogies, onboard systems, couplers, platform interfaces, and clearance
references, with placements and display colours applied for inspection.

The bridge deliberately does not make FreeCAD the source of truth.
Authoritative geometry stays in the Python source; FreeCAD is the compact
tracked review format for assembly inspection, drawing generation, and
partner mark-up.

## Licence

Apache 2.0 for the Python code. Generated CAD review artifacts under
`catalog/freecad/` follow the same open-hardware intent as the rest of
the `hardware/` tree.
