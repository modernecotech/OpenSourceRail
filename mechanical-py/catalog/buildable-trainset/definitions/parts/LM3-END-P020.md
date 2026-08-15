# LM3-END-P020 — T-OBS nose sensor pack, heated window services, and washer kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 2 ea |
| Parent assembly | `LM3-END-SA700` |
| Procurement BOM lines | `E15`, `E18`, `E19` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Per-end obstacle-detection module aligned to the cowl optical/radar datum.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, sensor calibration, washer/heater test, 2oo2 verdict interface test, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-END-P020, CERT-LM3-END-P020, GAUGE-LM3-END-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- sensor calibration
- washer/heater test
- 2oo2 verdict interface test

## Source references

- `systems.py`
- `sensor_cowl.py`
- `LM3-OBS-330`
