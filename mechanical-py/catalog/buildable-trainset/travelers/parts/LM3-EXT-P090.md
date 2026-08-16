# Shop traveler — LM3-EXT-P090 — fire-rated GFRP roof-module, dry-seal, and removable skirt material kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 3.05 h |
| Route | `BID` |
| Procurement BOM lines | `B7` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier-qualified exterior GFRP roof-module and seal material pack |
| Grade / part class | fire-rated roof-module laminate consumables, EPDM dry-seal stock, removable skirt blanks, and retained-fastener consumables |
| Governing standard | supplier laminate and seal certificates plus project EN 45545, ozone/UV, ingress, and LM3-BDY-160 mould-process evidence |
| Form factor | kitted roof-module reinforcement/core/resin/finish consumables, extruded EPDM seals, skirt blanks, trim stock, and coupon material |
| Nominal section | supports 1,000 mm roof-module mould pitch, dry joints, drain paths, removable skirts, and anti-lift/clip hardware interfaces |
| Finish / protection | UV-stable roof finish, sealed cut edges, ozone-resistant EPDM, and galvanic isolation at retained hardware |
| Traceability | laminate batch, seal batch, cure/coupon trace, service-removal record, and water-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- EN 45545 evidence
- roof laminate coupon
- seal certificate
- water and debris-ingress check

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, EN 45545 evidence, roof laminate coupon, seal certificate, service-removal trial, water and debris-ingress check
- Tooling basis: RFQ-LM3-EXT-P090, CERT-LM3-EXT-P090, GAUGE-LM3-EXT-P090-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P090-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P090-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P090-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P090`<br>`DOC-LM3-SHELL-A200` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P090`<br>`CERT-LM3-EXT-P090` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P090-ENVELOPE`<br>`FIX-LM3-SHELL-A200` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: EN 45545 evidence | quality inspection | 0.25 | `QA-LM3-EXT-P090` | EN 45545 evidence | quality inspector |
| 50 | verify acceptance gate: roof laminate coupon | quality inspection | 0.25 | `QA-LM3-EXT-P090` | roof laminate coupon | quality inspector |
| 60 | verify acceptance gate: seal certificate | quality inspection | 0.25 | `QA-LM3-EXT-P090` | seal certificate | quality inspector |
| 70 | verify acceptance gate: service-removal trial | quality inspection | 0.25 | `QA-LM3-EXT-P090` | service-removal trial | quality inspector |
| 80 | verify acceptance gate: water and debris-ingress check | quality inspection | 0.25 | `LEAK-TEST-LM3-EXT-P090` | water and debris-ingress check | quality inspector |
| 90 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P090`<br>`KIT-LM3-SHELL-A200` | item is released, tagged, and staged for parent assembly | cell lead |

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
