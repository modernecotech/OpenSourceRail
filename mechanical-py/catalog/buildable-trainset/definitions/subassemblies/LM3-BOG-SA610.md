# LM3-BOG-SA610 — powered bogie assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | bogie weld and assembly cell |
| Procurement BOM lines | `B4`, `G21` |
| Maturity | `release-candidate` |

## Children

- `LM3-BOG-P010`
- `LM3-BOG-P030`
- `LM3-BOG-P040`
- `LM3-BOG-P050`
- `LM3-BOG-P060`
- `LM3-TRC-P010`
- `LM3-TRC-P020`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BOG-SA610 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-certified running gear, supplier traction drive equipment, supplier HVAC and air-distribution kit |
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
- Inspection methods: child acceptance evidence review, frame NDT, wheelset/bearing certificate, motor/gearbox alignment, static brake test, VT, MT/UT where classed, post-weld datum survey, alignment survey
- Tooling basis: FIX-LM3-BOG-SA610, KIT-LM3-BOG-SA610, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BOG-P010` — powered bogie welded H-frame and motor-cradle weldment

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `structural-weld`, `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - bogie fixture survey
  - weld/NDT record
  - motor-cradle proof

### 2. `LM3-BOG-P030` — powered-bogie guards, cable guides, WSP brackets, and inspection covers

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - service access check
  - harness clearance
  - fastener torque record

### 3. `LM3-BOG-P040` — powered-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit

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

### 4. `LM3-BOG-P050` — powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - torque-link gauge
  - bracket NDT
  - motor removal clearance
  - fastener locking record

### 5. `LM3-BOG-P060` — powered-bogie brake/WSP/speed-sensor harness and junction-bracket kit

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

### 6. `LM3-TRC-P010` — motor-350kw-hm47-class axle traction motor

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - motor datasheet
  - thermal curve
  - mounting-foot load proof
  - EMC evidence

### 7. `LM3-TRC-P020` — single-stage reduction gearbox and flexible coupling

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - gear ratio certificate
  - oil access check
  - coupling alignment


## Hold points

- frame NDT
- wheelset/bearing certificate
- motor/gearbox alignment
- static brake test

## Source references

- `bogie/assembly.py`
- `LM3-BOG-400`
