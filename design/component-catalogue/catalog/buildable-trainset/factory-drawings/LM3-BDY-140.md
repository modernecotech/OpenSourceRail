# LM3-BDY-140 — battery tray, vent, door and window structural interfaces

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle structures + battery/door/glazing integration
- Factory package: `LM3-FRP-110`
- Source: `docs/rolling-stock/light-metro-3car/body.md`, `docs/rolling-stock/light-metro-3car/traction.md`, `docs/rolling-stock/light-metro-3car/interfaces.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-BDY-P050` — battery tray rails, vent plenum, and service-lid gutter kit | `MAKE` / `release-candidate` | 3 kit | 6200 × 900 × 520 | battery support rails, vent plenum and service gutter |
| `LM3-BDY-P100` — door portal reinforcement, threshold beam, and cassette shim kit | `MAKE` / `release-candidate` | 12 opening kit | 1500 × 260 × 2150 | door carrier/portal with threshold and four-point datum |
| `LM3-BDY-P110` — window carrier ring, bonded-gasket land, and replacement jack-point inserts | `MAKE` / `release-candidate` | 18 opening kit | 1650 × 140 × 1250 | replaceable glazing pressure frame, seal and drain |

## Required views

- under-seat battery rail, door portal and window-carrier elevations
- tray retention, vent/drain, threshold and glazing-land sections
- supplier keep-out, removal path, gauge and structural attachment details

## Unresolved inputs

- released crash, battery-restraint, door and glazing interface reactions
- supplier-frozen coupler, battery, door and window installation envelopes
- released structural, seal/drain, corrosion and service-removal requirements

## Required outputs

- coupler-pocket, battery-rail, door-portal and window-carrier detail drawings
- machined datum, shim/adjustment, seal compression and drain schedules
- supplier keep-out, installation and complete service-removal maps
- weld/fastener/bond authority, tolerance and inspection characteristic lists

## Required verification

- independent structural and retention calculation review
- post-weld datum plus door/window aperture survey
- carrier proof, dry fit and timed supplier-cassette replacement trials
- battery drain/vent and door/window water-ingress tests

## Mandatory drawing controls

- drawing number, title, sheet, scale, units, projection, revision and issue status
- named design, checking, manufacturing, quality and approval responsibilities
- material/grade, finish/protection, mass and applicable process specification
- functional datums, geometric tolerances, fits, clearances and inspection characteristics
- part/assembly IDs, quantities, configuration applicability and revision-compatible BOM
- joining method, weld/adhesive/fastener authority and special-process hold points
- supplier-controlled dimensions and keep-outs identified rather than assumed
- tooling/gauge references, inspection method, acceptance criteria and evidence route

## Tooling and issue record

Tooling: `LM3-TOOL-STEEL-FIXTURE`, `LM3-TOOL-DATUM-GAUGE`, `LM3-TOOL-DOOR-GAUGE`, `LM3-TOOL-WINDOW-GAUGE`, `LM3-TOOL-SEAL-GAUGE`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
