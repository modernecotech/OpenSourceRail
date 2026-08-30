# LM3-TRC-P040 — battery-225kwh-lfp-800v under-seat traction battery pack

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 ea |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T5`, `T6` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Optimizer-selected per-car pack; final supplier must fit tray, cooling, BMS, and vent path.

## Material specification

| Field | Value |
|---|---|
| Material family | supplier high-voltage traction equipment |
| Grade / part class | battery / inverter / contactor / charger certified equipment class |
| Governing standard | supplier rail traction specification plus project HVIL, EMC, isolation, and thermal evidence |
| Form factor | sealed HV module, enclosure, orange HV harness, connectors, cooling interfaces, and labels |
| Nominal section | tray, connector, bend-radius, vent, and service envelope frozen by RFQ drawing |
| Finish / protection | supplier enclosure protection, orange HV marking, bonding, and coolant compatibility |
| Traceability | serialised HV equipment CoC, firmware/config revision, insulation record, and evidence pack |

Evidence required:

- certificate of conformity
- incoming inspection record
- isolation test record
- HVIL / EMC evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, cell/module certificate, isolation test, vent/fire containment data, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P040, CERT-LM3-TRC-P040, GAUGE-LM3-TRC-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- cell/module certificate
- isolation test
- vent/fire containment data

## Source references

- `design-iteration-summary.md`
- `systems.py`
- `LM3-BDY-140`
