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
| `osr_mech.civil` | Precast U-girder for elevated spans (RFC 0011), at-grade/elevated ballastless slab panels, precast pad footing, precast L-unit platform edge |
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

The source geometry uses the local `osr_mech.cad` facade. Under
`FreeCADCmd` that facade emits native FreeCAD `Part` shapes directly; in
ordinary Python it keeps lightweight volume and bounding-box metadata so
the unit tests can run without a local FreeCAD install.

For an end-to-end civil review, run
`scripts/freecad_civil_systems_example.sh`. It creates
[`catalog/freecad/civil-systems-integration-test.FCStd`](catalog/freecad/civil-systems-integration-test.FCStd)
with canonical viaduct, elevated-station, ground-station, turnout, and two
complete three-car trainset assemblies plus executable bearing, track-support,
platform-height, and clearance checks. Its paired
[`catalog/freecad/civil-systems-integration-test.json`](catalog/freecad/civil-systems-integration-test.json)
provides stable asset IDs, transforms, relationships, design-reference
operational state, validation results, and a hash of the native model.

Key rolling-stock source entry points:

| Source | Scope |
|---|---|
| [`src/osr_mech/rolling_stock/trainset.py`](src/osr_mech/rolling_stock/trainset.py) | Trainset family assembly and motorisation |
| [`src/osr_mech/rolling_stock/car_body.py`](src/osr_mech/rolling_stock/car_body.py) | Concept-aligned layered car body: structure, exterior, interior, HVAC ducts, LV/data, HV/PV, thermal/fire routes |
| [`src/osr_mech/rolling_stock/sensor_cowl.py`](src/osr_mech/rolling_stock/sensor_cowl.py) | Large glass end cowl and T-OBS nose envelope |
| [`src/osr_mech/rolling_stock/systems.py`](src/osr_mech/rolling_stock/systems.py) | Doors, batteries, couplers, electronics, charging, sensor packs |
| [`src/osr_mech/rolling_stock/bogie/`](src/osr_mech/rolling_stock/bogie/) | Powered and trailer bogie components |
| [`src/osr_mech/cad_templates/rolling_stock.py`](src/osr_mech/cad_templates/rolling_stock.py) | Chassis/body sheet-metal templates |
| [`src/osr_mech/design_definition.py`](src/osr_mech/design_definition.py) | Top-down design-space iteration, scoring, and candidate selection |
| [`src/osr_mech/buildable_trainset.py`](src/osr_mech/buildable_trainset.py) | Buildable product tree from parts through trainset assemblies |

## Buildable trainset handoff

The buildable trainset generator turns the optimized `light-metro-3car`
baseline into a usable manufacturing handoff. It is still pre-release
engineering data, but it is structured so a fabricator can start drawing,
RFQ, routing, QA, and first-article planning without reverse-engineering
the CAD tree.

Generated artifacts live in
[`catalog/buildable-trainset/`](catalog/buildable-trainset/):

| Artifact | Purpose |
|---|---|
| [`buildable-trainset-manifest.md`](catalog/buildable-trainset/buildable-trainset-manifest.md) | Product tree: fabricated parts, external components, subassemblies, assemblies, trainset |
| [`current-design-buildability-review.md`](catalog/buildable-trainset/current-design-buildability-review.md) | Green/yellow/red buildability findings and next closure actions |
| [`definitions/index.md`](catalog/buildable-trainset/definitions/index.md) | Drawing/RFQ seed: JSON + Markdown definition for every product-tree node, including structured material and process specs |
| [`travelers/index.md`](catalog/buildable-trainset/travelers/index.md) | Shop traveler seed: material/process controls, operation routers, labor estimates, tooling IDs, QA gates, approval/signoff blocks |

The generated travelers are intentionally `unsigned-template` records.
They are signable manufacturing forms, not already-approved build
records; a real build cell must fill approvals, signatures, dates,
inspection evidence, and NCR/deviation closure.

## Usage

