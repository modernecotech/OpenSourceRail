# LM3-BDY-P110 — window carrier ring, bonded-gasket land, and replacement jack-point inserts

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 18 opening kit |
| Parent assembly | `LM3-WIN-SA320` |
| Procurement BOM lines | `B2` |
| Maturity | `release-candidate` |

## Make / buy basis

Laser-cut carrier ring and local backing plates for bonded/gasketed glazing replacement.

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

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, surface-preparation record, adhesive batch/pot-life record, bond coupon where required
- Inspection methods: dimensional inspection, visual inspection, bond-land inspection, water/leak test where applicable, aperture gauge, bond-land surface check, water-ingress witness, replacement tool clearance
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P110-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- aperture gauge
- bond-land surface check
- water-ingress witness
- replacement tool clearance

## Source references

- `car_body.py`
- `cots_equipment.py`
- `LM3-WIN-210`
