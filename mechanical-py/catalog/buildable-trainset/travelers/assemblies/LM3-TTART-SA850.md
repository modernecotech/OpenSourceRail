# Shop traveler — LM3-TTART-SA850 — optional train-to-train open mid-connection articulation

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.02 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-TTART-SA850 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-EIF-SA650 child assembly material set, supplier-certified rail door system, rail-rated electrical / control equipment |
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
- Inspection methods: child acceptance evidence review, open-end option configuration record, train-to-train motion-envelope proof, walk-through gangway continuity, water ingress/drain test, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-TTART-SA850, KIT-LM3-TTART-SA850, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TTART-SA850-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TTART-SA850-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TTART-SA850-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 0.69 | `TRV-LM3-TTART-SA850`<br>`FIX-LM3-TTART-SA850`<br>`KIT-LM3-TTART-SA850` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-EIF-SA650: common configurable train-end interface set | final assembly and commissioning cell | 1.05 | `FIX-LM3-TTART-SA850`<br>`GAUGE-LM3-EIF-SA650`<br>`TORQUE-LM3-EIF-SA650` | placement zone and joint controls accepted: common configurable train-end interface, option bolt grid, seal/drain datums, and selected-end record | operator |
| 30 | install and integrate LM3-ART-P040: train-to-train open-end articulation, gangway, drawbar, turntable, and service-jumper cassette | final assembly and commissioning cell | 1.23 | `FIX-LM3-TTART-SA850`<br>`GAUGE-LM3-ART-P040`<br>`TORQUE-LM3-ART-P040` | placement zone and joint controls accepted: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope | operator |
| 40 | install and integrate LM3-ART-P041: train-to-train jumper blanking, transition harness, isolation label, and dust-cover kit | final assembly and commissioning cell | 1.35 | `FIX-LM3-TTART-SA850`<br>`GAUGE-LM3-ART-P041`<br>`TORQUE-LM3-ART-P041` | placement zone and joint controls accepted: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope | operator |
| 50 | hold point: open-end option configuration record | quality inspection | 0.35 | `QA-LM3-TTART-SA850` | open-end option configuration record | quality inspector |
| 60 | hold point: train-to-train motion-envelope proof | quality inspection | 0.35 | `QA-LM3-TTART-SA850` | train-to-train motion-envelope proof | quality inspector |
| 70 | hold point: walk-through gangway continuity | quality inspection | 0.35 | `ELEC-TEST-LM3-TTART-SA850` | walk-through gangway continuity | quality inspector |
| 80 | hold point: water ingress/drain test | quality inspection | 0.35 | `LEAK-TEST-LM3-TTART-SA850` | water ingress/drain test | quality inspector |
| 90 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-TTART-SA850`<br>`NCR-LM3-TTART-SA850` | all operation and QA signoffs are complete | manufacturing engineer |

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
