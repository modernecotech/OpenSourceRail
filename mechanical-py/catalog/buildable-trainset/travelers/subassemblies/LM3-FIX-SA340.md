# Shop traveler — LM3-FIX-SA340 — common service-rail, captive-fastener, and fixture-adapter installation

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 5.54 h |
| Build cell | interior pre-fit and final assembly cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-FIX-SA340 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-controlled external component, formed sheet metal / stainless local hardware |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze
- Inspection methods: child acceptance evidence review, rail datum survey, fastener-family audit, fixture load-evidence check, service/removal demonstration
- Tooling basis: FIX-LM3-FIX-SA340, KIT-LM3-FIX-SA340, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-FIX-SA340-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-FIX-SA340-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-FIX-SA340-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | interior pre-fit and final assembly cell | 0.69 | `TRV-LM3-FIX-SA340`<br>`FIX-LM3-FIX-SA340`<br>`KIT-LM3-FIX-SA340` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-FIX-P010: OSR-RAIL-42 common ceiling, waist, and seat-zone service rail kit | interior pre-fit and final assembly cell | 1.05 | `FIX-LM3-FIX-SA340`<br>`GAUGE-LM3-FIX-P010`<br>`TORQUE-LM3-FIX-P010` | placement zone and joint controls accepted: saloon interior, PRM aisle, ceiling, and service-panel zone | operator |
| 30 | install and integrate LM3-FIX-P020: four-family captive fastener, floating nut, isolator, and access-fastener kit | interior pre-fit and final assembly cell | 1.05 | `FIX-LM3-FIX-SA340`<br>`GAUGE-LM3-FIX-P020`<br>`TORQUE-LM3-FIX-P020` | placement zone and joint controls accepted: common OSR-RAIL-42 interior datum and keyed low-voltage service zone | operator |
| 40 | install and integrate LM3-FIX-P030: standard passenger-fixture saddle and equipment adapter kit | interior pre-fit and final assembly cell | 1.05 | `FIX-LM3-FIX-SA340`<br>`GAUGE-LM3-FIX-P030`<br>`TORQUE-LM3-FIX-P030` | placement zone and joint controls accepted: common OSR-RAIL-42 interior datum and keyed low-voltage service zone | operator |
| 50 | hold point: rail datum survey | quality inspection | 0.35 | `GAUGE-LM3-FIX-SA340` | rail datum survey | quality inspector |
| 60 | hold point: fastener-family audit | quality inspection | 0.35 | `TORQUE-LM3-FIX-SA340` | fastener-family audit | quality inspector |
| 70 | hold point: fixture load-evidence check | quality inspection | 0.35 | `QA-LM3-FIX-SA340` | fixture load-evidence check | quality inspector |
| 80 | hold point: service/removal demonstration | quality inspection | 0.35 | `QA-LM3-FIX-SA340` | service/removal demonstration | quality inspector |
| 90 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-FIX-SA340`<br>`NCR-LM3-FIX-SA340` | all operation and QA signoffs are complete | manufacturing engineer |

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
