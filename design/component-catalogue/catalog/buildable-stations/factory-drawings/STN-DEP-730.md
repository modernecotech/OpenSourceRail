# STN-DEP-730 — depot workshop, vehicle lift and building-services integration

- Revision: `A-DRAFT`
- Issue status: `definition-seed-not-issued`
- Scope type: `deployment-led-supplier-interface`
- Owner: depot equipment + building services integration
- Release package: `STN-FRP-090`
- Source: `docs/rfcs/0014-depot-design-standard.md`, `docs/rolling-stock/light-metro-3car/field-rerailing-concept.md`, `design/component-catalogue/catalog/buildable-stations/default-product-specifications.md`
- Coordinate basis: catalogue station X is along track from platform centre, Y is lateral from track/station centreline and Z is vertical in the local station frame; deployment drawings must transform this frame to accepted survey control while preserving the 350 mm platform-to-top-of-rail interface

## Controlled product scope

| Product | Route / maturity | Release path | Variants | Reference default |
|---|---|---|---:|---|
| `STN-DEP-P060` — main workshop, synchronized LM3 lift/bogie-change bay, overhaul/inspection bays, 40 t crane, wash plant, stores, and wheel-lathe package | `BID` / `buildable-after-building-and-equipment-freeze` | `deployment-specific` | 1 | [`specified`](../default-product-specifications.md#stn-dep-p060) |
| `STN-DEP-P070` — depot cooled controls room, LV, compressed-air, fire, lighting, CCTV, LAN, access-control, and maintenance-data kit | `BID` / `buildable-after-services-and-supplier-freeze` | `deployment-specific` | 1 | [`specified`](../default-product-specifications.md#stn-dep-p070) |

## Required views

- workshop equipment, bays and service-clearance plan
- lift/crane/lathe/wash foundations and structural reactions
- cooling, LV, air, fire, data, emergency isolation and bogie-extraction sequence

## Unresolved inputs

- selected equipment loads, heat rejection, utilities and maintenance envelopes
- site building, fire, structural, energy and environmental approvals
- released LM3 lift points, bogie extraction path and service requirements

## Required outputs

- equipment layouts, foundations, clearances and replacement paths
- power/microgrid/battery isolation, fire, cooling and controls drawings
- workshop lift, crane, pit, wash, stores and maintenance-data schedules

## Required verification

- supplier FAT, certification and equipment foundation survey
- charging, energy, fire, cooling and emergency-isolation SAT
- synchronised lift, mechanical lock, bogie extraction and crane proof

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

Tools/gauges: `STN-TOOL-VEHICLE-LIFT-GAUGE`, `STN-TOOL-CHARGER-ALIGNMENT`, `STN-TOOL-ENERGY-ISOLATION-TEST`.

The JSON beside this page retains deliberately blank native/published file,
checksum, survey/supplier, calculation and named approval fields.

Boundary: This is a drafting/checking brief built from catalogue products, reference defaults and open inputs. It is not a dimensioned fabrication or construction drawing, supplier selection, signed calculation, survey, permit or authority to manufacture, build, energise or operate.
