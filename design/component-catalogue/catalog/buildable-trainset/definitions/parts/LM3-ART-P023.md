# LM3-ART-P023 — inter-car passenger bridge, turntable and flexible interior-panel set

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

The bridge and turntable provide a flush, anti-slip passenger path across the full released articulation envelope with guarded pinch zones.

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
| Material family | passenger interior COTS kit |
| Grade / part class | fire-rated seat, flooring, trim, lighting, PIS, CCTV, signage, and grab-rail kit |
| Governing standard | supplier interior specification plus project EN 45545/fire-smoke evidence where applicable |
| Form factor | late-installed saloon kit with fasteners, access panels, looms, and labels |
| Nominal section | saloon, PRM aisle, emergency egress, and service-panel envelope frozen by RFQ drawing |
| Finish / protection | fire/smoke compliant finish, anti-slip flooring, and cleanable passenger surfaces |
| Traceability | batch CoC, fire-material certificates, and installation traceability |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire-material certificate pack
- egress/lighting evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, passenger load proof, anti-slip evidence, gap/step gauge, pinch/shear hazard review, full-motion sweep, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P023, CERT-LM3-ART-P023, GAUGE-LM3-ART-P023-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- passenger load proof
- anti-slip evidence
- gap/step gauge
- pinch/shear hazard review
- full-motion sweep

## Source references

- `articulation.md`
- `LM3-SYS-170`
