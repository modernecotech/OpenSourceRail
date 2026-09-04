# LM3-FIX-235 — common service rail, fastener and fixture adapters

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: vehicle integration + manufacturing engineering
- Factory package: `LM3-FRP-070`
- Source: `docs/rolling-stock/light-metro-3car/interior-layout.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-FIX-P010` — OSR-RAIL-42 common ceiling, waist, and seat-zone service rail kit | `MAKE` / `release-candidate` | 3 car kit | 15000 × 42 × 18 | OSR-RAIL-42 extrusion with repeated datum marks |
| `LM3-FIX-P020` — four-family captive fastener, floating nut, isolator, and access-fastener kit | `SOURCE` / `buildable-after-supplier-freeze` | 3 car kit | 520 × 360 × 160 | four captive fastener families and isolators |
| `LM3-FIX-P030` — standard passenger-fixture saddle and equipment adapter kit | `MAKE` / `concept` | 3 car kit | 520 × 420 × 180 | seat, handrail and equipment adapter variants |

## Required views

- rail extrusion and installed-coordinate views
- foot, end-stop and adapter variants
- grip, locking, isolation and accessible-removal details

## Unresolved inputs

- fixture-specific service/ultimate loads and attachment envelopes
- selected rail alloy/temper, fastener, isolator and finish data
- carbody attachment capacity and electrical/galvanic constraints

## Required outputs

- rail extrusion, cut/drill, end-stop and foot drawing
- seat, handrail, PIS/CCTV and cable-support adapter variants
- fastener grip, locking, torque-authority and captive-part schedule
- installed coordinate, orientation and accessible-removal map

## Required verification

- rail/foot and fixture-specific calculation review
- adapter and installed-grip gauges
- representative pull/slip/rotation proof
- egress, snag, isolation and timed replacement inspection

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

Tooling: `LM3-TOOL-SERVICE-RAIL`, `LM3-TOOL-FIXTURE-PROOF`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
