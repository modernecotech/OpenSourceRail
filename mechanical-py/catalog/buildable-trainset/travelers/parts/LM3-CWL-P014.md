# Shop traveler — LM3-CWL-P014 — CWL-FRP-04 lower apron and anti-climber cover fiberglass cast

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B8` |

## Material specification

| Field | Value |
|---|---|
| Material family | fire-retardant fiberglass composite |
| Grade / part class | E-glass FRP cast kit with bonded/moulded inserts |
| Governing standard | supplier laminate schedule plus project fire/smoke and structural coupon evidence |
| Form factor | multi-part moulded shell, bonded inserts, service hatch lands, and trim edges |
| Nominal section | laminate schedule, insert pattern, split line, and trim datum frozen by supplier drawing |
| Finish / protection | UV-stable exterior gelcoat/paint with sealed cut edges and insert corrosion isolation |
| Traceability | laminate batch, resin batch, cure record, insert pull-out record, and coupon traceability |

Evidence required:

- laminate coupon
- cure record
- insert pull-out evidence
- fire-smoke certificate

## Process specification

- Primary processes: inspect mould/trim fixture, apply release system, cut dry reinforcement or panel blank, lay up / infuse / press laminate, controlled cure, demould and post-cure where required, trim/drill to controlled datum, fit inserts/clips/gaskets, dry-fit to parent fixture
- Joining methods: potted/captive inserts, retained fasteners or clip grid, adhesive/sealant only where removal and repair rules allow
- Special process controls: released laminate schedule, resin/adhesive batch and shelf-life check, mould release record, cure temperature/time record, fire-material certificate check, edge sealing and dust-control rule, A/B-end interchange rule, glass carrier and sensor datum protection
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, mould release record, lamp pocket gauge, drain-path water test, split-line gap check, water-ingress test, repair coupon demonstration
- Tooling basis: MOULD/FIX-LM3-CWL-P014 plus TRIM-GAUGE-LM3-CWL-P014
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-CWL-P014-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-CWL-P014-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-CWL-P014-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-CWL-P014`<br>`DOC-LM3-CWL-SA710` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-CWL-FAB`<br>`GAUGE-LM3-CWL-P014-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-CWL-SA710`<br>`TORQUE-LM3-CWL-P014` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: mould release record | quality inspection | 0.25 | `QA-LM3-CWL-P014` | mould release record | quality inspector |
| 50 | verify acceptance gate: laminate coupon | quality inspection | 0.25 | `QA-LM3-CWL-P014` | laminate coupon | quality inspector |
| 60 | verify acceptance gate: lamp pocket gauge | quality inspection | 0.25 | `GAUGE-LM3-CWL-P014` | lamp pocket gauge | quality inspector |
| 70 | verify acceptance gate: drain-path water test | quality inspection | 0.25 | `LEAK-TEST-LM3-CWL-P014` | drain-path water test | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-CWL-P014`<br>`KIT-LM3-CWL-SA710` | item is released, tagged, and staged for parent assembly | cell lead |

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
