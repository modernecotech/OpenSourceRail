# STN-CNP-200 — platform canopy steel, footing and roof assembly

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `hybrid-fabrication-definition`
- Owner: structural engineer + steel fabricator
- Release package: `STN-FRP-020`
- Source: `docs/stations/standard-archetype/canopy.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-CNP-P010` — 6 m galvanised HEA portal-frame steel kit | `MAKE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-CNP-P020` — canopy footing, reinforcement, base plate, and anchor-bolt kit | `MAKE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-CNP-P030` — factory-bonded solar roof sandwich panel with MC4 leads | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 7 | [`specified`](../default-product-specifications.md#stn-cnp-p030) |

## Required views

- canopy framing plan and elevations
- member, weld/bolt, baseplate and anchor sections
- roof cassette, joint, gutter and erection details

## Unresolved inputs

- site wind, snow, seismic, thermal and maintenance load cases
- accepted steel, coating, roof-panel, PV and connector systems
- surveyed foundation, platform, electrical and drainage interfaces

## Required outputs

- portal cut/weld, baseplate, anchor-template and erection drawings
- roof-panel layout, joints, gutters, penetrations and edge details
- PV string, isolation, bonding and cable-route schedule

## Required verification

- steel certificates, weld/NDT and frame survey
- anchor-template and erected-frame survey
- roof watertightness, PV insulation/polarity and bond-continuity tests

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

Tools/gauges: `STN-TOOL-PORTAL-FIXTURE`, `STN-TOOL-ANCHOR-TEMPLATE`, `STN-TOOL-ROOF-WATER-TEST`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
