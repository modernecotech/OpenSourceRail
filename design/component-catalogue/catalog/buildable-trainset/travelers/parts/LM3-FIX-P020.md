# Shop traveler — LM3-FIX-P020 — four-family captive fastener, floating nut, isolator, and access-fastener kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B2`, `B21` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier-controlled external component |
| Grade / part class | COTS/BID component class matched to OSR envelope |
| Governing standard | supplier specification plus project interface, safety, EMC/fire, and lifecycle evidence |
| Form factor | preassembled supplier module with installation kit |
| Nominal section | mass, volume, mounting datum, service clearance, and connector envelope frozen by RFQ drawing |
| Finish / protection | supplier finish/protection accepted by OSR evidence pack |
| Traceability | serialised CoC, datasheet, revision, and incoming inspection record |

Evidence required:

- certificate of conformity
- incoming inspection record
- datasheet / evidence pack

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, supplier certificate, batch/finish trace, installed-grip gauge, locking and captive-part audit
- Tooling basis: RFQ-LM3-FIX-P020, CERT-LM3-FIX-P020, GAUGE-LM3-FIX-P020-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-FIX-P020-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-FIX-P020-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-FIX-P020-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-FIX-P020`<br>`DOC-LM3-FIX-SA340` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-FIX-P020`<br>`CERT-LM3-FIX-P020` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-FIX-P020-ENVELOPE`<br>`FIX-LM3-FIX-SA340` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: supplier certificate | quality inspection | 0.25 | `QA-LM3-FIX-P020` | supplier certificate | quality inspector |
| 50 | verify acceptance gate: batch/finish trace | quality inspection | 0.25 | `QA-LM3-FIX-P020` | batch/finish trace | quality inspector |
| 60 | verify acceptance gate: installed-grip gauge | quality inspection | 0.25 | `GAUGE-LM3-FIX-P020` | installed-grip gauge | quality inspector |
| 70 | verify acceptance gate: locking and captive-part audit | quality inspection | 0.25 | `QA-LM3-FIX-P020` | locking and captive-part audit | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-FIX-P020`<br>`KIT-LM3-FIX-SA340` | item is released, tagged, and staged for parent assembly | cell lead |

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
