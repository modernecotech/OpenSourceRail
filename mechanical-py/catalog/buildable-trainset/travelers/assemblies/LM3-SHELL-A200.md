# Shop traveler — LM3-SHELL-A200 — painted carbody frame with one-metre clip-on fiberglass exterior

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 9.55 h |
| Build cell | paint / clip-on body / glazing cells |
| Procurement BOM lines | `B5`, `B6`, `B7`, `B20`, `B28` |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-SHELL-A200 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-BDY-SA120 child assembly material set, fire-retardant exterior fiberglass sandwich, stainless retention hardware and elastomer seal kit, LM3-WIN-SA320 child assembly material set, fire-retardant fiberglass composite |
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
- Inspection methods: child acceptance evidence review, corrosion report, clip and anti-lift witness map, eight-hour trainset body route, water ingress pre-test, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-SHELL-A200, KIT-LM3-SHELL-A200, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-SHELL-A200-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-SHELL-A200-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-SHELL-A200-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | paint / clip-on body / glazing cells | 0.93 | `TRV-LM3-SHELL-A200`<br>`FIX-LM3-SHELL-A200`<br>`KIT-LM3-SHELL-A200` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-SA120: carbody spaceframe and floor assembly | paint / clip-on body / glazing cells | 1.12 | `FIX-LM3-SHELL-A200`<br>`GAUGE-LM3-BDY-SA120`<br>`TORQUE-LM3-BDY-SA120` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-BDY-P130: one-metre clip-on fiberglass side and roof body module | paint / clip-on body / glazing cells | 1.17 | `FIX-LM3-SHELL-A200`<br>`GAUGE-LM3-BDY-P130`<br>`TORQUE-LM3-BDY-P130` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 40 | install and integrate LM3-BDY-P140: keyed clip rail, captive retainer, anti-lift, and dry-seal car kit | paint / clip-on body / glazing cells | 1.05 | `FIX-LM3-SHELL-A200`<br>`GAUGE-LM3-BDY-P140`<br>`TORQUE-LM3-BDY-P140` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 50 | install and integrate LM3-WIN-SA320: side glazing cassette installation | paint / clip-on body / glazing cells | 1.12 | `FIX-LM3-SHELL-A200`<br>`GAUGE-LM3-WIN-SA320`<br>`TORQUE-LM3-WIN-SA320` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 60 | install and integrate LM3-EXT-P080: fire-rated composite exterior side sandwich-panel kit | paint / clip-on body / glazing cells | 1.17 | `FIX-LM3-SHELL-A200`<br>`GAUGE-LM3-EXT-P080`<br>`TORQUE-LM3-EXT-P080` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 70 | install and integrate LM3-EXT-P090: fire-rated composite roof fairing and exterior skirt-panel kit | paint / clip-on body / glazing cells | 1.29 | `FIX-LM3-SHELL-A200`<br>`GAUGE-LM3-EXT-P090`<br>`TORQUE-LM3-EXT-P090` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 80 | hold point: corrosion report | quality inspection | 0.35 | `QA-LM3-SHELL-A200` | corrosion report | quality inspector |
| 90 | hold point: clip and anti-lift witness map | quality inspection | 0.35 | `QA-LM3-SHELL-A200` | clip and anti-lift witness map | quality inspector |
| 100 | hold point: eight-hour trainset body route | quality inspection | 0.35 | `QA-LM3-SHELL-A200` | eight-hour trainset body route | quality inspector |
| 110 | hold point: water ingress pre-test | quality inspection | 0.35 | `LEAK-TEST-LM3-SHELL-A200` | water ingress pre-test | quality inspector |
| 120 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-SHELL-A200`<br>`NCR-LM3-SHELL-A200` | all operation and QA signoffs are complete | manufacturing engineer |

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
