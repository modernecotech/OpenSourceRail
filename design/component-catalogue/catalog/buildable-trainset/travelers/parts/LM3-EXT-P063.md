# Shop traveler — LM3-EXT-P063 — stainless grab-pole, handrail, joint, and insulated adapter kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B15` |

## Material specification

| Field | Value |
|---|---|
| Material family | modular passenger handrail and stanchion system |
| Grade / part class | 304/316 stainless tube candidate, radiused cast/machined joints, insulated common-rail saddles, anti-rotation keys and captive locking hardware |
| Governing standard | supplier material/finish specification plus project passenger load, fatigue, fire, accessibility, corrosion, electrical-isolation and snag evidence |
| Form factor | cut-to-length repeated tubes and replaceable elbows/tees fixed at structural floor/ceiling/service-rail datums without loading liners |
| Nominal section | tube diameter/wall, joint engagement, support span, reachable zones, adapter geometry and fastener grip fixed by LM3-INT-230 drawings and calculation |
| Finish / protection | brushed/passivated cleanable surface, radiused ends, no exposed threads, isolated mixed metals and sealed floor penetrations |
| Traceability | tube heat/batch, fitting/fastener lot, cut list, joint locking witness, installed survey and proof-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- fixture-specific proof-load evidence
- reach/egress survey
- locking audit
- timed joint replacement

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, material/finish certificate, joint locking record, fixture-specific proof-load evidence, reach, egress and snag survey
- Tooling basis: RFQ-LM3-EXT-P063, CERT-LM3-EXT-P063, GAUGE-LM3-EXT-P063-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P063-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P063-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P063-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P063`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P063`<br>`CERT-LM3-EXT-P063` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P063-ENVELOPE`<br>`FIX-LM3-INT-SA330` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: material/finish certificate | quality inspection | 0.25 | `QA-LM3-EXT-P063` | material/finish certificate | quality inspector |
| 50 | verify acceptance gate: joint locking record | quality inspection | 0.25 | `QA-LM3-EXT-P063` | joint locking record | quality inspector |
| 60 | verify acceptance gate: fixture-specific proof-load evidence | quality inspection | 0.25 | `QA-LM3-EXT-P063` | fixture-specific proof-load evidence | quality inspector |
| 70 | verify acceptance gate: reach, egress and snag survey | quality inspection | 0.25 | `GAUGE-LM3-EXT-P063` | reach, egress and snag survey | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P063`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

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
