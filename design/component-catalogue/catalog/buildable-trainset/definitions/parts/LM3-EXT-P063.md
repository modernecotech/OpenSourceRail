# LM3-EXT-P063 — stainless grab-pole, handrail, joint, and insulated adapter kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B15` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Cut-to-length modular tubes terminate in replaceable common-rail saddles; primary passenger loads bypass liners and trim.

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
| Material family | modular passenger handrail and stanchion system |
| Grade / part class | 304/316 stainless tube candidate, radiused cast/machined joints, insulated common-rail saddles, anti-rotation keys and captive locking hardware |
| Governing standard | supplier material/finish specification plus project passenger load, fatigue, fire, accessibility, corrosion, electrical-isolation and snag evidence |
| Form factor | cut-to-length repeated tubes and replaceable elbows/tees fixed at structural floor/ceiling/service-rail datums without loading liners |
| Nominal section | tube diameter/wall, joint engagement, support span, reachable zones, adapter geometry and fastener grip fixed by LM3-INT-230 drawings and calculation |
| Finish / protection | brushed/passivated cleanable surface, radiused ends, no exposed threads, isolated mixed metals and sealed floor penetrations |
| Traceability | tube heat/batch, fitting/fastener lot, cut list, joint locking witness, installed survey and proof-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- fixture-specific proof-load evidence
- reach/egress survey
- locking audit
- timed joint replacement

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, material/finish certificate, joint locking record, fixture-specific proof-load evidence, reach, egress and snag survey
- Tooling basis: RFQ-LM3-EXT-P063, CERT-LM3-EXT-P063, GAUGE-LM3-EXT-P063-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- material/finish certificate
- joint locking record
- fixture-specific proof-load evidence
- reach, egress and snag survey

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B15`
- `LM3-INT-230`
