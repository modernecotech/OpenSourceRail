# LM3-INT-P021 — ceiling light-trough bezel, diffuser carrier, and emergency-luminaire closeout set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car set |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Short repeated mouldings register the plug-in light modules independently of the large liner panels and remain removable with captive hardware.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, fire-material certificate, light cassette gauge, emergency-feed identification, module removal trial
- Tooling basis: FIX-LM3-INT-FAB plus GAUGE-LM3-INT-P021-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- fire-material certificate
- light cassette gauge
- emergency-feed identification
- module removal trial

## Source references

- `cabin-fiberglass.md`
- `small_components.py`
- `LM3-INT-240`
