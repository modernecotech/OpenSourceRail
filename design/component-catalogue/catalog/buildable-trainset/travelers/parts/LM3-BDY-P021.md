# Shop traveler — LM3-BDY-P021 — underframe cross-bearer, door-bay outrigger, and equipment-bracket pack

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B1` |

## Material specification

| Field | Value |
|---|---|
| Material family | formed sheet metal / stainless local hardware |
| Grade / part class | S355 or 304/316 stainless local bracket/tray candidate, selected by exposure zone |
| Governing standard | EN 10025 / EN 10088 certificate as applicable plus project bonding/corrosion evidence |
| Form factor | laser-cut, folded, drilled sheet/plate with inserts, studs, clips, and labels |
| Nominal section | thickness, stainless grade, and galvanic isolation frozen by v2A controlled drawing |
| Finish / protection | zinc/paint/stainless passivation, orange HV marking, edge protection, and sealing as applicable |
| Traceability | heat number, coating batch, bonding test, and installation batch traceability |

Evidence required:

- mill certificate
- coating/passivation record
- bonding continuity record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, cut-list identity, cross-bearer profile gauge, station map, fixture tack survey
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P021-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BDY-P021-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BDY-P021-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BDY-P021-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BDY-P021`<br>`DOC-LM3-BDY-SA110` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-BDY-FAB`<br>`GAUGE-LM3-BDY-P021-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-BDY-SA110`<br>`TORQUE-LM3-BDY-P021` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: cut-list identity | quality inspection | 0.25 | `QA-LM3-BDY-P021` | cut-list identity | quality inspector |
| 50 | verify acceptance gate: cross-bearer profile gauge | quality inspection | 0.25 | `GAUGE-LM3-BDY-P021` | cross-bearer profile gauge | quality inspector |
| 60 | verify acceptance gate: station map | quality inspection | 0.25 | `QA-LM3-BDY-P021` | station map | quality inspector |
| 70 | verify acceptance gate: fixture tack survey | quality inspection | 0.25 | `GAUGE-LM3-BDY-P021` | fixture tack survey | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BDY-P021`<br>`KIT-LM3-BDY-SA110` | item is released, tagged, and staged for parent assembly | cell lead |

## Operator / inspection signoff block

| Role | Name | Date | Signature | Status |
|---|---|---|---|---|
| operator |  |  |  | `blank` |
| cell lead |  |  |  | `blank` |
| quality inspector |  |  |  | `blank` |
| manufacturing engineer |  |  |  | `blank` |

## Nonconformance / deviation log

| NCR / deviation ID | Operation seq | Disposition | Approver | Closure date |
|---|---:|---|---|---|
|  |  |  |  |  |
