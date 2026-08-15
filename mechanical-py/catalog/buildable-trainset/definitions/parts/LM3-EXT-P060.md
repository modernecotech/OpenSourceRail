# LM3-EXT-P060 — seats, grab rails, flooring, lighting, PIS, CCTV, intercom, signage kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `B12`, `B13`, `B14`, `B15`, `B16`, `B18`, `B19`, `E14`, `E15`, `A1`, `A2`, `A3`, `A4` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Late-installed passenger fit-out kit after shell paint and leak checks.

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
- Inspection methods: incoming visual inspection, envelope fit check, fire certificates, egress gauge, lighting lux test, network enumeration
- Tooling basis: RFQ-LM3-EXT-P060, CERT-LM3-EXT-P060, GAUGE-LM3-EXT-P060-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- fire certificates
- egress gauge
- lighting lux test
- network enumeration

## Source references

- `cots_equipment.py`
- `bom-skeleton.md B12-B19/A1-A4`
- `LM3-INT-230`
