# LM3-EXT-P061 — welded resilient floor covering, cove, nosing, and adhesive system

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 135 m2 |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B13` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

One supplier-qualified rail flooring system covers the board joints, coved edges, steps, hatches, thresholds and repair patches.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-FLOOR-FORBO` — [Forbo Flooring Systems Transport Flooring rail systems](https://www.forbo.com/flooring/en-aa/products/transport-flooring/rail-floor-coverings/bxw6nd)
- Procurement state: `sample-and-rfq`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Use the supplier system for first articles; qualify local board/covering as a complete substrate, adhesive, weld, cove, hatch and fire-tested system rather than swapping one layer.
- Known fit gaps: Structural board selection and the final covering/adhesive combination remain to be frozen.
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
| Material family | rail fire-rated resilient floor-covering system |
| Grade / part class | supplier-matched sheet covering, welded-seam rod, coving, step nosing, primer, adhesive and repair-patch system |
| Governing standard | supplier rail flooring specification plus project fire/smoke/toxicity, slip, wear, cleaning-agent and substrate-compatibility evidence |
| Form factor | single-system sheet layout with heat-welded seams, coved edges, sealed penetrations, removable hatch cuts and replaceable threshold pieces |
| Nominal section | roll direction, seam map, cove radius, nosing, threshold termination, adhesive spread and hatch joint fixed by the released installation drawing |
| Finish / protection | anti-slip cleanable finish with no open edges, water traps or incompatible sealant/adhesive combinations |
| Traceability | covering/rod/primer/adhesive batch and expiry, substrate moisture/cleanliness record, cure log, seam sample and installed zone map |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire/smoke certificate
- adhesive compatibility/cure record
- seam peel sample
- slip evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire/smoke certificate, adhesive compatibility and cure record, welded-seam peel sample, slip and cleanability evidence
- Tooling basis: RFQ-LM3-EXT-P061, CERT-LM3-EXT-P061, GAUGE-LM3-EXT-P061-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- fire/smoke certificate
- adhesive compatibility and cure record
- welded-seam peel sample
- slip and cleanability evidence

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B13`
- `LM3-INT-230`
