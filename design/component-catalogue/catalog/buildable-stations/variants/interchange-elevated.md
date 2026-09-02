# `interchange-elevated` station definition

**Status:** deterministic design-reference package; not construction release.

The shared envelope, canopy, accessibility, services, compliance and
43-drawing register live in [`docs/stations/standard-archetype/`](../../../../../docs/stations/standard-archetype/).
This page is the complete archetype delta and stable-ID bridge into its BOM,
traveler, FreeCAD installed/exploded states and IFC4.3 assembly.

## Parameter delta from `standard`

| Parameter | Standard | This variant |
|---|---:|---:|
| `platform_count` | 2 | 4 |
| `platform_layout` | side | stacked |
| `platform_l_units` | 0 | 80 |
| `at_grade_track_channel_count` | 1 | 0 |
| `at_grade_slab_panels` | 10 | 0 |
| `guideway_edge_modules` | 40 | 0 |
| `total_canopy_bays` | 20 | 40 |
| `platform_canopy_area_m2` | 504.0 | 1008.0 |
| `site_canopy_target_m2` | 1800.0 | 3200.0 |
| `auxiliary_canopy_required_area_m2` | 1296.0 | 2192.0 |
| `auxiliary_canopy_module_count` | 7 | 12 |
| `auxiliary_canopy_installed_area_m2` | 1309.0 | 2244.0 |
| `auxiliary_canopy_target_overbuild_m2` | 13.0 | 52.0 |
| `auxiliary_canopy_kwp` | 222.5 | 381.5 |
| `tpss_kva` | 0 | 1000 |
| `access_type` | ground-level-side-access | elevated-transfer-concourse-with-pedestrian-overbridge |

Unique product rows: `STN-CHG-P020`, `STN-ACC-P020`, `STN-ACC-P030`

## Controlled handoffs

- BOM: `build/bom/stations/interchange-elevated.csv`
- traveler: [`../travelers/interchange-elevated.md`](../travelers/interchange-elevated.md)
- FreeCAD: [`../../../models/cad/stations/station-interchange-elevated.FCStd`](../../../models/cad/stations/station-interchange-elevated.FCStd)
- assembly-state map: [`../../../models/cad/stations/station-interchange-elevated.assembly-review.json`](../../../models/cad/stations/station-interchange-elevated.assembly-review.json)
- IFC4.3: [`../../../../../engineering/models/bim/reference/stations/station-interchange-elevated.ifc`](../../../../../engineering/models/bim/reference/stations/station-interchange-elevated.ifc)

## Product/drawing/connection identity

The definition-sheet ID keeps the product ID intact. It identifies the
deployment drawing that must be produced and approved; it does not claim
that a construction drawing has already been released. `CONN` rows identify
where a controlled fastener, anchor, seal, terminal, weld or grout schedule is required.

