# LM3-BDY-SA120 — carbody spaceframe and floor assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | weld and fixture cell |
| Procurement BOM lines | `B3`, `B4` |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-SA110`
- `LM3-BDY-P060`
- `LM3-BDY-P070`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BDY-SA120 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-BDY-SA110 child assembly material set, rail structural steel |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, fixture tack/weld, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, WPS-controlled structural welding, adhesive/bonded/gasketed sealing interfaces
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, weld map release, WPS/WPQR and welder qualification, surface preparation record, adhesive/sealant batch and cure record
- Inspection methods: child acceptance evidence review, door/window aperture survey, roof rail survey, carbody dimensional report, VT, MT/UT where classed, post-weld datum survey, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-BDY-SA120, KIT-LM3-BDY-SA120, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-SA110` — underframe datum weldment

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - material release
  - fixture tack survey
  - weld/NDT release
  - post-weld datum survey

### 2. `LM3-BDY-P060` — low-floor centre pan and raised bogie-end deck set

- Placement zone: bogie frame, axle, brake, suspension, and underframe marriage datums
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - PRM floor height
  - egress aisle gauge
  - deck weld inspection

### 3. `LM3-BDY-P070` — side-wall post, door portal, waist rail, and cant rail kit

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - door cassette gauge
  - window cassette gauge
  - side-frame survey


## Hold points

- door/window aperture survey
- roof rail survey
- carbody dimensional report

## Source references

- `car_body.py`
- `LM3-BDY-100`
