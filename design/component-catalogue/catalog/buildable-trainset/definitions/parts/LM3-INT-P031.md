# LM3-INT-P031 — window reveal, setting-block inspection cover, and blind/label land set

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

Four-piece removable reveals protect glazing edges and allow the complete window cassette to be extracted without removing the sidewall liner run.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, surface-preparation record, adhesive batch/pot-life record, bond coupon where required
- Inspection methods: dimensional inspection, visual inspection, bond-land inspection, water/leak test where applicable, fire-material certificate, glass-edge clearance, cassette removal sweep, sharp-edge inspection
- Tooling basis: FIX-LM3-INT-FAB plus GAUGE-LM3-INT-P031-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- fire-material certificate
- glass-edge clearance
- cassette removal sweep
- sharp-edge inspection

## Source references

- `cabin-fiberglass.md`
- `cots_equipment.py`
- `LM3-WIN-210`
