# LM3-INT-P032 — waist cable-cover, low-voltage access lid, and retained quarter-turn fastener set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 6 side set |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

A repeated waist-level cover family gives direct access to segregated LV/data routes without disturbing windows, seats, or main liner panels.

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
- Inspection methods: dimensional inspection, visual inspection, bond-land inspection, water/leak test where applicable, bond continuity, insulation/isolation check where applicable, fire-material certificate, segregation inspection, captive-fastener audit, cover removal/rattle check
- Tooling basis: FIX-LM3-INT-FAB plus GAUGE-LM3-INT-P032-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- fire-material certificate
- segregation inspection
- captive-fastener audit
- cover removal/rattle check

## Source references

- `cabin-fiberglass.md`
- `small_components.py`
- `LM3-INT-245`
