# LM3-CAR-A900 — complete repeated car module

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `assembly` |
| Quantity per trainset | 3 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-SHELL-A200`
- `LM3-DOOR-SA310`
- `LM3-INT-SA330`
- `LM3-FIX-SA340`
- `LM3-LGT-SA350`
- `LM3-ROOF-SA410`
- `LM3-HV-SA510`
- `LM3-BOG-SA610`
- `LM3-BOG-SA620`
- `LM3-AUX-P010`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-CAR-A900 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-SHELL-A200 child assembly material set, LM3-DOOR-SA310 child assembly material set, LM3-INT-SA330 child assembly material set, LM3-FIX-SA340 child assembly material set, LM3-LGT-SA350 child assembly material set, LM3-ROOF-SA410 child assembly material set, LM3-HV-SA510 child assembly material set, LM3-BOG-SA610 child assembly material set, LM3-BOG-SA620 child assembly material set, supplier-certified running gear |
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
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, car weigh, door/HVAC/static systems test, bogie marriage report, low-speed yard movement, continuity, insulation/isolation, functional static test, alignment survey, static brake test
- Tooling basis: FIX-LM3-CAR-A900, KIT-LM3-CAR-A900, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-SHELL-A200` — painted carbody frame with one-metre clip-on fiberglass exterior

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - corrosion report
  - clip and anti-lift witness map
  - eight-hour trainset body route
  - water ingress pre-test

### 2. `LM3-DOOR-SA310` — door cassette and threshold assembly

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - door gauge fit
  - obstruction test
  - closed-and-locked test

### 3. `LM3-INT-SA330` — interior and passenger systems fit-out

- Placement zone: saloon interior, PRM aisle, ceiling, and service-panel zone
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - egress check
  - fire-material pack
  - liner/trim fit survey
  - lighting/PIS/CCTV static test

### 4. `LM3-FIX-SA340` — common service-rail, captive-fastener, and fixture-adapter installation

- Placement zone: common OSR-RAIL-42 interior datum and keyed low-voltage service zone
- Interfaces: `mechanical datum`
- Join classes: `service-rail-captive-fastener`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - rail datum survey
  - fastener-family audit
  - fixture load-evidence check
  - service/removal demonstration

### 5. `LM3-LGT-SA350` — modular main, emergency, and doorway lighting installation

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `service-rail-captive-fastener`, `electrical-data`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - connector key audit
  - lighting lux map
  - emergency-feed isolation and duration test
  - module replacement demonstration

### 6. `LM3-ROOF-SA410` — roof HVAC, PV, antenna, and service-equipment assembly

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `low-voltage/data`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - roof leak test
  - HVAC drain test
  - PV isolation/bonding check

### 7. `LM3-HV-SA510` — per-car LFP battery, two controllers, DC auxiliary/charge interface, mist, and cooling assembly

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`, `low-voltage/data`, `fluid/thermal`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - HVIL test
  - insulation resistance
  - coolant pressure test
  - first energisation release

### 8. `LM3-BOG-SA610` — complete powered bogie with running unit, bogie-mounted drive and body connection

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - frame NDT
  - wheelset/bearing certificate
  - motor/gearbox alignment
  - static brake test

### 9. `LM3-BOG-SA620` — complete trailer bogie with running unit and body connection

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - frame NDT
  - wheelset/bearing certificate
  - ride-height setup
  - static brake test

### 10. `LM3-AUX-P010` — secondary-suspension compressor, dryer, reservoir, and isolation-manifold kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - pressure certificate
  - leak test
  - dryer function
  - relief-valve test
  - service-access check


## Hold points

- car weigh
- door/HVAC/static systems test
- bogie marriage report
- low-speed yard movement

## Source references

- `trainset.py`
- `freecad_trainset.py`
- `fabrication-plan.md`
