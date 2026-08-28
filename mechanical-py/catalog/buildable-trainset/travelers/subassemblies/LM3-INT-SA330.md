# Shop traveler — LM3-INT-SA330 — interior and passenger systems fit-out

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 11.39 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

## Material specification

| Field | Value |
|---|---|
| Material family | assembly material set |
| Grade / part class | LM3-INT-SA330 inherits released child material specifications |
| Governing standard | all child material standards plus assembly-level torque, bonding, coating, and cleanliness controls |
| Form factor | rail-rated electrical / control equipment, supplier HVAC and air-distribution kit, fire-rated cabin fiberglass / phenolic composite |
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


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-INT-SA330-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-INT-SA330-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-INT-SA330-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 0.93 | `TRV-LM3-INT-SA330`<br>`FIX-LM3-INT-SA330`<br>`KIT-LM3-INT-SA330` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-EXT-P060: seats, grab rails, flooring, PIS, CCTV, intercom, and signage kit | final assembly and commissioning cell | 1.35 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P060`<br>`TORQUE-LM3-EXT-P060` | placement zone and joint controls accepted: saloon interior, PRM aisle, ceiling, and service-panel zone | operator |
| 30 | install and integrate LM3-INT-P010: HVAC diffusers, side return ducts, saloon grilles, and access panels | final assembly and commissioning cell | 1.77 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P010`<br>`TORQUE-LM3-INT-P010` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 40 | install and integrate LM3-INT-P020: FRP/phenolic ceiling liner, light trough, and HVAC plenum cover set | final assembly and commissioning cell | 1.77 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P020`<br>`TORQUE-LM3-INT-P020` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 50 | install and integrate LM3-INT-P030: FRP/phenolic sidewall liner, window reveal, and cable-cover panel set | final assembly and commissioning cell | 1.17 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P030`<br>`TORQUE-LM3-INT-P030` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 60 | install and integrate LM3-INT-P040: FRP battery strake covers, seat-base fairings, and service-hatch shells | final assembly and commissioning cell | 1.47 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P040`<br>`TORQUE-LM3-INT-P040` | placement zone and joint controls accepted: under-seat HV bay, side-pin dock zone, and segregated cable route | operator |
| 70 | install and integrate LM3-INT-P050: FRP vestibule kick panels, PRM ramp/step covers, and door-pocket trims | final assembly and commissioning cell | 1.23 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P050`<br>`TORQUE-LM3-INT-P050` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 80 | hold point: egress check | quality inspection | 0.35 | `QA-LM3-INT-SA330` | egress check | quality inspector |
| 90 | hold point: fire-material pack | quality inspection | 0.35 | `QA-LM3-INT-SA330` | fire-material pack | quality inspector |
| 100 | hold point: liner/trim fit survey | quality inspection | 0.35 | `GAUGE-LM3-INT-SA330` | liner/trim fit survey | quality inspector |
| 110 | hold point: lighting/PIS/CCTV static test | quality inspection | 0.35 | `QA-LM3-INT-SA330` | lighting/PIS/CCTV static test | quality inspector |
| 120 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-INT-SA330`<br>`NCR-LM3-INT-SA330` | all operation and QA signoffs are complete | manufacturing engineer |

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
