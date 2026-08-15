# LM3-CTRL-P030 — maintenance HMI, depot pendant, emergency controls, and safety-relay kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 1 trainset kit |
| Parent assembly | `LM3-SYS-SA900` |
| Procurement BOM lines | `E10`, `E11`, `E12`, `E13`, `E16` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Human-service and hardwired emergency interfaces remain segregated from normal unattended operation.

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
- Inspection methods: incoming visual inspection, envelope fit check, key/guarded-control test, emergency input test, 2oo2 relay test, stowage and access check
- Tooling basis: RFQ-LM3-CTRL-P030, CERT-LM3-CTRL-P030, GAUGE-LM3-CTRL-P030-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- key/guarded-control test
- emergency input test
- 2oo2 relay test
- stowage and access check

## Source references

- `bom-skeleton.md E10-E13/E16`
- `systems.py`
- `LM3-ELC-300`
