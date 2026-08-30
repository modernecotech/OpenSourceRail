# LM3-TRC-SA615 — bogie-mounted motor, gearbox, flexible coupling and torque-reaction drive unit

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | traction drive clean assembly cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-TRC-P010`
- `LM3-TRC-P020`
- `LM3-BOG-P050`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-TRC-SA615 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier traction drive equipment, supplier HVAC and air-distribution kit, rail structural steel |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, adhesive/bonded/gasketed sealing interfaces, bonding/earthing, segregated harness/fluid routing
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, motor/gearbox serial match, coupling alignment, torque-link proof, insulation/rotation test, removal-envelope trial, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test, alignment survey, static brake test
- Tooling basis: FIX-LM3-TRC-SA615, KIT-LM3-TRC-SA615, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-TRC-P010` — motor-350kw-hm47-class axle traction motor

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

### 2. `LM3-TRC-P020` — single-stage reduction gearbox and flexible coupling

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - gear ratio certificate
  - oil access check
  - coupling alignment

### 3. `LM3-BOG-P050` — powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit

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


## Hold points

- motor/gearbox serial match
- coupling alignment
- torque-link proof
- insulation/rotation test
- removal-envelope trial

## Source references

- `bogie/motor.py`
- `bogie/gearbox.py`
- `bogie/assembly.py`
- `LM3-TRC-500`
