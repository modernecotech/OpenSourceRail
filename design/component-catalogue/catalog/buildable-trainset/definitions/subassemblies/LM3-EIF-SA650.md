# LM3-EIF-SA650 — common configurable train-end interface set

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 2 |
| Build cell | end-interface fixture / final assembly cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-END-P060`
- `LM3-END-P061`
- `LM3-END-P062`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-EIF-SA650 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | common structural end-interface steel and seal datum kit, panoramic end-option interface closeout kit, open mid-connection end-option interface kit |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze
- Inspection methods: child acceptance evidence review, common bolt-grid survey, selected end-option fit gauge, seal and drain continuity, panoramic-or-open-mid configuration record
- Tooling basis: FIX-LM3-EIF-SA650, KIT-LM3-EIF-SA650, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-END-P060` — common reversible end-interface carrier ring, option bolt grid, and sealing datum kit

- Placement zone: common configurable train-end interface, option bolt grid, seal/drain datums, and selected-end record
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - option bolt-grid survey
  - seal datum continuity
  - A/B interchange check
  - end-option fit gauge

### 2. `LM3-END-P061` — panoramic-end option shim, cowl/glass carrier, and sensor datum closeout kit

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - panoramic option fit gauge
  - glass/cowl datum transfer
  - sensor datum check
  - water-ingress pre-test

### 3. `LM3-END-P062` — mid open-connection option portal trim, bellows clamp, threshold bridge, and drain kit

- Placement zone: configurable end-interface, open gangway, train-to-train articulation, and service-jumper envelope
- Interfaces: `mechanical datum`, `fluid/thermal`, `safety interlock`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - open-portal gauge
  - bellows clamp fit
  - threshold/turntable level check
  - drain-path water test


## Hold points

- common bolt-grid survey
- selected end-option fit gauge
- seal and drain continuity
- panoramic-or-open-mid configuration record

## Source references

- `articulation.md`
- `end-cowl.md`
- `interfaces.md`
- `LM3-END-650`
