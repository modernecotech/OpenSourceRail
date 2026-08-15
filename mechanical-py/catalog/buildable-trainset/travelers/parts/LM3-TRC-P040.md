# Shop traveler — LM3-TRC-P040 — battery-225kwh-lfp-800v under-seat traction battery pack

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.55 h |
| Route | `BID` |
| Procurement BOM lines | `T5`, `T6` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier high-voltage traction equipment |
| Grade / part class | battery / inverter / contactor / charger certified equipment class |
| Governing standard | supplier rail traction specification plus project HVIL, EMC, isolation, and thermal evidence |
| Form factor | sealed HV module, enclosure, orange HV harness, connectors, cooling interfaces, and labels |
| Nominal section | tray, connector, bend-radius, vent, and service envelope frozen by RFQ drawing |
| Finish / protection | supplier enclosure protection, orange HV marking, bonding, and coolant compatibility |
| Traceability | serialised HV equipment CoC, firmware/config revision, insulation record, and evidence pack |

Evidence required:

- certificate of conformity
- incoming inspection record
- isolation test record
- HVIL / EMC evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, cell/module certificate, isolation test, vent/fire containment data, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P040, CERT-LM3-TRC-P040, GAUGE-LM3-TRC-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-TRC-P040-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-TRC-P040-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-TRC-P040-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-TRC-P040`<br>`DOC-LM3-HV-SA510` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-TRC-P040`<br>`CERT-LM3-TRC-P040` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-TRC-P040-ENVELOPE`<br>`FIX-LM3-HV-SA510` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: cell/module certificate | quality inspection | 0.25 | `QA-LM3-TRC-P040` | cell/module certificate | quality inspector |
| 50 | verify acceptance gate: isolation test | quality inspection | 0.25 | `ELEC-TEST-LM3-TRC-P040` | isolation test | quality inspector |
| 60 | verify acceptance gate: vent/fire containment data | quality inspection | 0.25 | `QA-LM3-TRC-P040` | vent/fire containment data | quality inspector |
| 70 | final item release to parent assembly | production control | 0.25 | `REL-LM3-TRC-P040`<br>`KIT-LM3-HV-SA510` | item is released, tagged, and staged for parent assembly | cell lead |

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
