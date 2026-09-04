# STN-SYS-310 — passenger systems, fare equipment and plinth coordination

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `supplier-interface-definition`
- Owner: passenger systems integrator
- Release package: `STN-FRP-040`
- Source: `docs/stations/standard-archetype/accessibility.md`, `docs/stations/standard-archetype/services.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-PAX-P010` — S-SBC station/depot host and rack enclosure | `SOURCE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-PAX-P020` — passenger-information display and route-strip kit | `SOURCE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-PAX-P030` — CCTV, PA loudspeaker, help-point, radio, and station-LAN kit | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 7 | [`specified`](../default-product-specifications.md#stn-pax-p030) |
| `STN-PAX-P040` — fare gate, accessible gate, and validator equipment kit | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 7 | [`specified`](../default-product-specifications.md#stn-pax-p040) |
| `STN-PAX-P050` — ticket-vending machine equipment kit | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 6 | [`specified`](../default-product-specifications.md#stn-pax-p050) |
| `STN-PAX-P060` — seating, wheelchair-zone marking, wayfinding, and accessible-signage kit | `SOURCE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-PAX-P070` — anchored rolled-steel fare-lane / validator plinth with protected cable void | `MAKE` / `release-candidate` | `reusable-definition` | 7 | not required |
| `STN-PAX-P080` — anchored rolled-steel TVM plinth with protected power/data entry | `MAKE` / `release-candidate` | `reusable-definition` | 6 | not required |

## Required views

- equipment, coverage, sightline and accessible-route plan
- power/data/network and OCC interface diagram
- gate/TVM plinth, anchor, service-entry and replacement-clearance details

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
