# LM3-FULLSET-A300 — three LM3 train modules joined as one walk-through full set

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `trainset` |
| Quantity per trainset | 1 |
| Build cell | long final assembly track / depot commissioning road |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-TRAINSET-A000`
- `LM3-TTART-SA850`
- `LM3-SYS-SA900`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-FULLSET-A300 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-TRAINSET-A000 child assembly material set, LM3-TTART-SA850 child assembly material set, LM3-SYS-SA900 child assembly material set |
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
- Inspection methods: child acceptance evidence review, three-train alignment and end-option configuration record, two train-to-train open gangway joint motion sweeps, full-set trainline continuity and safety-loop proof, long-consist FEM screening accepted, static and dynamic release for full-set operation, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-FULLSET-A300, KIT-LM3-FULLSET-A300, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-TRAINSET-A000` — complete light-metro trainset

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - trainset weigh
  - static brake/door/HVAC/HV tests
  - FEM screening accepted
  - dynamic-test release

### 2. `LM3-TTART-SA850` — optional train-to-train open mid-connection articulation

- Placement zone: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - open-end option configuration record
  - train-to-train motion-envelope proof
  - walk-through gangway continuity
  - water ingress/drain test

### 3. `LM3-SYS-SA900` — train control, communication, and safety electronics assembly

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

- three-train alignment and end-option configuration record
- two train-to-train open gangway joint motion sweeps
- full-set trainline continuity and safety-loop proof
- long-consist FEM screening accepted
- static and dynamic release for full-set operation

## Source references

- `train-end-interface.md`
- `full-set-3train-assembly.md`
- `freecad_trainset.py`
- `freecad_fea.py`
- `LM3-SYS-175`
