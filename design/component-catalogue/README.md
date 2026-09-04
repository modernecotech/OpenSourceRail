# Parametric Component Catalogue

Reusable OpenSourceRail rolling-stock, track, station, and civil-kit components
are expressed as parametric Python geometry. Deployment survey, railway
alignment, ground conditions, structural release calculations, and the
federated civil model have separate authorities.

## Design philosophy

The catalogue is biased toward **prefabrication and maintainable mechanical
connections**. Design choices use three priorities:

1. **Reduce bespoke site design.** Reusable families and stated planning
   envelopes reduce repeated work. A competent deployment engineer must still
   select, adapt, analyse, detail, and release every site-specific application.

2. **Minimise site welding and wet work.** Bolted steel and precast elements
   are preferred where the released structural, durability, transport, and
   construction design supports them. Foundations, closures, reinforcement,
   grouting, rail welding, and temporary works remain deployment-specific.

3. **Design for transport and assembly.** Catalogue modules target practical
   road transport and repeatable erection, but actual vehicle limits, lifting
   studies, crane selection, temporary works, crew, and programme are released
   for each deployment.

## What's in scope

| Module | Components |
|---|---|
| `osr_mech.track` | Rail profile (54E1 / 60E1), precast mono-block sleeper, Pandrol-style fastener, assembled track panel |
| `osr_mech.civil` | OSR-Pi20/Pi25 decked beams, special U-girders, OSR-ST6/elevated direct-fixation trackforms, soil/access foundation catalogue, resource production plan, substructures and platform edges (RFC 0011) |
| `osr_mech.station` | Seven station families: precast platform/guideway, platform and auxiliary solar canopies, passenger/MEP/access/charging systems, terminal turnout and main-heavy depot interfaces |
| `osr_mech.rolling_stock` | Car body, bogies, trainsets, doors, batteries, traction/electronics, T-OBS, COTS fit-out and the common service-rail/fastener/fixture system |
| `osr_mech.cad_templates` | Fabrication templates plus supplier-neutral COTS fixture envelopes |

The CAD is an envelope and design-review package, not a
homologated production drawing set. It now includes COTS-inspired
fixture geometry, rolling-stock systems, and sheet-metal/chassis
templates. Remaining production-detail work includes supplier-exact
SKUs, weld maps, tolerance stacks, FEA-ready brackets, harness clamp
locations, and controlled 2D manufacturing drawings.

Supplier-neutral fixture models intentionally remain generic until a
procurement freeze. A selected SKU closes the CAD gap only when its
datasheet envelope, mounting keep-outs, service-removal path, and
revision are captured in the parametric source and matching drawing
register.

The generated station/civil [factory and deployment work packages](catalog/buildable-stations/factory-release-work-packages.md)
cover all 45 stable product families with 18 controlled drawing/interface IDs.
Their [readiness register](catalog/buildable-stations/factory-release-readiness.md)
keeps every package open until reusable drawings, exact supplier configurations,
site surveys/calculations, tools, tests and named approvals are recorded.
The accompanying [open-product reference defaults](catalog/buildable-stations/default-product-specifications.md)
give all 29 unresolved families practical performance values and cost-conscious
configurations without pretending that a supplier, site design or authority approval
has been selected.
Eighteen generated [drawing-definition seeds](catalog/buildable-stations/factory-drawings/index.md)
then bind those product/default records to exact drawing ownership, views, source
inputs, tools and verification tasks; every seed remains explicitly unissued.

The separate [buildable civil catalogue](catalog/buildable-civil/README.md)
reconciles all 19 deterministic federation types: nine civil-owned geometry
types and ten controlled track, station, vehicle, or coordination interfaces.
Its six [release packages](catalog/buildable-civil/factory-release-work-packages.md)
and nine [drawing-definition briefs](catalog/buildable-civil/factory-drawings/index.md)
fail closed when an IFC type hash changes. They do not replace project survey,
ground, reinforcement/prestress, structural, temporary-works, supplier, test,
independent-check, or approval evidence.

## Parametric inputs

