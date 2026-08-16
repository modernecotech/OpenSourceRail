# Shop traveler — LM3-EXT-P080 — fire-rated GFRP side-module laminate, core, gelcoat, and consumable kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `BID` |
| Procurement BOM lines | `B6` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier-qualified exterior GFRP side-module material pack |
| Grade / part class | UV-stable E-glass/vinyl-ester or equivalent fire-rated side-module laminate, core, gelcoat, release, and coupon consumables |
| Governing standard | supplier laminate certificate plus project EN 45545 fire/smoke and LM3-BDY-160 mould-process evidence |
| Form factor | kitted dry reinforcement, resin system, local core, gelcoat/paint-primer, release consumables, insert-potting consumables, and witness-coupon stock |
| Nominal section | supports 1,000 mm side-module mould pitch, 994 mm finished module width, solid/window/door trim variants, and solid clip lands |
| Finish / protection | UV-stable exterior finish system with sealed cut-edge compatibility and mixed-metal insert isolation |
| Traceability | fibre/resin/core/gelcoat batch, shelf-life record, cure/coupon trace, and fire certificate |

Evidence required:

- certificate of conformity
- incoming inspection record
- EN 45545 evidence
- laminate coupon
- resin/fibre batch trace
- mould release record

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, EN 45545 evidence, laminate coupon, resin/fibre batch trace, mould release record
- Tooling basis: RFQ-LM3-EXT-P080, CERT-LM3-EXT-P080, GAUGE-LM3-EXT-P080-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P080-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P080-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P080-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P080`<br>`DOC-LM3-SHELL-A200` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P080`<br>`CERT-LM3-EXT-P080` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P080-ENVELOPE`<br>`FIX-LM3-SHELL-A200` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: EN 45545 evidence | quality inspection | 0.25 | `QA-LM3-EXT-P080` | EN 45545 evidence | quality inspector |
| 50 | verify acceptance gate: laminate coupon | quality inspection | 0.25 | `QA-LM3-EXT-P080` | laminate coupon | quality inspector |
| 60 | verify acceptance gate: resin/fibre batch trace | quality inspection | 0.25 | `QA-LM3-EXT-P080` | resin/fibre batch trace | quality inspector |
| 70 | verify acceptance gate: mould release record | quality inspection | 0.25 | `QA-LM3-EXT-P080` | mould release record | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P080`<br>`KIT-LM3-SHELL-A200` | item is released, tagged, and staged for parent assembly | cell lead |

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
