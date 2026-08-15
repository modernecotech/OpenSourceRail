# LM3-TRAINSET-A000 — complete light-metro trainset

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `trainset` |
| Quantity per trainset | 1 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-CAR-A900`
- `LM3-END-SA700`
- `LM3-ART-SA800`
- `LM3-SYS-SA900`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-TRAINSET-A000 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-CAR-A900 child assembly material set, LM3-END-SA700 child assembly material set, LM3-ART-SA800 child assembly material set, LM3-SYS-SA900 child assembly material set |
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
- Inspection methods: child acceptance evidence review, trainset weigh, static brake/door/HVAC/HV tests, FEM screening accepted, dynamic-test release, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-TRAINSET-A000, KIT-LM3-TRAINSET-A000, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-CAR-A900` — complete repeated car module

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - car weigh
  - door/HVAC/static systems test
  - bogie marriage report
  - low-speed yard movement

### 2. `LM3-END-SA700` — train-end cowl, coupler, crash, and sensor assembly

- Placement zone: train-end cowl, crash, coupler, and sensor datum stack
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - A/B end interchange
  - coupler datum survey
  - sensor calibration
  - recovery interface check

### 3. `LM3-ART-SA800` — inter-car articulation and trainline assembly

- Placement zone: inter-car articulation, gangway, trainline, and flexible-service envelope
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - motion-envelope proof
  - trainline continuity
  - water ingress/drain test

### 4. `LM3-SYS-SA900` — train control, communication, and safety electronics assembly

- Placement zone: LV cabinet, trainline, network, and diagnostic harness zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - network enumeration
  - firmware record
  - self-test
  - event-recorder write/read test


## Hold points

- trainset weigh
- static brake/door/HVAC/HV tests
- FEM screening accepted
- dynamic-test release

## Source references

- `trainset.py`
- `freecad_assembly_review.py`
- `freecad_fea.py`
- `drawing-register.md`