Every component takes its parameters from the RFC-level choices the
operator has already made in `design.toml`:

- **Rolling-stock family** → platform length → canopy bay count.
- **Track-geometry preset** → rail profile + sleeper spacing.
- **Station archetype** → bay count + facility mast count.
- **Civil class** (at-grade / elevated / bridge) → ST6 or Pi20/Pi25 product, foundation zone and special-span interface
  + pier spacing or ballast depth.

`design.toml` supplies planning selections to both the Rust pipeline and the
component catalogue. It is not the sole source for a deployment: accepted GIS
and survey data, OSR-ALN alignment, released analysis and drawings, supplier
records, and operational evidence retain their own controlled authorities.

## Canonical Source

The Python CAD source files under [`src/osr_mech/`](src/osr_mech/) are
the design basis. Tracked FreeCAD `.FCStd` files under
[`models/cad/`](models/cad/) are the compact assembly-review
artifacts. Neutral CAD exports are local-only scratch files when a
supplier specifically asks for them.

The source geometry uses the local `osr_mech.cad` facade. Under
`FreeCADCmd` that facade emits native FreeCAD `Part` shapes directly; in
ordinary Python it keeps lightweight volume and bounding-box metadata so
the unit tests can run without a local FreeCAD install.

For a component-and-system integration review in FreeCAD, run
`scripts/freecad_civil_systems_example.sh`. It creates
[`models/cad/civil-systems-integration-test.FCStd`](models/cad/civil-systems-integration-test.FCStd)
with reference viaduct, elevated-station, ground-station, turnout, and two
complete three-car trainset assemblies plus executable bearing, track-support,
platform-height, and clearance checks. Its paired
[`models/cad/civil-systems-integration-test.json`](models/cad/civil-systems-integration-test.json)
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
| [`small-component-standard.md`](catalog/buildable-trainset/small-component-standard.md) | Four fastener families, common rail, keyed connectors, modular illumination and serviceable door/window boundaries |
| [`exterior-finish-system.md`](catalog/buildable-trainset/exterior-finish-system.md) | Mandatory base protection, rail-use livery film zones, and trial-only CaCO3 radiative roof-coating qualification gates |
| [`factory-release-work-packages.md`](catalog/buildable-trainset/factory-release-work-packages.md) | Sixteen controlled chassis, body, bogie, door/window, fascia, roof, interior, finish, electrical and recovery drawing/interface work packages |
| [`factory-release-readiness.md`](catalog/buildable-trainset/factory-release-readiness.md) | Package-level drawing, product revision, tooling, verification and approval readiness; all 16 remain open |
| [`factory-drawings/`](catalog/buildable-trainset/factory-drawings/index.md) | Twenty-nine product-, tooling-, source- and package-bound drafting/checking briefs covering all 62 locally made rows; none is issued for manufacture |
| [`mass-budget.md`](catalog/buildable-trainset/mass-budget.md) | Nine-category optimizer subtotal, engineering reserve and controlled planning tare |
| [`mass-closure-ledger.md`](catalog/buildable-trainset/mass-closure-ledger.md) | Product-level mass responsibility, evidence state, lightweight design-space comparison and recovery-reaction link |
| [`critical-path.md`](catalog/buildable-trainset/critical-path.md) and [`factory-plan.md`](catalog/buildable-trainset/factory-plan.md) | First-article sequence, labour, work centres, space and machinery planning |
| [`cots-candidates.md`](catalog/buildable-trainset/cots-candidates.md) and [`supplier-anchors.md`](catalog/buildable-trainset/supplier-anchors.md) | Exact catalogue/RFQ candidates and controlled local-equivalent boundaries for all bought-in rows |
| [`first-article-execution-pack.md`](catalog/buildable-trainset/first-article-execution-pack.md) and [`first-article-evidence-status.md`](catalog/buildable-trainset/first-article-evidence-status.md) | Ordered execution route and fail-closed status for the 13 supplier, analysis, physical-test and mass-properties gates |
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

# From this design/component-catalogue directory, check FreeCAD / Flatpak
# availability and the tracked output locations.
../../tools/automation/freecad-generate.sh --check

