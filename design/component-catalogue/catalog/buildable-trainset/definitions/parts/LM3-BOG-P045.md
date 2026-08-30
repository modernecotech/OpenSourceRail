# LM3-BOG-P045 — trailer-bogie primary suspension spring, guide and bump-stop set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 bogie set |
| Parent assembly | `LM3-BOG-SA621` |
| Procurement BOM lines | `G5`, `G12` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Matched, batch-traceable primary springs and elastomer guides are selected from the released trailer axle-load and dynamic model.

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
| Material family | supplier-controlled external component |
| Grade / part class | COTS/BID component class matched to OSR envelope |
| Governing standard | supplier specification plus project interface, safety, EMC/fire, and lifecycle evidence |
| Form factor | preassembled supplier module with installation kit |
| Nominal section | mass, volume, mounting datum, service clearance, and connector envelope frozen by RFQ drawing |
| Finish / protection | supplier finish/protection accepted by OSR evidence pack |
| Traceability | serialised CoC, datasheet, revision, and incoming inspection record |

Evidence required:

- certificate of conformity
- incoming inspection record
- datasheet / evidence pack

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, load-deflection curves, matched-height report, compound/batch certificates, installed preload and clearance survey
- Tooling basis: RFQ-LM3-BOG-P045, CERT-LM3-BOG-P045, GAUGE-LM3-BOG-P045-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- load-deflection curves
- matched-height report
- compound/batch certificates
- installed preload and clearance survey

## Source references

- `bogie/suspension.py`
- `LM3-BOG-410`
