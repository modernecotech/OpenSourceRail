# LM3-SYS-SA900 — train control, communication, and safety electronics assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `assembly` |
| Quantity per trainset | 1 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-CTRL-P010`
- `LM3-CTRL-P020`
- `LM3-CTRL-P030`
- `LM3-CTRL-P040`
- `LM3-CTRL-P050`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-SYS-SA900 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail-rated electrical / control equipment, supplier-controlled external component, rail structural steel, supplier crash/coupler system |
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
- Inspection methods: child acceptance evidence review, network enumeration, firmware record, self-test, event-recorder write/read test, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-SYS-SA900, KIT-LM3-SYS-SA900, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-CTRL-P010` — T-ECU/S and T-ECU/A compute and safety-control cabinet kit

- Placement zone: LV cabinet, trainline, network, and diagnostic harness zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - hardware BOM check
  - self-test
  - network enumeration
  - firmware record
  - safety-output test

### 2. `LM3-CTRL-P020` — navigation, balise, 5G, LoRa, GNSS, IMU, and roof-antenna kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - SKU/firmware record
  - antenna VSWR
  - GNSS/IMU test
  - balise read
  - radio link test

### 3. `LM3-CTRL-P030` — maintenance HMI, depot pendant, emergency controls, and safety-relay kit

- Placement zone: LV cabinet, trainline, network, and diagnostic harness zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - key/guarded-control test
  - emergency input test
  - 2oo2 relay test
  - stowage and access check

### 4. `LM3-CTRL-P040` — pre-terminated LV trainline harness, DIN cabinet, and terminal-distribution kit

- Placement zone: LV cabinet, trainline, network, and diagnostic harness zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - continuity/hipot
  - pinout check
  - label inspection
  - segregation survey
  - configuration record

### 5. `LM3-CTRL-P050` — operational and crashworthy event-recorder storage kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - write/read test
  - retention configuration
  - crashworthy certificate
  - download/recovery test


## Hold points

- network enumeration
- firmware record
- self-test
- event-recorder write/read test

## Source references

- `systems.py`
- `hardware/rolling-stock-integration.md`
- `LM3-ELC-300`
