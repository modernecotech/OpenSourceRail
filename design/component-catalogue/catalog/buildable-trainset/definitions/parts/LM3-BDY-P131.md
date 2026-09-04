# LM3-BDY-P131 — one-metre clip-on window-edge fiberglass side module

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 24 module |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B6` |
| Maturity | `release-candidate` |

## Make / buy basis

CNC-trimmed window-bay variant with sealed reveal edge, drainage break, and removable glazing-cassette clearance.

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

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, adhesive bonding or gasketed interface preparation
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control, surface-preparation record, adhesive batch/pot-life record, bond coupon where required
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, bond-land inspection, water/leak test where applicable, window trim nest, sealed-edge inspection, cassette removal sweep, master-frame dry fit
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P131-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- window trim nest
- sealed-edge inspection
- cassette removal sweep
- master-frame dry fit

## Source references

- `modular_fiberglass_body.py`
- `body.md`
- `LM3-BDY-160`
