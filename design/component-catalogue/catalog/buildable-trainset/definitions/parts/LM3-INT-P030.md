# LM3-INT-P030 — FRP/phenolic sidewall liner, window reveal, and cable-cover panel set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 6 side kit |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Fire-rated cabin sidewall panels and window reveals that hide secondary structure while preserving window replacement and cable-tray access.

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

- Primary processes: inspect mould/trim fixture, apply release system, cut dry reinforcement or panel blank, lay up / infuse / press laminate, controlled cure, demould and post-cure where required, trim/drill to controlled datum, fit inserts/clips/gaskets, dry-fit to parent fixture
- Joining methods: potted/captive inserts, retained fasteners or clip grid, adhesive/sealant only where removal and repair rules allow
- Special process controls: released laminate schedule, resin/adhesive batch and shelf-life check, mould release record, cure temperature/time record, fire-material certificate check, edge sealing and dust-control rule, passenger-facing edge-radius rule, anti-slip rule for PRM/step panels
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, fire-material certificate, window-reveal gauge, access-panel removal, edge-radius inspection, sharp-edge inspection, rattle check, cleanability inspection
- Tooling basis: MOULD/FIX-LM3-INT-P030 plus TRIM-GAUGE-LM3-INT-P030
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build

## Acceptance gates

- fire-material certificate
- window-reveal gauge
- access-panel removal
- edge-radius inspection

## Source references

- `cabin-fiberglass.md`
- `body.md`
- `LM3-INT-245`
