# LM3-EXT-P070 — roof antennas, service walkway pads, lifting covers, and maintenance labels

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-ROOF-SA410` |
| Procurement BOM lines | `E21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Service and radio-accessory roof package integrated around HVAC and PV keep-outs.

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
- Inspection methods: incoming visual inspection, envelope fit check, antenna VSWR test, walkway slip certificate, lifting-cover fit, roof bonding check, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-EXT-P070, CERT-LM3-EXT-P070, GAUGE-LM3-EXT-P070-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- antenna VSWR test
- walkway slip certificate
- lifting-cover fit
- roof bonding check

## Source references

- `systems.py`
- `interfaces.md`
- `LM3-ELC-300`
