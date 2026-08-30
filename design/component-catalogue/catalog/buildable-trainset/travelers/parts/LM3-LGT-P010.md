# Shop traveler — LM3-LGT-P010 — 1.2 m plug-in main LED lighting cassette and captive mounting kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B16` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier-certified rail door system |
| Grade / part class | COTS/BID electric passenger door cassette |
| Governing standard | supplier rail door specification plus EN 14752 evidence where applicable |
| Form factor | preassembled door cassette with seals, drive, controller, and emergency release |
| Nominal section | supplier envelope frozen by RFQ drawing |
| Finish / protection | supplier corrosion/fire/smoke protection accepted by OSR evidence pack |
| Traceability | serialised supplier CoC, revision, and lifecycle evidence |

Evidence required:

- certificate of conformity
- incoming inspection record
- obstruction / locked-loop evidence
- fire-smoke certificate pack

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, rail fire certificate, shock/vibration evidence, photometric/lux test, plug polarity and retention test
- Tooling basis: RFQ-LM3-LGT-P010, CERT-LM3-LGT-P010, GAUGE-LM3-LGT-P010-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-LGT-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-LGT-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-LGT-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-LGT-P010`<br>`DOC-LM3-LGT-SA350` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-LGT-P010`<br>`CERT-LM3-LGT-P010` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-LGT-P010-ENVELOPE`<br>`FIX-LM3-LGT-SA350` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: rail fire certificate | quality inspection | 0.25 | `QA-LM3-LGT-P010` | rail fire certificate | quality inspector |
| 50 | verify acceptance gate: shock/vibration evidence | quality inspection | 0.25 | `QA-LM3-LGT-P010` | shock/vibration evidence | quality inspector |
| 60 | verify acceptance gate: photometric/lux test | quality inspection | 0.25 | `QA-LM3-LGT-P010` | photometric/lux test | quality inspector |
| 70 | verify acceptance gate: plug polarity and retention test | quality inspection | 0.25 | `QA-LM3-LGT-P010` | plug polarity and retention test | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-LGT-P010`<br>`KIT-LM3-LGT-SA350` | item is released, tagged, and staged for parent assembly | cell lead |

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
