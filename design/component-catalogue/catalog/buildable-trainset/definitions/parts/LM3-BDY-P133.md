# LM3-BDY-P133 — one-metre clip-on fiberglass roof skin and equipment-fairing module

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 48 module |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B7` |
| Maturity | `release-candidate` |

## Make / buy basis

Dedicated roof-bay moulding uses the common pitch with controlled HVAC, PV, antenna, access, and drainage trim variants.

## Material specification

| Field | Value |
|---|---|
| Material family | fire-rated cabin fiberglass / phenolic composite |
| Grade / part class | EN 45545 HL2 candidate FRP, phenolic, or glass/basalt-fibre sandwich interior panel |
| Governing standard | EN 45545-2 interior material evidence plus supplier laminate/phenolic panel certificate |
| Form factor | moulded or CNC-trimmed liner, reveal, cover, hatch, and kick-panel shells with potted inserts |
| Nominal section | panel thickness, edge return, insert pattern, and clip grid per LM3-INT v2A drawing |
| Finish / protection | cleanable interior gelcoat/paint or decorative film with sealed edges and anti-slip finish where walked on |
| Traceability | laminate/panel batch, resin/cure or board batch, insert batch, adhesive batch, and fire certificate |

Evidence required:

- fire-material certificate
- laminate/panel batch record
- insert pull-out evidence
- trim/cure record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, surface-preparation record, adhesive batch/pot-life record, bond coupon where required, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond-land inspection, water/leak test where applicable, bond continuity, insulation/isolation check where applicable, roof mould/trim record, anti-lift proof, equipment keep-out gauge, water/debris-ingress test
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P133-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- roof mould/trim record
- anti-lift proof
- equipment keep-out gauge
- water/debris-ingress test

## Source references

- `modular_fiberglass_body.py`
- `roof-fitout.md`
- `LM3-BDY-160`
