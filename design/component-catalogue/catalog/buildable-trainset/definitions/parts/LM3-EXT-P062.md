# LM3-EXT-P062 — longitudinal passenger and priority-seat modules

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 60 seat |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B14` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Repeatable seat modules use the common service rail and calculated saddle adapters instead of unique brackets through floor panels.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-SEAT-FAINSA` — [Fainsa Metro and urban rail passenger seating](https://fainsa.com/en/railway/)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: The OSR common rail and adapters are local; seat shells, frames and handrails may be locally made after fire, abuse-load, sharp-edge, corrosion and accessibility validation.
- Known fit gaps: Exact seat model, upholstery, spacing, handrail geometry and calculated attachment loads remain open.
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
| Material family | rail passenger-seat module and calculated mounting kit |
| Grade / part class | fire-rated longitudinal seat shells/cushions, metallic frame, common-rail saddles, anti-rotation keys, isolators and captive locking hardware |
| Governing standard | supplier rail-seat specification plus project fire/smoke, occupant/abuse load, sharp-edge, accessibility, corrosion and cleanability evidence |
| Form factor | replaceable seat modules mounted only through LM3-FIX saddles to structural/common rails, never through finish panels |
| Nominal section | seat pitch, cant, aisle/PRM clearance, hand clearance, saddle engagement and fastener grip fixed by LM3-INT-230 drawings and released load calculation |
| Finish / protection | cleanable graffiti-resistant finish, radiused passenger edges, isolated dissimilar metals and accessible captive service fasteners |
| Traceability | seat serial/batch, fire certificate, adapter variant, fastener lot, torque/locking witness and installed position map |

Evidence required:

- certificate of conformity
- incoming inspection record
- seat/occupant load evidence
- fixture proof
- egress/cleaning gauge
- timed module replacement

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire/smoke certificate, seat/occupant load evidence, fastener and anti-rotation record, egress and cleaning-clearance gauge
- Tooling basis: RFQ-LM3-EXT-P062, CERT-LM3-EXT-P062, GAUGE-LM3-EXT-P062-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- fire/smoke certificate
- seat/occupant load evidence
- fastener and anti-rotation record
- egress and cleaning-clearance gauge

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B14`
- `LM3-INT-230`
