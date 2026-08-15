# Shop traveler — LM3-EXT-P080 — fire-rated composite exterior side sandwich-panel kit

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
| Material family | fire-retardant fiberglass composite |
| Grade / part class | E-glass or basalt-fibre/vinyl-ester end-cowl laminate and insert kit |
| Governing standard | supplier laminate schedule plus project fire/smoke, coupon, and insert pull-out evidence |
| Form factor | moulded cowl cast, solid flanges, local core in broad skins, potted inserts, and trim/repair coupons |
| Nominal section | laminate thickness, ply drop, core map, insert pattern, split line, and trim datum per LM3-BDY-155 |
| Finish / protection | UV-stable exterior gelcoat/paint, sealed cut edges, gasketed seams, and mixed-metal isolation |
| Traceability | laminate batch, resin batch, cure record, insert pull-out record, adhesive batch, and coupon traceability |

Evidence required:

- certificate of conformity
- incoming inspection record
- laminate coupon
- cure record
- insert pull-out evidence
- fire-smoke certificate

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, EN 45545 evidence, panel dimensional report, insert pull-out, bond coupon and water test
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
| 50 | verify acceptance gate: panel dimensional report | quality inspection | 0.25 | `QA-LM3-EXT-P080` | panel dimensional report | quality inspector |
| 60 | verify acceptance gate: insert pull-out | quality inspection | 0.25 | `QA-LM3-EXT-P080` | insert pull-out | quality inspector |
| 70 | verify acceptance gate: bond coupon and water test | quality inspection | 0.25 | `LEAK-TEST-LM3-EXT-P080` | bond coupon and water test | quality inspector |
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
