# LM3-ART-P040 — train-to-train open-end articulation, gangway, drawbar, turntable, and service-jumper cassette

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 0 joint kit |
| Parent assembly | `LM3-TTART-SA850` |
| Procurement BOM lines | `B9`, `B29` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier open-end gangway/articulation cassette for joining two otherwise complete train modules through their common end-interface frames.

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
| Material family | supplier-certified rail door system |
| Grade / part class | COTS/BID electric passenger door cassette |
| Governing standard | supplier rail door specification plus EN 14752 evidence where applicable |
| Form factor | preassembled door cassette with seals, drive, controller, and emergency release |
| Nominal section | supplier envelope frozen by RFQ drawing |
| Finish / protection | supplier corrosion/fire/smoke protection accepted by OSR evidence pack |
| Traceability | serialised supplier CoC, revision, and lifecycle evidence |

Evidence required:

- certificate of conformity
- incoming inspection record
- obstruction / locked-loop evidence
- fire-smoke certificate pack

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, train-to-train motion-envelope proof, walk-through gangway fire evidence, trainline continuity, water ingress/drain test, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P040, CERT-LM3-ART-P040, GAUGE-LM3-ART-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- train-to-train motion-envelope proof
- walk-through gangway fire evidence
- trainline continuity
- water ingress/drain test

## Source references

- `systems.py`
- `articulation.md`
- `interfaces.md`
- `LM3-SYS-175`

## Notes

Optional for modular consists. The reference LM3-3car uses closed panoramic ends and therefore carries zero of this kit.
