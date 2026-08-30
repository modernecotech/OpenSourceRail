# Shop traveler — LM3-EXT-P061 — welded resilient floor covering, cove, nosing, and adhesive system

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B13` |

## Material specification

| Field | Value |
|---|---|
| Material family | rail fire-rated resilient floor-covering system |
| Grade / part class | supplier-matched sheet covering, welded-seam rod, coving, step nosing, primer, adhesive and repair-patch system |
| Governing standard | supplier rail flooring specification plus project fire/smoke/toxicity, slip, wear, cleaning-agent and substrate-compatibility evidence |
| Form factor | single-system sheet layout with heat-welded seams, coved edges, sealed penetrations, removable hatch cuts and replaceable threshold pieces |
| Nominal section | roll direction, seam map, cove radius, nosing, threshold termination, adhesive spread and hatch joint fixed by the released installation drawing |
| Finish / protection | anti-slip cleanable finish with no open edges, water traps or incompatible sealant/adhesive combinations |
| Traceability | covering/rod/primer/adhesive batch and expiry, substrate moisture/cleanliness record, cure log, seam sample and installed zone map |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire/smoke certificate
- adhesive compatibility/cure record
- seam peel sample
- slip evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire/smoke certificate, adhesive compatibility and cure record, welded-seam peel sample, slip and cleanability evidence
- Tooling basis: RFQ-LM3-EXT-P061, CERT-LM3-EXT-P061, GAUGE-LM3-EXT-P061-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P061-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P061-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P061-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P061`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P061`<br>`CERT-LM3-EXT-P061` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P061-ENVELOPE`<br>`FIX-LM3-INT-SA330` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: fire/smoke certificate | quality inspection | 0.25 | `QA-LM3-EXT-P061` | fire/smoke certificate | quality inspector |
| 50 | verify acceptance gate: adhesive compatibility and cure record | quality inspection | 0.25 | `QA-LM3-EXT-P061` | adhesive compatibility and cure record | quality inspector |
| 60 | verify acceptance gate: welded-seam peel sample | quality inspection | 0.25 | `NDT-LM3-EXT-P061` | welded-seam peel sample | quality inspector |
| 70 | verify acceptance gate: slip and cleanability evidence | quality inspection | 0.25 | `QA-LM3-EXT-P061` | slip and cleanability evidence | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P061`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

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
