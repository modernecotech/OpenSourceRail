# LM3-FIX-P020 — four-family captive fastener, floating nut, isolator, and access-fastener kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-FIX-SA340` |
| Procurement BOM lines | `B2`, `B21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

M6 captive, M8 calculated-fixture, quarter-turn access, and M10 sealed exterior families replace ad-hoc fastener selection.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-FASTENER-BOLLHOFF` — [Böllhoff RIVNUT blind rivet nuts and setting systems](https://www.boellhoff.com/us-en/products/special-fasteners/rivnut-blind-rivet-nuts-and-rivstud-blind-rivet-studs/)
- Procurement state: `catalogue-sourceable-after-sizing`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Equivalent inserts and captive hardware are allowed only by joint family after substrate-specific setting trials, proof loads, corrosion and removal-cycle tests.
- Known fit gaps: Exact grip range, head, thread, material and setting force must be selected from each released joint drawing.
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
| Material family | supplier-controlled external component |
| Grade / part class | COTS/BID component class matched to OSR envelope |
| Governing standard | supplier specification plus project interface, safety, EMC/fire, and lifecycle evidence |
| Form factor | preassembled supplier module with installation kit |
| Nominal section | mass, volume, mounting datum, service clearance, and connector envelope frozen by RFQ drawing |
| Finish / protection | supplier finish/protection accepted by OSR evidence pack |
| Traceability | serialised CoC, datasheet, revision, and incoming inspection record |

Evidence required:

- certificate of conformity
- incoming inspection record
- datasheet / evidence pack

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, supplier certificate, batch/finish trace, installed-grip gauge, locking and captive-part audit
- Tooling basis: RFQ-LM3-FIX-P020, CERT-LM3-FIX-P020, GAUGE-LM3-FIX-P020-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- supplier certificate
- batch/finish trace
- installed-grip gauge
- locking and captive-part audit

## Source references

- `small_components.py`
- `bom-skeleton.md B2/B21`
- `LM3-INT-230`
