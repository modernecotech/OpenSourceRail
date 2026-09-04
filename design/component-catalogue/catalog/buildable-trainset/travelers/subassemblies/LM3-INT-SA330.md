# Shop traveler — LM3-INT-SA330 — interior and passenger systems fit-out

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 26.5 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | None directly assigned |

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


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-INT-SA330-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-INT-SA330-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-INT-SA330-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 1.97 | `TRV-LM3-INT-SA330`<br>`FIX-LM3-INT-SA330`<br>`KIT-LM3-INT-SA330` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-EXT-P060: stepped floor-board and removable service-hatch system | final assembly and commissioning cell | 1.17 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P060`<br>`TORQUE-LM3-EXT-P060` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 30 | install and integrate LM3-EXT-P061: welded resilient floor covering, cove, nosing, and adhesive system | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P061`<br>`TORQUE-LM3-EXT-P061` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 40 | install and integrate LM3-EXT-P062: longitudinal passenger and priority-seat modules | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P062`<br>`TORQUE-LM3-EXT-P062` | placement zone and joint controls accepted: saloon interior, PRM aisle, ceiling, and service-panel zone | operator |
| 50 | install and integrate LM3-EXT-P063: stainless grab-pole, handrail, joint, and insulated adapter kit | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P063`<br>`TORQUE-LM3-EXT-P063` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 60 | install and integrate LM3-EXT-P064: passenger-information display, speaker, amplifier, and mounting kit | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P064`<br>`TORQUE-LM3-EXT-P064` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 70 | install and integrate LM3-EXT-P065: CCTV camera, passenger intercom, PoE/data, and mounting kit | final assembly and commissioning cell | 1.35 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P065`<br>`TORQUE-LM3-EXT-P065` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 80 | install and integrate LM3-EXT-P066: PRM, safety-signage, emergency-lighting, extinguisher, and first-aid kit | final assembly and commissioning cell | 1.35 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-EXT-P066`<br>`TORQUE-LM3-EXT-P066` | placement zone and joint controls accepted: common OSR-RAIL-42 interior datum and keyed low-voltage service zone | operator |
| 90 | install and integrate LM3-INT-P010: HVAC diffusers, side return ducts, saloon grilles, and access panels | final assembly and commissioning cell | 1.77 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P010`<br>`TORQUE-LM3-INT-P010` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 100 | install and integrate LM3-INT-P020: FRP/phenolic ceiling liner panel set | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P020`<br>`TORQUE-LM3-INT-P020` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 110 | install and integrate LM3-INT-P021: ceiling light-trough bezel, diffuser carrier, and emergency-luminaire closeout set | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P021`<br>`TORQUE-LM3-INT-P021` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 120 | install and integrate LM3-INT-P022: HVAC plenum cover, diffuser transition, detector bezel, and ceiling service-hatch set | final assembly and commissioning cell | 1.77 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P022`<br>`TORQUE-LM3-INT-P022` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 130 | install and integrate LM3-INT-P030: FRP/phenolic sidewall liner panel set | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P030`<br>`TORQUE-LM3-INT-P030` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 140 | install and integrate LM3-INT-P031: window reveal, setting-block inspection cover, and blind/label land set | final assembly and commissioning cell | 1.17 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P031`<br>`TORQUE-LM3-INT-P031` | placement zone and joint controls accepted: side/end glazing aperture and bonded carrier datum | operator |
| 150 | install and integrate LM3-INT-P032: waist cable-cover, low-voltage access lid, and retained quarter-turn fastener set | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P032`<br>`TORQUE-LM3-INT-P032` | placement zone and joint controls accepted: primary structure datum and final assembly interface | operator |
| 160 | install and integrate LM3-INT-P040: FRP battery strake cover panel set | final assembly and commissioning cell | 1.35 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P040`<br>`TORQUE-LM3-INT-P040` | placement zone and joint controls accepted: exterior-access side HV bay beneath seat zone, side-pin dock zone, outward vent, and segregated cable route | operator |
| 170 | install and integrate LM3-INT-P041: seat-base fairing, retained equipment hatch, and rail-saddle closeout set | final assembly and commissioning cell | 1.17 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P041`<br>`TORQUE-LM3-INT-P041` | placement zone and joint controls accepted: saloon interior, PRM aisle, ceiling, and service-panel zone | operator |
| 180 | install and integrate LM3-INT-P050: FRP vestibule kick-panel and threshold-closeout set | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P050`<br>`TORQUE-LM3-INT-P050` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 190 | install and integrate LM3-INT-P051: PRM transition-ramp, bogie-deck step-cover, contrast-nosing, and anti-slip set | final assembly and commissioning cell | 1.05 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P051`<br>`TORQUE-LM3-INT-P051` | placement zone and joint controls accepted: bogie frame, axle, brake, suspension, and underframe marriage datums | operator |
| 200 | install and integrate LM3-INT-P052: door-pocket liner, sensitive-edge clearance trim, and removable jamb-cover set | final assembly and commissioning cell | 1.23 | `FIX-LM3-INT-SA330`<br>`GAUGE-LM3-INT-P052`<br>`TORQUE-LM3-INT-P052` | placement zone and joint controls accepted: side door aperture and low-floor threshold datum | operator |
| 210 | hold point: egress check | quality inspection | 0.35 | `QA-LM3-INT-SA330` | egress check | quality inspector |
| 220 | hold point: fire-material pack | quality inspection | 0.35 | `QA-LM3-INT-SA330` | fire-material pack | quality inspector |
| 230 | hold point: liner/trim fit survey | quality inspection | 0.35 | `GAUGE-LM3-INT-SA330` | liner/trim fit survey | quality inspector |
| 240 | hold point: lighting/PIS/CCTV static test | quality inspection | 0.35 | `QA-LM3-INT-SA330` | lighting/PIS/CCTV static test | quality inspector |
| 250 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-INT-SA330`<br>`NCR-LM3-INT-SA330` | all operation and QA signoffs are complete | manufacturing engineer |

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
