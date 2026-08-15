# LM3-INT-P010 — HVAC diffusers, side return ducts, saloon grilles, and access panels

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-INT-SA330` |
| Procurement BOM lines | `T14` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Interior air distribution kit between roof HVAC drops and the passenger saloon.

## Material specification

| Field | Value |
|---|---|
| Material family | supplier HVAC and air-distribution kit |
| Grade / part class | hot-climate roof HVAC / fire-rated interior duct kit |
| Governing standard | supplier rail/bus HVAC specification plus project EMC, vibration, and fire evidence |
| Form factor | packaged roof unit, curb gasket, diffusers, ducts, grilles, and access panels |
| Nominal section | roof curb and saloon envelope frozen by RFQ drawing |
| Finish / protection | supplier coating, condensate protection, and fire-rated interior surfaces |
| Traceability | unit serial number, refrigerant/coolant data, CoC, and fire-material batch |

Evidence required:

- certificate of conformity
- incoming inspection record
- capacity test evidence
- fire-material certificate

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, airflow balance, rattle check, access-panel removal, fire-material certificate, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-INT-P010, CERT-LM3-INT-P010, GAUGE-LM3-INT-P010-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- airflow balance
- rattle check
- access-panel removal
- fire-material certificate

## Source references

- `car_body.py`
- `cots_equipment.py`
- `LM3-HVAC-220`
