# Shop traveler — LM3-ART-SA800 — complete inter-car structural articulation, passenger gangway and service transfer

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.3 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA800 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-ART-SA810 child assembly material set, LM3-ART-SA820 child assembly material set, LM3-ART-SA830 child assembly material set |
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
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable
- Inspection methods: child acceptance evidence review, motion-envelope proof, trainline continuity, water ingress/drain test, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-ART-SA800, KIT-LM3-ART-SA800, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-SA800-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-SA800-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-SA800-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 0.69 | `TRV-LM3-ART-SA800`<br>`FIX-LM3-ART-SA800`<br>`KIT-LM3-ART-SA800` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-ART-SA810: structural articulation joint and anti-lift load path | final assembly and commissioning cell | 1.28 | `FIX-LM3-ART-SA800`<br>`GAUGE-LM3-ART-SA810`<br>`TORQUE-LM3-ART-SA810` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 30 | install and integrate LM3-ART-SA820: passenger gangway bellows, bridge and turntable subassembly | final assembly and commissioning cell | 1.4 | `FIX-LM3-ART-SA800`<br>`GAUGE-LM3-ART-SA820`<br>`TORQUE-LM3-ART-SA820` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 40 | install and integrate LM3-ART-SA830: articulation service-transfer and segregated trainline subassembly | final assembly and commissioning cell | 1.58 | `FIX-LM3-ART-SA800`<br>`GAUGE-LM3-ART-SA830`<br>`TORQUE-LM3-ART-SA830` | placement zone and joint controls accepted: inter-car articulation, gangway, trainline, and flexible-service envelope | operator |
| 50 | hold point: motion-envelope proof | quality inspection | 0.35 | `QA-LM3-ART-SA800` | motion-envelope proof | quality inspector |
| 60 | hold point: trainline continuity | quality inspection | 0.35 | `ELEC-TEST-LM3-ART-SA800` | trainline continuity | quality inspector |
| 70 | hold point: water ingress/drain test | quality inspection | 0.35 | `LEAK-TEST-LM3-ART-SA800` | water ingress/drain test | quality inspector |
| 80 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-ART-SA800`<br>`NCR-LM3-ART-SA800` | all operation and QA signoffs are complete | manufacturing engineer |

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
