# Shop traveler — LM3-CWL-P016 — CWL-FRP-06 backing-ring flange fiberglass cast set

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
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, mould release record, glass-carrier land survey, bond-line witness, A/B interchange check, split-line gap check, water-ingress test, repair coupon demonstration
- Tooling basis: MOULD/FIX-LM3-CWL-P016 plus TRIM-GAUGE-LM3-CWL-P016
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-CWL-P016-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-CWL-P016-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-CWL-P016-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-CWL-P016`<br>`DOC-LM3-CWL-SA710` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-CWL-FAB`<br>`GAUGE-LM3-CWL-P016-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-CWL-SA710`<br>`TORQUE-LM3-CWL-P016` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: mould release record | quality inspection | 0.25 | `QA-LM3-CWL-P016` | mould release record | quality inspector |
| 50 | verify acceptance gate: glass-carrier land survey | quality inspection | 0.25 | `GAUGE-LM3-CWL-P016` | glass-carrier land survey | quality inspector |
| 60 | verify acceptance gate: bond-line witness | quality inspection | 0.25 | `QA-LM3-CWL-P016` | bond-line witness | quality inspector |
| 70 | verify acceptance gate: A/B interchange check | quality inspection | 0.25 | `QA-LM3-CWL-P016` | A/B interchange check | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-CWL-P016`<br>`KIT-LM3-CWL-SA710` | item is released, tagged, and staged for parent assembly | cell lead |

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
