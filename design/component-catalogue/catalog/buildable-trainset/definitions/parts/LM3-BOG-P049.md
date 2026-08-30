# LM3-BOG-P049 — trailer-bogie brake calipers, parking actuators, pads and wheel-slide hardware

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 bogie set |
| Parent assembly | `LM3-BOG-SA621` |
| Procurement BOM lines | `G8`, `G9`, `G16` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

A rail brake supplier matches caliper, actuator, disc and pad friction pair to the released stopping, thermal and parking-brake cases.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, brake-force calculation, friction-pair certificate, thermal capacity, parking holding test, WSP functional test, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P049, CERT-LM3-BOG-P049, GAUGE-LM3-BOG-P049-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- brake-force calculation
- friction-pair certificate
- thermal capacity
- parking holding test
- WSP functional test

## Source references

- `bogie/brake.py`
- `systems.py`
- `LM3-BOG-410`
