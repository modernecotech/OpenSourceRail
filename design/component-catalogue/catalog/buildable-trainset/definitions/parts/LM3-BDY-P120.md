# LM3-BDY-P120 — jacking pad, lifting eye, towing lug, and recovery-label kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-BDY-SA110` |
| Procurement BOM lines | `B26` |
| Maturity | `release-candidate` |

## Make / buy basis

Locally fabricated and proof-marked recovery fittings tied into released underframe load paths.

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
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, material traceability, weld/NDT record, proof load, four-point depot interface gauge, datum and label inspection
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P120-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- material traceability
- weld/NDT record
- proof load
- four-point depot interface gauge
- datum and label inspection

## Source references

- `bom-skeleton.md B26`
- `car_body.py`
- `LM3-BDY-100`