# From this design/component-catalogue directory, regenerate every tracked FreeCAD
# review document, FEM screening model, and screenshot set.
../../tools/automation/freecad-generate.sh --all

# Render the two-scene civil/rolling-stock twin and encode the front-page GIF.
../../tools/automation/freecad-generate.sh --digital-twin-animation

# Render the source-linked track/station/viaduct/train production twin.
../../tools/automation/freecad-generate.sh --fabrication-twin

# From this design/component-catalogue directory, iterate the rolling-stock design
# space and then generate the buildable product tree, definitions, and
# unsigned shop travelers.
../../tools/automation/design-iterate.sh
../../tools/automation/buildable-trainset.sh

# Build a FreeCAD review assembly.
# The launcher uses native FreeCADCmd or the FreeCAD Flatpak and handles
# FreeCAD's script argument quirks.
scripts/freecad_trainset.sh --family light-metro-3car

# Build the single-car review assembly; both bogies use the shared
# wheelbase/chassis placement datum.
scripts/freecad_trainset.sh --family urban-shuttle-1car --out models/cad/single-car-assembly.FCStd

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

The generated `mass-closure-ledger.json` maps all 120 LM3 product rows into
the nine optimizer mass categories without treating simplified envelope
geometry as a weighed production solid. It also keeps the lightest existing
design-space candidate and its recovery reactions visible as an unpromoted
study until production-CAD, supplier, calibrated weighing and weight/balance
evidence close the design.

## Handoff to structural engineering

The tracked handoff package is the Python source, FreeCAD `.FCStd`
review assemblies, screenshots, and design notes. A deployment partner
can generate local neutral CAD exports from the same source if their
toolchain requires them, but those exports are not committed because
they are bulky and reproducible.

The component docstrings carry common screening cases for early comparison:

- EN 1991-2 rail loading (LM71 × α = 0.83 for light metro).
- Eurocode 8 seismic screening at PGA 0.3 g.
- Wind: 50 m/s basic wind speed (typhoon-class).
- Thermal: ΔT = 70 K for steel, 35 K for concrete.

These values do not establish site suitability or structural capacity. Every
deployment must derive its applicable actions, combinations, material data,
ground response, fatigue and durability requirements, then release the chosen
or adapted family through project calculations and drawings.

## FreeCAD assembly bridge

### FreeCAD MCP bridge

The supported installer provides FreeCAD through Flatpak. An optional
MIT-licensed FreeCAD MCP addon/server may be used for interactive local review;
restart FreeCAD, switch to the **MCP Addon** workbench, and start its RPC server
before starting an MCP client. The optional
repository-local MCP client example is in
[`../../.mcp.json`](../../.mcp.json); it expects `freecad-mcp` on `PATH` and
uses localhost only with text feedback by default. Machine-specific
installation paths belong in the user's local configuration.

The MCP server is an interaction layer, not the design authority. New
designs should be added as reproducible FreeCAD source scripts under
`src/osr_mech/`, with `.FCStd` files treated as generated review artifacts.

The repository-level entry point is
[`../../tools/automation/freecad-generate.sh`](../../tools/automation/freecad-generate.sh). It
orchestrates the package launchers below so CI, maintainers, and
deployment partners can regenerate the same artifacts from one command:

- `--models` → `models/cad/trainset-light-metro-3car.FCStd`
- `--assemblies` → assembled/exploded chassis-bogie and body review
  documents plus `assembly-geometry-review.md`
- `--fem` → CalculiX `.inp` / `.dat` / `.frd` study folders, result
  PNGs, `screening-summary.{md,json}`, and
  `models/cad/fea-screening-models.FCStd`
- `--screenshots` and `--station-scenes` → stable documentation images
  under `docs/screenshots/freecad/` and `docs/screenshots/stations/`
- `--samawah-line-twin` → the full-line FreeCAD/JSON asset twin plus the
  Blender perspective S5 operations scene, MP4, and README GIF

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
`models/cad/` follow the same open-hardware intent as the rest of
the `control-electronics/` tree.
