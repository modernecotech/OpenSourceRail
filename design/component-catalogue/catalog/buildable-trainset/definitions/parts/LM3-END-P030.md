# LM3-END-P030 — cowl service hatch, sensor backing bracket, washer-tube, and heater-cable clip kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 2 end kit |
| Parent assembly | `LM3-END-SA700` |
| Procurement BOM lines | `E19` |
| Maturity | `release-candidate` |

## Make / buy basis

Local brackets and service access hardware for the nose sensor and heated glass services.

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
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, hatch water test, sensor datum check, heater-cable separation, washer tube leak test
- Tooling basis: FIX-LM3-END-FAB plus GAUGE-LM3-END-P030-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- hatch water test
- sensor datum check
- heater-cable separation
- washer tube leak test

## Source references

- `sensor_cowl.py`
- `mechanical_interfaces.py`
- `LM3-OBS-330`
