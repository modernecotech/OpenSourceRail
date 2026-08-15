# LM3-CTRL-P020 — navigation, balise, 5G, LoRa, GNSS, IMU, and roof-antenna kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 1 trainset kit |
| Parent assembly | `LM3-SYS-SA900` |
| Procurement BOM lines | `E3`, `E4`, `E5`, `E6`, `E7`, `E8`, `E21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Commodity navigation and communications devices are installed as individually traceable modules on the train network.

## Material specification

| Field | Value |
|---|---|
| Material family | rail-rated electrical / control equipment |
| Grade / part class | LV/data harness, cabinet, sensor, antenna, and trainline kit |
| Governing standard | supplier rail electronics specification plus project EMC, IP, and fire evidence |
| Form factor | cabinet, harness, connector, sensor, bracket, antenna, and label kit |
| Nominal section | connector, bend-radius, service-loop, and mounting envelope frozen by RFQ drawing |
| Finish / protection | halogen/fire-rated cable where required, IP sealing, bonding, and label protection |
| Traceability | serialised equipment CoC, firmware/config record, harness batch, and continuity record |

Evidence required:

- certificate of conformity
- incoming inspection record
- continuity test
- EMC/IP evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, SKU/firmware record, antenna VSWR, GNSS/IMU test, balise read, radio link test
- Tooling basis: RFQ-LM3-CTRL-P020, CERT-LM3-CTRL-P020, GAUGE-LM3-CTRL-P020-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- SKU/firmware record
- antenna VSWR
- GNSS/IMU test
- balise read
- radio link test

## Source references

- `bom-skeleton.md E3-E8/E21`
- `systems.py`
- `LM3-COM-600`
