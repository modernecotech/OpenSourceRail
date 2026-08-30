# LM3-AUX-P010 — secondary-suspension compressor, dryer, reservoir, and isolation-manifold kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-CAR-A900` |
| Procurement BOM lines | `G21` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

One local air-supply package per car serves its two secondary-suspension bogies without creating a trainwide pneumatic brake line.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-BRAKE-KNORR` — [Knorr-Bremse WheelAct/AxleAct rail brake actuation and PistonSupply/DrySupply air supply](https://rail.knorr-bremse.com/en/se/portfolio/products-and-systems/braking-systems/actuation/)
- Procurement state: `system-rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Pads, discs, hoses and overhaul parts can localise first under brake-supplier approval; caliper/actuator or compressor substitutes require stopping, parking, thermal, WSP, degraded-mode and endurance revalidation.
- Known fit gaps: The LM3 brake concept needs supplier confirmation of actuation energy, caliper variant, disc/pad pair, parking brake and whether the suspension-only compressor can support the selected brake architecture.
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
- Inspection methods: incoming visual inspection, envelope fit check, pressure certificate, leak test, dryer function, relief-valve test, service-access check, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-AUX-P010, CERT-LM3-AUX-P010, GAUGE-LM3-AUX-P010-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- pressure certificate
- leak test
- dryer function
- relief-valve test
- service-access check

## Source references

- `bom-skeleton.md G21`
- `bogie/suspension.py`
- `systems.py`
