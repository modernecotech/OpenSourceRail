# LM3-BDY-SA110 — underframe datum weldment

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | weld and fixture cell |
| Procurement BOM lines | `B3`, `B4`, `B26` |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-P010`
- `LM3-BDY-P020`
- `LM3-BDY-P030`
- `LM3-BDY-P120`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BDY-SA110 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel |
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
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, weld map release, WPS/WPQR and welder qualification
- Inspection methods: child acceptance evidence review, material release, fixture tack survey, weld/NDT release, post-weld datum survey, VT, MT/UT where classed
- Tooling basis: FIX-LM3-BDY-SA110, KIT-LM3-BDY-SA110, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-P010` — laser-cut side sill beam, LH/RH

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - heat traceability
  - dimensional check
  - weld VT/MT where classed

### 2. `LM3-BDY-P020` — underframe centre spine and cross-bearer kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - tube/plate certs
  - fixture survey
  - bogie-centre datum report

### 3. `LM3-BDY-P030` — bolster box, air-spring pad, and centre-pivot insert set

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - line-bore report
  - air-spring datum survey
  - NDT report

### 4. `LM3-BDY-P120` — jacking pad, lifting eye, towing lug, and recovery-label kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - material traceability
  - weld/NDT record
  - proof load
  - four-point depot interface gauge
  - datum and label inspection


## Hold points

- material release
- fixture tack survey
- weld/NDT release
- post-weld datum survey

## Source references

- `fabrication-plan.md`
- `LM3-BDY-110`
