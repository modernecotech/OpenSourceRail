# `standard` station definition

**Status:** deterministic design-reference package; not construction release.

The shared envelope, canopy, accessibility, services, compliance and
43-drawing register live in [`docs/stations/standard-archetype/`](../../../../../docs/stations/standard-archetype/).
This page is the complete archetype delta and stable-ID bridge into its BOM,
traveler, FreeCAD installed/exploded states and IFC4.3 assembly.

## Parameter delta from `standard`

| Parameter | Standard | This variant |
|---|---:|---:|
| _none_ | — | — |

Unique product rows: none; this is the governing shared variant.

## Controlled handoffs

- BOM: `build/bom/stations/standard.csv`
- traveler: [`../travelers/standard.md`](../travelers/standard.md)
- FreeCAD: [`../../../models/cad/stations/station-standard.FCStd`](../../../models/cad/stations/station-standard.FCStd)
- assembly-state map: [`../../../models/cad/stations/station-standard.assembly-review.json`](../../../models/cad/stations/station-standard.assembly-review.json)
- IFC4.3: [`../../../../../engineering/models/bim/reference/stations/station-standard.ifc`](../../../../../engineering/models/bim/reference/stations/station-standard.ifc)

## Product/drawing/connection identity

The definition-sheet ID keeps the product ID intact. It identifies the
deployment drawing that must be produced and approved; it does not claim
that a construction drawing has already been released. `CONN` rows identify
where a controlled fastener, anchor, seal, terminal, weld or grout schedule is required.

| Product ID | Parent | Route | Definition sheet | Shared drawings | Connection control |
|---|---|---|---|---|---|
| `STN-CIV-P010` | `STN-PLT-SA200` | `MAKE` | `STN-CIV-P010-DRW-STANDARD` | — | — |
| `STN-CIV-P020` | `STN-PLT-SA200` | `MAKE` | `STN-CIV-P020-DRW-STANDARD` | — | `STN-CIV-P020-CONN` |
| `STN-CIV-P030` | `STN-CIV-SA100` | `MAKE` | `STN-CIV-P030-DRW-STANDARD` | `OSR-STD-M-002` | — |
| `STN-CIV-P040` | `STN-PLT-SA200` | `MAKE` | `STN-CIV-P040-DRW-STANDARD` | `OSR-STD-A-011` | — |
| `STN-PLT-P010` | `STN-PLT-SA200` | `SOURCE` | `STN-PLT-P010-DRW-STANDARD` | `OSR-STD-A-011` | — |
| `STN-CNP-P010` | `STN-CNP-SA300` | `MAKE` | `STN-CNP-P010-DRW-STANDARD` | — | — |
| `STN-CNP-P020` | `STN-CIV-SA100` | `MAKE` | `STN-CNP-P020-DRW-STANDARD` | `OSR-STD-S-001`, `OSR-STD-S-002` | `STN-CNP-P020-CONN` |
| `STN-CNP-P030` | `STN-CNP-SA300` | `BID` | `STN-CNP-P030-DRW-STANDARD` | `OSR-STD-E-003` | `STN-CNP-P030-CONN` |
| `STN-CNP-P040` | `STN-CNP-SA300` | `BID` | `STN-CNP-P040-DRW-STANDARD` | `OSR-STD-E-003`, `OSR-STD-E-004`, `OSR-STD-E-008` | — |
| `STN-MEP-P010` | `STN-MEP-SA400` | `MAKE` | `STN-MEP-P010-DRW-STANDARD` | `OSR-STD-A-013`, `OSR-STD-M-001` | `STN-MEP-P010-CONN` |
| `STN-MEP-P020` | `STN-MEP-SA400` | `BID` | `STN-MEP-P020-DRW-STANDARD` | `OSR-STD-E-001`, `OSR-STD-E-005` | — |
| `STN-MEP-P030` | `STN-MEP-SA400` | `SOURCE` | `STN-MEP-P030-DRW-STANDARD` | `OSR-STD-E-002`, `OSR-STD-E-005` | — |
| `STN-MEP-P040` | `STN-MEP-SA400` | `SOURCE` | `STN-MEP-P040-DRW-STANDARD` | `OSR-STD-F-001`, `OSR-STD-F-004` | — |
| `STN-PAX-P010` | `STN-PAX-SA500` | `SOURCE` | `STN-PAX-P010-DRW-STANDARD` | — | — |
| `STN-PAX-P020` | `STN-PAX-SA500` | `SOURCE` | `STN-PAX-P020-DRW-STANDARD` | `OSR-STD-E-007` | — |
| `STN-PAX-P030` | `STN-PAX-SA500` | `BID` | `STN-PAX-P030-DRW-STANDARD` | `OSR-STD-E-006`, `OSR-STD-E-007` | — |
| `STN-PAX-P040` | `STN-PAX-SA500` | `BID` | `STN-PAX-P040-DRW-STANDARD` | `OSR-STD-A-003`, `OSR-STD-A-014` | `STN-PAX-P040-CONN` |
| `STN-PAX-P050` | `STN-PAX-SA500` | `BID` | `STN-PAX-P050-DRW-STANDARD` | `OSR-STD-A-003` | — |
| `STN-PAX-P070` | `STN-PAX-SA500` | `MAKE` | `STN-PAX-P070-DRW-STANDARD` | `OSR-STD-A-014`, `OSR-STD-S-007` | `STN-PAX-P070-CONN` |
| `STN-PAX-P080` | `STN-PAX-SA500` | `MAKE` | `STN-PAX-P080-DRW-STANDARD` | `OSR-STD-A-003`, `OSR-STD-S-007` | `STN-PAX-P080-CONN` |
| `STN-PAX-P060` | `STN-PAX-SA500` | `SOURCE` | `STN-PAX-P060-DRW-STANDARD` | `OSR-STD-T-001`, `OSR-STD-T-003` | — |
| `STN-ACC-P010` | `STN-ACC-SA600` | `MAKE` | `STN-ACC-P010-DRW-STANDARD` | `OSR-STD-A-012`, `OSR-STD-M-004` | — |
| `STN-CNP-P050` | `STN-CNP-SA300` | `BID` | `STN-CNP-P050-DRW-STANDARD` | — | — |
| `STN-CNP-P060` | `STN-CNP-SA300` | `MAKE` | `STN-CNP-P060-DRW-STANDARD` | — | `STN-CNP-P060-CONN` |
| `STN-CNP-P070` | `STN-CIV-SA100` | `MAKE` | `STN-CNP-P070-DRW-STANDARD` | — | `STN-CNP-P070-CONN` |
| `STN-CNP-P080` | `STN-CNP-SA300` | `BID` | `STN-CNP-P080-DRW-STANDARD` | `OSR-STD-E-003`, `OSR-STD-E-004` | — |
| `STN-CNP-P090` | `STN-CNP-SA300` | `SOURCE` | `STN-CNP-P090-DRW-STANDARD` | — | — |
| `STN-CHG-P010` | `STN-CHG-SA700` | `BID` | `STN-CHG-P010-DRW-STANDARD` | — | `STN-CHG-P010-CONN` |

