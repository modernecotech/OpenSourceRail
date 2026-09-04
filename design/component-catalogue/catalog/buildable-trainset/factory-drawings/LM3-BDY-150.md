# LM3-BDY-150 — exterior GFRP material, mould and trim control

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: composites engineering + fabricator
- Factory package: `LM3-FRP-020`
- Source: `docs/rolling-stock/light-metro-3car/modular-fiberglass-body.md`, `docs/rolling-stock/light-metro-3car/dedicated-parts-and-moulds.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-BDY-P130` — one-metre clip-on solid-side fiberglass body module | `MAKE` / `release-candidate` | 48 module | 1000 × 120 × 3050 | one-metre clip-on side/roof module with solid attachment lands |
| `LM3-BDY-P131` — one-metre clip-on window-edge fiberglass side module | `MAKE` / `release-candidate` | 24 module | 1000 × 160 × 3050 | window-edge side module with reveal and drain clearance |
| `LM3-BDY-P132` — one-metre clip-on door-edge fiberglass side module | `MAKE` / `release-candidate` | 24 module | 1000 × 180 × 3050 | door-edge side module with pocket and threshold closeout |
| `LM3-BDY-P133` — one-metre clip-on fiberglass roof skin and equipment-fairing module | `MAKE` / `release-candidate` | 48 module | 1000 × 2850 × 420 | roof skin and equipment-fairing trim variant |
| `LM3-BDY-P140` — keyed clip rail, captive retainer, anti-lift, and dry-seal car kit | `MAKE` / `release-candidate` | 3 car kit | 15800 × 180 × 160 | keyed clip rail, retainers and dry-seal route |

## Required views

- tool-face and split-line views
- laminate/core/insert sections
- trim, drill, edge and repair-zone maps

## Unresolved inputs

- accepted laminate, core, gelcoat, insert, seal and fire-material system
- frozen car bay map and door/window/roof service-clearance model
- released clip, anti-lift, pressure and debris load cases

## Required outputs

- A/B tool-face, split, draft, trim and insert drawings
- solid/window/door/roof variant CNC trim and drill definitions
- clip, seal, anti-lift and drain interface drawing
- serialized module/bay configuration and repair map

## Required verification

- mould survey and witness coupon
- trim/drill first article
- master-frame interchange and anti-lift proof
- water, vibration and timed module replacement trial

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

Tooling: `LM3-TOOL-SIDE-MOULD`, `LM3-TOOL-SIDE-VARIANT-NEST`, `LM3-TOOL-ROOF-MOULD`, `LM3-TOOL-TRIM-DRILL`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
