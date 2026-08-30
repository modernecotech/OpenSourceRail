# LM3-ART-P041 — train-to-train jumper blanking, transition harness, isolation label, and dust-cover kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 0 joint kit |
| Parent assembly | `LM3-TTART-SA850` |
| Procurement BOM lines | `B24` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Pre-terminated service transition and blanking hardware for open-end train-to-train gangway joints and protected unused end connectors.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, pinout test, blanking cover ingress check, isolation label inspection, bend-radius sweep, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P041, CERT-LM3-ART-P041, GAUGE-LM3-ART-P041-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- pinout test
- blanking cover ingress check
- isolation label inspection
- bend-radius sweep

## Source references

- `articulation.md`
- `interfaces.md`
- `LM3-SYS-175`

## Notes

Optional for open mid-connection end configuration.
