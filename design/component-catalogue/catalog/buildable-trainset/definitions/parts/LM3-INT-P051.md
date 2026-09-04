# LM3-INT-P051 — PRM transition-ramp, bogie-deck step-cover, contrast-nosing, and anti-slip set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 6 end-zone set |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Dedicated high-wear transition pieces can be replaced independently and are gauged against the structural floor rather than adjacent trim.

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
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, fire-material certificate, PRM transition gauge, anti-slip/contrast evidence, trip-edge inspection
- Tooling basis: FIX-LM3-INT-FAB plus GAUGE-LM3-INT-P051-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- fire-material certificate
- PRM transition gauge
- anti-slip/contrast evidence
- trip-edge inspection

## Source references

- `cabin-fiberglass.md`
- `body.md`
- `LM3-INT-255`
