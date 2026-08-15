# LM3-BOG-P020 — trailer bogie welded H-frame

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 ea |
| Parent assembly | `LM3-BOG-SA620` |
| Procurement BOM lines | `G2` |
| Maturity | `release-candidate` |

## Make / buy basis

Common trailer frame without motor cradle and traction gearbox mounts.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, bogie fixture survey, weld/NDT record, air-spring datum survey
- Tooling basis: FIX-LM3-BOG-FAB plus GAUGE-LM3-BOG-P020-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- bogie fixture survey
- weld/NDT record
- air-spring datum survey

## Source references

- `bogie/frame.py`
- `bogie/assembly.py`
- `LM3-BOG-410`
