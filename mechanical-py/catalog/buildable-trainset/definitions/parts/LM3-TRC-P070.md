# LM3-TRC-P070 — HV contactor, fuse, pre-charge, service-disconnect, and current-sensor panel

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T11`, `T16` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier-certified high-voltage protection panel between battery, charger, PV, and inverter.

## Material specification

| Field | Value |
|---|---|
| Material family | roof electrical energy equipment |
| Grade / part class | PV module / resistor / clamp / isolator kit |
| Governing standard | supplier datasheet plus project bonding, isolation, fire, and vibration evidence |
| Form factor | module, thermal shield, aluminum/stainless clamp hardware, and UV-rated harness |
| Nominal section | roof keep-out, clamp pitch, and thermal clearance frozen by RFQ drawing |
| Finish / protection | UV/weather protection, hot-surface labelling, and galvanic isolation where required |
| Traceability | module serials, resistance/PV flash data, CoC, and harness batch |

Evidence required:

- certificate of conformity
- incoming inspection record
- electrical datasheet
- bonding/isolation record

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, isolation test, pre-charge timing, fuse rating evidence, service-disconnect lockout, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P070, CERT-LM3-TRC-P070, GAUGE-LM3-TRC-P070-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- isolation test
- pre-charge timing
- fuse rating evidence
- service-disconnect lockout

## Source references

- `bom-skeleton.md T11/T16`
- `systems.py`
- `LM3-HV-310`
