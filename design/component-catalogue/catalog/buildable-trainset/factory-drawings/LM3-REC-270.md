# LM3-REC-270 — jacking, lifting, towing and field-rerailing interface

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle structures + recovery engineer
- Factory package: `LM3-FRP-100`
- Source: `docs/rolling-stock/light-metro-3car/field-rerailing-concept.md`, `docs/rolling-stock/light-metro-3car/body.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-BDY-P120` — jacking pad, lifting eye, towing lug, and recovery-label kit | `MAKE` / `release-candidate` | 3 car kit | 1600 × 900 × 280 | jacking, lifting and towing interface kit |

## Required views

- J1--J4 underside and side-location views
- keyed adapter, pad, eye and lug sections
- support combinations, reactions, stop conditions and recovery sequence diagrams

## Unresolved inputs

- individual-car mass and centre-of-gravity envelopes
- released underframe, articulation, bogie-retention and coupler load cases
- selected depot and portable recovery equipment interfaces

## Required outputs

- J1--J4 pad, lifting eye, tow/rerailing lug and keyed-adapter drawings
- permitted support combinations, reactions, stop conditions and labels
- vehicle isolation, brake release, bogie retention and recovery diagrams
- proof-load, inspection, NDT, maintenance and damage-rejection schedule

## Required verification

- structural and weld/NDT calculation review
- four-point datum/interchange gauge
- representative proof and asymmetric/loss-of-pressure trials
- timed depot lift and field rerailing demonstration by trained crews

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

Tooling: `LM3-TOOL-STEEL-FIXTURE`, `LM3-TOOL-DATUM-GAUGE`, `LM3-TOOL-LIFT-COLUMNS`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
