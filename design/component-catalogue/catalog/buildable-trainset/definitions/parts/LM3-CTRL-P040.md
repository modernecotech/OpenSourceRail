# LM3-CTRL-P040 — pre-terminated LV trainline harness, DIN cabinet, and terminal-distribution kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-SYS-SA900` |
| Procurement BOM lines | `E17`, `E20`, `E22` |
| Maturity | `release-candidate` |

## Make / buy basis

Locally built harness/cabinet kits implement the released connector, segregation, label, and clamp schedules.

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
- Inspection methods: dimensional inspection, visual inspection, continuity/hipot, pinout check, label inspection, segregation survey, configuration record
- Tooling basis: FIX-LM3-CTRL-FAB plus GAUGE-LM3-CTRL-P040-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- continuity/hipot
- pinout check
- label inspection
- segregation survey
- configuration record

## Source references

- `bom-skeleton.md E17/E20/E22`
- `systems.py`
- `LM3-ELC-300`
