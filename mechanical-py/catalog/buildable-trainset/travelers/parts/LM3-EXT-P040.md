# Shop traveler — LM3-EXT-P040 — hvac-24kw-direct-hv-dc roof HVAC

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.55 h |
| Route | `BID` |
| Procurement BOM lines | `T14` |

## Material specification

| Field | Value |
|---|---|
| Material family | supplier HVAC and air-distribution kit |
| Grade / part class | hot-climate roof HVAC / fire-rated interior duct kit |
| Governing standard | supplier rail/bus HVAC specification plus project EMC, vibration, and fire evidence |
| Form factor | packaged roof unit, curb gasket, diffusers, ducts, grilles, and access panels |
| Nominal section | roof curb and saloon envelope frozen by RFQ drawing |
| Finish / protection | supplier coating, condensate protection, and fire-rated interior surfaces |
| Traceability | unit serial number, refrigerant/coolant data, CoC, and fire-material batch |

Evidence required:

- certificate of conformity
- incoming inspection record
- capacity test evidence
- fire-material certificate

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, +50 C capacity evidence, condensate drain test, EMC/vibration evidence, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-EXT-P040, CERT-LM3-EXT-P040, GAUGE-LM3-EXT-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P040-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P040-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P040-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P040`<br>`DOC-LM3-ROOF-SA410` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P040`<br>`CERT-LM3-EXT-P040` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P040-ENVELOPE`<br>`FIX-LM3-ROOF-SA410` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: +50 C capacity evidence | quality inspection | 0.25 | `QA-LM3-EXT-P040` | +50 C capacity evidence | quality inspector |
| 50 | verify acceptance gate: condensate drain test | quality inspection | 0.25 | `LEAK-TEST-LM3-EXT-P040` | condensate drain test | quality inspector |
| 60 | verify acceptance gate: EMC/vibration evidence | quality inspection | 0.25 | `QA-LM3-EXT-P040` | EMC/vibration evidence | quality inspector |
| 70 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P040`<br>`KIT-LM3-ROOF-SA410` | item is released, tagged, and staged for parent assembly | cell lead |

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
