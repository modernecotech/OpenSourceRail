# LM3-BOG-P041 — trailer-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 3 bogie kit |
| Parent assembly | `LM3-BOG-SA620` |
| Procurement BOM lines | `G3`, `G4`, `G5`, `G6`, `G7`, `G8`, `G9`, `G10`, `G11`, `G12`, `G14`, `G15`, `G16` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

The trailer-bogie G3-G16 safety-critical rotating, suspension, braking, pivot, restraint, and sensing package stays supplier-certified.

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
- Inspection methods: incoming visual inspection, envelope fit check, wheelset certificates, bearing records, spring/damper certificates, brake test, sensor test, ride-height report, functional static test, emergency/recovery function check where applicable
- Tooling basis: RFQ-LM3-BOG-P041, CERT-LM3-BOG-P041, GAUGE-LM3-BOG-P041-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- wheelset certificates
- bearing records
- spring/damper certificates
- brake test
- sensor test
- ride-height report

## Source references

- `bogie/wheelset.py`
- `bogie/brake.py`
- `bogie/suspension.py`
- `LM3-BOG-410`
