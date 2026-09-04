# LM3-FIN-P010 — pre-cut exterior livery graphic film, edge-seal, datum-mark, and repair-patch kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B20`, `B28` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Rail-application graphic film replaces masked colour-band painting on smooth cured GFRP and cowl surfaces; it never replaces steel primer/topcoat, laminate gelcoat, fire protection, labels, or sealants.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-FINISH-3M` — [3M Commercial Branding and Transportation rail-application graphic films including Controltac 180mC](https://www.3m.com/3M/en_US/p/d/b00026338/)
- Procurement state: `sample-and-system-rfq`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Print, plot, kit, apply, inspect and repair locally using the selected film/ink/overlaminate system; qualify a regional equivalent only as a complete system on the released LM3 base finish.
- Known fit gaps: Exact film, colour/ink, overlaminate, edge treatment, fire evidence, hot-climate durability and warranty territory remain to be selected and tested.
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
- Inspection methods: incoming visual inspection, envelope fit check, supplier rail-use statement, substrate/cure acceptance, adhesion coupon, edge/overlap inspection, cleaning/removal trial
- Tooling basis: RFQ-LM3-FIN-P010, CERT-LM3-FIN-P010, GAUGE-LM3-FIN-P010-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- supplier rail-use statement
- substrate/cure acceptance
- adhesion coupon
- edge/overlap inspection
- cleaning/removal trial

## Source references

- `exterior-finish-process.md`
- `modular_fiberglass_body.py`
- `LM3-BDY-160`
