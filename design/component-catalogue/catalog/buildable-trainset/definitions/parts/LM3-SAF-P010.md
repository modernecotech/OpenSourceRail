# LM3-SAF-P010 — battery temperature/off-gas detection, electrical-enclosure smoke detection, and localized mist kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-HV-SA510` |
| Procurement BOM lines | `T9`, `T10` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Per-car battery reservoir, DC pump, stainless pipe, nozzles, outward vents, and diagnostic sensors; no saloon or electrical-bay suppression.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-FIRE-FOGTEC` — [FOGTEC rail fire detection and high-pressure water-mist systems](https://fogtec-international.com/rail/)
- Procurement state: `rfq-and-hazard-test-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local detectors, pipework, reservoir and pumps may be introduced only within a vehicle fire-hazard analysis and propagation-tested suppression/detection system.
- Known fit gaps: Battery chemistry, enclosure, detection thresholds, nozzle layout, reservoir and control integration remain project-specific.
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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, detector certificate, loop continuity, mist proof-flow, reservoir/pump/pressure diagnostic, event-recorder input, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-SAF-P010, CERT-LM3-SAF-P010, GAUGE-LM3-SAF-P010-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- detector certificate
- loop continuity
- mist proof-flow
- reservoir/pump/pressure diagnostic
- event-recorder input

## Source references

- `bom-skeleton.md T9/T10`
- `systems.py`
- `LM3-SAF-340`
