# LM3-ART-SA800 — inter-car articulation and trainline assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `assembly` |
| Quantity per trainset | 2 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-ART-P010`
- `LM3-ART-P020`
- `LM3-ART-P030`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ART-SA800 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-controlled external component, rail-rated electrical / control equipment |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, adhesive/bonded/gasketed sealing interfaces, bonding/earthing, segregated harness/fluid routing
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, surface preparation record, adhesive/sealant batch and cure record, LOTO/HV safety rule, EMC/bonding release, software/configuration record where applicable
- Inspection methods: child acceptance evidence review, motion-envelope proof, trainline continuity, water ingress/drain test, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-ART-SA800, KIT-LM3-ART-SA800, calibrated torque/gauge set
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

### 2. `LM3-ART-P020` — gangway, lower spherical pivot, upper links, bellows, turntable, and trainline kit

- Placement zone: inter-car articulation, gangway, trainline, and flexible-service envelope
- Interfaces: `mechanical datum`, `low-voltage/data`, `safety interlock`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - motion-envelope proof
  - fire evidence
  - water ingress/drain test

### 3. `LM3-ART-P030` — inter-car HV/LV jumper, coolant hose loop, energy chain, and drain sleeve kit

- Placement zone: under-seat HV bay, side-pin dock zone, and segregated cable route
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

- motion-envelope proof
- trainline continuity
- water ingress/drain test

## Source references

- `articulation.md`
- `systems.py`
- `LM3-SYS-170`
