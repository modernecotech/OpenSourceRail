# Shop traveler — LM3-ROOF-SA410 — roof HVAC, PV, antenna, and service-equipment assembly

| Field | Value |
|---|---|
| Traveler type | `assembly-node` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 18.1 h |
| Build cell | final assembly and commissioning cell |
| Procurement BOM lines | `B7` |

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


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-ROOF-SA410-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-ROOF-SA410-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-ROOF-SA410-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, fixture, child kit, and latest definition package | final assembly and commissioning cell | 1.25 | `TRV-LM3-ROOF-SA410`<br>`FIX-LM3-ROOF-SA410`<br>`KIT-LM3-ROOF-SA410` | all child definitions/revisions match the traveler index | cell lead |
| 20 | install and integrate LM3-BDY-P080: roof bow, HVAC rail, PV rail, and cable-tray bracket kit | final assembly and commissioning cell | 1.84 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-BDY-P080`<br>`TORQUE-LM3-BDY-P080` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 30 | install and integrate LM3-ROOF-P010: HVAC curb, drop-duct collar, condensate tray, and drain fitting kit | final assembly and commissioning cell | 1.77 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-ROOF-P010`<br>`TORQUE-LM3-ROOF-P010` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 40 | install and integrate LM3-ROOF-P020: PV bonded-pad lands, raised rail kit, bonding jumpers, and roof isolation labels | final assembly and commissioning cell | 1.47 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-ROOF-P020`<br>`TORQUE-LM3-ROOF-P020` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 50 | install and integrate LM3-ROOF-P030: removable HVAC curb fairing, intake/exhaust skirt, and access-hatch moulding set | final assembly and commissioning cell | 1.77 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-ROOF-P030`<br>`TORQUE-LM3-ROOF-P030` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 60 | install and integrate LM3-ROOF-P040: PV junction plinth, cable-gland cover, antenna closeout, and walkway edge set | final assembly and commissioning cell | 1.53 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-ROOF-P040`<br>`TORQUE-LM3-ROOF-P040` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 70 | install and integrate LM3-EXT-P040: hvac-24kw-direct-hv-dc roof HVAC | final assembly and commissioning cell | 1.72 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-EXT-P040`<br>`TORQUE-LM3-EXT-P040` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 80 | install and integrate LM3-EXT-P050: roof PV module and edge-clamp kit | final assembly and commissioning cell | 1.3 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-EXT-P050`<br>`TORQUE-LM3-EXT-P050` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 90 | install and integrate LM3-EXT-P070: roof antennas, service walkway pads, lifting covers, and maintenance labels | final assembly and commissioning cell | 1.35 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-EXT-P070`<br>`TORQUE-LM3-EXT-P070` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 100 | install and integrate LM3-FIN-P020: calcium-carbonate radiative roof-coating qualification and exposed-roof application kit | final assembly and commissioning cell | 1.1 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-FIN-P020`<br>`TORQUE-LM3-FIN-P020` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 110 | install and integrate LM3-TRC-P050: roof-mounted regen dump resistor and thermal shield kit | final assembly and commissioning cell | 1.65 | `FIX-LM3-ROOF-SA410`<br>`GAUGE-LM3-TRC-P050`<br>`TORQUE-LM3-TRC-P050` | placement zone and joint controls accepted: roof equipment rail, curb, and service-access zone | operator |
| 120 | hold point: roof leak test | quality inspection | 0.35 | `LEAK-TEST-LM3-ROOF-SA410` | roof leak test | quality inspector |
| 130 | hold point: HVAC drain test | quality inspection | 0.35 | `LEAK-TEST-LM3-ROOF-SA410` | HVAC drain test | quality inspector |
| 140 | hold point: PV isolation/bonding check | quality inspection | 0.35 | `ELEC-TEST-LM3-ROOF-SA410` | PV isolation/bonding check | quality inspector |
| 150 | close traveler, attach nonconformance/deviation log, and release to next parent | production control | 0.3 | `REL-LM3-ROOF-SA410`<br>`NCR-LM3-ROOF-SA410` | all operation and QA signoffs are complete | manufacturing engineer |

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
