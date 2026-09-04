# STN-DEP-710 — depot throat turnout, routes and track geometry

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `deployment-interface-definition`
- Owner: permanent-way + signalling integration
- Release package: `STN-FRP-080`
- Source: `docs/rfcs/0014-depot-design-standard.md`, `docs/rfcs/0012-switches-and-crossings.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-DEP-P030` — 1:9 depot-throat turnout assembly replicated from the terminal turnout standard | `MAKE` / `buildable-after-turnout-design-and-site-freeze` | `deployment-specific` | 1 | [`specified`](../default-product-specifications.md#stn-dep-p030) |

## Required views

- depot throat and route layout
- turnout assembly, detection and cable interfaces
- clearance, stop, hand-wind and degraded-operation details

## Unresolved inputs

- boundary/topographical/utility/geotechnical surveys and environmental approvals
- released fleet plan, movements, swept paths and maintenance concept
- controlled depot layout, gradients, drainage/outfall and track standards

## Required outputs

- earthworks, pavement, drainage, boundary and service-road drawings
- stabling, inspection, wash and workshop track-layout drawings
- turnout, stop-block, walkways, crossings and clearance-control schedule

## Required verification

- formation, compaction, drainage and pavement records
- track geometry, clearance and stop-block proof
- route, detection and vehicle swept-path demonstration

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

Tools/gauges: `STN-TOOL-DEPOT-SET-OUT`, `STN-TOOL-TRACK-GEOMETRY`, `STN-TOOL-DRAINAGE-TEST`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
