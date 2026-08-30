# LM3-TRC-P010 — motor-350kw-hm47-class axle traction motor

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 6 ea |
| Parent assembly | `LM3-TRC-SA615` |
| Procurement BOM lines | `T1` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Optimizer-selected 250 kW motor class; CAD baseline carries the promoted envelope.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-MOTOR-ABB-AMXM` — [ABB AMXM railway traction motor](https://www.abb.com/global/en/areas/motion/traction/traction-motor/amxm)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Buy the initial motor; local rewind, bearings and eventually a locally manufactured equivalent require the frozen torque-speed, cooling, insulation, shaft, foot, mass and EMC interfaces plus type tests.
- Known fit gaps: The current HM47-class planning envelope is not an ABB order code; ABB must confirm a 250 kW continuous / 350 kW short-peak, 800 V-compatible configuration and mass envelope.
- Mandatory equivalence:
  - same or better released fit, mounting datums, connector keying and service envelope
  - same or better mass, load, duty-cycle, thermal, electrical and environmental ratings
  - same or better functional safety, fire, EMC, cybersecurity and applicable rail evidence
  - documented failure modes, maintenance intervals, spares and obsolescence route
  - first-article inspection plus component, subassembly and vehicle regression tests
  - signed design-authority substitution record preserving the original anchor and evidence hashes

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
