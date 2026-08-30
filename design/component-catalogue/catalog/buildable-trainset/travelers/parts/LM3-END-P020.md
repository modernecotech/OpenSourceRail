# Shop traveler — LM3-END-P020 — T-OBS nose sensor pack, heated window services, and washer kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.55 h |
| Route | `BID` |
| Procurement BOM lines | `E15`, `E18`, `E19` |

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, sensor calibration, washer/heater test, 2oo2 verdict interface test, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-END-P020, CERT-LM3-END-P020, GAUGE-LM3-END-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-END-P020-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-END-P020-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-END-P020-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-END-P020`<br>`DOC-LM3-END-SA700` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-END-P020`<br>`CERT-LM3-END-P020` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-END-P020-ENVELOPE`<br>`FIX-LM3-END-SA700` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: sensor calibration | quality inspection | 0.25 | `QA-LM3-END-P020` | sensor calibration | quality inspector |
| 50 | verify acceptance gate: washer/heater test | quality inspection | 0.25 | `QA-LM3-END-P020` | washer/heater test | quality inspector |
| 60 | verify acceptance gate: 2oo2 verdict interface test | quality inspection | 0.25 | `QA-LM3-END-P020` | 2oo2 verdict interface test | quality inspector |
| 70 | final item release to parent assembly | production control | 0.25 | `REL-LM3-END-P020`<br>`KIT-LM3-END-SA700` | item is released, tagged, and staged for parent assembly | cell lead |

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
