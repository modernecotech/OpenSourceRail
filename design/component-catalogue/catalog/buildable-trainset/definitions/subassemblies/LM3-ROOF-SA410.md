# LM3-ROOF-SA410 — roof HVAC, PV, antenna, and service-equipment assembly

| Field | Value |
|---|---|
| Definition type | Assembly node |
| Layer | `subassembly` |
| Quantity per trainset | 3 |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | `B7` |
| Maturity | `release-candidate` |

## Children

- `LM3-BDY-P080`
- `LM3-ROOF-P010`
- `LM3-ROOF-P020`
- `LM3-ROOF-P030`
- `LM3-ROOF-P040`
- `LM3-EXT-P040`
- `LM3-EXT-P050`
- `LM3-EXT-P070`
- `LM3-FIN-P020`
- `LM3-TRC-P050`

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-ROOF-SA410 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | formed sheet metal / stainless local hardware, rail structural steel, supplier HVAC and air-distribution kit, roof electrical energy equipment, rail laminated safety glazing |
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
- Inspection methods: child acceptance evidence review, roof leak test, HVAC drain test, PV isolation/bonding check, water/leak test, bond/gasket witness check, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-ROOF-SA410, KIT-LM3-ROOF-SA410, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Integration design

### 1. `LM3-BDY-P080` — roof bow, HVAC rail, PV rail, and cable-tray bracket kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `structural-weld`, `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - roof rail pitch
  - HVAC curb gauge
  - PV clamp pull test

### 2. `LM3-ROOF-P010` — HVAC curb, drop-duct collar, condensate tray, and drain fitting kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - curb flatness
  - drop-duct gauge
  - condensate drain flow test
  - roof leak test

### 3. `LM3-ROOF-P020` — PV bonded-pad lands, raised rail kit, bonding jumpers, and roof isolation labels

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `adhesive-bonded-panel`, `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - rail pitch survey
  - bond pull coupon
  - earth continuity
  - module keep-out gauge

### 4. `LM3-ROOF-P030` — removable HVAC curb fairing, intake/exhaust skirt, and access-hatch moulding set

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - fairing trim gauge
  - HVAC airflow keep-out
  - hatch removal trial
  - roof leak test

### 5. `LM3-ROOF-P040` — PV junction plinth, cable-gland cover, antenna closeout, and walkway edge set

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: released joint calculation plus interface-control drawing and calibrated-tool procedure
- Joint release status: `joint-calculation-required`
- Verification:
  - gland/closeout trim gauge
  - drain-path test
  - bonding access check
  - service-removal trial

### 6. `LM3-EXT-P040` — hvac-24kw-direct-hv-dc roof HVAC

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `gasketed-removable-panel`, `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - +50 C capacity evidence
  - condensate drain test
  - EMC/vibration evidence

### 7. `LM3-EXT-P050` — roof PV module and edge-clamp kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - module datasheet
  - clamp pull test
  - isolation/bonding check

### 8. `LM3-EXT-P070` — roof antennas, service walkway pads, lifting covers, and maintenance labels

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `low-voltage/data`
- Join classes: `bolted-structural-datum`, `electrical-data`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - antenna VSWR test
  - walkway slip certificate
  - lifting-cover fit
  - roof bonding check

### 9. `LM3-FIN-P020` — calcium-carbonate radiative roof-coating qualification and exposed-roof application kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`
- Join classes: `bolted-structural-datum`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - rail fire/chemical evidence
  - GFRP adhesion and flexibility
  - UV/abrasion/wash ageing
  - initial and aged solar reflectance/emittance
  - one-car thermal/maintenance trial

### 10. `LM3-TRC-P050` — roof-mounted regen dump resistor and thermal shield kit

- Placement zone: roof equipment rail, curb, and service-access zone
- Interfaces: `mechanical datum`, `high-voltage electrical`, `fluid/thermal`
- Join classes: `bolted-structural-datum`, `electrical-data`, `fluid-thermal`
- Torque authority: accepted supplier installation manual plus released OSR interface-control drawing
- Joint release status: `supplier-freeze-required`
- Verification:
  - resistance certificate
  - thermal clearance
  - roof bonding
  - hot-surface label


## Hold points

- roof leak test
- HVAC drain test
- PV isolation/bonding check

## Source references

- `systems.py`
- `LM3-HVAC-220`
- `LM3-HV-325`
