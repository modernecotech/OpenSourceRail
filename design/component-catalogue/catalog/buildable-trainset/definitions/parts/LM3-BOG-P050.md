# LM3-BOG-P050 — powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 bogie kit |
| Parent assembly | `LM3-TRC-SA615` |
| Procurement BOM lines | `G18` |
| Maturity | `release-candidate` |

## Make / buy basis

Local fabricated brackets close the motor reaction path into the powered bogie frame.

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
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, torque-link gauge, bracket NDT, motor removal clearance, fastener locking record
- Tooling basis: FIX-LM3-BOG-FAB plus GAUGE-LM3-BOG-P050-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- torque-link gauge
- bracket NDT
- motor removal clearance
- fastener locking record

## Source references

- `bogie/assembly.py`
- `bogie/motor.py`
- `LM3-TRC-500`
