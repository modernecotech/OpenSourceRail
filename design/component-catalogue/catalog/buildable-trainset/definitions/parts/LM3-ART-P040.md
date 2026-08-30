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
