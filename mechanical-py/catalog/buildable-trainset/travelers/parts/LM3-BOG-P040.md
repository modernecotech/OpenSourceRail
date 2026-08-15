# Shop traveler — LM3-BOG-P040 — powered-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.3 h |
| Route | `BID` |
| Procurement BOM lines | `G3`, `G4`, `G5`, `G6`, `G7`, `G8`, `G9`, `G10`, `G11`, `G12`, `G14`, `G15`, `G16` |

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
- Inspection methods: incoming visual inspection, envelope fit check, wheelset certificates, bearing records, spring/damper certificates, brake test, sensor test, ride-height report, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P040, CERT-LM3-BOG-P040, GAUGE-LM3-BOG-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BOG-P040-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BOG-P040-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BOG-P040-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BOG-P040`<br>`DOC-LM3-BOG-SA610` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-BOG-P040`<br>`CERT-LM3-BOG-P040` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-BOG-P040-ENVELOPE`<br>`FIX-LM3-BOG-SA610` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: wheelset certificates | quality inspection | 0.25 | `QA-LM3-BOG-P040` | wheelset certificates | quality inspector |
| 50 | verify acceptance gate: bearing records | quality inspection | 0.25 | `QA-LM3-BOG-P040` | bearing records | quality inspector |
| 60 | verify acceptance gate: spring/damper certificates | quality inspection | 0.25 | `QA-LM3-BOG-P040` | spring/damper certificates | quality inspector |
| 70 | verify acceptance gate: brake test | quality inspection | 0.25 | `QA-LM3-BOG-P040` | brake test | quality inspector |
| 80 | verify acceptance gate: sensor test | quality inspection | 0.25 | `QA-LM3-BOG-P040` | sensor test | quality inspector |
| 90 | verify acceptance gate: ride-height report | quality inspection | 0.25 | `QA-LM3-BOG-P040` | ride-height report | quality inspector |
| 100 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BOG-P040`<br>`KIT-LM3-BOG-SA610` | item is released, tagged, and staged for parent assembly | cell lead |

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
