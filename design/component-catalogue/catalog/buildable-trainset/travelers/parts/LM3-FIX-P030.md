# Shop traveler — LM3-FIX-P030 — standard passenger-fixture saddle and equipment adapter kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B14`, `B15`, `E14` |

## Material specification

| Field | Value |
|---|---|
| Material family | calculated passenger-fixture saddle and adapter family |
| Grade / part class | laser-cut/folded 304/316 or coated S355 saddles with radiused edges, anti-rotation keys, isolators and M8 captive/floating joints |
| Governing standard | fixture-specific released load calculation/drawing plus material, fastener, fire, corrosion, proof-load and passenger-safety evidence |
| Form factor | common rail-side saddle blank CNC-trimmed/drilled into seat, handrail and equipment variants without transferring primary loads through trim panels |
| Nominal section | rail engagement, edge radius, anti-rotation feature, hole/slot range and fixture keep-out fixed by the controlled adapter drawing |
| Finish / protection | passivated or coated surfaces, electrically/galvanically isolated interfaces and cleanable snag-free passenger edges |
| Traceability | material/finish batch, adapter variant, fastener lot, installed position map, torque/locking record and first-article proof test |

Evidence required:

- certificate of conformity
- incoming inspection record
- adapter gauge
- fixture load proof
- egress and snag inspection

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, adapter gauge, fixture-specific load calculation, proof-load sample, egress and snag check
- Tooling basis: FIX-LM3-FIX-FAB plus GAUGE-LM3-FIX-P030-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-FIX-P030-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-FIX-P030-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-FIX-P030-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-FIX-P030`<br>`DOC-LM3-FIX-SA340` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-FIX-FAB`<br>`GAUGE-LM3-FIX-P030-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-FIX-SA340`<br>`TORQUE-LM3-FIX-P030` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: adapter gauge | quality inspection | 0.25 | `GAUGE-LM3-FIX-P030` | adapter gauge | quality inspector |
| 50 | verify acceptance gate: fixture-specific load calculation | quality inspection | 0.25 | `QA-LM3-FIX-P030` | fixture-specific load calculation | quality inspector |
| 60 | verify acceptance gate: proof-load sample | quality inspection | 0.25 | `QA-LM3-FIX-P030` | proof-load sample | quality inspector |
| 70 | verify acceptance gate: egress and snag check | quality inspection | 0.25 | `QA-LM3-FIX-P030` | egress and snag check | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-FIX-P030`<br>`KIT-LM3-FIX-SA340` | item is released, tagged, and staged for parent assembly | cell lead |

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
