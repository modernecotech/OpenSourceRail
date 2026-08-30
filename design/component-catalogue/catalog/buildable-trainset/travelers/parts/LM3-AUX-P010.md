# Shop traveler — LM3-AUX-P010 — secondary-suspension compressor, dryer, reservoir, and isolation-manifold kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `SOURCE` |
| Procurement BOM lines | `G21` |

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
- Inspection methods: incoming visual inspection, envelope fit check, pressure certificate, leak test, dryer function, relief-valve test, service-access check, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-AUX-P010, CERT-LM3-AUX-P010, GAUGE-LM3-AUX-P010-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-AUX-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-AUX-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-AUX-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-AUX-P010`<br>`DOC-LM3-CAR-A900` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-AUX-P010`<br>`CERT-LM3-AUX-P010` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-AUX-P010-ENVELOPE`<br>`FIX-LM3-CAR-A900` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: pressure certificate | quality inspection | 0.25 | `LEAK-TEST-LM3-AUX-P010` | pressure certificate | quality inspector |
| 50 | verify acceptance gate: leak test | quality inspection | 0.25 | `LEAK-TEST-LM3-AUX-P010` | leak test | quality inspector |
| 60 | verify acceptance gate: dryer function | quality inspection | 0.25 | `QA-LM3-AUX-P010` | dryer function | quality inspector |
| 70 | verify acceptance gate: relief-valve test | quality inspection | 0.25 | `QA-LM3-AUX-P010` | relief-valve test | quality inspector |
| 80 | verify acceptance gate: service-access check | quality inspection | 0.25 | `QA-LM3-AUX-P010` | service-access check | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-AUX-P010`<br>`KIT-LM3-CAR-A900` | item is released, tagged, and staged for parent assembly | cell lead |

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
