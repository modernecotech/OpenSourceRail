# Shop traveler — LM3-LGT-SA350 — modular main, emergency, and doorway lighting installation

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 5.19 h |
| Build cell | interior pre-fit and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-LGT-SA350 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier-certified rail door system |
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
- Inspection methods: child acceptance evidence review, connector key audit, lighting lux map, emergency-feed isolation and duration test, module replacement demonstration, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-LGT-SA350, KIT-LM3-LGT-SA350, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-LGT-SA350-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-LGT-SA350-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-LGT-SA350-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | interior pre-fit and commissioning cell | 0.61 | `TRV-LM3-LGT-SA350`<br>`FIX-LM3-LGT-SA350`<br>`KIT-LM3-LGT-SA350` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-LGT-P010: 1.2 m plug-in main LED lighting cassette and captive mounting kit | interior pre-fit and commissioning cell | 1.35 | `FIX-LM3-LGT-SA350`<br>`GAUGE-LM3-LGT-P010`<br>`TORQUE-LM3-LGT-P010` | placement zone and joint controls accepted: common OSR-RAIL-42 interior datum and keyed low-voltage service zone | operator |
| 30 | install and integrate LM3-LGT-P020: emergency and doorway lighting modules with independent keyed feeder kit | interior pre-fit and commissioning cell | 1.53 | `FIX-LM3-LGT-SA350`<br>`GAUGE-LM3-LGT-P020`<br>`TORQUE-LM3-LGT-P020` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 40 | hold point: connector key audit | quality inspection | 0.35 | `QA-LM3-LGT-SA350` | connector key audit | quality inspector |
| 50 | hold point: lighting lux map | quality inspection | 0.35 | `QA-LM3-LGT-SA350` | lighting lux map | quality inspector |
| 60 | hold point: emergency-feed isolation and duration test | quality inspection | 0.35 | `ELEC-TEST-LM3-LGT-SA350` | emergency-feed isolation and duration test | quality inspector |
| 70 | hold point: module replacement demonstration | quality inspection | 0.35 | `QA-LM3-LGT-SA350` | module replacement demonstration | quality inspector |
| 80 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-LGT-SA350`<br>`NCR-LM3-LGT-SA350` | all operation and QA signoffs are complete | manufacturing engineer |

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
