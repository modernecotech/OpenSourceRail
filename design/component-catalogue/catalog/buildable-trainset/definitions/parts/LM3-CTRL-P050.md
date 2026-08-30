# LM3-CTRL-P050 — operational and crashworthy event-recorder storage kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 1 trainset kit |
| Parent assembly | `LM3-SYS-SA900` |
| Procurement BOM lines | `E9`, `E23` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Operational NVMe storage and the crashworthy memory module are separately serialized but released as one recorder kit.

## Material specification

| Field | Value |
|---|---|
| Material family | supplier crash/coupler system |
| Grade / part class | automatic coupler and crash-energy absorber kit |
| Governing standard | supplier crashworthiness specification plus project recovery and interface evidence |
| Form factor | coupler head, draft gear, absorber, jumper hardware, and bolted mounting kit |
| Nominal section | coupler pocket envelope and load path frozen by RFQ drawing |
| Finish / protection | supplier coating, preservation, and rescue/recovery labels |
| Traceability | serialised coupler/absorber CoC, overhaul status, and proof evidence |

Evidence required:

- certificate of conformity
- incoming inspection record
- crash-energy evidence
- bolt/torque evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, write/read test, retention configuration, crashworthy certificate, download/recovery test
- Tooling basis: RFQ-LM3-CTRL-P050, CERT-LM3-CTRL-P050, GAUGE-LM3-CTRL-P050-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- write/read test
- retention configuration
- crashworthy certificate
- download/recovery test

## Source references

- `bom-skeleton.md E9/E23`
- `systems.py`
- `LM3-ELC-300`
