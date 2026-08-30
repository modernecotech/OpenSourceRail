# LM3-TRC-P030 — two independent motor controllers, isolated LV DC/DC, MPPT, station protection, and cooling-loop kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T3`, `T4`, `T7`, `T13`, `T20`, `T23` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Per-car 800 V-class traction, auxiliary, PV, and station-interface electronics; no central AC bus.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, HVIL test, coolant pressure test, EMC/bonding check, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-TRC-P030, CERT-LM3-TRC-P030, GAUGE-LM3-TRC-P030-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- HVIL test
- coolant pressure test
- EMC/bonding check

## Source references

- `systems.py`
- `bom-skeleton.md T3/T12/T13/T20/T23`
- `LM3-HV-320`
