# Shop traveler — LM3-BDY-P050 — battery tray rails, vent plenum, and service-lid gutter kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.95 h |
| Route | `MAKE` |
| Procurement BOM lines | `B2`, `T17` |

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

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, battery gauge fit, vent-path inspection, gasket land check
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P050-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BDY-P050-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BDY-P050-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BDY-P050-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BDY-P050`<br>`DOC-LM3-HV-SA510` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-BDY-FAB`<br>`GAUGE-LM3-BDY-P050-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-HV-SA510`<br>`TORQUE-LM3-BDY-P050` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: battery gauge fit | quality inspection | 0.25 | `GAUGE-LM3-BDY-P050` | battery gauge fit | quality inspector |
| 50 | verify acceptance gate: vent-path inspection | quality inspection | 0.25 | `QA-LM3-BDY-P050` | vent-path inspection | quality inspector |
| 60 | verify acceptance gate: gasket land check | quality inspection | 0.25 | `QA-LM3-BDY-P050` | gasket land check | quality inspector |
| 70 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BDY-P050`<br>`KIT-LM3-HV-SA510` | item is released, tagged, and staged for parent assembly | cell lead |

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
