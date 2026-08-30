# Shop traveler — LM3-ART-P023 — inter-car passenger bridge, turntable and flexible interior-panel set

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
| Material family | passenger interior COTS kit |
| Grade / part class | fire-rated seat, flooring, trim, lighting, PIS, CCTV, signage, and grab-rail kit |
| Governing standard | supplier interior specification plus project EN 45545/fire-smoke evidence where applicable |
| Form factor | late-installed saloon kit with fasteners, access panels, looms, and labels |
| Nominal section | saloon, PRM aisle, emergency egress, and service-panel envelope frozen by RFQ drawing |
| Finish / protection | fire/smoke compliant finish, anti-slip flooring, and cleanable passenger surfaces |
| Traceability | batch CoC, fire-material certificates, and installation traceability |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire-material certificate pack
- egress/lighting evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, passenger load proof, anti-slip evidence, gap/step gauge, pinch/shear hazard review, full-motion sweep, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P023, CERT-LM3-ART-P023, GAUGE-LM3-ART-P023-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-P023-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-P023-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-P023-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-ART-P023`<br>`DOC-LM3-ART-SA820` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-ART-P023`<br>`CERT-LM3-ART-P023` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-ART-P023-ENVELOPE`<br>`FIX-LM3-ART-SA820` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: passenger load proof | quality inspection | 0.25 | `QA-LM3-ART-P023` | passenger load proof | quality inspector |
| 50 | verify acceptance gate: anti-slip evidence | quality inspection | 0.25 | `QA-LM3-ART-P023` | anti-slip evidence | quality inspector |
| 60 | verify acceptance gate: gap/step gauge | quality inspection | 0.25 | `GAUGE-LM3-ART-P023` | gap/step gauge | quality inspector |
| 70 | verify acceptance gate: pinch/shear hazard review | quality inspection | 0.25 | `QA-LM3-ART-P023` | pinch/shear hazard review | quality inspector |
| 80 | verify acceptance gate: full-motion sweep | quality inspection | 0.25 | `QA-LM3-ART-P023` | full-motion sweep | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-ART-P023`<br>`KIT-LM3-ART-SA820` | item is released, tagged, and staged for parent assembly | cell lead |

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
