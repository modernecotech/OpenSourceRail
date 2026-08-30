# Shop traveler — LM3-BDY-P130 — one-metre clip-on fiberglass side and roof body module

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 6.35 h |
| Route | `MAKE` |
| Procurement BOM lines | `B6`, `B7` |

## Material specification

| Field | Value |
|---|---|
| Material family | fire-retardant exterior fiberglass sandwich |
| Grade / part class | UV-stable E-glass/vinyl-ester 1,000 mm body module with local core and potted inserts |
| Governing standard | project exterior laminate schedule plus EN 45545 fire/smoke, insert, vibration, and aerodynamic evidence |
| Form factor | 994 mm finished side/window/door/roof variants CNC-trimmed from a common 1,000 mm mould pitch |
| Nominal section | 28 mm nominal sandwich with solid clip lands, sealed edges, and replaceable 6 mm EPDM joints |
| Finish / protection | UV-stable exterior gelcoat/paint, sealed cut edges, drained joints, and mixed-metal isolation |
| Traceability | laminate/resin/cure batch, module serial, trim record, insert batch, and fire certificate |

Evidence required:

- certificate of conformity
- incoming inspection record
- laminate coupon
- insert/clip proof
- master-frame fit
- water/vibration evidence

## Process specification

- Primary processes: inspect mould/trim fixture, apply release system, cut dry reinforcement or panel blank, lay up / infuse / press laminate, controlled cure, demould and post-cure where required, trim/drill to controlled datum, fit inserts/clips/gaskets, dry-fit to parent fixture
- Joining methods: potted/captive inserts, retained fasteners or clip grid, adhesive/sealant only where removal and repair rules allow
- Special process controls: released laminate schedule, resin/adhesive batch and shelf-life check, mould release record, cure temperature/time record, fire-material certificate check, edge sealing and dust-control rule, A/B-end interchange rule, glass carrier and sensor datum protection
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, material/fire certificate, trim gauge, insert pull-out, master-frame dry fit, split-line gap check, water-ingress test, repair coupon demonstration
- Tooling basis: MOULD/FIX-LM3-BDY-P130 plus TRIM-GAUGE-LM3-BDY-P130
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BDY-P130-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BDY-P130-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BDY-P130-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-BDY-P130`<br>`DOC-LM3-SHELL-A200` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | inspect mould and trim fixture, release material batch, and apply release system | composite moulding cell | 0.65 | `MOULD-LM3-BDY-P130`<br>`TRIM-GAUGE-LM3-BDY-P130` | mould release record and material shelf-life accepted | operator |
| 30 | lay up glass-fibre reinforcement, core, solid lands, and insert bosses in mould | composite moulding cell | 1.35 | `MOULD-LM3-BDY-P130`<br>`PLYBOOK-LM3-BDY-P130` | ply/core/insert checklist matches released laminate schedule | operator |
| 40 | infuse or wet-lay laminate, control cure, demould, and retain witness coupons | controlled cure area | 1.1 | `CURE-LM3-BDY-P130`<br>`COUPON-LM3-BDY-P130` | cure record, demould inspection, and coupon trace are complete | operator |
| 50 | CNC trim and drill to datum, seal cut edges, and mark serial/revision | trim and drill cell | 0.85 | `TRIM-GAUGE-LM3-BDY-P130`<br>`GAUGE-LM3-BDY-P130-DATUM` | trim, drill, and sealed-edge records match the released variant | operator |
| 60 | fit inserts, clips, retainers, gaskets, or captive fasteners and dry-fit to parent fixture | module fit-up cell | 0.8 | `FIX-LM3-SHELL-A200`<br>`TORQUE-LM3-BDY-P130`<br>`GAUGE-LM3-BDY-P130` | fit-up evidence recorded before release to assembly | operator |
| 70 | verify acceptance gate: material/fire certificate | quality inspection | 0.25 | `QA-LM3-BDY-P130` | material/fire certificate | quality inspector |
| 80 | verify acceptance gate: trim gauge | quality inspection | 0.25 | `GAUGE-LM3-BDY-P130` | trim gauge | quality inspector |
| 90 | verify acceptance gate: insert pull-out | quality inspection | 0.25 | `QA-LM3-BDY-P130` | insert pull-out | quality inspector |
| 100 | verify acceptance gate: master-frame dry fit | quality inspection | 0.25 | `QA-LM3-BDY-P130` | master-frame dry fit | quality inspector |
| 110 | final item release to parent assembly | production control | 0.25 | `REL-LM3-BDY-P130`<br>`KIT-LM3-SHELL-A200` | item is released, tagged, and staged for parent assembly | cell lead |

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
