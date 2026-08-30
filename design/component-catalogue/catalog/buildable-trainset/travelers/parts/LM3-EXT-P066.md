# Shop traveler — LM3-EXT-P066 — PRM, safety-signage, emergency-lighting, extinguisher, and first-aid kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 2.8 h |
| Route | `SOURCE` |
| Procurement BOM lines | `A1`, `A2`, `A3`, `A4` |

## Material specification

| Field | Value |
|---|---|
| Material family | controlled PRM and emergency-equipment location kit |
| Grade / part class | passenger call controls, tactile/visual labels, battery-backed exit markers, certified extinguisher/first-aid brackets, tamper seals and common adapters |
| Governing standard | selected national accessibility/fire rules plus supplier fire, photometric, battery-duration, extinguisher/bracket, label-durability and lifecycle evidence |
| Form factor | fixed equipment installed to the released location schedule; replenishable/expiring contents remain separately recorded operator stock |
| Nominal section | reachable controls, contrast/tactile content, illuminated sightlines, bracket loads, egress keep-outs and service access fixed by project review |
| Finish / protection | cleanable UV/chemical-resistant labels, radiused tamper-resistant brackets and protected emergency battery/connector interfaces |
| Traceability | equipment serial/batch, label revision/language, battery date, extinguisher/first-aid expiry, seal number and installed location audit |

Evidence required:

- certificate of conformity
- incoming inspection record
- accessible reach/contrast review
- emergency-light duration test
- expiry audit
- egress survey

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, accessible reach/contrast review, emergency-light duration test, equipment certificate/expiry audit, location and egress survey
- Tooling basis: RFQ-LM3-EXT-P066, CERT-LM3-EXT-P066, GAUGE-LM3-EXT-P066-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-EXT-P066-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-EXT-P066-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-EXT-P066-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-EXT-P066`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | receive supplier component and quarantine until evidence pack passes | receiving inspection | 0.45 | `RFQ-LM3-EXT-P066`<br>`CERT-LM3-EXT-P066` | supplier certificate/datasheet/revision accepted | quality inspector |
| 30 | perform envelope, mounting, service-removal, and connector checks | incoming fit-check cell | 0.75 | `GAUGE-LM3-EXT-P066-ENVELOPE`<br>`FIX-LM3-INT-SA330` | component fits without parent datum rework | operator |
| 40 | verify acceptance gate: accessible reach/contrast review | quality inspection | 0.25 | `QA-LM3-EXT-P066` | accessible reach/contrast review | quality inspector |
| 50 | verify acceptance gate: emergency-light duration test | quality inspection | 0.25 | `QA-LM3-EXT-P066` | emergency-light duration test | quality inspector |
| 60 | verify acceptance gate: equipment certificate/expiry audit | quality inspection | 0.25 | `QA-LM3-EXT-P066` | equipment certificate/expiry audit | quality inspector |
| 70 | verify acceptance gate: location and egress survey | quality inspection | 0.25 | `GAUGE-LM3-EXT-P066` | location and egress survey | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-EXT-P066`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

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
