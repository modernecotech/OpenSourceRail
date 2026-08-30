# Shop traveler — LM3-BOG-P047 — trailer-bogie to carbody connection: air springs, emergency spring, centre pivot, yaw links and dampers

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `BID` |
| Procurement BOM lines | `G6`, `G7`, `G10`, `G11`, `G12` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier-certified running gear |
| Grade / part class | wheelset / bearing / brake / suspension safety-critical kit |
| Governing standard | supplier rail running-gear specification plus project brake, ride-height, and traceability evidence |
| Form factor | machined/forged rotating parts, brake hardware, suspension elements, and fastener kit |
| Nominal section | bogie interface envelope frozen by RFQ drawing |
| Finish / protection | supplier corrosion protection and lubrication preservation |
| Traceability | serialised wheelset, bearing, brake, and suspension records |

Evidence required:

- certificate of conformity
- incoming inspection record
- wheelset/bearing certificates
- brake evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, vertical/lateral load curves, pivot proof and articulation limit, damper curves hot/cold, ride-height and anti-lift survey, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P047, CERT-LM3-BOG-P047, GAUGE-LM3-BOG-P047-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BOG-P047-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BOG-P047-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BOG-P047-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BOG-P047`<br>`DOC-LM3-BOG-SA620` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-BOG-P047`<br>`CERT-LM3-BOG-P047` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-BOG-P047-ENVELOPE`<br>`FIX-LM3-BOG-SA620` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: vertical/lateral load curves | quality inspection | 0.25 | `QA-LM3-BOG-P047` | vertical/lateral load curves | quality inspector |
| 50 | verify acceptance gate: pivot proof and articulation limit | quality inspection | 0.25 | `QA-LM3-BOG-P047` | pivot proof and articulation limit | quality inspector |
| 60 | verify acceptance gate: damper curves hot/cold | quality inspection | 0.25 | `QA-LM3-BOG-P047` | damper curves hot/cold | quality inspector |
| 70 | verify acceptance gate: ride-height and anti-lift survey | quality inspection | 0.25 | `GAUGE-LM3-BOG-P047` | ride-height and anti-lift survey | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BOG-P047`<br>`KIT-LM3-BOG-SA620` | item is released, tagged, and staged for parent assembly | cell lead |

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
