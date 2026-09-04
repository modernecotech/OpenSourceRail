# LM3-BOG-400 — powered bogie local frame, guards and service installation

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Owner: bogie fabricator + traction/brake integration
- Factory package: `LM3-FRP-130`
- Source: `docs/rolling-stock/light-metro-3car/bogie.md`, `docs/rolling-stock/light-metro-3car/traction.md`
- Coordinate basis: vehicle X longitudinal from car centre, Y lateral from vehicle centreline, Z vertical from top of rail; drawing-specific fabrication datums must be released and related back to this basis

## Controlled product scope

| Product | Route / maturity | Reference quantity | Design-reference envelope (mm) | Representation |
|---|---|---:|---:|---|
| `LM3-BOG-P010` — powered bogie welded H-frame and motor-cradle weldment | `MAKE` / `release-candidate` | 3 ea | 3400 × 2500 × 620 | welded H-frame with axlebox and bolster datums |
| `LM3-BOG-P030` — powered-bogie guards, cable guides, WSP brackets, and inspection covers | `MAKE` / `release-candidate` | 3 kit | 3200 × 2350 × 460 | guards, cable guides, brackets and covers |
| `LM3-BOG-P050` — powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit | `MAKE` / `release-candidate` | 3 bogie kit | 1400 × 420 × 300 | motor torque link, stop and lanyard bracket |
| `LM3-BOG-P060` — powered-bogie brake/WSP/speed-sensor harness and junction-bracket kit | `MAKE` / `release-candidate` | 3 bogie kit | 3000 × 2100 × 220 | bogie harness route and junction brackets |

## Required views

- powered H-frame plan, elevations and structural sections
- motor cradle, torque link, brake, guard and sensor bracket details
- weld/NDT, machining datums, harness route and full-motion clearance views

## Unresolved inputs

- released bogie-frame, motor, brake, suspension and fatigue load cases
- supplier-frozen wheelset, motor, gearbox, brake, spring and damper envelopes
- released weld class, machining datum, cable protection and motion keep-outs

## Required outputs

- powered H-frame cut, bend, machining and weld drawings
- motor cradle, torque-link, guard, brake and sensor bracket drawings
- brake/WSP/speed-sensor harness board, clamp-coordinate and junction schedule
- weld/NDT, corrosion, serial trace and bogie configuration maps

## Required verification

- independent EN 13749 structural/fatigue calculation review
- fixture/tack, post-weld and machined-datum surveys
- classed weld NDT and torque-link/guard proof inspections
- supplier dry fit, harness motion sweep, continuity and insulation tests

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

Tooling: `LM3-TOOL-BOGIE-STAND`, `LM3-TOOL-MOTOR-ALIGN`, `LM3-TOOL-HARNESS-BOARD`, `LM3-TOOL-DATUM-GAUGE`.

The machine-readable JSON beside this page contains the deliberately blank
native/published file references, checksum, sheet/scale and approval fields.

Boundary: This seed aggregates controlled scope and design-reference envelopes. It is not a dimensioned production drawing, released tool surface, NC definition, signed calculation or authority to manufacture.
