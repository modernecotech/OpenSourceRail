# LM3-SHELL-A200 — painted carbody frame with one-metre clip-on fiberglass exterior

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `assembly` |
| Quantity per trainset | 3 |
| Build cell | paint / clip-on body / glazing cells |
| Procurement BOM lines | `B5`, `B6`, `B7`, `B20`, `B28` |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-SA120`
- `LM3-BDY-P130`
- `LM3-BDY-P140`
- `LM3-WIN-SA320`
- `LM3-EXT-P080`
- `LM3-EXT-P090`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-SHELL-A200 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-BDY-SA120 child assembly material set, fire-retardant exterior fiberglass sandwich, stainless retention hardware and elastomer seal kit, LM3-WIN-SA320 child assembly material set, fire-retardant fiberglass composite |
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
- Inspection methods: child acceptance evidence review, corrosion report, clip and anti-lift witness map, eight-hour trainset body route, water ingress pre-test, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-SHELL-A200, KIT-LM3-SHELL-A200, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-SA120` — carbody spaceframe and floor assembly

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - door/window aperture survey
  - roof rail survey
  - carbody dimensional report

### 2. `LM3-BDY-P130` — one-metre clip-on fiberglass side and roof body module

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - material/fire certificate
  - trim gauge
  - insert pull-out
  - master-frame dry fit

### 3. `LM3-BDY-P140` — keyed clip rail, captive retainer, anti-lift, and dry-seal car kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - clip proof load
  - anti-reversal gauge
  - retainer witness-mark check
  - water ingress test

### 4. `LM3-WIN-SA320` — side glazing cassette installation

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - aperture gauge
  - bond/gasket procedure
  - water ingress test

### 5. `LM3-EXT-P080` — fire-rated composite exterior side sandwich-panel kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - EN 45545 evidence
  - panel dimensional report
  - insert pull-out
  - bond coupon and water test

### 6. `LM3-EXT-P090` — fire-rated composite roof fairing and exterior skirt-panel kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - EN 45545 evidence
  - service-removal trial
  - fastener/insert proof
  - water and debris-ingress check


## Hold points

- corrosion report
- clip and anti-lift witness map
- eight-hour trainset body route
- water ingress pre-test

## Source references

- `modular_fiberglass_body.py`
- `sensor_cowl.py`
- `fabrication-plan.md`
