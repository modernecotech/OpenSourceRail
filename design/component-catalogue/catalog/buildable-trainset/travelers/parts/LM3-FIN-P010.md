# Shop traveler — LM3-FIN-P010 — pre-cut exterior livery graphic film, edge-seal, datum-mark, and repair-patch kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `BID` |
| Procurement BOM lines | `B20`, `B28` |

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
- Inspection methods: incoming visual inspection, envelope fit check, supplier rail-use statement, substrate/cure acceptance, adhesion coupon, edge/overlap inspection, cleaning/removal trial
- Tooling basis: RFQ-LM3-FIN-P010, CERT-LM3-FIN-P010, GAUGE-LM3-FIN-P010-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-FIN-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-FIN-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-FIN-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-FIN-P010`<br>`DOC-LM3-SHELL-A200` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-FIN-P010`<br>`CERT-LM3-FIN-P010` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-FIN-P010-ENVELOPE`<br>`FIX-LM3-SHELL-A200` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: supplier rail-use statement | quality inspection | 0.25 | `QA-LM3-FIN-P010` | supplier rail-use statement | quality inspector |
| 50 | verify acceptance gate: substrate/cure acceptance | quality inspection | 0.25 | `QA-LM3-FIN-P010` | substrate/cure acceptance | quality inspector |
| 60 | verify acceptance gate: adhesion coupon | quality inspection | 0.25 | `QA-LM3-FIN-P010` | adhesion coupon | quality inspector |
| 70 | verify acceptance gate: edge/overlap inspection | quality inspection | 0.25 | `QA-LM3-FIN-P010` | edge/overlap inspection | quality inspector |
| 80 | verify acceptance gate: cleaning/removal trial | quality inspection | 0.25 | `QA-LM3-FIN-P010` | cleaning/removal trial | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-FIN-P010`<br>`KIT-LM3-SHELL-A200` | item is released, tagged, and staged for parent assembly | cell lead |

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
