# LM3-BOG-SA611 — powered-bogie running unit: wheelsets, axleboxes, primary suspension and brakes

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | bogie clean assembly and brake cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-BOG-P040`
- `LM3-BOG-P042`
- `LM3-BOG-P044`
- `LM3-BOG-P048`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BOG-SA611 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier-certified running gear, supplier-controlled external component |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, wheelset identity, bearing installation, primary-height match, static brake/WSP test, free rotation, alignment survey, static brake test
- Tooling basis: FIX-LM3-BOG-SA611, KIT-LM3-BOG-SA611, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BOG-P040` — powered-bogie wheelset with axle-mounted brake discs

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - wheel/axle heat certificates
  - press-force chart
  - back-to-back and runout report
  - ultrasonic inspection
  - balance record

### 2. `LM3-BOG-P042` — powered-wheelset axlebox, sealed bearing unit, speed and temperature sensor set

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - bearing serial/clearance record
  - grease and seal certificate
  - axle journal fit
  - speed/temperature sensor calibration
  - rotation test

### 3. `LM3-BOG-P044` — powered-bogie primary suspension spring, guide and bump-stop set

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - load-deflection curves
  - matched-height report
  - compound/batch certificates
  - installed preload and clearance survey

### 4. `LM3-BOG-P048` — powered-bogie brake calipers, parking actuators, pads and wheel-slide hardware

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - brake-force calculation
  - friction-pair certificate
  - thermal capacity
  - parking holding test
  - WSP functional test


## Hold points

- wheelset identity
- bearing installation
- primary-height match
- static brake/WSP test
- free rotation

## Source references

- `bogie/wheelset.py`
- `bogie/brake.py`
- `bogie/suspension.py`
- `LM3-BOG-400`
