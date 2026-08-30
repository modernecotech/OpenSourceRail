# LM3-ART-P024 — articulation trainline carrier, support arms, abrasion liners and drain path

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `SOURCE` |
| Quantity per trainset | 2 carrier set |
| Parent assembly | `LM3-ART-SA830` |
| Procurement BOM lines | `B24` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

A replaceable energy-chain/support system controls service-loop bend radius and separates HV, LV/data and coolant across the joint.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-TRAINLINE-IGUS-HARTING` — [igus / HARTING e-chain dynamic cable carriers with Han rail connectors](https://www.igus.com/info/industries-railway-technology)
- Procurement state: `sample-and-rfq`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Hoses and cables may be made locally to controlled drawings; carrier, connector or jacket substitutions require bend-cycle, separation, IP, fire, current, pressure, EMC and breakaway tests.
- Known fit gaps: The final carrier series, connector inserts, cable compounds, hose lengths and articulation sweep remain to be frozen.
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
| Material family | fire-retardant fiberglass composite |
| Grade / part class | E-glass or basalt-fibre/vinyl-ester end-cowl laminate and insert kit |
| Governing standard | supplier laminate schedule plus project fire/smoke, coupon, and insert pull-out evidence |
| Form factor | moulded cowl cast, solid flanges, local core in broad skins, potted inserts, and trim/repair coupons |
| Nominal section | laminate thickness, ply drop, core map, insert pattern, split line, and trim datum per LM3-BDY-155 |
| Finish / protection | UV-stable exterior gelcoat/paint, sealed cut edges, gasketed seams, and mixed-metal isolation |
| Traceability | laminate batch, resin batch, cure record, insert pull-out record, adhesive batch, and coupon traceability |

Evidence required:

- certificate of conformity
- incoming inspection record
- laminate coupon
- cure record
- insert pull-out evidence
- fire-smoke certificate

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, HV safety plan, LOTO/service-disconnect rule, EMC/bonding evidence review, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, rated bend radius, dynamic sweep, abrasion/fire evidence, drain test, service replacement trial, bond continuity, insulation/isolation check, HVIL functional check where applicable, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P024, CERT-LM3-ART-P024, GAUGE-LM3-ART-P024-ENVELOPE
- Release level: SOURCE supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- rated bend radius
- dynamic sweep
- abrasion/fire evidence
- drain test
- service replacement trial

## Source references

- `articulation.md`
- `systems.py`
- `LM3-SYS-170`
