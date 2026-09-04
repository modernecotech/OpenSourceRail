# STN-CNP-220 — auxiliary canopy truss, roof bay and foundation interface

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `deployment-led-fabrication-definition`
- Owner: structural engineer + steel fabricator
- Release package: `STN-FRP-030`
- Source: `docs/stations/standard-archetype/canopy.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-CNP-P050` — 8.5 m × 22 m factory-bonded auxiliary solar-roof bay module | `BID` / `buildable-after-supplier-and-structural-release` | `supplier-configuration` | 7 | [`specified`](../default-product-specifications.md#stn-cnp-p050) |
| `STN-CNP-P060` — 22 m S355 transverse Warren-truss frame with two HSS 200 columns | `MAKE` / `buildable-after-structural-calculation-and-drawing-release` | `reusable-definition` | 7 | [`specified`](../default-product-specifications.md#stn-cnp-p060) |
| `STN-CNP-P070` — auxiliary-canopy pad footing, reinforcement, base plate, and anchor-bolt kit | `MAKE` / `buildable-after-site-structural-release` | `deployment-specific` | 7 | [`specified`](../default-product-specifications.md#stn-cnp-p070) |

## Required views

- module row plan and elevations
- truss member, node, splice, column and base sections
- foundation reactions, anchor template and erection sequence

## Unresolved inputs

- released site layout, egress, fire, drainage and maintenance-access plan
- site-specific structural calculation and foundation reactions
- selected roof/PV/lightning/edge-protection supplier configurations

## Required outputs

- repeatable truss fabrication and roof-bay module drawings
- site footing, anchor, erection, gutter/downpipe and access drawings
- PV string, protection, bonding and commissioning schedule

## Required verification

- truss weld/NDT and dimensional survey
- foundation pre-pour, anchor and erected-geometry surveys
- water, electrical, lightning and edge-protection acceptance tests

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

Tools/gauges: `STN-TOOL-TRUSS-FIXTURE`, `STN-TOOL-AUX-ANCHOR-TEMPLATE`, `STN-TOOL-AUX-ROOF-GAUGE`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
