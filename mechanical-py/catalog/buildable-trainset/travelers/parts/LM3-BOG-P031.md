# Shop traveler — LM3-BOG-P031 — trailer-bogie guards, cable guides, WSP brackets, and inspection covers

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.95 h |
| Route | `MAKE` |
| Procurement BOM lines | `G13`, `G20` |

## Material specification

| Field | Value |
|---|---|
| Material family | rail structural steel |
| Grade / part class | EN 10025 S355/S460 candidate bogie structural plate/RHS |
| Governing standard | EN 10025 material certificate; EN 15085 weld-quality evidence for classed rail weldments |
| Form factor | laser/plasma-cut plate, RHS/folded sections, machined bosses, and bracket kit |
| Nominal section | thickness/section per v2A controlled drawing and FEM release |
| Finish / protection | blast, primer/topcoat, cavity/weld-edge protection, and torque-stripe where applicable |
| Traceability | heat number, weld consumable batch, WPS/WPQR, welder ID, and NDT record |

Evidence required:

- mill certificate
- weld consumable certificate
- WPS/WPQR
- NDT report

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, bond continuity, insulation/isolation check where applicable, service access check, harness clearance, fastener torque record
- Tooling basis: FIX-LM3-BOG-FAB plus GAUGE-LM3-BOG-P031-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BOG-P031-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BOG-P031-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BOG-P031-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BOG-P031`<br>`DOC-LM3-BOG-SA620` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-BOG-FAB`<br>`GAUGE-LM3-BOG-P031-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-BOG-SA620`<br>`TORQUE-LM3-BOG-P031` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: service access check | quality inspection | 0.25 | `QA-LM3-BOG-P031` | service access check | quality inspector |
| 50 | verify acceptance gate: harness clearance | quality inspection | 0.25 | `QA-LM3-BOG-P031` | harness clearance | quality inspector |
| 60 | verify acceptance gate: fastener torque record | quality inspection | 0.25 | `TORQUE-LM3-BOG-P031` | fastener torque record | quality inspector |
| 70 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BOG-P031`<br>`KIT-LM3-BOG-SA620` | item is released, tagged, and staged for parent assembly | cell lead |

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
