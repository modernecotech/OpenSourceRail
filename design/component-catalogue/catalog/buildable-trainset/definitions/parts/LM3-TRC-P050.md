# LM3-TRC-P050 — roof-mounted regen dump resistor and thermal shield kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 ea |
| Parent assembly | `LM3-ROOF-SA410` |
| Procurement BOM lines | `T15` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Per-car roof resistor path for regen overvoltage and commissioning load tests.

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
| Material family | roof electrical energy equipment |
| Grade / part class | PV module / resistor / clamp / isolator kit |
| Governing standard | supplier datasheet plus project bonding, isolation, fire, and vibration evidence |
| Form factor | module, thermal shield, aluminum/stainless clamp hardware, and UV-rated harness |
| Nominal section | roof keep-out, clamp pitch, and thermal clearance frozen by RFQ drawing |
| Finish / protection | UV/weather protection, hot-surface labelling, and galvanic isolation where required |
| Traceability | module serials, resistance/PV flash data, CoC, and harness batch |

Evidence required:

- certificate of conformity
- incoming inspection record
- electrical datasheet
- bonding/isolation record

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, resistance certificate, thermal clearance, roof bonding, hot-surface label, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-TRC-P050, CERT-LM3-TRC-P050, GAUGE-LM3-TRC-P050-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- resistance certificate
- thermal clearance
- roof bonding
- hot-surface label

## Source references

- `bom-skeleton.md T15`
- `systems.py`
- `LM3-HV-325`
