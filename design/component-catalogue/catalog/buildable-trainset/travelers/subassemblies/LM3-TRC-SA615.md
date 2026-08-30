# Shop traveler — LM3-TRC-SA615 — bogie-mounted motor, gearbox, flexible coupling and torque-reaction drive unit

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.44 h |
| Build cell | traction drive clean assembly cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-TRC-SA615 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier traction drive equipment, supplier HVAC and air-distribution kit, rail structural steel |
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
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, motor/gearbox serial match, coupling alignment, torque-link proof, insulation/rotation test, removal-envelope trial, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test, alignment survey, static brake test
- Tooling basis: FIX-LM3-TRC-SA615, KIT-LM3-TRC-SA615, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TRC-SA615-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TRC-SA615-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TRC-SA615-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | traction drive clean assembly cell | 0.69 | `TRV-LM3-TRC-SA615`<br>`FIX-LM3-TRC-SA615`<br>`KIT-LM3-TRC-SA615` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-TRC-P010: motor-350kw-hm47-class axle traction motor | traction drive clean assembly cell | 1.35 | `FIX-LM3-TRC-SA615`<br>`GAUGE-LM3-TRC-P010`<br>`TORQUE-LM3-TRC-P010` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 30 | install and integrate LM3-TRC-P020: single-stage reduction gearbox and flexible coupling | traction drive clean assembly cell | 1.0 | `FIX-LM3-TRC-SA615`<br>`GAUGE-LM3-TRC-P020`<br>`TORQUE-LM3-TRC-P020` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 40 | install and integrate LM3-BOG-P050: powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit | traction drive clean assembly cell | 1.35 | `FIX-LM3-TRC-SA615`<br>`GAUGE-LM3-BOG-P050`<br>`TORQUE-LM3-BOG-P050` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 50 | hold point: motor/gearbox serial match | quality inspection | 0.35 | `QA-LM3-TRC-SA615` | motor/gearbox serial match | quality inspector |
| 60 | hold point: coupling alignment | quality inspection | 0.35 | `QA-LM3-TRC-SA615` | coupling alignment | quality inspector |
| 70 | hold point: torque-link proof | quality inspection | 0.35 | `TORQUE-LM3-TRC-SA615` | torque-link proof | quality inspector |
| 80 | hold point: insulation/rotation test | quality inspection | 0.35 | `QA-LM3-TRC-SA615` | insulation/rotation test | quality inspector |
| 90 | hold point: removal-envelope trial | quality inspection | 0.35 | `QA-LM3-TRC-SA615` | removal-envelope trial | quality inspector |
| 100 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-TRC-SA615`<br>`NCR-LM3-TRC-SA615` | all operation and QA signoffs are complete | manufacturing engineer |

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
