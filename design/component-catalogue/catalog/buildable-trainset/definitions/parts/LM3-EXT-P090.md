# LM3-EXT-P090 — fire-rated GFRP roof-module, dry-seal, and removable skirt material kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B7` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier-qualified roof-module laminate consumables, EPDM seal stock, trim materials, and removable skirt blanks feed the local mould/trim/clip process.

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
| Material family | supplier-qualified exterior GFRP roof-module and seal material pack |
| Grade / part class | fire-rated roof-module laminate consumables, EPDM dry-seal stock, removable skirt blanks, and retained-fastener consumables |
| Governing standard | supplier laminate and seal certificates plus project EN 45545, ozone/UV, ingress, and LM3-BDY-160 mould-process evidence |
| Form factor | kitted roof-module reinforcement/core/resin/finish consumables, extruded EPDM seals, skirt blanks, trim stock, and coupon material |
| Nominal section | supports 1,000 mm roof-module mould pitch, dry joints, drain paths, removable skirts, and anti-lift/clip hardware interfaces |
| Finish / protection | UV-stable roof finish, sealed cut edges, ozone-resistant EPDM, and galvanic isolation at retained hardware |
| Traceability | laminate batch, seal batch, cure/coupon trace, service-removal record, and water-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- EN 45545 evidence
- roof laminate coupon
- seal certificate
- water and debris-ingress check

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, EN 45545 evidence, roof laminate coupon, seal certificate, service-removal trial, water and debris-ingress check
- Tooling basis: RFQ-LM3-EXT-P090, CERT-LM3-EXT-P090, GAUGE-LM3-EXT-P090-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- EN 45545 evidence
- roof laminate coupon
- seal certificate
- service-removal trial
- water and debris-ingress check

## Source references

- `bom-skeleton.md B7`
- `modular_fiberglass_body.py`
- `LM3-BDY-160`
