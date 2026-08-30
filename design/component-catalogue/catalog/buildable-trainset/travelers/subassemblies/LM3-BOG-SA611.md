# Shop traveler — LM3-BOG-SA611 — powered-bogie running unit: wheelsets, axleboxes, primary suspension and brakes

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 7.83 h |
| Build cell | bogie clean assembly and brake cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BOG-SA611 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier-certified running gear, supplier-controlled external component |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, wheelset identity, bearing installation, primary-height match, static brake/WSP test, free rotation, alignment survey, static brake test
- Tooling basis: FIX-LM3-BOG-SA611, KIT-LM3-BOG-SA611, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BOG-SA611-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BOG-SA611-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BOG-SA611-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | bogie clean assembly and brake cell | 0.77 | `TRV-LM3-BOG-SA611`<br>`FIX-LM3-BOG-SA611`<br>`KIT-LM3-BOG-SA611` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BOG-P040: powered-bogie wheelset with axle-mounted brake discs | bogie clean assembly and brake cell | 1.28 | `FIX-LM3-BOG-SA611`<br>`GAUGE-LM3-BOG-P040`<br>`TORQUE-LM3-BOG-P040` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 30 | install and integrate LM3-BOG-P042: powered-wheelset axlebox, sealed bearing unit, speed and temperature sensor set | bogie clean assembly and brake cell | 1.4 | `FIX-LM3-BOG-SA611`<br>`GAUGE-LM3-BOG-P042`<br>`TORQUE-LM3-BOG-P042` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 40 | install and integrate LM3-BOG-P044: powered-bogie primary suspension spring, guide and bump-stop set | bogie clean assembly and brake cell | 1.05 | `FIX-LM3-BOG-SA611`<br>`GAUGE-LM3-BOG-P044`<br>`TORQUE-LM3-BOG-P044` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 50 | install and integrate LM3-BOG-P048: powered-bogie brake calipers, parking actuators, pads and wheel-slide hardware | bogie clean assembly and brake cell | 1.28 | `FIX-LM3-BOG-SA611`<br>`GAUGE-LM3-BOG-P048`<br>`TORQUE-LM3-BOG-P048` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 60 | hold point: wheelset identity | quality inspection | 0.35 | `QA-LM3-BOG-SA611` | wheelset identity | quality inspector |
| 70 | hold point: bearing installation | quality inspection | 0.35 | `QA-LM3-BOG-SA611` | bearing installation | quality inspector |
| 80 | hold point: primary-height match | quality inspection | 0.35 | `QA-LM3-BOG-SA611` | primary-height match | quality inspector |
| 90 | hold point: static brake/WSP test | quality inspection | 0.35 | `QA-LM3-BOG-SA611` | static brake/WSP test | quality inspector |
| 100 | hold point: free rotation | quality inspection | 0.35 | `QA-LM3-BOG-SA611` | free rotation | quality inspector |
| 110 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-BOG-SA611`<br>`NCR-LM3-BOG-SA611` | all operation and QA signoffs are complete | manufacturing engineer |

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
