# LM3-BOG-SA620 — trailer bogie assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | bogie weld and assembly cell |
| Procurement BOM lines | `B4`, `G21` |
| Maturity | `release-candidate` |

## Children

- `LM3-BOG-P020`
- `LM3-BOG-P031`
- `LM3-BOG-P041`
- `LM3-BOG-P061`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BOG-SA620 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-certified running gear |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, fixture tack/weld, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, WPS-controlled structural welding
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, weld map release, WPS/WPQR and welder qualification, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, frame NDT, wheelset/bearing certificate, ride-height setup, static brake test, VT, MT/UT where classed, post-weld datum survey, alignment survey
- Tooling basis: FIX-LM3-BOG-SA620, KIT-LM3-BOG-SA620, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BOG-P020` — trailer bogie welded H-frame

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - bogie fixture survey
  - weld/NDT record
  - air-spring datum survey

### 2. `LM3-BOG-P031` — trailer-bogie guards, cable guides, WSP brackets, and inspection covers

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - service access check
  - harness clearance
  - fastener torque record

### 3. `LM3-BOG-P041` — trailer-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - wheelset certificates
  - bearing records
  - spring/damper certificates
  - brake test
  - sensor test
  - ride-height report

### 4. `LM3-BOG-P061` — trailer-bogie brake/WSP/speed-sensor harness and junction-bracket kit

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - continuity test
  - connector IP rating
  - wheelset clearance
  - dynamic cable sweep


## Hold points

- frame NDT
- wheelset/bearing certificate
- ride-height setup
- static brake test

## Source references

- `bogie/assembly.py`
- `LM3-BOG-410`
