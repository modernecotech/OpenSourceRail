# LM3-ART-SA820 — passenger gangway bellows, bridge and turntable subassembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 2 |
| Build cell | gangway clean assembly cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-ART-P022`
- `LM3-ART-P023`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA820 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier-controlled external component, passenger interior COTS kit |
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
- Inspection methods: child acceptance evidence review, fire-material pack, bridge load test, gap/pinch gauge, water test, full-motion sweep, water/leak test, bond/gasket witness check
- Tooling basis: FIX-LM3-ART-SA820, KIT-LM3-ART-SA820, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-ART-P022` — inter-car double-wall corrugated bellows and clamp-frame set

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - fire/smoke evidence
  - pressure/water ingress test
  - fatigue-cycle evidence
  - replaceable-clamp demonstration

### 2. `LM3-ART-P023` — inter-car passenger bridge, turntable and flexible interior-panel set

- Placement zone: saloon interior, PRM aisle, ceiling, and service-panel zone
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - passenger load proof
  - anti-slip evidence
  - gap/step gauge
  - pinch/shear hazard review
  - full-motion sweep


## Hold points

- fire-material pack
- bridge load test
- gap/pinch gauge
- water test
- full-motion sweep

## Source references

- `articulation.md`
- `LM3-SYS-170`
