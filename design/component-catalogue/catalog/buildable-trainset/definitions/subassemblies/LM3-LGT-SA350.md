# LM3-LGT-SA350 — modular main, emergency, and doorway lighting installation

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | interior pre-fit and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-LGT-P010`
- `LM3-LGT-P020`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-LGT-SA350 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | supplier-certified rail door system |
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
- Inspection methods: child acceptance evidence review, connector key audit, lighting lux map, emergency-feed isolation and duration test, module replacement demonstration, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-LGT-SA350, KIT-LM3-LGT-SA350, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-LGT-P010` — 1.2 m plug-in main LED lighting cassette and captive mounting kit

- Placement zone: common OSR-RAIL-42 interior datum and keyed low-voltage service zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `service-rail-captive-fastener`, `electrical-data`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - rail fire certificate
  - shock/vibration evidence
  - photometric/lux test
  - plug polarity and retention test

### 2. `LM3-LGT-P020` — emergency and doorway lighting modules with independent keyed feeder kit

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `service-rail-captive-fastener`, `electrical-data`
- Torque authority: released OSR small-component standard plus accepted hardware batch and calibrated-tool procedure
- Joint release status: `standard-hardware-release-required`
- Verification:
  - emergency duration/effectiveness evidence
  - evacuation visibility test
  - feed isolation test
  - doorway illumination test


## Hold points

- connector key audit
- lighting lux map
- emergency-feed isolation and duration test
- module replacement demonstration

## Source references

- `small_components.py`
- `cots_equipment.py`
- `LM3-INT-230`
