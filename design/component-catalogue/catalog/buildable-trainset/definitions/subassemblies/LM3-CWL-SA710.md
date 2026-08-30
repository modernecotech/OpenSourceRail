# LM3-CWL-SA710 — front/back fiberglass cowl cast kit

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 2 |
| Build cell | composite moulding and trim cell |
| Procurement BOM lines | `B8` |
| Maturity | `release-candidate` |

## Children

- `LM3-CWL-P010`
- `LM3-CWL-P011`
- `LM3-CWL-P012`
- `LM3-CWL-P013`
- `LM3-CWL-P014`
- `LM3-CWL-P015`
- `LM3-CWL-P016`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-CWL-SA710 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | fire-retardant fiberglass composite |
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
- Inspection methods: child acceptance evidence review, laminate coupon release, insert pull-out, trim/drill survey, A/B-end dry-build water test, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-CWL-SA710, KIT-LM3-CWL-SA710, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-CWL-P010` — end-cowl fiberglass laminate, insert, adhesive, and coupon material kit

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - material batch trace
  - fire/smoke certificate
  - coupon layup record
  - adhesive shelf-life check

### 2. `LM3-CWL-P011` — CWL-FRP-01 upper brow and roof-cap fiberglass cast

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - mould release record
  - laminate coupon
  - trim-line gauge
  - roof-flange fit

### 3. `LM3-CWL-P012` — CWL-FRP-02 left cheek fiberglass cast

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - mould release record
  - laminate coupon
  - insert pull-out
  - split-gap gauge

### 4. `LM3-CWL-P013` — CWL-FRP-03 right cheek fiberglass cast

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - mould release record
  - laminate coupon
  - insert pull-out
  - split-gap gauge

### 5. `LM3-CWL-P014` — CWL-FRP-04 lower apron and anti-climber cover fiberglass cast

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - mould release record
  - laminate coupon
  - lamp pocket gauge
  - drain-path water test

### 6. `LM3-CWL-P015` — CWL-FRP-05 lamp, washer, and service-hatch fiberglass cast set

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`, `fluid/thermal`
- Join classes: `adhesive-bonded-panel`, `gasketed-removable-panel`, `bolted-structural-datum`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - mould release record
  - insert pull-out
  - gasket compression check
  - hatch removal trial

### 7. `LM3-CWL-P016` — CWL-FRP-06 backing-ring flange fiberglass cast set

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - mould release record
  - glass-carrier land survey
  - bond-line witness
  - A/B interchange check


## Hold points

- laminate coupon release
- insert pull-out
- trim/drill survey
- A/B-end dry-build water test

## Source references

- `end-cowl.md`
- `sensor_cowl.py`
- `LM3-BDY-155`
