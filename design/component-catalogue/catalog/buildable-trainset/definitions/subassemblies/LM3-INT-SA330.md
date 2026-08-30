# LM3-INT-SA330 — interior and passenger systems fit-out

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |
| Maturity | `release-candidate` |

## Children

- `LM3-EXT-P060`
- `LM3-EXT-P061`
- `LM3-EXT-P062`
- `LM3-EXT-P063`
- `LM3-EXT-P064`
- `LM3-EXT-P065`
- `LM3-EXT-P066`
- `LM3-INT-P010`
- `LM3-INT-P020`
- `LM3-INT-P030`
- `LM3-INT-P040`
- `LM3-INT-P050`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-INT-SA330 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | fire-rated structural floor-board and hatch system, rail fire-rated resilient floor-covering system, rail passenger-seat module and calculated mounting kit, modular passenger handrail and stanchion system, rail-rated passenger-information/audio equipment kit, rail-rated CCTV/passenger-intercom equipment kit, controlled PRM and emergency-equipment location kit, supplier HVAC and air-distribution kit, fire-rated cabin fiberglass / phenolic composite |
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
- Inspection methods: child acceptance evidence review, egress check, fire-material pack, liner/trim fit survey, lighting/PIS/CCTV static test, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-INT-SA330, KIT-LM3-INT-SA330, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-EXT-P060` — stepped floor-board and removable service-hatch system

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - fire certificate
  - panel load and deflection evidence
  - hatch removal trial
  - level/step and egress survey

### 2. `LM3-EXT-P061` — welded resilient floor covering, cove, nosing, and adhesive system

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - fire/smoke certificate
  - adhesive compatibility and cure record
  - welded-seam peel sample
  - slip and cleanability evidence

### 3. `LM3-EXT-P062` — longitudinal passenger and priority-seat modules

- Placement zone: saloon interior, PRM aisle, ceiling, and service-panel zone
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - fire/smoke certificate
  - seat/occupant load evidence
  - fastener and anti-rotation record
  - egress and cleaning-clearance gauge

### 4. `LM3-EXT-P063` — stainless grab-pole, handrail, joint, and insulated adapter kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - material/finish certificate
  - joint locking record
  - fixture-specific proof-load evidence
  - reach, egress and snag survey

### 5. `LM3-EXT-P064` — passenger-information display, speaker, amplifier, and mounting kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - fire/EMC evidence
  - network enumeration
  - audio/intelligibility test
  - display visibility and service-removal trial

### 6. `LM3-EXT-P065` — CCTV camera, passenger intercom, PoE/data, and mounting kit

- Placement zone: primary structure datum and final assembly interface
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - fire/EMC/IP evidence
  - network enumeration
  - camera coverage/privacy review
  - intercom call and service-removal trial

### 7. `LM3-EXT-P066` — PRM, safety-signage, emergency-lighting, extinguisher, and first-aid kit

- Placement zone: common OSR-RAIL-42 interior datum and keyed low-voltage service zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - accessible reach/contrast review
  - emergency-light duration test
  - equipment certificate/expiry audit
  - location and egress survey

### 8. `LM3-INT-P010` — HVAC diffusers, side return ducts, saloon grilles, and access panels

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - airflow balance
  - rattle check
  - access-panel removal
  - fire-material certificate

### 9. `LM3-INT-P020` — FRP/phenolic ceiling liner, light trough, and HVAC plenum cover set

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - fire-material certificate
  - trim-line gauge
  - fastener insert pull-out
  - rattle check

### 10. `LM3-INT-P030` — FRP/phenolic sidewall liner, window reveal, and cable-cover panel set

- Placement zone: side/end glazing aperture and bonded carrier datum
- Interfaces: `mechanical datum`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - fire-material certificate
  - window-reveal gauge
  - access-panel removal
  - edge-radius inspection

### 11. `LM3-INT-P040` — FRP battery strake covers, seat-base fairings, and service-hatch shells

- Placement zone: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - fire-material certificate
  - no-saloon-opening inspection
  - HV warning label check
  - sharp-edge inspection

### 12. `LM3-INT-P050` — FRP vestibule kick panels, PRM ramp/step covers, and door-pocket trims

- Placement zone: side door aperture and low-floor threshold datum
- Interfaces: `mechanical datum`, `safety interlock`
- Join classes: `bolted-structural-datum`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - fire-material certificate
  - PRM transition gauge
  - anti-slip witness
  - kick-panel retention test


## Hold points

- egress check
- fire-material pack
- liner/trim fit survey
- lighting/PIS/CCTV static test

## Source references

- `cots_equipment.py`
- `cabin-fiberglass.md`
- `LM3-INT-230`
- `LM3-INT-240`
