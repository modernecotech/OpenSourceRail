# LM3-SYS-170 — inter-car articulation adapter and retained interface

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle structures + articulation supplier
- Factory package: `LM3-FRP-120`
- Source: `docs/rolling-stock/light-metro-3car/articulation.md`, `docs/rolling-stock/light-metro-3car/body.md`, `docs/rolling-stock/light-metro-3car/interfaces.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-ART-P010` — articulation adapter frame, anti-lift keeper, and shim kit | `MAKE` / `release-candidate` | 2 kit | 2400 × 300 × 2400 | articulation adapter and anti-lift interface |

## Required views

- lower-pivot adapter plan/elevation and upper-link datums
- anti-lift keeper, shim, pin-retention and trainline-clearance sections
- full-motion envelope, lubrication, inspection and removal views

## Unresolved inputs

- released crash, articulation, anti-lift, gangway and end-equipment load cases
- frozen panoramic-end and open-mid supplier interface envelopes
- selected-end configuration, seal, drain, threshold and service-access requirements

## Required outputs

- common end ring, option bolt grid and articulation-adapter production drawings
- panoramic and open-mid shim/closeout configuration drawings
- anti-lift, service-hatch, sensor-backing, drain and threshold details
- serialized end-position option and interchangeability record

## Required verification

- independent structural, fatigue and full-motion calculation review
- end-ring/bolt-grid datum survey and A/B interchange gauge
- articulation sweep plus keeper/pin-retention inspection
- configured-end water, drain, threshold and service-removal trials

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

Tooling: `LM3-TOOL-STEEL-FIXTURE`, `LM3-TOOL-DATUM-GAUGE`, `LM3-TOOL-COWL-MOULD`, `LM3-TOOL-WATER-TEST`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
