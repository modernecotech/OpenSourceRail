# LM3-BDY-P060 — low-floor centre pan and removable service-floor support set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 set |
| Parent assembly | `LM3-BDY-SA120` |
| Procurement BOM lines | `B1`, `B12` |
| Maturity | `release-candidate` |

## Make / buy basis

Welded centre floor pan preserving the low-floor saloon and removable equipment-access bays.

## Material specification

| Field | Value |
|---|---|
| Material family | rail structural steel |
| Grade / part class | EN 10025 S355 candidate primary-structure RHS/folded plate |
| Governing standard | EN 10025 material certificate; EN 15085 weld-quality evidence for classed rail weldments |
| Form factor | laser-cut RHS/plate, press-brake folds, drilled/machined inserts, and bracket kit |
| Nominal section | thickness/section per v2A controlled drawing and FEM release |
| Finish / protection | blast, rail primer/topcoat, cavity wax/sealant, and weld-edge protection |
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
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, PRM floor height, egress aisle gauge, pan weld inspection
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P060-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- PRM floor height
- egress aisle gauge
- pan weld inspection

## Source references

- `car_body.py`
- `body.md`
- `LM3-BDY-100`
