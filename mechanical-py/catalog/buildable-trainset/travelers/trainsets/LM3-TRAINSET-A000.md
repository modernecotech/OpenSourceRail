# Shop traveler — LM3-TRAINSET-A000 — complete light-metro trainset

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 9.13 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-TRAINSET-A000 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-CAR-A900 child assembly material set, LM3-EIF-SA650 child assembly material set, LM3-END-SA700 child assembly material set, LM3-ART-SA800 child assembly material set, LM3-SYS-SA900 child assembly material set |
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
- Inspection methods: child acceptance evidence review, trainset weigh, static brake/door/HVAC/HV tests, FEM screening accepted, dynamic-test release, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-TRAINSET-A000, KIT-LM3-TRAINSET-A000, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TRAINSET-A000-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TRAINSET-A000-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TRAINSET-A000-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 0.85 | `TRV-LM3-TRAINSET-A000`<br>`FIX-LM3-TRAINSET-A000`<br>`KIT-LM3-TRAINSET-A000` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-CAR-A900: complete repeated car module | final assembly and commissioning cell | 1.05 | `FIX-LM3-TRAINSET-A000`<br>`GAUGE-LM3-CAR-A900`<br>`TORQUE-LM3-CAR-A900` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-EIF-SA650: common configurable train-end interface set | final assembly and commissioning cell | 1.05 | `FIX-LM3-TRAINSET-A000`<br>`GAUGE-LM3-EIF-SA650`<br>`TORQUE-LM3-EIF-SA650` | placement zone and joint controls accepted: common configurable train-end interface, option bolt grid, seal/drain datums, and selected-end record | operator |
| 40 | install and integrate LM3-END-SA700: train-end cowl, coupler, crash, and sensor assembly | final assembly and commissioning cell | 1.65 | `FIX-LM3-TRAINSET-A000`<br>`GAUGE-LM3-END-SA700`<br>`TORQUE-LM3-END-SA700` | placement zone and joint controls accepted: train-end cowl, crash, coupler, and sensor datum stack | operator |
| 50 | install and integrate LM3-ART-SA800: inter-car articulation and trainline assembly | final assembly and commissioning cell | 1.48 | `FIX-LM3-TRAINSET-A000`<br>`GAUGE-LM3-ART-SA800`<br>`TORQUE-LM3-ART-SA800` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 60 | install and integrate LM3-SYS-SA900: train control, communication, and safety electronics assembly | final assembly and commissioning cell | 1.35 | `FIX-LM3-TRAINSET-A000`<br>`GAUGE-LM3-SYS-SA900`<br>`TORQUE-LM3-SYS-SA900` | placement zone and joint controls accepted: LV cabinet, trainline, network, and diagnostic harness zone | operator |
| 70 | hold point: trainset weigh | quality inspection | 0.35 | `QA-LM3-TRAINSET-A000` | trainset weigh | quality inspector |
| 80 | hold point: static brake/door/HVAC/HV tests | quality inspection | 0.35 | `QA-LM3-TRAINSET-A000` | static brake/door/HVAC/HV tests | quality inspector |
| 90 | hold point: FEM screening accepted | quality inspection | 0.35 | `QA-LM3-TRAINSET-A000` | FEM screening accepted | quality inspector |
| 100 | hold point: dynamic-test release | quality inspection | 0.35 | `QA-LM3-TRAINSET-A000` | dynamic-test release | quality inspector |
| 110 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-TRAINSET-A000`<br>`NCR-LM3-TRAINSET-A000` | all operation and QA signoffs are complete | manufacturing engineer |

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
