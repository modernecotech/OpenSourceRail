# LM3-EXT-P066 — PRM, safety-signage, emergency-lighting, extinguisher, and first-aid kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `A1`, `A2`, `A3`, `A4` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

A controlled location schedule separates fixed PRM/call-button/signage/emergency-light equipment from operator-replenished extinguishers, first aid and seals.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-LIGHT-TEKNOWARE` — [Teknoware rail interior, emergency and exterior lighting](https://www.teknoware.com/rail/)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local luminaires are acceptable at the standard plug and mounting cassette after photometry, glare, fire, EMC, IP, emergency-duration and temperature tests.
- Known fit gaps: Exact lamp models, optics, voltage variants and emergency battery arrangement remain open.
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
| Material family | controlled PRM and emergency-equipment location kit |
| Grade / part class | passenger call controls, tactile/visual labels, battery-backed exit markers, certified extinguisher/first-aid brackets, tamper seals and common adapters |
| Governing standard | selected national accessibility/fire rules plus supplier fire, photometric, battery-duration, extinguisher/bracket, label-durability and lifecycle evidence |
| Form factor | fixed equipment installed to the released location schedule; replenishable/expiring contents remain separately recorded operator stock |
| Nominal section | reachable controls, contrast/tactile content, illuminated sightlines, bracket loads, egress keep-outs and service access fixed by project review |
| Finish / protection | cleanable UV/chemical-resistant labels, radiused tamper-resistant brackets and protected emergency battery/connector interfaces |
| Traceability | equipment serial/batch, label revision/language, battery date, extinguisher/first-aid expiry, seal number and installed location audit |

Evidence required:

- certificate of conformity
- incoming inspection record
- accessible reach/contrast review
- emergency-light duration test
- expiry audit
- egress survey

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, accessible reach/contrast review, emergency-light duration test, equipment certificate/expiry audit, location and egress survey
- Tooling basis: RFQ-LM3-EXT-P066, CERT-LM3-EXT-P066, GAUGE-LM3-EXT-P066-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- accessible reach/contrast review
- emergency-light duration test
- equipment certificate/expiry audit
- location and egress survey

## Source references

- `cots_equipment.py`
- `bom-skeleton.md A1-A4`
- `LM3-INT-230`
