# Shop traveler — LM3-END-P062 — mid open-connection option portal trim, bellows clamp, threshold bridge, and drain kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B2` |

## Material specification

| Field | Value |
|---|---|
| Material family | open mid-connection end-option interface kit |
| Grade / part class | machined bellows clamp frame, threshold bridge, turntable edge trim, drain tray, and fire-rated passenger portal closeout |
| Governing standard | released LM3-END-650-MID option drawing plus gangway, fire/smoke, slip, corrosion, and ingress evidence |
| Form factor | kitted open portal hardware replacing the panoramic cowl/glass at a train-to-train walk-through joint |
| Nominal section | selected only for train modules configured as mid open connections |
| Finish / protection | painted/passivated hardware, replaceable rubber seals, anti-slip threshold finish, and cleanable passenger trim |
| Traceability | hardware heat/batch, trim/seal batch, threshold survey, drain test, and selected-option record |

Evidence required:

- certificate of conformity
- incoming inspection record
- open-portal gauge
- bellows clamp fit
- threshold/turntable level check

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, open-portal gauge, bellows clamp fit, threshold/turntable level check, drain-path water test
- Tooling basis: FIX-LM3-END-FAB plus GAUGE-LM3-END-P062-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-END-P062-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-END-P062-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-END-P062-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-END-P062`<br>`DOC-LM3-EIF-SA650` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-END-FAB`<br>`GAUGE-LM3-END-P062-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-EIF-SA650`<br>`TORQUE-LM3-END-P062` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: open-portal gauge | quality inspection | 0.25 | `GAUGE-LM3-END-P062` | open-portal gauge | quality inspector |
| 50 | verify acceptance gate: bellows clamp fit | quality inspection | 0.25 | `QA-LM3-END-P062` | bellows clamp fit | quality inspector |
| 60 | verify acceptance gate: threshold/turntable level check | quality inspection | 0.25 | `QA-LM3-END-P062` | threshold/turntable level check | quality inspector |
| 70 | verify acceptance gate: drain-path water test | quality inspection | 0.25 | `LEAK-TEST-LM3-END-P062` | drain-path water test | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-END-P062`<br>`KIT-LM3-EIF-SA650` | item is released, tagged, and staged for parent assembly | cell lead |

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
