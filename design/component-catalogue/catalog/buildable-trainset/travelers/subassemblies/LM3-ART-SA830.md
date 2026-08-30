# Shop traveler — LM3-ART-SA830 — articulation service-transfer and segregated trainline subassembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.19 h |
| Build cell | harness, hose and articulation bench |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA830 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | fire-retardant fiberglass composite, rail-rated electrical / control equipment |
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
- Inspection methods: child acceptance evidence review, HV/LV segregation, continuity/pressure test, bend-radius sweep, drain test, replaceability trial, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-ART-SA830, KIT-LM3-ART-SA830, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-SA830-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-SA830-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-SA830-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | harness, hose and articulation bench | 0.61 | `TRV-LM3-ART-SA830`<br>`FIX-LM3-ART-SA830`<br>`KIT-LM3-ART-SA830` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-ART-P024: articulation trainline carrier, support arms, abrasion liners and drain path | harness, hose and articulation bench | 1.88 | `FIX-LM3-ART-SA830`<br>`GAUGE-LM3-ART-P024`<br>`TORQUE-LM3-ART-P024` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 30 | install and integrate LM3-ART-P030: inter-car HV/LV jumper, coolant hose loop, energy chain, and drain sleeve kit | harness, hose and articulation bench | 1.65 | `FIX-LM3-ART-SA830`<br>`GAUGE-LM3-ART-P030`<br>`TORQUE-LM3-ART-P030` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 40 | hold point: HV/LV segregation | quality inspection | 0.35 | `QA-LM3-ART-SA830` | HV/LV segregation | quality inspector |
| 50 | hold point: continuity/pressure test | quality inspection | 0.35 | `ELEC-TEST-LM3-ART-SA830` | continuity/pressure test | quality inspector |
| 60 | hold point: bend-radius sweep | quality inspection | 0.35 | `QA-LM3-ART-SA830` | bend-radius sweep | quality inspector |
| 70 | hold point: drain test | quality inspection | 0.35 | `LEAK-TEST-LM3-ART-SA830` | drain test | quality inspector |
| 80 | hold point: replaceability trial | quality inspection | 0.35 | `QA-LM3-ART-SA830` | replaceability trial | quality inspector |
| 90 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-ART-SA830`<br>`NCR-LM3-ART-SA830` | all operation and QA signoffs are complete | manufacturing engineer |

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
