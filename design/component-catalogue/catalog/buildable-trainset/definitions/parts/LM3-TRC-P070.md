# LM3-TRC-P070 — HV contactor, fuse, pre-charge, service-disconnect, and current-sensor panel

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T11`, `T16` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier-certified high-voltage protection panel between battery, charger, PV, and inverter.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, isolation test, pre-charge timing, fuse rating evidence, service-disconnect lockout, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P070, CERT-LM3-TRC-P070, GAUGE-LM3-TRC-P070-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- isolation test
- pre-charge timing
- fuse rating evidence
- service-disconnect lockout

## Source references

- `bom-skeleton.md T11/T16`
- `systems.py`
- `LM3-HV-310`
