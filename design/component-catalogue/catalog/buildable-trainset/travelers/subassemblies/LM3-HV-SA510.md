# Shop traveler — LM3-HV-SA510 — per-car LFP battery, two controllers, DC auxiliary/charge interface, mist, and cooling assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 16.41 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-HV-SA510 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | formed sheet metal / stainless local hardware, roof electrical energy equipment, supplier high-voltage traction equipment, supplier HVAC and air-distribution kit |
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
- Inspection methods: child acceptance evidence review, HVIL test, insulation resistance, coolant pressure test, first energisation release, continuity, insulation/isolation, functional static test
- Tooling basis: FIX-LM3-HV-SA510, KIT-LM3-HV-SA510, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-HV-SA510-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-HV-SA510-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-HV-SA510-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 1.17 | `TRV-LM3-HV-SA510`<br>`FIX-LM3-HV-SA510`<br>`KIT-LM3-HV-SA510` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-P050: battery tray rails, vent plenum, and service-lid gutter kit | final assembly and commissioning cell | 1.3 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-BDY-P050`<br>`TORQUE-LM3-BDY-P050` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 30 | install and integrate LM3-HV-P010: battery sliding trays, retention straps, service interlocks, and drain pans | final assembly and commissioning cell | 1.65 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-HV-P010`<br>`TORQUE-LM3-HV-P010` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 40 | install and integrate LM3-HV-P020: segregated HV cable tray, bonding studs, grommets, and orange cover set | final assembly and commissioning cell | 1.35 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-HV-P020`<br>`TORQUE-LM3-HV-P020` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 50 | install and integrate LM3-HV-P030: coolant manifold brackets, bleed/drain points, and insulated pipe clamp kit | final assembly and commissioning cell | 1.65 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-HV-P030`<br>`TORQUE-LM3-HV-P030` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 60 | install and integrate LM3-TRC-P030: two independent motor controllers, isolated LV DC/DC, MPPT, station protection, and cooling-loop kit | final assembly and commissioning cell | 1.48 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-TRC-P030`<br>`TORQUE-LM3-TRC-P030` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 70 | install and integrate LM3-TRC-P040: battery-225kwh-lfp-800v saloon-isolated side traction battery pack | final assembly and commissioning cell | 1.35 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-TRC-P040`<br>`TORQUE-LM3-TRC-P040` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 80 | install and integrate LM3-TRC-P060: station side-pin charging connector, actuator, shutter, and alignment target | final assembly and commissioning cell | 1.53 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-TRC-P060`<br>`TORQUE-LM3-TRC-P060` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 90 | install and integrate LM3-TRC-P070: HV contactor, fuse, pre-charge, service-disconnect, and current-sensor panel | final assembly and commissioning cell | 1.53 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-TRC-P070`<br>`TORQUE-LM3-TRC-P070` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 100 | install and integrate LM3-SAF-P010: battery temperature/off-gas detection, electrical-enclosure smoke detection, and localized mist kit | final assembly and commissioning cell | 1.7 | `FIX-LM3-HV-SA510`<br>`GAUGE-LM3-SAF-P010`<br>`TORQUE-LM3-SAF-P010` | placement zone and joint controls accepted: battery/traction/HVAC safety loop spanning HV bay, roof equipment, and event-recorder input | operator |
| 110 | hold point: HVIL test | quality inspection | 0.35 | `ELEC-TEST-LM3-HV-SA510` | HVIL test | quality inspector |
| 120 | hold point: insulation resistance | quality inspection | 0.35 | `QA-LM3-HV-SA510` | insulation resistance | quality inspector |
| 130 | hold point: coolant pressure test | quality inspection | 0.35 | `LEAK-TEST-LM3-HV-SA510` | coolant pressure test | quality inspector |
| 140 | hold point: first energisation release | quality inspection | 0.35 | `QA-LM3-HV-SA510` | first energisation release | quality inspector |
| 150 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-HV-SA510`<br>`NCR-LM3-HV-SA510` | all operation and QA signoffs are complete | manufacturing engineer |

## Operator / inspection signoff block

| Role | Name | Date | Signature | Status |
|---|---|---|---|---|
| operator |  |  |  | `blank` |
| cell lead |  |  |  | `blank` |
| quality inspector |  |  |  | `blank` |
| manufacturing engineer |  |  |  | `blank` |

## Nonconformance / deviation log

| NCR / deviation ID | Operation seq | Disposition | Approver | Closure date |
|---|---:|---|---|---|
|  |  |  |  |  |
