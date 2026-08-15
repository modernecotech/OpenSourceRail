# Shop traveler — LM3-ART-P030 — inter-car HV/LV jumper, coolant hose loop, energy chain, and drain sleeve kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `BID` |
| Procurement BOM lines | `B24` |

## Material specification

| Field | Value |
|---|---|
| Material family | rail-rated electrical / control equipment |
| Grade / part class | LV/data harness, cabinet, sensor, antenna, and trainline kit |
| Governing standard | supplier rail electronics specification plus project EMC, IP, and fire evidence |
| Form factor | cabinet, harness, connector, sensor, bracket, antenna, and label kit |
| Nominal section | connector, bend-radius, service-loop, and mounting envelope frozen by RFQ drawing |
| Finish / protection | halogen/fire-rated cable where required, IP sealing, bonding, and label protection |
| Traceability | serialised equipment CoC, firmware/config record, harness batch, and continuity record |

Evidence required:

- certificate of conformity
- incoming inspection record
- continuity test
- EMC/IP evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, bend-radius sweep, trainline continuity, coolant pressure test, water-drain test, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P030, CERT-LM3-ART-P030, GAUGE-LM3-ART-P030-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ART-P030-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ART-P030-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ART-P030-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-ART-P030`<br>`DOC-LM3-ART-SA800` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-ART-P030`<br>`CERT-LM3-ART-P030` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-ART-P030-ENVELOPE`<br>`FIX-LM3-ART-SA800` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: bend-radius sweep | quality inspection | 0.25 | `QA-LM3-ART-P030` | bend-radius sweep | quality inspector |
| 50 | verify acceptance gate: trainline continuity | quality inspection | 0.25 | `ELEC-TEST-LM3-ART-P030` | trainline continuity | quality inspector |
| 60 | verify acceptance gate: coolant pressure test | quality inspection | 0.25 | `LEAK-TEST-LM3-ART-P030` | coolant pressure test | quality inspector |
| 70 | verify acceptance gate: water-drain test | quality inspection | 0.25 | `LEAK-TEST-LM3-ART-P030` | water-drain test | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-ART-P030`<br>`KIT-LM3-ART-SA800` | item is released, tagged, and staged for parent assembly | cell lead |

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
