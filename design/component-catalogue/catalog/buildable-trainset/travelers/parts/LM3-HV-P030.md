# Shop traveler — LM3-HV-P030 — coolant manifold brackets, bleed/drain points, and insulated pipe clamp kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `T4`, `T7`, `T17`, `T20` |

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
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, pressure-test access, bleed point height check, pipe clamp pitch, thermal isolation inspection
- Tooling basis: FIX-LM3-HV-FAB plus GAUGE-LM3-HV-P030-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-HV-P030-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-HV-P030-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-HV-P030-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-HV-P030`<br>`DOC-LM3-HV-SA510` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-HV-FAB`<br>`GAUGE-LM3-HV-P030-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-HV-SA510`<br>`TORQUE-LM3-HV-P030` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: pressure-test access | quality inspection | 0.25 | `LEAK-TEST-LM3-HV-P030` | pressure-test access | quality inspector |
| 50 | verify acceptance gate: bleed point height check | quality inspection | 0.25 | `QA-LM3-HV-P030` | bleed point height check | quality inspector |
| 60 | verify acceptance gate: pipe clamp pitch | quality inspection | 0.25 | `QA-LM3-HV-P030` | pipe clamp pitch | quality inspector |
| 70 | verify acceptance gate: thermal isolation inspection | quality inspection | 0.25 | `ELEC-TEST-LM3-HV-P030` | thermal isolation inspection | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-HV-P030`<br>`KIT-LM3-HV-SA510` | item is released, tagged, and staged for parent assembly | cell lead |

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
