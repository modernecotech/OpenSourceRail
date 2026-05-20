# mechanical-py — parametric mechanical + civil + station catalogue

Every piece of the OpenSourceRail physical catalogue — rails, sleepers,
U-girders, station canopies, turnout kits, depot doors, solar mounts —
is expressed as a parametric `build123d` assembly.

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
revision are captured in build123d and the matching drawing register.

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

The Python build123d files under [`src/osr_mech/`](src/osr_mech/) are
the design basis. Generated STEP files under [`catalog/`](catalog/) are
exchange artifacts for CAD viewers, fabricators, and structural
engineering handoff.

Key rolling-stock source entry points:

| Source | Scope |
|---|---|
| [`src/osr_mech/rolling_stock/trainset.py`](src/osr_mech/rolling_stock/trainset.py) | Trainset family assembly and motorisation |
| [`src/osr_mech/rolling_stock/car_body.py`](src/osr_mech/rolling_stock/car_body.py) | Concept-aligned car body, livery, doors, windows, roof PV/HVAC |
| [`src/osr_mech/rolling_stock/sensor_cowl.py`](src/osr_mech/rolling_stock/sensor_cowl.py) | Large glass end cowl and T-OBS nose envelope |
| [`src/osr_mech/rolling_stock/systems.py`](src/osr_mech/rolling_stock/systems.py) | Doors, batteries, couplers, electronics, charging, sensor packs |
| [`src/osr_mech/rolling_stock/bogie/`](src/osr_mech/rolling_stock/bogie/) | Powered and trailer bogie components |
| [`src/osr_mech/cad_templates/rolling_stock.py`](src/osr_mech/cad_templates/rolling_stock.py) | Chassis/body sheet-metal templates |

## Usage

```bash
# One-time: install the package in editable mode.
pip install -e .[test]

# Regenerate every STEP artifact under catalog/.
osr-mech-export

# Or: call a single component from Python.
python3 -c "
from osr_mech.station.canopy import station_canopy
from osr_mech.common import StationArchetype, ConsistFamily
c = station_canopy(
    archetype=StationArchetype.STANDARD,
    consist=ConsistFamily.LIGHT_METRO_3CAR,
)
c.export_step('my-canopy.step')
"
```

## Testing

`pytest` validates volumes, masses, overall footprints, and solar-roof
area against the published numbers in the RFCs. A geometry test that
regresses mass outside ± 1 % fails — the RFC needs updating or the
model needs fixing, but the two can't silently diverge.

## Handoff to structural engineering

Every component emits STEP (ISO 10303-21) on `export_catalog`. STEP
round-trips into Revit, Tekla Structures, Civil 3D, and the open-source
FreeCAD / QGIS-IFC stack. The civil engineer at the deployment partner
reads the STEP, does their load check against local codes (Eurocode,
IBC, IRC, …), and either stamps it or tells us where to beef it up.

The published load envelopes (in the component docstrings) are
conservative — every kit is sized for the worst of:

- EN 1991-2 rail loading (LM71 × α = 0.83 for light metro).
- Eurocode 8 seismic (PGA 0.3 g, which covers most of the target
  deployment footprint from MENA through South Asia).
- Wind: 50 m/s basic wind speed (typhoon-class).
- Thermal: ΔT = 70 K for steel, 35 K for concrete.

Deployment sites with harsher envelopes need a beefed-up variant; we'd
rather add a "heavy" SKU than weaken the standard.

See [`catalog/README.md`](catalog/README.md) for the generated STEP
catalogue map.

## Licence

Apache 2.0 for the Python code. The STEP artifacts under `catalog/`
are CERN-OHL-S v2 (open hardware licence) — same intent as the rest
of the `hardware/` tree.
