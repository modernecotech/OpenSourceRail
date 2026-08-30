# LM3-CTRL-P010 — T-ECU/S and T-ECU/A compute and safety-control cabinet kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 1 trainset kit |
| Parent assembly | `LM3-SYS-SA900` |
| Procurement BOM lines | `E1`, `E2`, `E6`, `E14`, `E15` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

The controlled train-compute and safety-output cabinets are integrated after power, cooling, and network interfaces are frozen.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-CONTROL-MOXA` — [Moxa EN 50155 railway computers, Ethernet switches and wireless gateways](https://www.moxa.com/en/literature-library/rail-onboard-solution-brochure)
- Procurement state: `architecture-rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: OSR software remains portable behind published I/O, TSN/Ethernet and update interfaces; alternate compute/network hardware must pass timing, safety allocation, EMC, environmental, cybersecurity and whole-train hardware-in-loop tests.
- Known fit gaps: Moxa anchors computing/network hardware only; the independent safety controller, navigation sensors, HMI and safety relays need exact part selection and safety allocation.
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
| Material family | rail-rated electrical / control equipment |
| Grade / part class | LV/data harness, cabinet, sensor, antenna, and trainline kit |
| Governing standard | supplier rail electronics specification plus project EMC, IP, and fire evidence |
| Form factor | cabinet, harness, connector, sensor, bracket, antenna, and label kit |
| Nominal section | connector, bend-radius, service-loop, and mounting envelope frozen by RFQ drawing |
| Finish / protection | halogen/fire-rated cable where required, IP sealing, bonding, and label protection |
| Traceability | serialised equipment CoC, firmware/config record, harness batch, and continuity record |

Evidence required:

- certificate of conformity
- incoming inspection record
- continuity test
- EMC/IP evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, hardware BOM check, self-test, network enumeration, firmware record, safety-output test
- Tooling basis: RFQ-LM3-CTRL-P010, CERT-LM3-CTRL-P010, GAUGE-LM3-CTRL-P010-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- hardware BOM check
- self-test
- network enumeration
- firmware record
- safety-output test

## Source references

- `systems.py`
- `control-electronics/rolling-stock-integration.md`
- `LM3-ELC-300`
