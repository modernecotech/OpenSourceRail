# Shop traveler — LM3-DOOR-SA310 — door cassette and threshold assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.22 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-DOOR-SA310 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, formed sheet metal / stainless local hardware, supplier-certified rail door system |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, bonding/earthing, segregated harness/fluid routing
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable
- Inspection methods: child acceptance evidence review, door gauge fit, obstruction test, closed-and-locked test, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-DOOR-SA310, KIT-LM3-DOOR-SA310, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-DOOR-SA310-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-DOOR-SA310-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-DOOR-SA310-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 0.69 | `TRV-LM3-DOOR-SA310`<br>`FIX-LM3-DOOR-SA310`<br>`KIT-LM3-DOOR-SA310` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-P100: door portal reinforcement, threshold beam, and cassette shim kit | final assembly and commissioning cell | 1.35 | `FIX-LM3-DOOR-SA310`<br>`GAUGE-LM3-BDY-P100`<br>`TORQUE-LM3-BDY-P100` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 30 | install and integrate LM3-DOOR-P010: door four-point adjustable carrier, datum pin, dry seal, and keyed connector bracket kit | final assembly and commissioning cell | 1.53 | `FIX-LM3-DOOR-SA310`<br>`GAUGE-LM3-DOOR-P010`<br>`TORQUE-LM3-DOOR-P010` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 40 | install and integrate LM3-EXT-P010: electric plug/sliding door cassette | final assembly and commissioning cell | 1.3 | `FIX-LM3-DOOR-SA310`<br>`GAUGE-LM3-EXT-P010`<br>`TORQUE-LM3-EXT-P010` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 50 | hold point: door gauge fit | quality inspection | 0.35 | `GAUGE-LM3-DOOR-SA310` | door gauge fit | quality inspector |
| 60 | hold point: obstruction test | quality inspection | 0.35 | `QA-LM3-DOOR-SA310` | obstruction test | quality inspector |
| 70 | hold point: closed-and-locked test | quality inspection | 0.35 | `QA-LM3-DOOR-SA310` | closed-and-locked test | quality inspector |
| 80 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-DOOR-SA310`<br>`NCR-LM3-DOOR-SA310` | all operation and QA signoffs are complete | manufacturing engineer |

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
