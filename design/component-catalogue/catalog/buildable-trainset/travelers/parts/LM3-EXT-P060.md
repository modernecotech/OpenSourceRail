# Shop traveler — LM3-EXT-P060 — stepped floor-board and removable service-hatch system

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `B12` |

## Material specification

| Field | Value |
|---|---|
| Material family | fire-rated structural floor-board and hatch system |
| Grade / part class | rail-qualified aluminium-honeycomb/composite board candidate with aluminium edge closures, stainless retained hatch hardware, isolating pads and sealed inspection plugs |
| Governing standard | supplier rail floor specification plus project fire/smoke, concentrated/distributed load, fatigue, moisture, slip-interface and toxicity evidence |
| Form factor | CNC-cut numbered boards and flush removable hatches supported continuously at released crossmember/service-rail datums |
| Nominal section | board thickness, core/skin schedule, support pitch, edge distance, hatch rebates, service clearances and step transitions fixed by LM3-INT-230 drawings and calculation |
| Finish / protection | sealed cut edges and penetrations, isolated mixed-metal joints, no water-trapping pockets, and floor-covering-compatible prepared face |
| Traceability | board/panel batch, cut nest, edge-seal batch, retained-fastener lot, installed position, datum survey and load-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire/smoke certificate
- floor load/deflection evidence
- hatch removal trial
- level/step survey

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire certificate, panel load and deflection evidence, hatch removal trial, level/step and egress survey
- Tooling basis: RFQ-LM3-EXT-P060, CERT-LM3-EXT-P060, GAUGE-LM3-EXT-P060-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P060-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P060-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P060-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P060`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P060`<br>`CERT-LM3-EXT-P060` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P060-ENVELOPE`<br>`FIX-LM3-INT-SA330` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: fire certificate | quality inspection | 0.25 | `QA-LM3-EXT-P060` | fire certificate | quality inspector |
| 50 | verify acceptance gate: panel load and deflection evidence | quality inspection | 0.25 | `QA-LM3-EXT-P060` | panel load and deflection evidence | quality inspector |
| 60 | verify acceptance gate: hatch removal trial | quality inspection | 0.25 | `QA-LM3-EXT-P060` | hatch removal trial | quality inspector |
| 70 | verify acceptance gate: level/step and egress survey | quality inspection | 0.25 | `GAUGE-LM3-EXT-P060` | level/step and egress survey | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P060`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

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
