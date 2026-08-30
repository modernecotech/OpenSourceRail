# Shop traveler — LM3-ART-P020 — articulation lower spherical pivot, bearing housing and pin set

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `BID` |
| Procurement BOM lines | `B9` |

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
- Inspection methods: incoming visual inspection, envelope fit check, bearing static/dynamic capacity, pin material/NDT, proof load, lubrication/sealing plan, motion-envelope proof, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P020, CERT-LM3-ART-P020, GAUGE-LM3-ART-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-P020-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-P020-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-P020-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-ART-P020`<br>`DOC-LM3-ART-SA810` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-ART-P020`<br>`CERT-LM3-ART-P020` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-ART-P020-ENVELOPE`<br>`FIX-LM3-ART-SA810` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: bearing static/dynamic capacity | quality inspection | 0.25 | `QA-LM3-ART-P020` | bearing static/dynamic capacity | quality inspector |
| 50 | verify acceptance gate: pin material/NDT | quality inspection | 0.25 | `NDT-LM3-ART-P020` | pin material/NDT | quality inspector |
| 60 | verify acceptance gate: proof load | quality inspection | 0.25 | `QA-LM3-ART-P020` | proof load | quality inspector |
| 70 | verify acceptance gate: lubrication/sealing plan | quality inspection | 0.25 | `QA-LM3-ART-P020` | lubrication/sealing plan | quality inspector |
| 80 | verify acceptance gate: motion-envelope proof | quality inspection | 0.25 | `QA-LM3-ART-P020` | motion-envelope proof | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-ART-P020`<br>`KIT-LM3-ART-SA810` | item is released, tagged, and staged for parent assembly | cell lead |

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
