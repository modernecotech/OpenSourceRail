# LM3-ART-P030 — inter-car HV/LV jumper, coolant hose loop, energy chain, and drain sleeve kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 2 articulation kit |
| Parent assembly | `LM3-ART-SA800` |
| Procurement BOM lines | `B24` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Flexible services package that follows articulation yaw/pitch/roll without violating segregation or bend radius.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, bend-radius sweep, trainline continuity, coolant pressure test, water-drain test, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P030, CERT-LM3-ART-P030, GAUGE-LM3-ART-P030-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- bend-radius sweep
- trainline continuity
- coolant pressure test
- water-drain test

## Source references

- `articulation.md`
- `systems.py`
- `LM3-SYS-170`
