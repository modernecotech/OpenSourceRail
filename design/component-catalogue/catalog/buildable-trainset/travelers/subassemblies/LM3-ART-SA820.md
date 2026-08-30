# Shop traveler — LM3-ART-SA820 — passenger gangway bellows, bridge and turntable subassembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 5.11 h |
| Build cell | gangway clean assembly cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA820 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier-controlled external component, passenger interior COTS kit |
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
- Inspection methods: child acceptance evidence review, fire-material pack, bridge load test, gap/pinch gauge, water test, full-motion sweep, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-ART-SA820, KIT-LM3-ART-SA820, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-SA820-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-SA820-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-SA820-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | gangway clean assembly cell | 0.61 | `TRV-LM3-ART-SA820`<br>`FIX-LM3-ART-SA820`<br>`KIT-LM3-ART-SA820` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-ART-P022: inter-car double-wall corrugated bellows and clamp-frame set | gangway clean assembly cell | 1.35 | `FIX-LM3-ART-SA820`<br>`GAUGE-LM3-ART-P022`<br>`TORQUE-LM3-ART-P022` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-ART-P023: inter-car passenger bridge, turntable and flexible interior-panel set | gangway clean assembly cell | 1.1 | `FIX-LM3-ART-SA820`<br>`GAUGE-LM3-ART-P023`<br>`TORQUE-LM3-ART-P023` | placement zone and joint controls accepted: saloon interior, PRM aisle, ceiling, and service-panel zone | operator |
| 40 | hold point: fire-material pack | quality inspection | 0.35 | `QA-LM3-ART-SA820` | fire-material pack | quality inspector |
| 50 | hold point: bridge load test | quality inspection | 0.35 | `QA-LM3-ART-SA820` | bridge load test | quality inspector |
| 60 | hold point: gap/pinch gauge | quality inspection | 0.35 | `GAUGE-LM3-ART-SA820` | gap/pinch gauge | quality inspector |
| 70 | hold point: water test | quality inspection | 0.35 | `LEAK-TEST-LM3-ART-SA820` | water test | quality inspector |
| 80 | hold point: full-motion sweep | quality inspection | 0.35 | `QA-LM3-ART-SA820` | full-motion sweep | quality inspector |
| 90 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-ART-SA820`<br>`NCR-LM3-ART-SA820` | all operation and QA signoffs are complete | manufacturing engineer |

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
