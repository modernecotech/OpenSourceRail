# LM3-FIX-P010 — OSR-RAIL-42 common ceiling, waist, and seat-zone service rail kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-FIX-SA340` |
| Procurement BOM lines | `B2`, `B15`, `B21` |
| Maturity | `release-candidate` |

## Make / buy basis

One cut/drill gauge produces all common extruded aluminium equipment rails; local adapters, not rail variants, accommodate equipment.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, rail datum survey, end-deburr check, isolation/finish inspection, representative pull/slip test
- Tooling basis: FIX-LM3-FIX-FAB plus GAUGE-LM3-FIX-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- rail datum survey
- end-deburr check
- isolation/finish inspection
- representative pull/slip test

## Source references

- `small_components.py`
- `bom-skeleton.md B2/B15/B21`
- `LM3-INT-230`
