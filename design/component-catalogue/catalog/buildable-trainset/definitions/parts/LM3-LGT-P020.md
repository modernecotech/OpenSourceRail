# LM3-LGT-P020 — emergency and doorway lighting modules with independent keyed feeder kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-LGT-SA350` |
| Procurement BOM lines | `B16`, `A4` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Independent-feed emergency and doorway modules share service-rail mechanics but cannot be cross-connected to the main-light feed.

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
- Inspection methods: incoming visual inspection, envelope fit check, emergency duration/effectiveness evidence, evacuation visibility test, feed isolation test, doorway illumination test, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-LGT-P020, CERT-LM3-LGT-P020, GAUGE-LM3-LGT-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- emergency duration/effectiveness evidence
- evacuation visibility test
- feed isolation test
- doorway illumination test

## Source references

- `small_components.py`
- `cots_equipment.py`
- `bom-skeleton.md B16/A4`
- `LM3-INT-230`
