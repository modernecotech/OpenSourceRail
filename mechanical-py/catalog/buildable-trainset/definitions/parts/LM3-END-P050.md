# LM3-END-P050 — sealed headlight, tail/marker light, threshold-warning, and end-lamp harness kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 2 end kit |
| Parent assembly | `LM3-END-SA700` |
| Procurement BOM lines | `B17` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

One reversible lamp and warning-light package fits either cabless end cowl.

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
- Inspection methods: incoming visual inspection, envelope fit check, photometric certificate, function/polarity test, ingress protection, A/B-end interchange check
- Tooling basis: RFQ-LM3-END-P050, CERT-LM3-END-P050, GAUGE-LM3-END-P050-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- photometric certificate
- function/polarity test
- ingress protection
- A/B-end interchange check

## Source references

- `bom-skeleton.md B17`
- `sensor_cowl.py`
- `systems.py`
