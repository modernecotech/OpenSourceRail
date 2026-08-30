# LM3-EXT-P050 — roof PV module and edge-clamp kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 36 module |
| Parent assembly | `LM3-ROOF-SA410` |
| Procurement BOM lines | `T21` |
| Maturity | `release-candidate` |

## Make / buy basis

Flexible/rigid PV modules plus isolators and roof harness.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-PV-SUNMAN` — [Sunman Energy eArc lightweight photovoltaic modules](https://www.sunman-energy.com/earc/)
- Procurement state: `sample-and-rfq`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Equivalent local modules are acceptable after roof fire, isolation, vibration, hail/impact, walk-zone and bonded/clamped retention tests.
- Known fit gaps: Select an exact module and rail-compatible clamp/bond stack after the roof curvature and electrical string are frozen.
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
- Inspection methods: incoming visual inspection, envelope fit check, module datasheet, clamp pull test, isolation/bonding check, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-EXT-P050, CERT-LM3-EXT-P050, GAUGE-LM3-EXT-P050-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- module datasheet
- clamp pull test
- isolation/bonding check

## Source references

- `systems.py`
- `car_body.py`
- `LM3-HV-325`
