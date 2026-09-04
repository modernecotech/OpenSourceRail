# Shop traveler — LM3-BDY-SA110 — underframe datum weldment

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 8.36 h |
| Build cell | weld and fixture cell |
| Procurement BOM lines | `B3`, `B4`, `B26` |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BDY-SA110 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, formed sheet metal / stainless local hardware |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, fixture tack/weld, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, WPS-controlled structural welding
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, weld map release, WPS/WPQR and welder qualification
- Inspection methods: child acceptance evidence review, material release, fixture tack survey, weld/NDT release, post-weld datum survey, VT, MT/UT where classed
- Tooling basis: FIX-LM3-BDY-SA110, KIT-LM3-BDY-SA110, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BDY-SA110-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BDY-SA110-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BDY-SA110-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | weld and fixture cell | 0.85 | `TRV-LM3-BDY-SA110`<br>`FIX-LM3-BDY-SA110`<br>`KIT-LM3-BDY-SA110` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-P010: laser-cut side sill beam, LH/RH | weld and fixture cell | 1.12 | `FIX-LM3-BDY-SA110`<br>`GAUGE-LM3-BDY-P010`<br>`TORQUE-LM3-BDY-P010` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-BDY-P020: underframe centre spine and longitudinal load-path kit | weld and fixture cell | 1.12 | `FIX-LM3-BDY-SA110`<br>`GAUGE-LM3-BDY-P020`<br>`TORQUE-LM3-BDY-P020` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 40 | install and integrate LM3-BDY-P021: underframe cross-bearer, door-bay outrigger, and equipment-bracket pack | weld and fixture cell | 1.35 | `FIX-LM3-BDY-SA110`<br>`GAUGE-LM3-BDY-P021`<br>`TORQUE-LM3-BDY-P021` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 50 | install and integrate LM3-BDY-P030: bolster box, air-spring pad, and centre-pivot insert set | weld and fixture cell | 1.12 | `FIX-LM3-BDY-SA110`<br>`GAUGE-LM3-BDY-P030`<br>`TORQUE-LM3-BDY-P030` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 60 | install and integrate LM3-BDY-P120: jacking pad, lifting eye, towing lug, and recovery-label kit | weld and fixture cell | 1.1 | `FIX-LM3-BDY-SA110`<br>`GAUGE-LM3-BDY-P120`<br>`TORQUE-LM3-BDY-P120` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 70 | hold point: material release | quality inspection | 0.35 | `QA-LM3-BDY-SA110` | material release | quality inspector |
| 80 | hold point: fixture tack survey | quality inspection | 0.35 | `GAUGE-LM3-BDY-SA110` | fixture tack survey | quality inspector |
| 90 | hold point: weld/NDT release | quality inspection | 0.35 | `NDT-LM3-BDY-SA110` | weld/NDT release | quality inspector |
| 100 | hold point: post-weld datum survey | quality inspection | 0.35 | `GAUGE-LM3-BDY-SA110` | post-weld datum survey | quality inspector |
| 110 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-BDY-SA110`<br>`NCR-LM3-BDY-SA110` | all operation and QA signoffs are complete | manufacturing engineer |

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
