# LM3-TTART-SA850 — optional train-to-train open mid-connection articulation

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `assembly` |
| Quantity per trainset | 0 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `buildable-after-supplier-freeze` |

## Children

- `LM3-EIF-SA650`
- `LM3-ART-P040`
- `LM3-ART-P041`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-TTART-SA850 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | LM3-EIF-SA650 child assembly material set, supplier-certified rail door system, rail-rated electrical / control equipment |
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
- Inspection methods: child acceptance evidence review, open-end option configuration record, train-to-train motion-envelope proof, walk-through gangway continuity, water ingress/drain test, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-TTART-SA850, KIT-LM3-TTART-SA850, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-EIF-SA650` — common configurable train-end interface set

- Placement zone: common configurable train-end interface, option bolt grid, seal/drain datums, and selected-end record
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - common bolt-grid survey
  - selected end-option fit gauge
  - seal and drain continuity
  - panoramic-or-open-mid configuration record

### 2. `LM3-ART-P040` — train-to-train open-end articulation, gangway, drawbar, turntable, and service-jumper cassette

- Placement zone: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - train-to-train motion-envelope proof
  - walk-through gangway fire evidence
  - trainline continuity
  - water ingress/drain test

### 3. `LM3-ART-P041` — train-to-train jumper blanking, transition harness, isolation label, and dust-cover kit

- Placement zone: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - pinout test
  - blanking cover ingress check
  - isolation label inspection
  - bend-radius sweep


## Hold points

- open-end option configuration record
- train-to-train motion-envelope proof
- walk-through gangway continuity
- water ingress/drain test

## Source references

- `articulation.md`
- `systems.py`
- `LM3-SYS-175`
