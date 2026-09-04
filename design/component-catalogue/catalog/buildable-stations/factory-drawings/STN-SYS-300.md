# STN-SYS-300 — station LV, UPS, fire and services cabinet integration

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `supplier-interface-definition`
- Owner: station MEP engineer
- Release package: `STN-FRP-040`
- Source: `docs/stations/standard-archetype/services.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-MEP-P010` — weatherproof services cabinet, plinth, cooling, and maintenance-light kit | `MAKE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-MEP-P020` — incoming switchboard, distribution board, metering, UPS, and earthing kit | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 7 | [`specified`](../default-product-specifications.md#stn-mep-p020) |
| `STN-MEP-P030` — platform and emergency LED luminaire, support, and cable kit | `SOURCE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-MEP-P040` — fire detection, alarm interface, extinguisher, and evacuation-sign kit | `SOURCE` / `release-candidate` | `reusable-definition` | 7 | not required |

## Required views

- equipment and maintainability layout
- LV/UPS single-line and load schedule
- earthing, fire cause/effect, lighting and containment details

## Unresolved inputs

- frozen operator equipment, communications, fare and cyber interfaces
- utility, UPS, cooling, earthing, fire and evacuation requirements
- released accessibility, sightline, coverage and maintainability zones

## Required outputs

- cabinet/plinth fabrication and coordinated equipment-layout drawings
- power, data, containment, earth and fire-interface schedules
- equipment anchorage, accessible reach and replacement-clearance map

## Required verification

- plinth and anchorage dimensional/proof checks
- supplier FAT and station integrated functional tests
- accessibility, CCTV/PA coverage and power-loss survey

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

Tools/gauges: `STN-TOOL-CABINET-PLINTH-GAUGE`, `STN-TOOL-FARE-PLINTH-GAUGE`, `STN-TOOL-ACCESSIBILITY-GAUGE`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
