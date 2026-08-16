# Shop traveler — LM3-END-SA700 — train-end cowl, coupler, crash, and sensor assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 15.01 h |
| Build cell | composite / final assembly and commissioning cells |
| Procurement BOM lines | `B17`, `B26` |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-END-SA700 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, LM3-CWL-SA710 child assembly material set, fire-retardant fiberglass composite, supplier crash/coupler system, formed sheet metal / stainless local hardware |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, adhesive/bonded/gasketed sealing interfaces, bonding/earthing, segregated harness/fluid routing
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable
- Inspection methods: child acceptance evidence review, A/B end interchange, coupler datum survey, sensor calibration, recovery interface check, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-END-SA700, KIT-LM3-END-SA700, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-END-SA700-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-END-SA700-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-END-SA700-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | composite / final assembly and commissioning cells | 1.17 | `TRV-LM3-END-SA700`<br>`FIX-LM3-END-SA700`<br>`KIT-LM3-END-SA700` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-P040: coupler pocket, shear plate, and crash-can insert kit | composite / final assembly and commissioning cells | 1.18 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-BDY-P040`<br>`TORQUE-LM3-BDY-P040` | placement zone and joint controls accepted: train-end cowl, crash, coupler, and sensor datum stack | operator |
| 30 | install and integrate LM3-BDY-P090: end ring frame and anti-climber beam set | composite / final assembly and commissioning cells | 1.12 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-BDY-P090`<br>`TORQUE-LM3-BDY-P090` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 40 | install and integrate LM3-CWL-SA710: front/back fiberglass cowl cast kit | composite / final assembly and commissioning cells | 1.29 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-CWL-SA710`<br>`TORQUE-LM3-CWL-SA710` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 50 | install and integrate LM3-EXT-P030: single panoramic heated end-glass assembly | composite / final assembly and commissioning cells | 1.0 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-EXT-P030`<br>`TORQUE-LM3-EXT-P030` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 60 | install and integrate LM3-END-P010: automatic end coupler and crash-energy absorber | composite / final assembly and commissioning cells | 1.18 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-END-P010`<br>`TORQUE-LM3-END-P010` | placement zone and joint controls accepted: train-end cowl, crash, coupler, and sensor datum stack | operator |
| 70 | install and integrate LM3-END-P020: T-OBS nose sensor pack, heated window services, and washer kit | composite / final assembly and commissioning cells | 1.72 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-END-P020`<br>`TORQUE-LM3-END-P020` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 80 | install and integrate LM3-END-P030: cowl service hatch, sensor backing bracket, washer-tube, and heater-cable clip kit | composite / final assembly and commissioning cells | 1.77 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-END-P030`<br>`TORQUE-LM3-END-P030` | placement zone and joint controls accepted: train-end cowl, crash, coupler, and sensor datum stack | operator |
| 90 | install and integrate LM3-END-P040: e-coupler LV jumper, recovery trainline, and end harness breakaway kit | composite / final assembly and commissioning cells | 1.53 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-END-P040`<br>`TORQUE-LM3-END-P040` | placement zone and joint controls accepted: train-end cowl, crash, coupler, and sensor datum stack | operator |
| 100 | install and integrate LM3-END-P050: sealed headlight, tail/marker light, threshold-warning, and end-lamp harness kit | composite / final assembly and commissioning cells | 1.35 | `FIX-LM3-END-SA700`<br>`GAUGE-LM3-END-P050`<br>`TORQUE-LM3-END-P050` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 110 | hold point: A/B end interchange | quality inspection | 0.35 | `QA-LM3-END-SA700` | A/B end interchange | quality inspector |
| 120 | hold point: coupler datum survey | quality inspection | 0.35 | `GAUGE-LM3-END-SA700` | coupler datum survey | quality inspector |
| 130 | hold point: sensor calibration | quality inspection | 0.35 | `QA-LM3-END-SA700` | sensor calibration | quality inspector |
| 140 | hold point: recovery interface check | quality inspection | 0.35 | `QA-LM3-END-SA700` | recovery interface check | quality inspector |
| 150 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-END-SA700`<br>`NCR-LM3-END-SA700` | all operation and QA signoffs are complete | manufacturing engineer |

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
