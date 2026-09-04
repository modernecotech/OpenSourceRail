# LM3-BDY-P021 — underframe cross-bearer, door-bay outrigger, and equipment-bracket pack

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car pack |
| Parent assembly | `LM3-BDY-SA110` |
| Procurement BOM lines | `B1` |
| Maturity | `release-candidate` |

## Make / buy basis

Repeated laser-cut/folded transverse members are nested, station-marked, and gauged independently before the underframe weldment is closed.

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

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, cut-list identity, cross-bearer profile gauge, station map, fixture tack survey
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P021-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- cut-list identity
- cross-bearer profile gauge
- station map
- fixture tack survey

## Source references

- `car_body.py`
- `fabrication-plan.md`
- `LM3-BDY-110`
