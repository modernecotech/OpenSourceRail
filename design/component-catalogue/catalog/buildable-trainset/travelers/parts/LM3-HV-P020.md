# Shop traveler — LM3-HV-P020 — segregated HV cable tray, bonding studs, grommets, and orange cover set

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `T18` |

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, surface-preparation record, adhesive batch/pot-life record, bond coupon where required, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond-land inspection, water/leak test where applicable, bond continuity, insulation/isolation check where applicable, bend-radius gauge, cover fastener torque, orange-label inspection
- Tooling basis: FIX-LM3-HV-FAB plus GAUGE-LM3-HV-P020-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-HV-P020-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-HV-P020-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-HV-P020-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-HV-P020`<br>`DOC-LM3-HV-SA510` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-HV-FAB`<br>`GAUGE-LM3-HV-P020-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-HV-SA510`<br>`TORQUE-LM3-HV-P020` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: bend-radius gauge | quality inspection | 0.25 | `GAUGE-LM3-HV-P020` | bend-radius gauge | quality inspector |
| 50 | verify acceptance gate: bond continuity | quality inspection | 0.25 | `ELEC-TEST-LM3-HV-P020` | bond continuity | quality inspector |
| 60 | verify acceptance gate: cover fastener torque | quality inspection | 0.25 | `TORQUE-LM3-HV-P020` | cover fastener torque | quality inspector |
| 70 | verify acceptance gate: orange-label inspection | quality inspection | 0.25 | `QA-LM3-HV-P020` | orange-label inspection | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-HV-P020`<br>`KIT-LM3-HV-SA510` | item is released, tagged, and staged for parent assembly | cell lead |

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
