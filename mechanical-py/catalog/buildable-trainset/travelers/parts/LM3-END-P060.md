# Shop traveler — LM3-END-P060 — common reversible end-interface carrier ring, option bolt grid, and sealing datum kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B2` |

## Material specification

| Field | Value |
|---|---|
| Material family | common structural end-interface steel and seal datum kit |
| Grade / part class | S355 machined carrier ring, stainless option bolt-grid inserts, drain lands, and EPDM sealing datums |
| Governing standard | released LM3-END-650 interface-control drawing plus EN 15085 weld, corrosion, and ingress evidence |
| Form factor | jig-welded/machined end carrier ring with common panoramic/open-mid bolt pattern and replaceable seal lands |
| Nominal section | one common end position envelope accepting either LM3-END-SA700 or LM3-TTART-SA850 without primary-frame rework |
| Finish / protection | blast/prime/topcoat on steel, passivated stainless inserts, sealed drain edges, and isolated mixed-metal joints |
| Traceability | steel heat, weld consumable, insert batch, machining survey, seal batch, and configuration record |

Evidence required:

- certificate of conformity
- incoming inspection record
- option bolt-grid survey
- seal datum continuity
- configuration fit gauge

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, option bolt-grid survey, seal datum continuity, A/B interchange check, end-option fit gauge
- Tooling basis: FIX-LM3-END-FAB plus GAUGE-LM3-END-P060-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-END-P060-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-END-P060-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-END-P060-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-END-P060`<br>`DOC-LM3-EIF-SA650` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-END-FAB`<br>`GAUGE-LM3-END-P060-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-EIF-SA650`<br>`TORQUE-LM3-END-P060` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: option bolt-grid survey | quality inspection | 0.25 | `GAUGE-LM3-END-P060` | option bolt-grid survey | quality inspector |
| 50 | verify acceptance gate: seal datum continuity | quality inspection | 0.25 | `GAUGE-LM3-END-P060` | seal datum continuity | quality inspector |
| 60 | verify acceptance gate: A/B interchange check | quality inspection | 0.25 | `QA-LM3-END-P060` | A/B interchange check | quality inspector |
| 70 | verify acceptance gate: end-option fit gauge | quality inspection | 0.25 | `GAUGE-LM3-END-P060` | end-option fit gauge | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-END-P060`<br>`KIT-LM3-EIF-SA650` | item is released, tagged, and staged for parent assembly | cell lead |

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
