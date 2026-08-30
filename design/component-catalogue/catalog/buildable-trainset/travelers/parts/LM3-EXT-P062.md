# Shop traveler — LM3-EXT-P062 — longitudinal passenger and priority-seat modules

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B14` |

## Material specification

| Field | Value |
|---|---|
| Material family | rail passenger-seat module and calculated mounting kit |
| Grade / part class | fire-rated longitudinal seat shells/cushions, metallic frame, common-rail saddles, anti-rotation keys, isolators and captive locking hardware |
| Governing standard | supplier rail-seat specification plus project fire/smoke, occupant/abuse load, sharp-edge, accessibility, corrosion and cleanability evidence |
| Form factor | replaceable seat modules mounted only through LM3-FIX saddles to structural/common rails, never through finish panels |
| Nominal section | seat pitch, cant, aisle/PRM clearance, hand clearance, saddle engagement and fastener grip fixed by LM3-INT-230 drawings and released load calculation |
| Finish / protection | cleanable graffiti-resistant finish, radiused passenger edges, isolated dissimilar metals and accessible captive service fasteners |
| Traceability | seat serial/batch, fire certificate, adapter variant, fastener lot, torque/locking witness and installed position map |

Evidence required:

- certificate of conformity
- incoming inspection record
- seat/occupant load evidence
- fixture proof
- egress/cleaning gauge
- timed module replacement

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire/smoke certificate, seat/occupant load evidence, fastener and anti-rotation record, egress and cleaning-clearance gauge
- Tooling basis: RFQ-LM3-EXT-P062, CERT-LM3-EXT-P062, GAUGE-LM3-EXT-P062-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P062-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P062-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P062-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P062`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P062`<br>`CERT-LM3-EXT-P062` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P062-ENVELOPE`<br>`FIX-LM3-INT-SA330` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: fire/smoke certificate | quality inspection | 0.25 | `QA-LM3-EXT-P062` | fire/smoke certificate | quality inspector |
| 50 | verify acceptance gate: seat/occupant load evidence | quality inspection | 0.25 | `QA-LM3-EXT-P062` | seat/occupant load evidence | quality inspector |
| 60 | verify acceptance gate: fastener and anti-rotation record | quality inspection | 0.25 | `TORQUE-LM3-EXT-P062` | fastener and anti-rotation record | quality inspector |
| 70 | verify acceptance gate: egress and cleaning-clearance gauge | quality inspection | 0.25 | `GAUGE-LM3-EXT-P062` | egress and cleaning-clearance gauge | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P062`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

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
