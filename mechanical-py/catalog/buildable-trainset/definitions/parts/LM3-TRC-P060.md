# LM3-TRC-P060 — station side-pin charging connector, actuator, shutter, and alignment target

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T12`, `T19` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Conductive station charging interface with mechanical guide datum and safety interlocks.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, dock alignment test, HVIL test, shutter cycle test, emergency release, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P060, CERT-LM3-TRC-P060, GAUGE-LM3-TRC-P060-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- dock alignment test
- HVIL test
- shutter cycle test
- emergency release

## Source references

- `bom-skeleton.md T12/T19`
- `systems.py`
- `LM3-HV-310`
