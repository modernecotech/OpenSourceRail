# Shop traveler — LM3-BDY-P140 — keyed clip rail, captive retainer, anti-lift, and dry-seal car kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B7` |

## Material specification

| Field | Value |
|---|---|
| Material family | stainless retention hardware and elastomer seal kit |
| Grade / part class | keyed hook, captive over-centre clip, independent anti-lift retainer, backing plate, and railway-grade EPDM seal |
| Governing standard | released LM3-BDY-160 joint calculation plus project corrosion, fatigue, fire, and ingress requirements |
| Form factor | laser-cut/folded clip rails, captive hardware, potted backing plates, and extruded dry seals |
| Nominal section | common 1,000 mm pitch with asymmetric key and visible closed witness mark |
| Finish / protection | passivated stainless hardware, isolated mixed-metal interfaces, UV/ozone-resistant EPDM |
| Traceability | hardware heat/batch, seal batch, proof-lot record, and car module map |

Evidence required:

- certificate of conformity
- incoming inspection record
- clip proof-load lot
- seal certificate
- water-ingress record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, clip proof load, anti-reversal gauge, retainer witness-mark check, water ingress test
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P140-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BDY-P140-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BDY-P140-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BDY-P140-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BDY-P140`<br>`DOC-LM3-SHELL-A200` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-BDY-FAB`<br>`GAUGE-LM3-BDY-P140-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-SHELL-A200`<br>`TORQUE-LM3-BDY-P140` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: clip proof load | quality inspection | 0.25 | `QA-LM3-BDY-P140` | clip proof load | quality inspector |
| 50 | verify acceptance gate: anti-reversal gauge | quality inspection | 0.25 | `GAUGE-LM3-BDY-P140` | anti-reversal gauge | quality inspector |
| 60 | verify acceptance gate: retainer witness-mark check | quality inspection | 0.25 | `QA-LM3-BDY-P140` | retainer witness-mark check | quality inspector |
| 70 | verify acceptance gate: water ingress test | quality inspection | 0.25 | `LEAK-TEST-LM3-BDY-P140` | water ingress test | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BDY-P140`<br>`KIT-LM3-SHELL-A200` | item is released, tagged, and staged for parent assembly | cell lead |

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
