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

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-TRACTION-ABB` — [ABB BORDLINE CC400/ESC/PB and Traction Battery Pro reference platform](https://www.abb.com/global/en/industries/railway/segments/rolling-stock/light-rail-vehicles)
- Procurement state: `architecture-rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Treat each converter, battery, charger/contact system and protection panel as separable behind frozen DC-link, cooling, HVIL, network and mechanical interfaces; qualify lower-cost local modules one at a time.
- Known fit gaps: The ABB platform is a rail-qualified architecture anchor, not proof that one published configuration meets the LM3 800 V LFP, 225 kWh/car, side-pin charging, packaging or price targets.
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
