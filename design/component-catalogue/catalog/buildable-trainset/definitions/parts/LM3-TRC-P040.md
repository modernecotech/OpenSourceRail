# LM3-TRC-P040 — battery-225kwh-lfp-800v under-seat traction battery pack

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 ea |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T5`, `T6` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Optimizer-selected per-car pack; final supplier must fit tray, cooling, BMS, and vent path.

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
| Material family | supplier high-voltage traction equipment |
| Grade / part class | battery / inverter / contactor / charger certified equipment class |
| Governing standard | supplier rail traction specification plus project HVIL, EMC, isolation, and thermal evidence |
| Form factor | sealed HV module, enclosure, orange HV harness, connectors, cooling interfaces, and labels |
| Nominal section | tray, connector, bend-radius, vent, and service envelope frozen by RFQ drawing |
| Finish / protection | supplier enclosure protection, orange HV marking, bonding, and coolant compatibility |
| Traceability | serialised HV equipment CoC, firmware/config revision, insulation record, and evidence pack |

Evidence required:

- certificate of conformity
- incoming inspection record
- isolation test record
- HVIL / EMC evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review
- Inspection methods: incoming visual inspection, envelope fit check, cell/module certificate, isolation test, vent/fire containment data, bond continuity, insulation/isolation check, HVIL functional check where applicable
- Tooling basis: RFQ-LM3-TRC-P040, CERT-LM3-TRC-P040, GAUGE-LM3-TRC-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- cell/module certificate
- isolation test
- vent/fire containment data

## Source references

- `design-iteration-summary.md`
- `systems.py`
- `LM3-BDY-140`
