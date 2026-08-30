# LM3-ART-P021 — articulation upper lateral/yaw links, spherical joints and retained pins

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 2 joint set |
| Parent assembly | `LM3-ART-SA810` |
| Procurement BOM lines | `B9` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Paired upper links stabilize roll/yaw while the lower pivot carries the primary articulation loads; all rod ends and pins remain positively retained.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-JOINT-SCHAEFFLER` — [Schaeffler ELGES maintenance-free spherical plain bearings and rod ends](https://www.schaeffler.com/en/products-and-solutions/industrial/product-portfolio/plain-bearings/)
- Procurement state: `calculation-and-rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local housings, pins and links are preferred; bearing or rod-end substitution requires static/dynamic capacity, misalignment, liner, corrosion, temperature, sealing and fatigue equivalence.
- Known fit gaps: No catalogue bearing is selected until the articulation load spectrum, pin diameter, angular motion and safety factors are released.
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
- Inspection methods: incoming visual inspection, envelope fit check, link buckling/fatigue proof, joint angular capacity, pin retention inspection, full-motion sweep, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P021, CERT-LM3-ART-P021, GAUGE-LM3-ART-P021-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- link buckling/fatigue proof
- joint angular capacity
- pin retention inspection
- full-motion sweep

## Source references

- `systems.py`
- `articulation.md`
- `LM3-SYS-170`
