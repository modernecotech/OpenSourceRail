# Shop traveler — LM3-FAS-P010 — panoramic front-glass carrier ring, setting-block pockets, and secondary-retention frame

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B8`, `B27` |

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, carrier datum survey, glass-edge clearance gauge, secondary-retention proof, pane removal trial
- Tooling basis: FIX-LM3-FAS-FAB plus GAUGE-LM3-FAS-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-FAS-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-FAS-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-FAS-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-FAS-P010`<br>`DOC-LM3-CWL-SA710` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-FAS-FAB`<br>`GAUGE-LM3-FAS-P010-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-CWL-SA710`<br>`TORQUE-LM3-FAS-P010` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: carrier datum survey | quality inspection | 0.25 | `GAUGE-LM3-FAS-P010` | carrier datum survey | quality inspector |
| 50 | verify acceptance gate: glass-edge clearance gauge | quality inspection | 0.25 | `GAUGE-LM3-FAS-P010` | glass-edge clearance gauge | quality inspector |
| 60 | verify acceptance gate: secondary-retention proof | quality inspection | 0.25 | `QA-LM3-FAS-P010` | secondary-retention proof | quality inspector |
| 70 | verify acceptance gate: pane removal trial | quality inspection | 0.25 | `QA-LM3-FAS-P010` | pane removal trial | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-FAS-P010`<br>`KIT-LM3-CWL-SA710` | item is released, tagged, and staged for parent assembly | cell lead |

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
