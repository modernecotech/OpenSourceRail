# STN-TRK-600 — 1:9 turnout rail, crossing, bearer and track-end definition

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `hybrid-fabrication-definition`
- Owner: permanent-way engineer + turnout supplier
- Release package: `STN-FRP-070`
- Source: `docs/rfcs/0012-switches-and-crossings.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-TRK-P010` — 1:9 UIC60 stock-rail, machined switch-blade, and closure-rail kit | `MAKE` / `buildable-after-controlled-drawing-release` | `reusable-definition` | 2 | [`specified`](../default-product-specifications.md#stn-trk-p010) |
| `STN-TRK-P020` — cast-manganese frog, check-rail, stretcher-bar, and mechanical-lock kit | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 2 | [`specified`](../default-product-specifications.md#stn-trk-p020) |
| `STN-TRK-P030` — prestressed turnout sleeper, slide-chair, and elastic-fastener set | `SOURCE` / `buildable-after-supplier-freeze` | `supplier-configuration` | 2 | [`specified`](../default-product-specifications.md#stn-trk-p030) |
| `STN-TRK-P070` — terminal stop-block, passive end marker, foundation, and fixing kit | `SOURCE` / `buildable-after-site-geometry-freeze` | `deployment-specific` | 2 | [`specified`](../default-product-specifications.md#stn-trk-p070) |

## Required views

- turnout layout, chainage and rail geometry
- switch, closure, frog, check-rail and bearer details
- track-end, foundation, gauge and inspection schedules

## Unresolved inputs

- released wheel/rail interface, axle loads, route speed and climate envelope
- selected rail, frog, sleeper, actuator, detector and heater configurations
- site track alignment, signalling, drainage and track-end geometry

## Required outputs

- rail machining, switch/closure, gauge and weld drawings
- complete turnout assembly, harness, detection, heating and bench-test schedule
- site set-out, installation, stop-block and commissioning drawings

## Required verification

- material, machining, weld/NDT and dimensional records
- bench throw, lock, detection, hand-wind and heating proof
- installed geometry, route/detection and stop-block acceptance

## Mandatory drawing controls

- drawing number, title, sheet, scale, units, projection, revision and issue status
- named catalogue, deployment, supplier, checking, quality and approval responsibilities
- survey coordinate reference system, horizontal/vertical datums and controlled transformation
- material/grade, protection, durability life and applicable process specification
- functional datums, tolerances, fits, clearances and measurable inspection characteristics
- product/assembly IDs, configuration applicability, quantities and revision-compatible BOM
- supplier-controlled dimensions, reactions, access zones and utility interfaces identified rather than assumed
- temporary works, lifting/erection sequence, hold points and safe access where applicable
- tool/gauge references, inspection method, acceptance criteria and evidence route
- reusable definition and deployment-specific construction release shown as separate statuses

## Tooling and issue record

Tools/gauges: `STN-TOOL-TURNOUT-BENCH`, `STN-TOOL-BLADE-PROFILE-GAUGE`, `STN-TOOL-TRACK-GEOMETRY`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
