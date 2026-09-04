# Shop traveler — LM3-BDY-SA120 — carbody spaceframe and floor assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.64 h |
| Build cell | weld and fixture cell |
| Procurement BOM lines | `B3`, `B4` |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BDY-SA120 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-BDY-SA110 child assembly material set, rail structural steel |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, fixture tack/weld, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, WPS-controlled structural welding, adhesive/bonded/gasketed sealing interfaces
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, weld map release, WPS/WPQR and welder qualification, surface preparation record, adhesive/sealant batch and cure record
- Inspection methods: child acceptance evidence review, door/window aperture survey, roof rail survey, carbody dimensional report, VT, MT/UT where classed, post-weld datum survey, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-BDY-SA120, KIT-LM3-BDY-SA120, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BDY-SA120-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BDY-SA120-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BDY-SA120-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | weld and fixture cell | 0.77 | `TRV-LM3-BDY-SA120`<br>`FIX-LM3-BDY-SA120`<br>`KIT-LM3-BDY-SA120` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-SA110: underframe datum weldment | weld and fixture cell | 1.17 | `FIX-LM3-BDY-SA120`<br>`GAUGE-LM3-BDY-SA110`<br>`TORQUE-LM3-BDY-SA110` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-BDY-P060: low-floor centre pan and removable service-floor support set | weld and fixture cell | 1.0 | `FIX-LM3-BDY-SA120`<br>`GAUGE-LM3-BDY-P060`<br>`TORQUE-LM3-BDY-P060` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 40 | install and integrate LM3-BDY-P061: raised bogie-end deck, transition ramp, and removable hatch-frame set | weld and fixture cell | 1.17 | `FIX-LM3-BDY-SA120`<br>`GAUGE-LM3-BDY-P061`<br>`TORQUE-LM3-BDY-P061` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 50 | install and integrate LM3-BDY-P070: side-wall post, door portal, waist rail, and cant rail kit | weld and fixture cell | 1.18 | `FIX-LM3-BDY-SA120`<br>`GAUGE-LM3-BDY-P070`<br>`TORQUE-LM3-BDY-P070` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 60 | hold point: door/window aperture survey | quality inspection | 0.35 | `GAUGE-LM3-BDY-SA120` | door/window aperture survey | quality inspector |
| 70 | hold point: roof rail survey | quality inspection | 0.35 | `GAUGE-LM3-BDY-SA120` | roof rail survey | quality inspector |
| 80 | hold point: carbody dimensional report | quality inspection | 0.35 | `QA-LM3-BDY-SA120` | carbody dimensional report | quality inspector |
| 90 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-BDY-SA120`<br>`NCR-LM3-BDY-SA120` | all operation and QA signoffs are complete | manufacturing engineer |

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
