# LM3-ROOF-P010 — HVAC curb, drop-duct collar, condensate tray, and drain fitting kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 kit |
| Parent assembly | `LM3-ROOF-SA410` |
| Procurement BOM lines | `T14` |
| Maturity | `release-candidate` |

## Make / buy basis

Bolted/gasketed roof opening and drain tray that decouples final HVAC supplier choice from primary roof steel.

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
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, curb flatness, drop-duct gauge, condensate drain flow test, roof leak test
- Tooling basis: FIX-LM3-ROOF-FAB plus GAUGE-LM3-ROOF-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- curb flatness
- drop-duct gauge
- condensate drain flow test
- roof leak test

## Source references

- `car_body.py`
- `mechanical_interfaces.py`
- `LM3-HVAC-220`
