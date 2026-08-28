# Shop traveler — LM3-WIN-SA320 — side glazing cassette installation

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 5.68 h |
| Build cell | composite / glazing cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-WIN-SA320 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, fire-retardant fiberglass composite |
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
- Inspection methods: child acceptance evidence review, aperture gauge, bond/gasket procedure, water ingress test, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-WIN-SA320, KIT-LM3-WIN-SA320, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-WIN-SA320-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-WIN-SA320-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-WIN-SA320-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | composite / glazing cell | 0.69 | `TRV-LM3-WIN-SA320`<br>`FIX-LM3-WIN-SA320`<br>`KIT-LM3-WIN-SA320` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-P110: window carrier ring, bonded-gasket land, and replacement jack-point inserts | composite / glazing cell | 1.17 | `FIX-LM3-WIN-SA320`<br>`GAUGE-LM3-BDY-P110`<br>`TORQUE-LM3-BDY-P110` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 30 | install and integrate LM3-WIN-P010: replaceable window pressure frame, dry seal, drain, and captive retention kit | composite / glazing cell | 1.35 | `FIX-LM3-WIN-SA320`<br>`GAUGE-LM3-WIN-P010`<br>`TORQUE-LM3-WIN-P010` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 40 | install and integrate LM3-EXT-P020: side laminated glazing cassette | composite / glazing cell | 1.12 | `FIX-LM3-WIN-SA320`<br>`GAUGE-LM3-EXT-P020`<br>`TORQUE-LM3-EXT-P020` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 50 | hold point: aperture gauge | quality inspection | 0.35 | `GAUGE-LM3-WIN-SA320` | aperture gauge | quality inspector |
| 60 | hold point: bond/gasket procedure | quality inspection | 0.35 | `QA-LM3-WIN-SA320` | bond/gasket procedure | quality inspector |
| 70 | hold point: water ingress test | quality inspection | 0.35 | `LEAK-TEST-LM3-WIN-SA320` | water ingress test | quality inspector |
| 80 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-WIN-SA320`<br>`NCR-LM3-WIN-SA320` | all operation and QA signoffs are complete | manufacturing engineer |

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
