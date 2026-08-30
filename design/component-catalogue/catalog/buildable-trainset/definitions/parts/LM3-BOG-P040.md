# LM3-BOG-P040 — powered-bogie wheelset with axle-mounted brake discs

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 6 wheelset |
| Parent assembly | `LM3-BOG-SA611` |
| Procurement BOM lines | `G3`, `G8` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier-machined axle, wheels and brake-disc seats are procured as a dynamically balanced, traceable railway wheelset; wheels or axles are not mixed between qualified families.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-WHEELSET-GHH` — [GHH-BONATRANS urban-rail wheelsets](https://www.ghh-bonatrans.com/en/about-us/products-and-services/wheelset/)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local wheel/axle manufacture is encouraged only after metallurgy, forging, heat treatment, NDT, press-fit, profile, fatigue and route-specific standards are qualified and independently accepted.
- Known fit gaps: Wheel profile, diameter, axle journal, disc seats, material grades and load spectrum remain to be frozen.
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
| Material family | supplier-certified running gear |
| Grade / part class | wheelset / bearing / brake / suspension safety-critical kit |
| Governing standard | supplier rail running-gear specification plus project brake, ride-height, and traceability evidence |
| Form factor | machined/forged rotating parts, brake hardware, suspension elements, and fastener kit |
| Nominal section | bogie interface envelope frozen by RFQ drawing |
| Finish / protection | supplier corrosion protection and lubrication preservation |
| Traceability | serialised wheelset, bearing, brake, and suspension records |

Evidence required:

- certificate of conformity
- incoming inspection record
- wheelset/bearing certificates
- brake evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, wheel/axle heat certificates, press-force chart, back-to-back and runout report, ultrasonic inspection, balance record, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P040, CERT-LM3-BOG-P040, GAUGE-LM3-BOG-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- wheel/axle heat certificates
- press-force chart
- back-to-back and runout report
- ultrasonic inspection
- balance record

## Source references

- `bogie/wheelset.py`
- `bogie/brake.py`
- `LM3-BOG-400`
