# Shop traveler — LM3-EIF-SA650 — common configurable train-end interface set

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.56 h |
| Build cell | end-interface fixture / final assembly cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-EIF-SA650 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | common structural end-interface steel and seal datum kit, panoramic end-option interface closeout kit, open mid-connection end-option interface kit |
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
- Inspection methods: child acceptance evidence review, common bolt-grid survey, selected end-option fit gauge, seal and drain continuity, panoramic-or-open-mid configuration record
- Tooling basis: FIX-LM3-EIF-SA650, KIT-LM3-EIF-SA650, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EIF-SA650-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EIF-SA650-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EIF-SA650-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | end-interface fixture / final assembly cell | 0.69 | `TRV-LM3-EIF-SA650`<br>`FIX-LM3-EIF-SA650`<br>`KIT-LM3-EIF-SA650` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-END-P060: common reversible end-interface carrier ring, option bolt grid, and sealing datum kit | end-interface fixture / final assembly cell | 1.05 | `FIX-LM3-EIF-SA650`<br>`GAUGE-LM3-END-P060`<br>`TORQUE-LM3-END-P060` | placement zone and joint controls accepted: common configurable train-end interface, option bolt grid, seal/drain datums, and selected-end record | operator |
| 30 | install and integrate LM3-END-P061: panoramic-end option shim, cowl/glass carrier, and sensor datum closeout kit | end-interface fixture / final assembly cell | 1.47 | `FIX-LM3-EIF-SA650`<br>`GAUGE-LM3-END-P061`<br>`TORQUE-LM3-END-P061` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 40 | install and integrate LM3-END-P062: mid open-connection option portal trim, bellows clamp, threshold bridge, and drain kit | end-interface fixture / final assembly cell | 1.65 | `FIX-LM3-EIF-SA650`<br>`GAUGE-LM3-END-P062`<br>`TORQUE-LM3-END-P062` | placement zone and joint controls accepted: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope | operator |
| 50 | hold point: common bolt-grid survey | quality inspection | 0.35 | `GAUGE-LM3-EIF-SA650` | common bolt-grid survey | quality inspector |
| 60 | hold point: selected end-option fit gauge | quality inspection | 0.35 | `GAUGE-LM3-EIF-SA650` | selected end-option fit gauge | quality inspector |
| 70 | hold point: seal and drain continuity | quality inspection | 0.35 | `ELEC-TEST-LM3-EIF-SA650` | seal and drain continuity | quality inspector |
| 80 | hold point: panoramic-or-open-mid configuration record | quality inspection | 0.35 | `QA-LM3-EIF-SA650` | panoramic-or-open-mid configuration record | quality inspector |
| 90 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-EIF-SA650`<br>`NCR-LM3-EIF-SA650` | all operation and QA signoffs are complete | manufacturing engineer |

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
