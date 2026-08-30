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

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-HVAC-LONGERTEK` — [Longertek direct-DC rail HVAC platform](https://en.longertek.com/technological-innovation.html)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Keep the released 800 V-class input, thermal duty, refrigerant, drains, duct and CAN/Ethernet interface; source local coils, ducts and service parts after performance testing.
- Known fit gaps: Public material does not freeze the LM3 24 kW duty, rail evidence or roof envelope.
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
