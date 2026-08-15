# LM3-TRC-P010 — motor-350kw-hm47-class axle traction motor

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 6 ea |
| Parent assembly | `LM3-BOG-SA610` |
| Procurement BOM lines | `T1` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Optimizer-selected 250 kW motor class; CAD baseline carries the promoted envelope.

## Material specification

| Field | Value |
|---|---|
| Material family | supplier traction drive equipment |
| Grade / part class | traction motor / gearbox / coupling certified equipment class |
| Governing standard | supplier rail traction specification plus project EMC, thermal, and mount-load evidence |
| Form factor | preassembled motor, gearbox, coupling, seals, oil ports, and mounting hardware |
| Nominal section | bogie motor-cradle and axle interface frozen by RFQ drawing |
| Finish / protection | supplier coating, lubrication preservation, earthing/bonding, and thermal labels |
| Traceability | serialised drive equipment CoC, test report, oil data, and revision record |

Evidence required:

- certificate of conformity
- incoming inspection record
- thermal curve
- mounting-foot proof evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, motor datasheet, thermal curve, mounting-foot load proof, EMC evidence, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-TRC-P010, CERT-LM3-TRC-P010, GAUGE-LM3-TRC-P010-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- motor datasheet
- thermal curve
- mounting-foot load proof
- EMC evidence

## Source references

- `design-iteration-summary.md`
- `bogie/motor.py`
- `LM3-TRC-500`
