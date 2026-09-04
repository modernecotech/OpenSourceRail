# LM3-BDY-P020 — underframe centre spine and longitudinal load-path kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 kit |
| Parent assembly | `LM3-BDY-SA110` |
| Procurement BOM lines | `B1` |
| Maturity | `release-candidate` |

## Make / buy basis

Cut plate/RHS centre-spine kit for one car; QR-marked before welding and kept separate from the repeated cross-bearer pack.

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
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, tube/plate certs, spine straightness survey, bogie-centre datum report
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P020-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- tube/plate certs
- spine straightness survey
- bogie-centre datum report

## Source references

- `car_body.py`
- `fabrication-plan.md`
- `LM3-BDY-110`
