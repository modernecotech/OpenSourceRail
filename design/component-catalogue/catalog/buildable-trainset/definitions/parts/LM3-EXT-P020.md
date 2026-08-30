# LM3-EXT-P020 — side laminated glazing cassette

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 18 ea |
| Parent assembly | `LM3-WIN-SA320` |
| Procurement BOM lines | `B10` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier-neutral bonded/gasketed cassette sized by OSR aperture.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-GLASS-AGC` — [AGC Automotive rail glazing with framing system](https://www.agc-automotive.com/en/products-and-solutions/glass-with-framing-system)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local glass processors may replace AGC after laminate, heater, optical, edge, fire, impact and bond-system qualification against the frozen cassette drawing.
- Known fit gaps: Curvature, heater power, optical zones, laminate stack and frame/bond geometry remain project-specific.
- Mandatory equivalence:
  - same or better released fit, mounting datums, connector keying and service envelope
  - same or better mass, load, duty-cycle, thermal, electrical and environmental ratings
  - same or better functional safety, fire, EMC, cybersecurity and applicable rail evidence
  - documented failure modes, maintenance intervals, spares and obsolescence route
  - first-article inspection plus component, subassembly and vehicle regression tests
  - signed design-authority substitution record preserving the original anchor and evidence hashes

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
- Inspection methods: incoming visual inspection, envelope fit check, glazing certificate, water ingress test, replacement method
- Tooling basis: RFQ-LM3-EXT-P020, CERT-LM3-EXT-P020, GAUGE-LM3-EXT-P020-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- glazing certificate
- water ingress test
- replacement method

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B10`
- `LM3-WIN-210`
