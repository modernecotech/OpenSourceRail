# LM3-EXT-P060 — stepped floor-board and removable service-hatch system

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 135 m2 |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B12` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Locally CNC-cut floor-board panels and removable hatches mount to surveyed support rails without trapping wet services.

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
| Material family | fire-rated structural floor-board and hatch system |
| Grade / part class | rail-qualified aluminium-honeycomb/composite board candidate with aluminium edge closures, stainless retained hatch hardware, isolating pads and sealed inspection plugs |
| Governing standard | supplier rail floor specification plus project fire/smoke, concentrated/distributed load, fatigue, moisture, slip-interface and toxicity evidence |
| Form factor | CNC-cut numbered boards and flush removable hatches supported continuously at released crossmember/service-rail datums |
| Nominal section | board thickness, core/skin schedule, support pitch, edge distance, hatch rebates, service clearances and step transitions fixed by LM3-INT-230 drawings and calculation |
| Finish / protection | sealed cut edges and penetrations, isolated mixed-metal joints, no water-trapping pockets, and floor-covering-compatible prepared face |
| Traceability | board/panel batch, cut nest, edge-seal batch, retained-fastener lot, installed position, datum survey and load-test record |

Evidence required:

- certificate of conformity
- incoming inspection record
- fire/smoke certificate
- floor load/deflection evidence
- hatch removal trial
- level/step survey

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, fire certificate, panel load and deflection evidence, hatch removal trial, level/step and egress survey
- Tooling basis: RFQ-LM3-EXT-P060, CERT-LM3-EXT-P060, GAUGE-LM3-EXT-P060-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- fire certificate
- panel load and deflection evidence
- hatch removal trial
- level/step and egress survey

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B12`
- `LM3-INT-230`
