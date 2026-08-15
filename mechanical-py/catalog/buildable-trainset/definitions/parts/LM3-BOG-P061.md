# LM3-BOG-P061 — trailer-bogie brake/WSP/speed-sensor harness and junction-bracket kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 bogie kit |
| Parent assembly | `LM3-BOG-SA620` |
| Procurement BOM lines | `G14`, `G15`, `G17` |
| Maturity | `release-candidate` |

## Make / buy basis

Locally built, continuity-tested rugged harness with fabricated sensor brackets and junctions for trailer-bogie brake and wheel-slide protection.

## Material specification

| Field | Value |
|---|---|
| Material family | rail structural steel |
| Grade / part class | EN 10025 S355/S460 candidate bogie structural plate/RHS |
| Governing standard | EN 10025 material certificate; EN 15085 weld-quality evidence for classed rail weldments |
| Form factor | laser/plasma-cut plate, RHS/folded sections, machined bosses, and bracket kit |
| Nominal section | thickness/section per v2A controlled drawing and FEM release |
| Finish / protection | blast, primer/topcoat, cavity/weld-edge protection, and torque-stripe where applicable |
| Traceability | heat number, weld consumable batch, WPS/WPQR, welder ID, and NDT record |

Evidence required:

- mill certificate
- weld consumable certificate
- WPS/WPQR
- NDT report

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, bond continuity, insulation/isolation check where applicable, continuity test, connector IP rating, wheelset clearance, dynamic cable sweep
- Tooling basis: FIX-LM3-BOG-FAB plus GAUGE-LM3-BOG-P061-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- continuity test
- connector IP rating
- wheelset clearance
- dynamic cable sweep

## Source references

- `bogie/brake.py`
- `systems.py`
- `LM3-ELC-300`
