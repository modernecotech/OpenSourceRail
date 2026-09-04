# LM3-ROOF-P030 — removable HVAC curb fairing, intake/exhaust skirt, and access-hatch moulding set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car set |
| Parent assembly | `LM3-ROOF-SA410` |
| Procurement BOM lines | `B7`, `T14` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Non-structural GFRP fairings close the HVAC-to-roof transition while remaining removable without disturbing the certified HVAC curb or lifting points.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, fairing trim gauge, HVAC airflow keep-out, hatch removal trial, roof leak test
- Tooling basis: FIX-LM3-ROOF-FAB plus GAUGE-LM3-ROOF-P030-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- fairing trim gauge
- HVAC airflow keep-out
- hatch removal trial
- roof leak test

## Source references

- `roof-fitout.md`
- `systems.py`
- `LM3-HVAC-220`
