# LM3-FIN-P020 — calcium-carbonate radiative roof-coating qualification and exposed-roof application kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-ROOF-SA410` |
| Procurement BOM lines | `B20`, `B28` |
| Maturity | `concept` |

## Make / buy basis

Candidate high-reflectance CaCO3-acrylic coating is confined to exposed roof fairings after a coupon and one-car field trial; PV, glazing, antennas, heat exchangers, walkways, drains, labels, seals, bonds, and service lands remain masked.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-COOLROOF-PURDUE` — [Purdue University research reference — no nominated commercial supplier 2020 CaCO3-acrylic passive radiative-cooling paint formulation](https://docs.lib.purdue.edu/coolingpubs/369/)
- Procurement state: `coupon-development-and-one-car-trial-only`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Develop/mix trial coupons locally under competent coatings and occupational-hygiene control; do not purchase or apply fleet-wide until a controlled commercial formulation and rail evidence are released.
- Known fit gaps: No commercial rail-qualified product, vehicle durability pack, fire evidence or released LM3 application procedure is established by the research paper.
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
| Material family | rail laminated safety glazing |
| Grade / part class | bonded/gasketed laminated safety-glass cassette |
| Governing standard | supplier rail glazing specification plus project fire/smoke and impact evidence |
| Form factor | laminated glass cassette with heater/bond/gasket hardware as required |
| Nominal section | aperture envelope and bond/gasket land frozen by RFQ drawing |
| Finish / protection | edge seal, heater isolation, and supplier-approved cleaning/protection |
| Traceability | pane/cassette serial number, CoC, heater record, and installation batch |

Evidence required:

- certificate of conformity
- incoming inspection record
- glazing certificate
- heater/isolation record

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release
- Inspection methods: incoming visual inspection, envelope fit check, rail fire/chemical evidence, GFRP adhesion and flexibility, UV/abrasion/wash ageing, initial and aged solar reflectance/emittance, one-car thermal/maintenance trial, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable
- Tooling basis: RFQ-LM3-FIN-P020, CERT-LM3-FIN-P020, GAUGE-LM3-FIN-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- rail fire/chemical evidence
- GFRP adhesion and flexibility
- UV/abrasion/wash ageing
- initial and aged solar reflectance/emittance
- one-car thermal/maintenance trial

## Source references

- `exterior-finish-process.md`
- `roof-fitout.md`
- `LM3-BDY-160`
