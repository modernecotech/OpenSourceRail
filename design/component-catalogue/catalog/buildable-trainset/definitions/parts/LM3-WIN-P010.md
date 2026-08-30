# LM3-WIN-P010 — replaceable window pressure frame, dry seal, drain, and captive retention kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 18 opening kit |
| Parent assembly | `LM3-WIN-SA320` |
| Procurement BOM lines | `B10` |
| Maturity | `concept` |

## Make / buy basis

Supplier bonds glass within its aluminium cassette; the OSR pressure frame and dry seal allow routine removal without cutting adhesive at the carbody.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control, surface-preparation record, adhesive batch/pot-life record, bond coupon where required
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, bond-land inspection, water/leak test where applicable, pressure-frame gauge, retention calculation, seal compression record, water-ingress and replacement trial
- Tooling basis: FIX-LM3-WIN-FAB plus GAUGE-LM3-WIN-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- pressure-frame gauge
- retention calculation
- seal compression record
- water-ingress and replacement trial

## Source references

- `small_components.py`
- `cots_equipment.py`
- `bom-skeleton.md B10`
- `LM3-WIN-210`
