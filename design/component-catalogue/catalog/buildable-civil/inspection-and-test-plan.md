# Civil Inspection and Test Plan

> Status: **unfilled protocol — not fabrication, construction, inspection or test evidence**.

This plan assigns unique characteristics to every civil package prerequisite, drawing,
reusable IFC type, tool/gauge, workface control and handover output. Project-specific
values and results remain blank until competent teams execute an authorised workfront.

Packages: **6** · Characteristics: **114**.

Point types: **H** mandatory hold, **W** witness, **R** record review.

| Package | Lane | Characteristics | H | W | R | Status |
|---|---|---:|---:|---:|---:|---|
| `CIV-FRP-100` — precast superstructure and guideway edge | `reusable-product` | 24 | 10 | 7 | 7 | `open` |
| `CIV-FRP-110` — pier column and precast cap | `hybrid-project-product` | 21 | 8 | 7 | 6 | `open` |
| `CIV-FRP-120` — bearing, restraint and replacement interfaces | `supplier-configured` | 16 | 7 | 4 | 5 | `open` |
| `CIV-FRP-130` — at-grade slab and transition | `deployment-led-product` | 18 | 8 | 5 | 5 | `open` |
| `CIV-INT-200` — track and station-deck interfaces | `coordination-interface` | 16 | 9 | 3 | 4 | `open` |
| `CIV-INT-210` — station and vehicle envelope interfaces | `coordination-interface` | 19 | 12 | 3 | 4 | `open` |

## Execution Rules

- bind every result to project, asset/workfront, location, drawing/method revision, people, plant and date
- coordination IFC, an empty form or planned inspection is not performed evidence
- stop and contain affected work on failure; link the accepted NCR/RFI disposition and repeated inspection before release
- do not sample away survey control, foundations, lifting, bearings, movement joints, track geometry, platform stepping or other safety/interface characteristics
- handover requires accepted as-builts, tests, temporary-condition register, NCR status and receiving-party signature

Use [`construction-control-record-template.json`](evidence/construction-control-record-template.json)
for each asset/workfront and retain the ITP characteristic IDs when importing into a project QMS.
All project release evidence remains governed by the [deployment checklist](../../../../docs/civil/deployment-release-checklist.md).
