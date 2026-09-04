# Shop traveler — LM3-INT-P032 — waist cable-cover, low-voltage access lid, and retained quarter-turn fastener set

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B21` |

## Material specification

| Field | Value |
|---|---|
| Material family | fire-rated cabin fiberglass / phenolic composite |
| Grade / part class | EN 45545 HL2 candidate FRP, phenolic, or glass/basalt-fibre sandwich interior panel |
| Governing standard | EN 45545-2 interior material evidence plus supplier laminate/phenolic panel certificate |
| Form factor | moulded or CNC-trimmed liner, reveal, cover, hatch, and kick-panel shells with potted inserts |
| Nominal section | panel thickness, edge return, insert pattern, and clip grid per LM3-INT v2A drawing |
| Finish / protection | cleanable interior gelcoat/paint or decorative film with sealed edges and anti-slip finish where walked on |
| Traceability | laminate/panel batch, resin/cure or board batch, insert batch, adhesive batch, and fire certificate |

Evidence required:

- fire-material certificate
- laminate/panel batch record
- insert pull-out evidence
- trim/cure record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, surface-preparation record, adhesive batch/pot-life record, bond coupon where required, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond-land inspection, water/leak test where applicable, bond continuity, insulation/isolation check where applicable, fire-material certificate, segregation inspection, captive-fastener audit, cover removal/rattle check
- Tooling basis: FIX-LM3-INT-FAB plus GAUGE-LM3-INT-P032-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-INT-P032-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-INT-P032-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-INT-P032-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-INT-P032`<br>`DOC-LM3-INT-SA330` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-INT-FAB`<br>`GAUGE-LM3-INT-P032-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-INT-SA330`<br>`TORQUE-LM3-INT-P032` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: fire-material certificate | quality inspection | 0.25 | `QA-LM3-INT-P032` | fire-material certificate | quality inspector |
| 50 | verify acceptance gate: segregation inspection | quality inspection | 0.25 | `QA-LM3-INT-P032` | segregation inspection | quality inspector |
| 60 | verify acceptance gate: captive-fastener audit | quality inspection | 0.25 | `TORQUE-LM3-INT-P032` | captive-fastener audit | quality inspector |
| 70 | verify acceptance gate: cover removal/rattle check | quality inspection | 0.25 | `QA-LM3-INT-P032` | cover removal/rattle check | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-INT-P032`<br>`KIT-LM3-INT-SA330` | item is released, tagged, and staged for parent assembly | cell lead |

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