| Product ID | Parent | Route | Definition sheet | Shared drawings | Connection control |
|---|---|---|---|---|---|
| `STN-CIV-P010` | `STN-PLT-SA200` | `MAKE` | `STN-CIV-P010-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-CIV-P020` | `STN-PLT-SA200` | `MAKE` | `STN-CIV-P020-DRW-INTERCHANGE-ELEVATED` | — | `STN-CIV-P020-CONN` |
| `STN-CIV-P030` | `STN-CIV-SA100` | `MAKE` | `STN-CIV-P030-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-M-002` | — |
| `STN-PLT-P010` | `STN-PLT-SA200` | `SOURCE` | `STN-PLT-P010-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-011` | — |
| `STN-CNP-P010` | `STN-CNP-SA300` | `MAKE` | `STN-CNP-P010-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-CNP-P020` | `STN-CIV-SA100` | `MAKE` | `STN-CNP-P020-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-S-001`, `OSR-STD-S-002` | `STN-CNP-P020-CONN` |
| `STN-CNP-P030` | `STN-CNP-SA300` | `BID` | `STN-CNP-P030-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-003` | `STN-CNP-P030-CONN` |
| `STN-CNP-P040` | `STN-CNP-SA300` | `BID` | `STN-CNP-P040-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-003`, `OSR-STD-E-004`, `OSR-STD-E-008` | — |
| `STN-MEP-P010` | `STN-MEP-SA400` | `MAKE` | `STN-MEP-P010-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-013`, `OSR-STD-M-001` | `STN-MEP-P010-CONN` |
| `STN-MEP-P020` | `STN-MEP-SA400` | `BID` | `STN-MEP-P020-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-001`, `OSR-STD-E-005` | — |
| `STN-MEP-P030` | `STN-MEP-SA400` | `SOURCE` | `STN-MEP-P030-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-002`, `OSR-STD-E-005` | — |
| `STN-MEP-P040` | `STN-MEP-SA400` | `SOURCE` | `STN-MEP-P040-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-F-001`, `OSR-STD-F-004` | — |
| `STN-PAX-P010` | `STN-PAX-SA500` | `SOURCE` | `STN-PAX-P010-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-PAX-P020` | `STN-PAX-SA500` | `SOURCE` | `STN-PAX-P020-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-007` | — |
| `STN-PAX-P030` | `STN-PAX-SA500` | `BID` | `STN-PAX-P030-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-006`, `OSR-STD-E-007` | — |
| `STN-PAX-P040` | `STN-PAX-SA500` | `BID` | `STN-PAX-P040-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-003`, `OSR-STD-A-014` | `STN-PAX-P040-CONN` |
| `STN-PAX-P050` | `STN-PAX-SA500` | `BID` | `STN-PAX-P050-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-003` | — |
| `STN-PAX-P070` | `STN-PAX-SA500` | `MAKE` | `STN-PAX-P070-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-014`, `OSR-STD-S-007` | `STN-PAX-P070-CONN` |
| `STN-PAX-P080` | `STN-PAX-SA500` | `MAKE` | `STN-PAX-P080-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-003`, `OSR-STD-S-007` | `STN-PAX-P080-CONN` |
| `STN-PAX-P060` | `STN-PAX-SA500` | `SOURCE` | `STN-PAX-P060-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-T-001`, `OSR-STD-T-003` | — |
| `STN-ACC-P010` | `STN-ACC-SA600` | `MAKE` | `STN-ACC-P010-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-A-012`, `OSR-STD-M-004` | — |
| `STN-CNP-P050` | `STN-CNP-SA300` | `BID` | `STN-CNP-P050-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-CNP-P060` | `STN-CNP-SA300` | `MAKE` | `STN-CNP-P060-DRW-INTERCHANGE-ELEVATED` | — | `STN-CNP-P060-CONN` |
| `STN-CNP-P070` | `STN-CIV-SA100` | `MAKE` | `STN-CNP-P070-DRW-INTERCHANGE-ELEVATED` | — | `STN-CNP-P070-CONN` |
| `STN-CNP-P080` | `STN-CNP-SA300` | `BID` | `STN-CNP-P080-DRW-INTERCHANGE-ELEVATED` | `OSR-STD-E-003`, `OSR-STD-E-004` | — |
| `STN-CNP-P090` | `STN-CNP-SA300` | `SOURCE` | `STN-CNP-P090-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-CHG-P010` | `STN-CHG-SA700` | `BID` | `STN-CHG-P010-DRW-INTERCHANGE-ELEVATED` | — | `STN-CHG-P010-CONN` |
| `STN-CHG-P020` | `STN-CHG-SA700` | `BID` | `STN-CHG-P020-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-ACC-P020` | `STN-ACC-SA600` | `BID` | `STN-ACC-P020-DRW-INTERCHANGE-ELEVATED` | — | — |
| `STN-ACC-P030` | `STN-ACC-SA600` | `BID` | `STN-ACC-P030-DRW-INTERCHANGE-ELEVATED` | — | — |

## Assembly hierarchy

| Assembly ID | Work cell | Direct children |
|---|---|---|
| `STN-CIV-SA100` | civil works | `STN-CIV-P030`, `STN-CNP-P020`, `STN-CNP-P070` |
| `STN-PLT-SA200` | civil/platform construction | `STN-CIV-P010`, `STN-CIV-P020`, `STN-PLT-P010` |
| `STN-CNP-SA300` | steel erection and solar | `STN-CNP-P010`, `STN-CNP-P030`, `STN-CNP-P040`, `STN-CNP-P050`, `STN-CNP-P060`, `STN-CNP-P080`, `STN-CNP-P090` |
| `STN-MEP-SA400` | MEP installation | `STN-MEP-P010`, `STN-MEP-P020`, `STN-MEP-P030`, `STN-MEP-P040` |
| `STN-CHG-SA700` | traction power and charging | `STN-CHG-P010`, `STN-CHG-P020` |
| `STN-PAX-SA500` | systems fit-out | `STN-PAX-P010`, `STN-PAX-P020`, `STN-PAX-P030`, `STN-PAX-P040`, `STN-PAX-P050`, `STN-PAX-P060`, `STN-PAX-P070`, `STN-PAX-P080` |
| `STN-ACC-SA600` | access works | `STN-ACC-P010`, `STN-ACC-P020`, `STN-ACC-P030` |
| `STN-STATION-A900` | station integration | `STN-CIV-SA100`, `STN-PLT-SA200`, `STN-CNP-SA300`, `STN-MEP-SA400`, `STN-CHG-SA700`, `STN-PAX-SA500`, `STN-ACC-SA600` |

## Release boundary

Site survey, geotechnical and structural calculations, supplier selections,
local accessibility/fire approval, signed drawings, inspection records and
as-built survey remain mandatory before construction or operation.