```bash
# One-time: install the package in editable mode.
pip install -e .[test]

# From this mechanical-py directory, check FreeCAD / Flatpak
# availability and the tracked output locations.
../scripts/freecad-generate.sh --check

# From this mechanical-py directory, regenerate every tracked FreeCAD
# review document, FEM screening model, and screenshot set.
../scripts/freecad-generate.sh --all

# Render the two-scene civil/rolling-stock twin and encode the front-page GIF.
../scripts/freecad-generate.sh --digital-twin-animation

# Render the source-linked track/station/viaduct/train production twin.
../scripts/freecad-generate.sh --fabrication-twin

# From this mechanical-py directory, iterate the rolling-stock design
# space and then generate the buildable product tree, definitions, and
# unsigned shop travelers.
../scripts/design-iterate.sh
../scripts/buildable-trainset.sh

# Build a FreeCAD review assembly.
# The launcher uses native FreeCADCmd or the FreeCAD Flatpak and handles
# FreeCAD's script argument quirks.
scripts/freecad_trainset.sh --family light-metro-3car

# Build the single-car review assembly; both bogies use the shared
# wheelbase/chassis placement datum.
scripts/freecad_trainset.sh --family urban-shuttle-1car --out catalog/freecad/single-car-assembly.FCStd

# Build chassis/bogie and full-body FreeCAD documents with assembled
# and disassembled/exploded review states, plus geometry-check markdown.
scripts/freecad_assembly_review.sh

# Build the native FreeCAD replacement catalogue for civil, track,
# station, depot, and rolling-stock fabrication-template parts, plus
# at-grade/elevated platform and station-canopy assemblies.
scripts/freecad_catalog.sh

# Run first-pass FreeCAD/CalculiX screening FEA beam models and
# solver-result PNGs for chassis, bogie, and body load cases.
scripts/freecad_fea.sh

# Capture FreeCAD GUI screenshots from the review/FEA documents.
# Uses Xvfb automatically when available and refreshes the stable
# docs/screenshots/freecad/ latest image set.
scripts/freecad_screenshots.sh

# Build and capture FreeCAD station, ballastless track, and rolling-stock
# scene renders for at-grade, elevated, and interchange configurations.
scripts/freecad_station_scenes.sh

```

## Testing

`pytest` validates volumes, masses, overall footprints, and solar-roof
area against the published numbers in the RFCs. A geometry test that
regresses mass outside ± 1 % fails — the RFC needs updating or the
model needs fixing, but the two can't silently diverge.

The buildable-trainset tests also verify that every product-tree node has
a definition and shop traveler, that all children/parents resolve, that
material/process specs are present, and that traveler operations carry
labor, tooling, approval, QA, and signoff fields.

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

### FreeCAD MCP bridge

FreeCAD 1.1.3 is available through Flatpak on the development workstation,
and the optional MIT-licensed FreeCAD MCP addon/server is installed for
local use. For this Flatpak, the addon is installed under FreeCAD's
versioned user directory (`.../FreeCAD/v1-1/Mod/`). Restart FreeCAD,
switch to the **MCP Addon** workbench, and
start its RPC server before starting an MCP client. The optional
repository-local MCP client example is in
[`../.mcp.json`](../.mcp.json); it expects `freecad-mcp` on `PATH` and
uses localhost only with text feedback by default. Machine-specific
installation paths belong in the user's local configuration.

The MCP server is an interaction layer, not the design authority. New
designs should be added as reproducible FreeCAD source scripts under
`src/osr_mech/`, with `.FCStd` files treated as generated review artifacts.

The repository-level entry point is
[`../scripts/freecad-generate.sh`](../scripts/freecad-generate.sh). It
orchestrates the package launchers below so CI, maintainers, and
deployment partners can regenerate the same artifacts from one command:

- `--models` → `catalog/freecad/trainset-light-metro-3car.FCStd`
- `--assemblies` → assembled/exploded chassis-bogie and body review
  documents plus `assembly-geometry-review.md`
- `--fem` → CalculiX `.inp` / `.dat` / `.frd` study folders, result
  PNGs, `screening-summary.{md,json}`, and
  `catalog/freecad/fea-screening-models.FCStd`
- `--screenshots` and `--station-scenes` → stable documentation images
  under `docs/screenshots/freecad/` and `docs/screenshots/stations/`
- `--samawah-line-twin` → the full-line FreeCAD/JSON asset twin plus the
  Blender 5.2 perspective S5 operations scene, MP4, and README GIF

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
