# LM3-LGT-P010 — 1.2 m plug-in main LED lighting cassette and captive mounting kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 66 module |
| Parent assembly | `LM3-LGT-SA350` |
| Procurement BOM lines | `B16` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Twenty-two identical replaceable cassettes per car eliminate field-cut strip, loose terminations, and long fragile light runs.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, rail fire certificate, shock/vibration evidence, photometric/lux test, plug polarity and retention test
- Tooling basis: RFQ-LM3-LGT-P010, CERT-LM3-LGT-P010, GAUGE-LM3-LGT-P010-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- rail fire certificate
- shock/vibration evidence
- photometric/lux test
- plug polarity and retention test

## Source references

- `small_components.py`
- `cots_equipment.py`
- `bom-skeleton.md B16`
- `LM3-INT-230`
