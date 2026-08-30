# LM3-ART-P022 — inter-car double-wall corrugated bellows and clamp-frame set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 2 gangway set |
| Parent assembly | `LM3-ART-SA820` |
| Procurement BOM lines | `B9` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

A supplier-tailored metro gangway bellows seals the passenger connection without becoming part of the structural draw/buff load path.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-GANGWAY-HUBNER` — [HÜBNER modular metro/urban-rail gangway systems](https://www.hubner-group.com/en/products/gangway-systems/gangway-systems-for-metros-subways-and-suburban-railways/)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Bellows textile, panels and bridge pieces may localise after fire, fatigue, water, passenger load, pinch-gap and full-motion testing to the frozen clamp frames.
- Known fit gaps: The vehicle-specific bellows, bridge, turntable, clamp and open-end drawbar geometry remains to be engineered with the supplier.
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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, fire/smoke evidence, pressure/water ingress test, fatigue-cycle evidence, replaceable-clamp demonstration, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P022, CERT-LM3-ART-P022, GAUGE-LM3-ART-P022-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- fire/smoke evidence
- pressure/water ingress test
- fatigue-cycle evidence
- replaceable-clamp demonstration

## Source references

- `articulation.md`
- `LM3-SYS-170`
