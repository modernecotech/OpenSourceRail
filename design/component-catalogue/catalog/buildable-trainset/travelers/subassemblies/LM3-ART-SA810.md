# Shop traveler — LM3-ART-SA810 — structural articulation joint and anti-lift load path

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.43 h |
| Build cell | articulation bench and proof-load cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA810 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-certified running gear, supplier-controlled external component |
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
- Inspection methods: child acceptance evidence review, pin/bearing identity, shimmed datum survey, proof load, lubrication/seal release, motion sweep, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-ART-SA810, KIT-LM3-ART-SA810, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-SA810-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-SA810-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-SA810-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | articulation bench and proof-load cell | 0.69 | `TRV-LM3-ART-SA810`<br>`FIX-LM3-ART-SA810`<br>`KIT-LM3-ART-SA810` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-ART-P010: articulation adapter frame, anti-lift keeper, and shim kit | articulation bench and proof-load cell | 1.18 | `FIX-LM3-ART-SA810`<br>`GAUGE-LM3-ART-P010`<br>`TORQUE-LM3-ART-P010` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 30 | install and integrate LM3-ART-P020: articulation lower spherical pivot, bearing housing and pin set | articulation bench and proof-load cell | 1.28 | `FIX-LM3-ART-SA810`<br>`GAUGE-LM3-ART-P020`<br>`TORQUE-LM3-ART-P020` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 40 | install and integrate LM3-ART-P021: articulation upper lateral/yaw links, spherical joints and retained pins | articulation bench and proof-load cell | 1.23 | `FIX-LM3-ART-SA810`<br>`GAUGE-LM3-ART-P021`<br>`TORQUE-LM3-ART-P021` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 50 | hold point: pin/bearing identity | quality inspection | 0.35 | `QA-LM3-ART-SA810` | pin/bearing identity | quality inspector |
| 60 | hold point: shimmed datum survey | quality inspection | 0.35 | `GAUGE-LM3-ART-SA810` | shimmed datum survey | quality inspector |
| 70 | hold point: proof load | quality inspection | 0.35 | `QA-LM3-ART-SA810` | proof load | quality inspector |
| 80 | hold point: lubrication/seal release | quality inspection | 0.35 | `QA-LM3-ART-SA810` | lubrication/seal release | quality inspector |
| 90 | hold point: motion sweep | quality inspection | 0.35 | `QA-LM3-ART-SA810` | motion sweep | quality inspector |
| 100 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-ART-SA810`<br>`NCR-LM3-ART-SA810` | all operation and QA signoffs are complete | manufacturing engineer |

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
