# Shop traveler — LM3-ART-P024 — articulation trainline carrier, support arms, abrasion liners and drain path

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B24` |

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, rated bend radius, dynamic sweep, abrasion/fire evidence, drain test, service replacement trial, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P024, CERT-LM3-ART-P024, GAUGE-LM3-ART-P024-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-P024-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-P024-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-P024-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-ART-P024`<br>`DOC-LM3-ART-SA830` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-ART-P024`<br>`CERT-LM3-ART-P024` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-ART-P024-ENVELOPE`<br>`FIX-LM3-ART-SA830` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: rated bend radius | quality inspection | 0.25 | `QA-LM3-ART-P024` | rated bend radius | quality inspector |
| 50 | verify acceptance gate: dynamic sweep | quality inspection | 0.25 | `QA-LM3-ART-P024` | dynamic sweep | quality inspector |
| 60 | verify acceptance gate: abrasion/fire evidence | quality inspection | 0.25 | `QA-LM3-ART-P024` | abrasion/fire evidence | quality inspector |
| 70 | verify acceptance gate: drain test | quality inspection | 0.25 | `LEAK-TEST-LM3-ART-P024` | drain test | quality inspector |
| 80 | verify acceptance gate: service replacement trial | quality inspection | 0.25 | `QA-LM3-ART-P024` | service replacement trial | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-ART-P024`<br>`KIT-LM3-ART-SA830` | item is released, tagged, and staged for parent assembly | cell lead |

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
