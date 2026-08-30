# Shop traveler — LM3-END-P040 — e-coupler LV jumper, recovery trainline, and end harness breakaway kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `BID` |
| Procurement BOM lines | `B22`, `E17` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier crash/coupler system |
| Grade / part class | automatic coupler and crash-energy absorber kit |
| Governing standard | supplier crashworthiness specification plus project recovery and interface evidence |
| Form factor | coupler head, draft gear, absorber, jumper hardware, and bolted mounting kit |
| Nominal section | coupler pocket envelope and load path frozen by RFQ drawing |
| Finish / protection | supplier coating, preservation, and rescue/recovery labels |
| Traceability | serialised coupler/absorber CoC, overhaul status, and proof evidence |

Evidence required:

- certificate of conformity
- incoming inspection record
- crash-energy evidence
- bolt/torque evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, pinout test, breakaway force check, ingress protection, rescue compatibility, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-END-P040, CERT-LM3-END-P040, GAUGE-LM3-END-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-END-P040-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-END-P040-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-END-P040-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-END-P040`<br>`DOC-LM3-END-SA700` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-END-P040`<br>`CERT-LM3-END-P040` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-END-P040-ENVELOPE`<br>`FIX-LM3-END-SA700` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: pinout test | quality inspection | 0.25 | `QA-LM3-END-P040` | pinout test | quality inspector |
| 50 | verify acceptance gate: breakaway force check | quality inspection | 0.25 | `QA-LM3-END-P040` | breakaway force check | quality inspector |
| 60 | verify acceptance gate: ingress protection | quality inspection | 0.25 | `QA-LM3-END-P040` | ingress protection | quality inspector |
| 70 | verify acceptance gate: rescue compatibility | quality inspection | 0.25 | `QA-LM3-END-P040` | rescue compatibility | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-END-P040`<br>`KIT-LM3-END-SA700` | item is released, tagged, and staged for parent assembly | cell lead |

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
