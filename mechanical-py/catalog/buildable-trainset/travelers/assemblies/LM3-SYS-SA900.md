# Shop traveler — LM3-SYS-SA900 — train control, communication, and safety electronics assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 9.15 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-SYS-SA900 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail-rated electrical / control equipment, supplier-controlled external component, rail structural steel, supplier crash/coupler system |
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
- Inspection methods: child acceptance evidence review, network enumeration, firmware record, self-test, event-recorder write/read test, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-SYS-SA900, KIT-LM3-SYS-SA900, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-SYS-SA900-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-SYS-SA900-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-SYS-SA900-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 0.85 | `TRV-LM3-SYS-SA900`<br>`FIX-LM3-SYS-SA900`<br>`KIT-LM3-SYS-SA900` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-CTRL-P010: T-ECU/S and T-ECU/A compute and safety-control cabinet kit | final assembly and commissioning cell | 1.4 | `FIX-LM3-SYS-SA900`<br>`GAUGE-LM3-CTRL-P010`<br>`TORQUE-LM3-CTRL-P010` | placement zone and joint controls accepted: LV cabinet, trainline, network, and diagnostic harness zone | operator |
| 30 | install and integrate LM3-CTRL-P020: navigation, balise, 5G, LoRa, GNSS, IMU, and roof-antenna kit | final assembly and commissioning cell | 1.4 | `FIX-LM3-SYS-SA900`<br>`GAUGE-LM3-CTRL-P020`<br>`TORQUE-LM3-CTRL-P020` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 40 | install and integrate LM3-CTRL-P030: maintenance HMI, depot pendant, emergency controls, and safety-relay kit | final assembly and commissioning cell | 1.35 | `FIX-LM3-SYS-SA900`<br>`GAUGE-LM3-CTRL-P030`<br>`TORQUE-LM3-CTRL-P030` | placement zone and joint controls accepted: LV cabinet, trainline, network, and diagnostic harness zone | operator |
| 50 | install and integrate LM3-CTRL-P040: pre-terminated LV trainline harness, DIN cabinet, and terminal-distribution kit | final assembly and commissioning cell | 1.4 | `FIX-LM3-SYS-SA900`<br>`GAUGE-LM3-CTRL-P040`<br>`TORQUE-LM3-CTRL-P040` | placement zone and joint controls accepted: LV cabinet, trainline, network, and diagnostic harness zone | operator |
| 60 | install and integrate LM3-CTRL-P050: operational and crashworthy event-recorder storage kit | final assembly and commissioning cell | 1.05 | `FIX-LM3-SYS-SA900`<br>`GAUGE-LM3-CTRL-P050`<br>`TORQUE-LM3-CTRL-P050` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 70 | hold point: network enumeration | quality inspection | 0.35 | `QA-LM3-SYS-SA900` | network enumeration | quality inspector |
| 80 | hold point: firmware record | quality inspection | 0.35 | `QA-LM3-SYS-SA900` | firmware record | quality inspector |
| 90 | hold point: self-test | quality inspection | 0.35 | `QA-LM3-SYS-SA900` | self-test | quality inspector |
| 100 | hold point: event-recorder write/read test | quality inspection | 0.35 | `QA-LM3-SYS-SA900` | event-recorder write/read test | quality inspector |
| 110 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-SYS-SA900`<br>`NCR-LM3-SYS-SA900` | all operation and QA signoffs are complete | manufacturing engineer |

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
