# LM3-WIN-SA320 — side glazing cassette installation

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 18 |
| Build cell | composite / glazing cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-P110`
- `LM3-WIN-P010`
- `LM3-EXT-P020`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-WIN-SA320 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, replaceable aluminium window-retention and elastomer seal kit, fire-retardant fiberglass composite |
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
- Inspection methods: child acceptance evidence review, aperture gauge, bond/gasket procedure, water ingress test, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-WIN-SA320, KIT-LM3-WIN-SA320, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-P110` — window carrier ring, bonded-gasket land, and replacement jack-point inserts

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - aperture gauge
  - bond-land surface check
  - water-ingress witness
  - replacement tool clearance

### 2. `LM3-WIN-P010` — replaceable window pressure frame, dry seal, drain, and captive retention kit

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`, `fluid/thermal`
- Join classes: `cassette-floating-fastener`, `fluid-thermal`
- Torque authority: released cassette interface drawing and calculation plus supplier installation manual
- Joint release status: `cassette-interface-release-required`
- Verification:
  - pressure-frame gauge
  - retention calculation
  - seal compression record
  - water-ingress and replacement trial

### 3. `LM3-EXT-P020` — side laminated glazing cassette

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - glazing certificate
  - water ingress test
  - replacement method


## Hold points

- aperture gauge
- bond/gasket procedure
- water ingress test

## Source references

- `cots_equipment.py`
- `LM3-WIN-210`