## Assembly hierarchy

| Assembly ID | Work cell | Direct children |
|---|---|---|
| `STN-CIV-SA100` | civil works | `STN-CIV-P030`, `STN-CNP-P020`, `STN-CNP-P070` |
| `STN-PLT-SA200` | civil/platform construction | `STN-CIV-P010`, `STN-CIV-P020`, `STN-CIV-P040`, `STN-PLT-P010` |
| `STN-CNP-SA300` | steel erection and solar | `STN-CNP-P010`, `STN-CNP-P030`, `STN-CNP-P040`, `STN-CNP-P050`, `STN-CNP-P060`, `STN-CNP-P080`, `STN-CNP-P090` |
| `STN-MEP-SA400` | MEP installation | `STN-MEP-P010`, `STN-MEP-P020`, `STN-MEP-P030`, `STN-MEP-P040` |
| `STN-CHG-SA700` | traction power and charging | `STN-CHG-P010` |
| `STN-PAX-SA500` | systems fit-out | `STN-PAX-P010`, `STN-PAX-P020`, `STN-PAX-P030`, `STN-PAX-P040`, `STN-PAX-P050`, `STN-PAX-P060`, `STN-PAX-P070`, `STN-PAX-P080` |
| `STN-ACC-SA600` | access works | `STN-ACC-P010` |
| `STN-STATION-A900` | station integration | `STN-CIV-SA100`, `STN-PLT-SA200`, `STN-CNP-SA300`, `STN-MEP-SA400`, `STN-CHG-SA700`, `STN-PAX-SA500`, `STN-ACC-SA600` |

## Release boundary

Site survey, geotechnical and structural calculations, supplier selections,
local accessibility/fire approval, signed drawings, inspection records and
as-built survey remain mandatory before construction or operation.
