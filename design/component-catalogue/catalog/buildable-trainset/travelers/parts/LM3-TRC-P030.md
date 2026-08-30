# Shop traveler — LM3-TRC-P030 — two independent motor controllers, isolated LV DC/DC, MPPT, station protection, and cooling-loop kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.55 h |
| Route | `BID` |
| Procurement BOM lines | `T3`, `T4`, `T7`, `T13`, `T20`, `T23` |

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, HVIL test, coolant pressure test, EMC/bonding check, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-TRC-P030, CERT-LM3-TRC-P030, GAUGE-LM3-TRC-P030-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TRC-P030-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TRC-P030-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TRC-P030-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-TRC-P030`<br>`DOC-LM3-HV-SA510` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-TRC-P030`<br>`CERT-LM3-TRC-P030` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-TRC-P030-ENVELOPE`<br>`FIX-LM3-HV-SA510` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: HVIL test | quality inspection | 0.25 | `ELEC-TEST-LM3-TRC-P030` | HVIL test | quality inspector |
| 50 | verify acceptance gate: coolant pressure test | quality inspection | 0.25 | `LEAK-TEST-LM3-TRC-P030` | coolant pressure test | quality inspector |
| 60 | verify acceptance gate: EMC/bonding check | quality inspection | 0.25 | `QA-LM3-TRC-P030` | EMC/bonding check | quality inspector |
| 70 | final item release to parent assembly | production control | 0.25 | `REL-LM3-TRC-P030`<br>`KIT-LM3-HV-SA510` | item is released, tagged, and staged for parent assembly | cell lead |

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
