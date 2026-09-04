# STN-PWR-500 — wayside charger cabinet and vehicle docking interface

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `supplier-interface-definition`
- Owner: traction power + vehicle integration
- Release package: `STN-FRP-060`
- Source: `docs/rolling-stock/light-metro-3car/interfaces.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-CHG-P010` — station charging cabinet, protection, cable, and wayside connector kit | `BID` / `buildable-after-supplier-freeze` | `supplier-configuration` | 6 | [`specified`](../default-product-specifications.md#stn-chg-p010) |

## Required views

- cabinet/contact arrangement and service clearances
- DC power, protection, isolation and interlock diagram
- vehicle/contact alignment datum, guarded envelope and abort sequence

## Unresolved inputs

- utility fault level, capacity, metering and protection requirements
- selected charger and transformer/rectifier supplier data
- released vehicle docking envelope and operational charging duty

## Required outputs

- equipment arrangement, foundation reaction and maintainability drawings
- single-line, protection, earthing, isolation and cable schedules
- vehicle/wayside datum, alignment, interlock and abort interface control

## Required verification

- supplier FAT and protection-coordination review
- earthing, insulation, isolation and utility witness tests
- vehicle alignment, charge, abort and emergency-isolation SAT

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

Tools/gauges: `STN-TOOL-CHARGER-ALIGNMENT`, `STN-TOOL-EARTH-BOND-TEST`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
