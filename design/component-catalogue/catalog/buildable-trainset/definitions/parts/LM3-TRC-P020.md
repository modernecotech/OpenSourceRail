# LM3-TRC-P020 — single-stage reduction gearbox and flexible coupling

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 6 ea |
| Parent assembly | `LM3-TRC-SA615` |
| Procurement BOM lines | `G19`, `T2` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Gearbox mounted on powered bogie axle with supplier coupling.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-GEAR-VOITH-SE` — [Voith SE-type single-stage axle-mounted metro gear unit and gear coupling](https://www.voith.com/corp-en/drives-transmissions/gear-units.html)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local housings/gears may replace the anchor only after tooth, bearing, lubrication, fatigue, efficiency, noise, overspeed and endurance qualification with the frozen motor/wheelset interfaces.
- Known fit gaps: Ratio, centre distance, torque, coupling, reaction-link and lubrication configuration remain to be quoted.
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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, gear ratio certificate, oil access check, coupling alignment
- Tooling basis: RFQ-LM3-TRC-P020, CERT-LM3-TRC-P020, GAUGE-LM3-TRC-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- gear ratio certificate
- oil access check
- coupling alignment

## Source references

- `bogie/gearbox.py`
- `bom-skeleton.md T2/G19`
- `LM3-TRC-500`
