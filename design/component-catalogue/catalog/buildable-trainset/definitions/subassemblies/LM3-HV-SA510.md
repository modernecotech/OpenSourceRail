# LM3-HV-SA510 — per-car LFP battery, two controllers, DC auxiliary/charge interface, mist, and cooling assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-P050`
- `LM3-HV-P010`
- `LM3-HV-P020`
- `LM3-HV-P030`
- `LM3-TRC-P030`
- `LM3-TRC-P040`
- `LM3-TRC-P060`
- `LM3-TRC-P070`
- `LM3-SAF-P010`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-HV-SA510 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | formed sheet metal / stainless local hardware, roof electrical energy equipment, supplier high-voltage traction equipment, supplier HVAC and air-distribution kit |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, bonding/earthing, segregated harness/fluid routing
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable
- Inspection methods: child acceptance evidence review, HVIL test, insulation resistance, coolant pressure test, first energisation release, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-HV-SA510, KIT-LM3-HV-SA510, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-P050` — battery tray rails, vent plenum, and service-lid gutter kit

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - battery gauge fit
  - vent-path inspection
  - gasket land check

### 2. `LM3-HV-P010` — battery sliding trays, retention straps, service interlocks, and drain pans

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - battery module gauge
  - retention pull test
  - tray slide/removal test
  - drain-path inspection

### 3. `LM3-HV-P020` — segregated HV cable tray, bonding studs, grommets, and orange cover set

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - bend-radius gauge
  - bond continuity
  - cover fastener torque
  - orange-label inspection

### 4. `LM3-HV-P030` — coolant manifold brackets, bleed/drain points, and insulated pipe clamp kit

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - pressure-test access
  - bleed point height check
  - pipe clamp pitch
  - thermal isolation inspection

### 5. `LM3-TRC-P030` — two independent motor controllers, isolated LV DC/DC, MPPT, station protection, and cooling-loop kit

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`, `high-voltage electrical`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - HVIL test
  - coolant pressure test
  - EMC/bonding check

### 6. `LM3-TRC-P040` — battery-225kwh-lfp-800v saloon-isolated side traction battery pack

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - cell/module certificate
  - isolation test
  - no-saloon-opening inspection
  - outward vent/fire containment data

### 7. `LM3-TRC-P060` — station side-pin charging connector, actuator, shutter, and alignment target

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - dock alignment test
  - HVIL test
  - shutter cycle test
  - emergency release

### 8. `LM3-TRC-P070` — HV contactor, fuse, pre-charge, service-disconnect, and current-sensor panel

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - isolation test
  - pre-charge timing
  - fuse rating evidence
  - service-disconnect lockout

### 9. `LM3-SAF-P010` — battery temperature/off-gas detection, electrical-enclosure smoke detection, and localized mist kit

- Placement zone: battery/traction/HVAC safety loop spanning HV bay, roof equipment, and event-recorder input
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - detector certificate
  - loop continuity
  - mist proof-flow
  - reservoir/pump/pressure diagnostic
  - event-recorder input


## Hold points

- HVIL test
- insulation resistance
- coolant pressure test
- first energisation release

## Source references

- `systems.py`
- `LM3-HV-310`
- `LM3-HV-320`
