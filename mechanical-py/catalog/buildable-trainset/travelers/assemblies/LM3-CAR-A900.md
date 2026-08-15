# Shop traveler — LM3-CAR-A900 — complete repeated car module

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 13.24 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-CAR-A900 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-SHELL-A200 child assembly material set, LM3-DOOR-SA310 child assembly material set, LM3-INT-SA330 child assembly material set, LM3-ROOF-SA410 child assembly material set, LM3-HV-SA510 child assembly material set, LM3-BOG-SA610 child assembly material set, LM3-BOG-SA620 child assembly material set, supplier-certified running gear |
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
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, car weigh, door/HVAC/static systems test, bogie marriage report, low-speed yard movement, continuity, insulation/isolation, functional static test, alignment survey, static brake test
- Tooling basis: FIX-LM3-CAR-A900, KIT-LM3-CAR-A900, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-CAR-A900-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-CAR-A900-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-CAR-A900-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 1.09 | `TRV-LM3-CAR-A900`<br>`FIX-LM3-CAR-A900`<br>`KIT-LM3-CAR-A900` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-SHELL-A200: painted carbody frame with one-metre clip-on fiberglass exterior | final assembly and commissioning cell | 1.17 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-SHELL-A200`<br>`TORQUE-LM3-SHELL-A200` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 30 | install and integrate LM3-DOOR-SA310: door cassette and threshold assembly | final assembly and commissioning cell | 1.3 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-DOOR-SA310`<br>`TORQUE-LM3-DOOR-SA310` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 40 | install and integrate LM3-INT-SA330: interior and passenger systems fit-out | final assembly and commissioning cell | 1.05 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-INT-SA330`<br>`TORQUE-LM3-INT-SA330` | placement zone and joint controls accepted: saloon interior, PRM aisle, ceiling, and service-panel zone | operator |
| 50 | install and integrate LM3-ROOF-SA410: roof HVAC, PV, antenna, and service-equipment assembly | final assembly and commissioning cell | 1.9 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-ROOF-SA410`<br>`TORQUE-LM3-ROOF-SA410` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 60 | install and integrate LM3-HV-SA510: per-car LFP battery, two controllers, DC auxiliary/charge interface, mist, and cooling assembly | final assembly and commissioning cell | 1.83 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-HV-SA510`<br>`TORQUE-LM3-HV-SA510` | placement zone and joint controls accepted: under-seat HV bay, side-pin dock zone, and segregated cable route | operator |
| 70 | install and integrate LM3-BOG-SA610: powered bogie assembly | final assembly and commissioning cell | 1.05 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-BOG-SA610`<br>`TORQUE-LM3-BOG-SA610` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 80 | install and integrate LM3-BOG-SA620: trailer bogie assembly | final assembly and commissioning cell | 1.05 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-BOG-SA620`<br>`TORQUE-LM3-BOG-SA620` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 90 | install and integrate LM3-AUX-P010: secondary-suspension compressor, dryer, reservoir, and isolation-manifold kit | final assembly and commissioning cell | 1.1 | `FIX-LM3-CAR-A900`<br>`GAUGE-LM3-AUX-P010`<br>`TORQUE-LM3-AUX-P010` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 100 | hold point: car weigh | quality inspection | 0.35 | `QA-LM3-CAR-A900` | car weigh | quality inspector |
| 110 | hold point: door/HVAC/static systems test | quality inspection | 0.35 | `QA-LM3-CAR-A900` | door/HVAC/static systems test | quality inspector |
| 120 | hold point: bogie marriage report | quality inspection | 0.35 | `QA-LM3-CAR-A900` | bogie marriage report | quality inspector |
| 130 | hold point: low-speed yard movement | quality inspection | 0.35 | `QA-LM3-CAR-A900` | low-speed yard movement | quality inspector |
| 140 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-CAR-A900`<br>`NCR-LM3-CAR-A900` | all operation and QA signoffs are complete | manufacturing engineer |

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
