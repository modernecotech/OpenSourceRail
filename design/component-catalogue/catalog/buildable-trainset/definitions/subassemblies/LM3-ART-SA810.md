# LM3-ART-SA810 — structural articulation joint and anti-lift load path

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 2 |
| Build cell | articulation bench and proof-load cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-ART-P010`
- `LM3-ART-P020`
- `LM3-ART-P021`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA810 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-certified running gear, supplier-controlled external component |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, adhesive/bonded/gasketed sealing interfaces
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record
- Inspection methods: child acceptance evidence review, pin/bearing identity, shimmed datum survey, proof load, lubrication/seal release, motion sweep, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-ART-SA810, KIT-LM3-ART-SA810, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-ART-P010` — articulation adapter frame, anti-lift keeper, and shim kit

- Placement zone: inter-car articulation, gangway, trainline, and flexible-service envelope
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - motion envelope
  - bearing proof
  - shim pack record

### 2. `LM3-ART-P020` — articulation lower spherical pivot, bearing housing and pin set

- Placement zone: inter-car articulation, gangway, trainline, and flexible-service envelope
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - bearing static/dynamic capacity
  - pin material/NDT
  - proof load
  - lubrication/sealing plan
  - motion-envelope proof

### 3. `LM3-ART-P021` — articulation upper lateral/yaw links, spherical joints and retained pins

- Placement zone: inter-car articulation, gangway, trainline, and flexible-service envelope
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - link buckling/fatigue proof
  - joint angular capacity
  - pin retention inspection
  - full-motion sweep


## Hold points

- pin/bearing identity
- shimmed datum survey
- proof load
- lubrication/seal release
- motion sweep

## Source references

- `articulation.md`
- `systems.py`
- `LM3-SYS-170`
