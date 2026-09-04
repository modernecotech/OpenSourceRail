# LM3-ELC-300 — low-voltage trainline harness and terminal distribution

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: electrical integration + vehicle manufacturing
- Factory package: `LM3-FRP-160`
- Source: `docs/rolling-stock/light-metro-3car/interfaces.md`, `docs/rolling-stock/light-metro-3car/interior-layout.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-CTRL-P040` — pre-terminated LV trainline harness, DIN cabinet, and terminal-distribution kit | `MAKE` / `release-candidate` | 3 car kit | 8000 × 2000 × 240 | LV trainline harness and distribution cabinets |

## Required views

- per-car trainline and terminal-cabinet route plan/elevations
- connector, branch, service-loop and penetration schedule
- segregation, clamp coordinates, bend radii, labels and continuity-test details

## Unresolved inputs

- frozen control, safety, PIS/CCTV, door, brake and inter-car I/O schedule
- selected rail cable, connector, cabinet and terminal component data
- released EMC, fire, segregation, service-loop and network requirements

## Required outputs

- wire/connector/terminal schedule and harness-board drawing
- per-car route, branch, penetration, clamp-coordinate and service-loop drawings
- cabinet/terminal allocation, ferrule, label and keying schedule
- continuity, insulation, network-enumeration and as-built configuration forms

## Required verification

- independent schematic, pinout and segregation review
- first harness-board dimensional and connector-keying inspection
- 100 percent continuity/insulation test plus shield/bond audit
- installed bend-radius, chafe, service access and network-enumeration inspection

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

Tooling: `LM3-TOOL-HARNESS-BOARD`, `LM3-TOOL-FINAL-DATUM`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
