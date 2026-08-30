# LM3-END-P040 — e-coupler LV jumper, recovery trainline, and end harness breakaway kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 2 end kit |
| Parent assembly | `LM3-END-SA700` |
| Procurement BOM lines | `B22`, `E17` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Electrical trainline and rescue interface paired with the automatic mechanical coupler.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-COUPLER-DELLNER430` — [Dellner automatic coupler Type 430 with pivot anchor](https://www.dellner.com/products/automatic-couplers/automatic-coupler-type-430)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local pocket, covers and harness may be manufactured to the Dellner interface; another coupler requires buff/draft, crash, rescue, gathering range, electrical head and fatigue compatibility evidence.
- Known fit gaps: The published 600/500 kN family is an anchor; height, articulation, fold, electrical head, crash stroke and OSR pocket loads remain to be frozen.
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
| Material family | supplier crash/coupler system |
| Grade / part class | automatic coupler and crash-energy absorber kit |
| Governing standard | supplier crashworthiness specification plus project recovery and interface evidence |
| Form factor | coupler head, draft gear, absorber, jumper hardware, and bolted mounting kit |
| Nominal section | coupler pocket envelope and load path frozen by RFQ drawing |
| Finish / protection | supplier coating, preservation, and rescue/recovery labels |
| Traceability | serialised coupler/absorber CoC, overhaul status, and proof evidence |

Evidence required:

- certificate of conformity
- incoming inspection record
- crash-energy evidence
- bolt/torque evidence

## Process specification

- Primary processes: receive, quarantine, evidence review, incoming fit check, release to parent kit
- Joining methods: bolted/torqued installation, sealed, gasketed, bonded, or clipped interface as supplier envelope requires
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, pinout test, breakaway force check, ingress protection, rescue compatibility, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-END-P040, CERT-LM3-END-P040, GAUGE-LM3-END-P040-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- pinout test
- breakaway force check
- ingress protection
- rescue compatibility

## Source references

- `systems.py`
- `interfaces.md`
- `LM3-SYS-160`
