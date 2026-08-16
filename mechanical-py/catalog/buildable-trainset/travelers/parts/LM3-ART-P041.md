# Shop traveler — LM3-ART-P041 — train-to-train jumper blanking, transition harness, isolation label, and dust-cover kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B24` |

## Material specification

| Field | Value |
|---|---|
| Material family | rail-rated electrical / control equipment |
| Grade / part class | LV/data harness, cabinet, sensor, antenna, and trainline kit |
| Governing standard | supplier rail electronics specification plus project EMC, IP, and fire evidence |
| Form factor | cabinet, harness, connector, sensor, bracket, antenna, and label kit |
| Nominal section | connector, bend-radius, service-loop, and mounting envelope frozen by RFQ drawing |
| Finish / protection | halogen/fire-rated cable where required, IP sealing, bonding, and label protection |
| Traceability | serialised equipment CoC, firmware/config record, harness batch, and continuity record |

Evidence required:

- certificate of conformity
- incoming inspection record
- continuity test
- EMC/IP evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, pinout test, blanking cover ingress check, isolation label inspection, bend-radius sweep, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P041, CERT-LM3-ART-P041, GAUGE-LM3-ART-P041-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-P041-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-P041-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-P041-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-ART-P041`<br>`DOC-LM3-TTART-SA850` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-ART-P041`<br>`CERT-LM3-ART-P041` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-ART-P041-ENVELOPE`<br>`FIX-LM3-TTART-SA850` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: pinout test | quality inspection | 0.25 | `QA-LM3-ART-P041` | pinout test | quality inspector |
| 50 | verify acceptance gate: blanking cover ingress check | quality inspection | 0.25 | `QA-LM3-ART-P041` | blanking cover ingress check | quality inspector |
| 60 | verify acceptance gate: isolation label inspection | quality inspection | 0.25 | `ELEC-TEST-LM3-ART-P041` | isolation label inspection | quality inspector |
| 70 | verify acceptance gate: bend-radius sweep | quality inspection | 0.25 | `QA-LM3-ART-P041` | bend-radius sweep | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-ART-P041`<br>`KIT-LM3-TTART-SA850` | item is released, tagged, and staged for parent assembly | cell lead |

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
