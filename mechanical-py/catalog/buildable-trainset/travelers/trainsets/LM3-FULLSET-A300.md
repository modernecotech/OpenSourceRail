# Shop traveler — LM3-FULLSET-A300 — three LM3 train modules joined as one walk-through full set

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.37 h |
| Build cell | long final assembly track / depot commissioning road |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-FULLSET-A300 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-TRAINSET-A000 child assembly material set, LM3-TTART-SA850 child assembly material set, LM3-SYS-SA900 child assembly material set |
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
- Inspection methods: child acceptance evidence review, three-train alignment and end-option configuration record, two train-to-train open gangway joint motion sweeps, full-set trainline continuity and safety-loop proof, long-consist FEM screening accepted, static and dynamic release for full-set operation, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-FULLSET-A300, KIT-LM3-FULLSET-A300, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-FULLSET-A300-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-FULLSET-A300-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-FULLSET-A300-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | long final assembly track / depot commissioning road | 0.69 | `TRV-LM3-FULLSET-A300`<br>`FIX-LM3-FULLSET-A300`<br>`KIT-LM3-FULLSET-A300` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-TRAINSET-A000: complete light-metro trainset | long final assembly track / depot commissioning road | 1.05 | `FIX-LM3-FULLSET-A300`<br>`GAUGE-LM3-TRAINSET-A000`<br>`TORQUE-LM3-TRAINSET-A000` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-TTART-SA850: optional train-to-train open mid-connection articulation | long final assembly track / depot commissioning road | 1.23 | `FIX-LM3-FULLSET-A300`<br>`GAUGE-LM3-TTART-SA850`<br>`TORQUE-LM3-TTART-SA850` | placement zone and joint controls accepted: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope | operator |
| 40 | install and integrate LM3-SYS-SA900: train control, communication, and safety electronics assembly | long final assembly track / depot commissioning road | 1.35 | `FIX-LM3-FULLSET-A300`<br>`GAUGE-LM3-SYS-SA900`<br>`TORQUE-LM3-SYS-SA900` | placement zone and joint controls accepted: LV cabinet, trainline, network, and diagnostic harness zone | operator |
| 50 | hold point: three-train alignment and end-option configuration record | quality inspection | 0.35 | `QA-LM3-FULLSET-A300` | three-train alignment and end-option configuration record | quality inspector |
| 60 | hold point: two train-to-train open gangway joint motion sweeps | quality inspection | 0.35 | `QA-LM3-FULLSET-A300` | two train-to-train open gangway joint motion sweeps | quality inspector |
| 70 | hold point: full-set trainline continuity and safety-loop proof | quality inspection | 0.35 | `ELEC-TEST-LM3-FULLSET-A300` | full-set trainline continuity and safety-loop proof | quality inspector |
| 80 | hold point: long-consist FEM screening accepted | quality inspection | 0.35 | `QA-LM3-FULLSET-A300` | long-consist FEM screening accepted | quality inspector |
| 90 | hold point: static and dynamic release for full-set operation | quality inspection | 0.35 | `QA-LM3-FULLSET-A300` | static and dynamic release for full-set operation | quality inspector |
| 100 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-FULLSET-A300`<br>`NCR-LM3-FULLSET-A300` | all operation and QA signoffs are complete | manufacturing engineer |

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
