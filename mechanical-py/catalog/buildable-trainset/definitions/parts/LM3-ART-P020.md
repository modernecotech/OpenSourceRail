# LM3-ART-P020 — gangway, lower spherical pivot, upper links, bellows, turntable, and trainline kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 2 kit |
| Parent assembly | `LM3-ART-SA800` |
| Procurement BOM lines | `B9` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Supplier gangway/articulation kit integrated through OSR adapter frame.

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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted, fluid compatibility check, hose/pipe routing release, safety interlock interface freeze, supplier lifecycle evidence review
- Inspection methods: incoming visual inspection, envelope fit check, motion-envelope proof, fire evidence, water ingress/drain test, pressure/leak test, drain-flow test where applicable, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-ART-P020, CERT-LM3-ART-P020, GAUGE-LM3-ART-P020-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- motion-envelope proof
- fire evidence
- water ingress/drain test

## Source references

- `systems.py`
- `articulation.md`
- `LM3-SYS-170`
