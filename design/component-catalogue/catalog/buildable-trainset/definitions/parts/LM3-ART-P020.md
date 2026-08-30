# LM3-ART-P020 — articulation lower spherical pivot, bearing housing and pin set

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

Supplier-sized spherical bearing, housing, pin, bushes and retainers transmit the released draw, buff, vertical and anti-lift loads through the OSR adapter.

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
| Material family | supplier-certified running gear |
| Grade / part class | wheelset / bearing / brake / suspension safety-critical kit |
| Governing standard | supplier rail running-gear specification plus project brake, ride-height, and traceability evidence |
| Form factor | machined/forged rotating parts, brake hardware, suspension elements, and fastener kit |
| Nominal section | bogie interface envelope frozen by RFQ drawing |
| Finish / protection | supplier corrosion protection and lubrication preservation |
| Traceability | serialised wheelset, bearing, brake, and suspension records |

Evidence required:

- certificate of conformity
- incoming inspection record
- wheelset/bearing certificates
- brake evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, bearing static/dynamic capacity, pin material/NDT, proof load, lubrication/sealing plan, motion-envelope proof, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P020, CERT-LM3-ART-P020, GAUGE-LM3-ART-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- bearing static/dynamic capacity
- pin material/NDT
- proof load
- lubrication/sealing plan
- motion-envelope proof

## Source references

- `systems.py`
- `articulation.md`
- `LM3-SYS-170`
