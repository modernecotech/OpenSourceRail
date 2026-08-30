# Shop traveler — LM3-BOG-P049 — trailer-bogie brake calipers, parking actuators, pads and wheel-slide hardware

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `BID` |
| Procurement BOM lines | `G8`, `G9`, `G16` |

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, brake-force calculation, friction-pair certificate, thermal capacity, parking holding test, WSP functional test, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P049, CERT-LM3-BOG-P049, GAUGE-LM3-BOG-P049-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BOG-P049-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BOG-P049-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BOG-P049-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BOG-P049`<br>`DOC-LM3-BOG-SA621` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-BOG-P049`<br>`CERT-LM3-BOG-P049` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-BOG-P049-ENVELOPE`<br>`FIX-LM3-BOG-SA621` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: brake-force calculation | quality inspection | 0.25 | `QA-LM3-BOG-P049` | brake-force calculation | quality inspector |
| 50 | verify acceptance gate: friction-pair certificate | quality inspection | 0.25 | `QA-LM3-BOG-P049` | friction-pair certificate | quality inspector |
| 60 | verify acceptance gate: thermal capacity | quality inspection | 0.25 | `QA-LM3-BOG-P049` | thermal capacity | quality inspector |
| 70 | verify acceptance gate: parking holding test | quality inspection | 0.25 | `QA-LM3-BOG-P049` | parking holding test | quality inspector |
| 80 | verify acceptance gate: WSP functional test | quality inspection | 0.25 | `QA-LM3-BOG-P049` | WSP functional test | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BOG-P049`<br>`KIT-LM3-BOG-SA621` | item is released, tagged, and staged for parent assembly | cell lead |

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
