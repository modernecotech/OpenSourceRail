# LM3-EXT-P080 — fire-rated composite exterior side sandwich-panel kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 6 side kit |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B6` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier panels are trimmed and bonded to the released side-frame apertures and attachment lands.

## Material specification

| Field | Value |
|---|---|
| Material family | fire-retardant fiberglass composite |
| Grade / part class | E-glass or basalt-fibre/vinyl-ester end-cowl laminate and insert kit |
| Governing standard | supplier laminate schedule plus project fire/smoke, coupon, and insert pull-out evidence |
| Form factor | moulded cowl cast, solid flanges, local core in broad skins, potted inserts, and trim/repair coupons |
| Nominal section | laminate thickness, ply drop, core map, insert pattern, split line, and trim datum per LM3-BDY-155 |
| Finish / protection | UV-stable exterior gelcoat/paint, sealed cut edges, gasketed seams, and mixed-metal isolation |
| Traceability | laminate batch, resin batch, cure record, insert pull-out record, adhesive batch, and coupon traceability |

Evidence required:

- certificate of conformity
- incoming inspection record
- laminate coupon
- cure record
- insert pull-out evidence
- fire-smoke certificate

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, EN 45545 evidence, panel dimensional report, insert pull-out, bond coupon and water test
- Tooling basis: RFQ-LM3-EXT-P080, CERT-LM3-EXT-P080, GAUGE-LM3-EXT-P080-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- EN 45545 evidence
- panel dimensional report
- insert pull-out
- bond coupon and water test

## Source references

- `bom-skeleton.md B6`
- `car_body.py`
- `LM3-BDY-150`
