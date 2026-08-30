# LM3-BOG-P043 — trailer-wheelset axlebox, sealed bearing unit, speed and temperature sensor set

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `external-component` |
| Route | `BID` |
| Quantity per trainset | 6 wheelset set |
| Parent assembly | `LM3-BOG-SA621` |
| Procurement BOM lines | `G4`, `G14`, `G15` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Ready-to-mount railway axlebox bearing units share the powered-bogie bearing and sensor interface where load calculations permit.

## Supplier anchor and local-equivalent route

- Anchor: `OSR-ANC-AXLEBOX-SKF` — [SKF ready-to-mount railway axlebox bearing units with sensors](https://www.skf.com/group/products/rolling-bearings/roller-bearings/tapered-roller-bearings/railway-tapered-roller-bearing-units)
- Procurement state: `rfq-required`
- Local equivalent allowed: yes, after the controlled equivalence dossier
- Localisation route: Local housings and sensor brackets may be made to the supplier-controlled bearing unit; an alternative bearing unit needs L10/load, fit, seal, grease, thermal, shock and field-monitoring evidence.
- Known fit gaps: Bearing size, journal fit, housing, grounding, speed/temperature sensor and cable interfaces remain to be frozen.
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
- Special process controls: RFQ envelope freeze, supplier certificate/revision check, incoming quarantine until evidence accepted
- Inspection methods: incoming visual inspection, envelope fit check, bearing serial/clearance record, grease and seal certificate, axle journal fit, speed/temperature sensor calibration, rotation test
- Tooling basis: RFQ-LM3-BOG-P043, CERT-LM3-BOG-P043, GAUGE-LM3-BOG-P043-ENVELOPE
- Release level: BID supplier-controlled process; OSR controls envelope and acceptance evidence

## Acceptance gates

- bearing serial/clearance record
- grease and seal certificate
- axle journal fit
- speed/temperature sensor calibration
- rotation test

## Source references

- `bogie/wheelset.py`
- `systems.py`
- `LM3-BOG-410`
