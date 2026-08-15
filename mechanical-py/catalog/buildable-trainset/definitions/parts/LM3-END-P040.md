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
