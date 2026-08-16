# LM3-END-SA700 — train-end cowl, coupler, crash, and sensor assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `assembly` |
| Quantity per trainset | 2 |
| Build cell | composite / final assembly and commissioning cells |
| Procurement BOM lines | `B17`, `B26` |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-P040`
- `LM3-BDY-P090`
- `LM3-CWL-SA710`
- `LM3-EXT-P030`
- `LM3-END-P010`
- `LM3-END-P020`
- `LM3-END-P030`
- `LM3-END-P040`
- `LM3-END-P050`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-END-SA700 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, LM3-CWL-SA710 child assembly material set, fire-retardant fiberglass composite, supplier crash/coupler system, formed sheet metal / stainless local hardware |
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
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable
- Inspection methods: child acceptance evidence review, A/B end interchange, coupler datum survey, sensor calibration, recovery interface check, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-END-SA700, KIT-LM3-END-SA700, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-P040` — coupler pocket, shear plate, and crash-can insert kit

- Placement zone: train-end cowl, crash, coupler, and sensor datum stack
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - coupler face datum
  - bolt-hole survey
  - crash-load drawing check

### 2. `LM3-BDY-P090` — end ring frame and anti-climber beam set

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - A/B interchange check
  - glass carrier land survey
  - anti-climber datum

### 3. `LM3-CWL-SA710` — front/back fiberglass cowl cast kit

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - laminate coupon release
  - insert pull-out
  - trim/drill survey
  - A/B-end dry-build water test

### 4. `LM3-EXT-P030` — single panoramic heated end-glass assembly

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - glass certificate
  - heater test
  - bond/gasket procedure

### 5. `LM3-END-P010` — automatic end coupler and crash-energy absorber

- Placement zone: train-end cowl, crash, coupler, and sensor datum stack
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - EN 15227 absorber evidence
  - recovery procedure
  - bolt torque record

### 6. `LM3-END-P020` — T-OBS nose sensor pack, heated window services, and washer kit

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`, `low-voltage/data`, `fluid/thermal`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - sensor calibration
  - washer/heater test
  - 2oo2 verdict interface test

### 7. `LM3-END-P030` — cowl service hatch, sensor backing bracket, washer-tube, and heater-cable clip kit

- Placement zone: train-end cowl, crash, coupler, and sensor datum stack
- Interfaces: `mechanical datum`, `low-voltage/data`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - hatch water test
  - sensor datum check
  - heater-cable separation
  - washer tube leak test

### 8. `LM3-END-P040` — e-coupler LV jumper, recovery trainline, and end harness breakaway kit

- Placement zone: train-end cowl, crash, coupler, and sensor datum stack
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - pinout test
  - breakaway force check
  - ingress protection
  - rescue compatibility

### 9. `LM3-END-P050` — sealed headlight, tail/marker light, threshold-warning, and end-lamp harness kit

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - photometric certificate
  - function/polarity test
  - ingress protection
  - A/B-end interchange check


## Hold points

- A/B end interchange
- coupler datum survey
- sensor calibration
- recovery interface check

## Source references

- `sensor_cowl.py`
- `systems.py`
- `LM3-SYS-160`
- `LM3-OBS-330`
