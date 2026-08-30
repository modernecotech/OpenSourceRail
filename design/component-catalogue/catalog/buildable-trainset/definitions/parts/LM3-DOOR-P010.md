# LM3-DOOR-P010 — door four-point adjustable carrier, datum pin, dry seal, and keyed connector bracket kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 12 opening kit |
| Parent assembly | `LM3-DOOR-SA310` |
| Procurement BOM lines | `B11`, `B25` |
| Maturity | `concept` |

## Make / buy basis

The certified door remains a complete supplier cassette; four common adjustable shoes absorb body tolerance and make removal predictable.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, carrier datum gauge, interface load calculation, seal compression record, connector keying and cassette replacement trial
- Tooling basis: FIX-LM3-DOOR-FAB plus GAUGE-LM3-DOOR-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- carrier datum gauge
- interface load calculation
- seal compression record
- connector keying and cassette replacement trial

## Source references

- `small_components.py`
- `systems.py`
- `bom-skeleton.md B11/B25`
- `LM3-DOOR-200`
