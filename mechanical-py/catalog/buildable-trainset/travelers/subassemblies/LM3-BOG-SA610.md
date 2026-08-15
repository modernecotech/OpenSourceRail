# Shop traveler — LM3-BOG-SA610 — powered bogie assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 12.29 h |
| Build cell | bogie weld and assembly cell |
| Procurement BOM lines | `B4`, `G21` |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-BOG-SA610 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail structural steel, supplier-certified running gear, supplier traction drive equipment, supplier HVAC and air-distribution kit |
| Nominal section | as defined by child drawings and assembly interface control drawing |
| Finish / protection | protect damaged coating, exposed edges, seals, bonds, and labels during assembly |
| Traceability | child serial/heat/batch records plus assembly traveler traceability |

Evidence required:

- child material certificates accepted
- assembly traveler traceability
- interface-control drawing revision

## Process specification

- Primary processes: release child kit, fixture or datum setup, fixture tack/weld, install children, torque/fit-up record, release to parent
- Joining methods: bolted/torqued interfaces, shimmed datum interfaces as required, WPS-controlled structural welding
- Special process controls: child definition/revision check, tooling calibration check, parent interface freeze, weld map release, WPS/WPQR and welder qualification, wheelset/bearing certificate review, ride-height setup
- Inspection methods: child acceptance evidence review, frame NDT, wheelset/bearing certificate, motor/gearbox alignment, static brake test, VT, MT/UT where classed, post-weld datum survey, alignment survey
- Tooling basis: FIX-LM3-BOG-SA610, KIT-LM3-BOG-SA610, calibrated torque/gauge set
- Release level: assembly traveler controlled; generated template is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-BOG-SA610-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-BOG-SA610-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-BOG-SA610-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | bogie weld and assembly cell | 1.01 | `TRV-LM3-BOG-SA610`<br>`FIX-LM3-BOG-SA610`<br>`KIT-LM3-BOG-SA610` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BOG-P010: powered bogie welded H-frame and motor-cradle weldment | bogie weld and assembly cell | 1.42 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-BOG-P010`<br>`TORQUE-LM3-BOG-P010` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 30 | install and integrate LM3-BOG-P030: powered-bogie guards, cable guides, WSP brackets, and inspection covers | bogie weld and assembly cell | 1.3 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-BOG-P030`<br>`TORQUE-LM3-BOG-P030` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 40 | install and integrate LM3-BOG-P040: powered-bogie certified wheelset, axlebox, suspension, brake, centre-pivot, yaw-link, and sensor kit | bogie weld and assembly cell | 1.63 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-BOG-P040`<br>`TORQUE-LM3-BOG-P040` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 50 | install and integrate LM3-BOG-P050: powered-bogie motor torque link, anti-rotation stop, and safety lanyard bracket kit | bogie weld and assembly cell | 1.35 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-BOG-P050`<br>`TORQUE-LM3-BOG-P050` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 60 | install and integrate LM3-BOG-P060: powered-bogie brake/WSP/speed-sensor harness and junction-bracket kit | bogie weld and assembly cell | 1.53 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-BOG-P060`<br>`TORQUE-LM3-BOG-P060` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 70 | install and integrate LM3-TRC-P010: motor-350kw-hm47-class axle traction motor | bogie weld and assembly cell | 1.35 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-TRC-P010`<br>`TORQUE-LM3-TRC-P010` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 80 | install and integrate LM3-TRC-P020: single-stage reduction gearbox and flexible coupling | bogie weld and assembly cell | 1.0 | `FIX-LM3-BOG-SA610`<br>`GAUGE-LM3-TRC-P020`<br>`TORQUE-LM3-TRC-P020` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 90 | hold point: frame NDT | quality inspection | 0.35 | `NDT-LM3-BOG-SA610` | frame NDT | quality inspector |
| 100 | hold point: wheelset/bearing certificate | quality inspection | 0.35 | `QA-LM3-BOG-SA610` | wheelset/bearing certificate | quality inspector |
| 110 | hold point: motor/gearbox alignment | quality inspection | 0.35 | `QA-LM3-BOG-SA610` | motor/gearbox alignment | quality inspector |
| 120 | hold point: static brake test | quality inspection | 0.35 | `QA-LM3-BOG-SA610` | static brake test | quality inspector |
| 130 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-BOG-SA610`<br>`NCR-LM3-BOG-SA610` | all operation and QA signoffs are complete | manufacturing engineer |

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
