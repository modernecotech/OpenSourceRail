# LM3-EXT-P010 — electric plug/sliding door cassette

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 12 ea |
| Parent assembly | `LM3-DOOR-SA310` |
| Procurement BOM lines | `B11`, `B25`, `E20` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Certified rail door supplier owns mechanics, seals, controller, and lifecycle evidence.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, EN 14752 evidence, obstruction test, closed-and-locked loop test, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-EXT-P010, CERT-LM3-EXT-P010, GAUGE-LM3-EXT-P010-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- EN 14752 evidence
- obstruction test
- closed-and-locked loop test

## Source references

- `bom-skeleton.md B11/B25`
- `systems.py`
- `LM3-DOOR-200`
