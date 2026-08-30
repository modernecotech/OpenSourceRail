# LM3-BOG-P046 — powered-bogie to carbody connection: air springs, emergency spring, centre pivot, yaw links and dampers

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 bogie set |
| Parent assembly | `LM3-BOG-SA610` |
| Procurement BOM lines | `G6`, `G7`, `G10`, `G11`, `G12` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

The complete body-to-bogie load path is one interface-controlled package even when springs, pivot and dampers are sourced from different qualified suppliers.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-SUSPENSION-CONTI` — [Continental rail primary suspension and secondary air-spring systems](https://www.continental-industry.com/global/en/products-solutions/airsprings-suspension/railway)
- Procurement state: `rfq-and-dynamics-freeze-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Springs, bushes and dampers may be sourced regionally after the multibody model, load-deflection/damping curves, compound ageing, fatigue and ride tests are repeated; pivot/anti-lift hardware stays separately calculated.
- Known fit gaps: Continental anchors spring systems; centre pivot, yaw-link and damper suppliers still require project RFQ and a common body-to-bogie interface control drawing.
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
- Inspection methods: incoming visual inspection, envelope fit check, vertical/lateral load curves, pivot proof and articulation limit, damper curves hot/cold, ride-height and anti-lift survey, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P046, CERT-LM3-BOG-P046, GAUGE-LM3-BOG-P046-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- vertical/lateral load curves
- pivot proof and articulation limit
- damper curves hot/cold
- ride-height and anti-lift survey

## Source references

- `bogie/suspension.py`
- `car_body.py`
- `LM3-BOG-400`
