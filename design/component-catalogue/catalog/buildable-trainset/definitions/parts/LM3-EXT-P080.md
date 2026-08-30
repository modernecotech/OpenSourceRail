# LM3-EXT-P080 — fire-rated GFRP side-module laminate, core, gelcoat, and consumable kit

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

Supplier-qualified glass-fibre, resin, core, gelcoat/paint, release film, and coupons feed local 1 m side-module moulding; no full-side bonded panel is used.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-COMPOSITE-GURIT` — [Gurit fire-retardant composite laminating and core materials](https://www.gurit.com/)
- Procurement state: `sample-and-rfq`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Resin, reinforcement, core and coating may be sourced locally only as a qualified laminate system with coupon, fire, weathering, insert and full-module evidence.
- Known fit gaps: No public product family alone establishes the complete LM3 rail fire/structural laminate; formulation and process qualification remain open.
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
| Material family | supplier-qualified exterior GFRP side-module material pack |
| Grade / part class | UV-stable E-glass/vinyl-ester or equivalent fire-rated side-module laminate, core, gelcoat, release, and coupon consumables |
| Governing standard | supplier laminate certificate plus project EN 45545 fire/smoke and LM3-BDY-160 mould-process evidence |
| Form factor | kitted dry reinforcement, resin system, local core, gelcoat/paint-primer, release consumables, insert-potting consumables, and witness-coupon stock |
| Nominal section | supports 1,000 mm side-module mould pitch, 994 mm finished module width, solid/window/door trim variants, and solid clip lands |
| Finish / protection | UV-stable exterior finish system with sealed cut-edge compatibility and mixed-metal insert isolation |
| Traceability | fibre/resin/core/gelcoat batch, shelf-life record, cure/coupon trace, and fire certificate |

Evidence required:

- certificate of conformity
- incoming inspection record
- EN 45545 evidence
- laminate coupon
- resin/fibre batch trace
- mould release record

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, EN 45545 evidence, laminate coupon, resin/fibre batch trace, mould release record
- Tooling basis: RFQ-LM3-EXT-P080, CERT-LM3-EXT-P080, GAUGE-LM3-EXT-P080-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- EN 45545 evidence
- laminate coupon
- resin/fibre batch trace
- mould release record

## Source references

- `bom-skeleton.md B6`
- `modular_fiberglass_body.py`
- `LM3-BDY-160`
