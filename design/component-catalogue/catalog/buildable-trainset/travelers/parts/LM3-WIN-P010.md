# Shop traveler — LM3-WIN-P010 — replaceable window pressure frame, dry seal, drain, and captive retention kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B10` |

## Material specification

| Field | Value |
|---|---|
| Material family | rail structural steel |
| Grade / part class | EN 10025 S355 candidate primary-structure RHS/folded plate |
| Governing standard | EN 10025 material certificate; EN 15085 weld-quality evidence for classed rail weldments |
| Form factor | laser-cut RHS/plate, press-brake folds, drilled/machined inserts, and bracket kit |
| Nominal section | thickness/section per v2A controlled drawing and FEM release |
| Finish / protection | blast, rail primer/topcoat, cavity wax/sealant, and weld-edge protection |
| Traceability | heat number, weld consumable batch, WPS/WPQR, welder ID, and NDT record |

Evidence required:

- mill certificate
- weld consumable certificate
- WPS/WPQR
- NDT report

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control, surface-preparation record, adhesive batch/pot-life record, bond coupon where required
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, bond-land inspection, water/leak test where applicable, pressure-frame gauge, retention calculation, seal compression record, water-ingress and replacement trial
- Tooling basis: FIX-LM3-WIN-FAB plus GAUGE-LM3-WIN-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-WIN-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-WIN-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-WIN-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-WIN-P010`<br>`DOC-LM3-WIN-SA320` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-WIN-FAB`<br>`GAUGE-LM3-WIN-P010-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-WIN-SA320`<br>`TORQUE-LM3-WIN-P010` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: pressure-frame gauge | quality inspection | 0.25 | `GAUGE-LM3-WIN-P010` | pressure-frame gauge | quality inspector |
| 50 | verify acceptance gate: retention calculation | quality inspection | 0.25 | `QA-LM3-WIN-P010` | retention calculation | quality inspector |
| 60 | verify acceptance gate: seal compression record | quality inspection | 0.25 | `QA-LM3-WIN-P010` | seal compression record | quality inspector |
| 70 | verify acceptance gate: water-ingress and replacement trial | quality inspection | 0.25 | `LEAK-TEST-LM3-WIN-P010` | water-ingress and replacement trial | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-WIN-P010`<br>`KIT-LM3-WIN-SA320` | item is released, tagged, and staged for parent assembly | cell lead |

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
