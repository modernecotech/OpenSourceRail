# LM3-ART-SA830 — articulation service-transfer and segregated trainline subassembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 2 |
| Build cell | harness, hose and articulation bench |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-ART-P024`
- `LM3-ART-P030`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA830 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | fire-retardant fiberglass composite, rail-rated electrical / control equipment |
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
- Inspection methods: child acceptance evidence review, HV/LV segregation, continuity/pressure test, bend-radius sweep, drain test, replaceability trial, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-ART-SA830, KIT-LM3-ART-SA830, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-ART-P024` — articulation trainline carrier, support arms, abrasion liners and drain path

- Placement zone: inter-car articulation, gangway, trainline, and flexible-service envelope
- Interfaces: `mechanical datum`, `low-voltage/data`, `fluid/thermal`, `safety interlock`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - rated bend radius
  - dynamic sweep
  - abrasion/fire evidence
  - drain test
  - service replacement trial

### 2. `LM3-ART-P030` — inter-car HV/LV jumper, coolant hose loop, energy chain, and drain sleeve kit

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - bend-radius sweep
  - trainline continuity
  - coolant pressure test
  - water-drain test


## Hold points

- HV/LV segregation
- continuity/pressure test
- bend-radius sweep
- drain test
- replaceability trial

## Source references

- `articulation.md`
- `systems.py`
- `LM3-SYS-170`
