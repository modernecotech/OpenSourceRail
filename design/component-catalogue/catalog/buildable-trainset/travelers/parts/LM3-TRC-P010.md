# Shop traveler — LM3-TRC-P010 — motor-350kw-hm47-class axle traction motor

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `BID` |
| Procurement BOM lines | `T1` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier traction drive equipment |
| Grade / part class | traction motor / gearbox / coupling certified equipment class |
| Governing standard | supplier rail traction specification plus project EMC, thermal, and mount-load evidence |
| Form factor | preassembled motor, gearbox, coupling, seals, oil ports, and mounting hardware |
| Nominal section | bogie motor-cradle and axle interface frozen by RFQ drawing |
| Finish / protection | supplier coating, lubrication preservation, earthing/bonding, and thermal labels |
| Traceability | serialised drive equipment CoC, test report, oil data, and revision record |

Evidence required:

- certificate of conformity
- incoming inspection record
- thermal curve
- mounting-foot proof evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, motor datasheet, thermal curve, mounting-foot load proof, EMC evidence, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-TRC-P010, CERT-LM3-TRC-P010, GAUGE-LM3-TRC-P010-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TRC-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TRC-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TRC-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-TRC-P010`<br>`DOC-LM3-TRC-SA615` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-TRC-P010`<br>`CERT-LM3-TRC-P010` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-TRC-P010-ENVELOPE`<br>`FIX-LM3-TRC-SA615` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: motor datasheet | quality inspection | 0.25 | `QA-LM3-TRC-P010` | motor datasheet | quality inspector |
| 50 | verify acceptance gate: thermal curve | quality inspection | 0.25 | `QA-LM3-TRC-P010` | thermal curve | quality inspector |
| 60 | verify acceptance gate: mounting-foot load proof | quality inspection | 0.25 | `QA-LM3-TRC-P010` | mounting-foot load proof | quality inspector |
| 70 | verify acceptance gate: EMC evidence | quality inspection | 0.25 | `QA-LM3-TRC-P010` | EMC evidence | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-TRC-P010`<br>`KIT-LM3-TRC-SA615` | item is released, tagged, and staged for parent assembly | cell lead |

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
