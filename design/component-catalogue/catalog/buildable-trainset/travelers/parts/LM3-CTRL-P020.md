# Shop traveler — LM3-CTRL-P020 — navigation, balise, 5G, LoRa, GNSS, IMU, and roof-antenna kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `SOURCE` |
| Procurement BOM lines | `E3`, `E4`, `E5`, `E6`, `E7`, `E8`, `E21` |

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, SKU/firmware record, antenna VSWR, GNSS/IMU test, balise read, radio link test
- Tooling basis: RFQ-LM3-CTRL-P020, CERT-LM3-CTRL-P020, GAUGE-LM3-CTRL-P020-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-CTRL-P020-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-CTRL-P020-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-CTRL-P020-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-CTRL-P020`<br>`DOC-LM3-SYS-SA900` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-CTRL-P020`<br>`CERT-LM3-CTRL-P020` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-CTRL-P020-ENVELOPE`<br>`FIX-LM3-SYS-SA900` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: SKU/firmware record | quality inspection | 0.25 | `QA-LM3-CTRL-P020` | SKU/firmware record | quality inspector |
| 50 | verify acceptance gate: antenna VSWR | quality inspection | 0.25 | `QA-LM3-CTRL-P020` | antenna VSWR | quality inspector |
| 60 | verify acceptance gate: GNSS/IMU test | quality inspection | 0.25 | `QA-LM3-CTRL-P020` | GNSS/IMU test | quality inspector |
| 70 | verify acceptance gate: balise read | quality inspection | 0.25 | `QA-LM3-CTRL-P020` | balise read | quality inspector |
| 80 | verify acceptance gate: radio link test | quality inspection | 0.25 | `QA-LM3-CTRL-P020` | radio link test | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-CTRL-P020`<br>`KIT-LM3-SYS-SA900` | item is released, tagged, and staged for parent assembly | cell lead |

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
