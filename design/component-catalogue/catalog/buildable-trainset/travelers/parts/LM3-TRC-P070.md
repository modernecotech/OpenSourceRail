# Shop traveler — LM3-TRC-P070 — HV contactor, fuse, pre-charge, service-disconnect, and current-sensor panel

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `T11`, `T16` |

## Material specification

| Field | Value |
|---|---|
| Material family | roof electrical energy equipment |
| Grade / part class | PV module / resistor / clamp / isolator kit |
| Governing standard | supplier datasheet plus project bonding, isolation, fire, and vibration evidence |
| Form factor | module, thermal shield, aluminum/stainless clamp hardware, and UV-rated harness |
| Nominal section | roof keep-out, clamp pitch, and thermal clearance frozen by RFQ drawing |
| Finish / protection | UV/weather protection, hot-surface labelling, and galvanic isolation where required |
| Traceability | module serials, resistance/PV flash data, CoC, and harness batch |

Evidence required:

- certificate of conformity
- incoming inspection record
- electrical datasheet
- bonding/isolation record

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, isolation test, pre-charge timing, fuse rating evidence, service-disconnect lockout, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P070, CERT-LM3-TRC-P070, GAUGE-LM3-TRC-P070-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TRC-P070-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TRC-P070-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TRC-P070-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-TRC-P070`<br>`DOC-LM3-HV-SA510` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-TRC-P070`<br>`CERT-LM3-TRC-P070` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-TRC-P070-ENVELOPE`<br>`FIX-LM3-HV-SA510` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: isolation test | quality inspection | 0.25 | `ELEC-TEST-LM3-TRC-P070` | isolation test | quality inspector |
| 50 | verify acceptance gate: pre-charge timing | quality inspection | 0.25 | `QA-LM3-TRC-P070` | pre-charge timing | quality inspector |
| 60 | verify acceptance gate: fuse rating evidence | quality inspection | 0.25 | `QA-LM3-TRC-P070` | fuse rating evidence | quality inspector |
| 70 | verify acceptance gate: service-disconnect lockout | quality inspection | 0.25 | `QA-LM3-TRC-P070` | service-disconnect lockout | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-TRC-P070`<br>`KIT-LM3-HV-SA510` | item is released, tagged, and staged for parent assembly | cell lead |

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
