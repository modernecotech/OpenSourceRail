# LM3-DOOR-SA310 — door cassette and threshold assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 12 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-P100`
- `LM3-EXT-P010`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-DOOR-SA310 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-certified rail door system |
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
- Inspection methods: child acceptance evidence review, door gauge fit, obstruction test, closed-and-locked test, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-DOOR-SA310, KIT-LM3-DOOR-SA310, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-P100` — door portal reinforcement, threshold beam, and cassette shim kit

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `structural-weld`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - door aperture gauge
  - threshold height survey
  - cassette shim record
  - water-drain path check

### 2. `LM3-EXT-P010` — electric plug/sliding door cassette

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - EN 14752 evidence
  - obstruction test
  - closed-and-locked loop test


## Hold points

- door gauge fit
- obstruction test
- closed-and-locked test

## Source references

- `systems.py`
- `LM3-DOOR-200`
