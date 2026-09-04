# Shop traveler — LM3-CWL-SA710 — front/back fiberglass cowl cast kit

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 15.25 h |
| Build cell | composite moulding and trim cell |
| Procurement BOM lines | `B8` |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-CWL-SA710 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | fire-retardant fiberglass composite, rail structural steel, formed sheet metal / stainless local hardware |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, adhesive/bonded/gasketed sealing interfaces
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record
- Inspection methods: child acceptance evidence review, laminate coupon release, insert pull-out, trim/drill survey, A/B-end dry-build water test, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-CWL-SA710, KIT-LM3-CWL-SA710, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-CWL-SA710-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-CWL-SA710-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-CWL-SA710-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | composite moulding and trim cell | 1.25 | `TRV-LM3-CWL-SA710`<br>`FIX-LM3-CWL-SA710`<br>`KIT-LM3-CWL-SA710` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-CWL-P010: end-cowl fiberglass laminate, insert, adhesive, and coupon material kit | composite moulding and trim cell | 1.29 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P010`<br>`TORQUE-LM3-CWL-P010` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 30 | install and integrate LM3-CWL-P011: CWL-FRP-01 upper brow and roof-cap fiberglass cast | composite moulding and trim cell | 1.17 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P011`<br>`TORQUE-LM3-CWL-P011` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 40 | install and integrate LM3-CWL-P012: CWL-FRP-02 left cheek fiberglass cast | composite moulding and trim cell | 1.17 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P012`<br>`TORQUE-LM3-CWL-P012` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 50 | install and integrate LM3-CWL-P013: CWL-FRP-03 right cheek fiberglass cast | composite moulding and trim cell | 1.17 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P013`<br>`TORQUE-LM3-CWL-P013` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 60 | install and integrate LM3-CWL-P014: CWL-FRP-04 lower apron and anti-climber cover fiberglass cast | composite moulding and trim cell | 1.17 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P014`<br>`TORQUE-LM3-CWL-P014` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 70 | install and integrate LM3-CWL-P015: CWL-FRP-05 lamp, washer, and service-hatch fiberglass cast set | composite moulding and trim cell | 1.59 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P015`<br>`TORQUE-LM3-CWL-P015` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 80 | install and integrate LM3-CWL-P016: CWL-FRP-06 backing-ring flange fiberglass cast set | composite moulding and trim cell | 1.17 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-CWL-P016`<br>`TORQUE-LM3-CWL-P016` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 90 | install and integrate LM3-FAS-P010: panoramic front-glass carrier ring, setting-block pockets, and secondary-retention frame | composite moulding and trim cell | 1.05 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-FAS-P010`<br>`TORQUE-LM3-FAS-P010` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 100 | install and integrate LM3-FAS-P020: reversible front-lamp cassette tray, aiming adjusters, and retained service bracket | composite moulding and trim cell | 1.05 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-FAS-P020`<br>`TORQUE-LM3-FAS-P020` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 110 | install and integrate LM3-FAS-P030: front glazing/lamp EPDM seal, drain rail, washer sleeve, and edge-closeout kit | composite moulding and trim cell | 1.47 | `FIX-LM3-CWL-SA710`<br>`GAUGE-LM3-FAS-P030`<br>`TORQUE-LM3-FAS-P030` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 120 | hold point: laminate coupon release | quality inspection | 0.35 | `QA-LM3-CWL-SA710` | laminate coupon release | quality inspector |
| 130 | hold point: insert pull-out | quality inspection | 0.35 | `QA-LM3-CWL-SA710` | insert pull-out | quality inspector |
| 140 | hold point: trim/drill survey | quality inspection | 0.35 | `GAUGE-LM3-CWL-SA710` | trim/drill survey | quality inspector |
| 150 | hold point: A/B-end dry-build water test | quality inspection | 0.35 | `LEAK-TEST-LM3-CWL-SA710` | A/B-end dry-build water test | quality inspector |
| 160 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-CWL-SA710`<br>`NCR-LM3-CWL-SA710` | all operation and QA signoffs are complete | manufacturing engineer |

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
