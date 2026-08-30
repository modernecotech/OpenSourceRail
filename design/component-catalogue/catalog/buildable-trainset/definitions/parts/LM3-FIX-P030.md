# LM3-FIX-P030 — standard passenger-fixture saddle and equipment adapter kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-FIX-SA340` |
| Procurement BOM lines | `B14`, `B15`, `E14` |
| Maturity | `concept` |

## Make / buy basis

A small adapter family attaches seats, handrails, PIS, CCTV and cable supports to the common rail without unique body brackets.

## Material specification

| Field | Value |
|---|---|
| Material family | formed sheet metal / stainless local hardware |
| Grade / part class | S355 or 304/316 stainless local bracket/tray candidate, selected by exposure zone |
| Governing standard | EN 10025 / EN 10088 certificate as applicable plus project bonding/corrosion evidence |
| Form factor | laser-cut, folded, drilled sheet/plate with inserts, studs, clips, and labels |
| Nominal section | thickness, stainless grade, and galvanic isolation frozen by v2A controlled drawing |
| Finish / protection | zinc/paint/stainless passivation, orange HV marking, edge protection, and sealing as applicable |
| Traceability | heat number, coating batch, bonding test, and installation batch traceability |

Evidence required:

- mill certificate
- coating/passivation record
- bonding continuity record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, adapter gauge, fixture-specific load calculation, proof-load sample, egress and snag check
- Tooling basis: FIX-LM3-FIX-FAB plus GAUGE-LM3-FIX-P030-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- adapter gauge
- fixture-specific load calculation
- proof-load sample
- egress and snag check

## Source references

- `small_components.py`
- `bom-skeleton.md B14/B15/E14`
- `LM3-INT-230`
