# Shop traveler — LM3-END-P061 — panoramic-end option shim, cowl/glass carrier, and sensor datum closeout kit

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
| Material family | panoramic end-option interface closeout kit |
| Grade / part class | machined shim/closeout plates, cowl/glass carrier transfer brackets, sensor datum plates, and EPDM seal stock |
| Governing standard | released LM3-END-650 panoramic option drawing plus glazing, sensor, corrosion, and water-ingress evidence |
| Form factor | kitted interface hardware between common carrier ring, fiberglass cowl, panoramic glass, lamps, and T-OBS sensors |
| Nominal section | selected for the two outer ends of the reference three-car trainset |
| Finish / protection | painted/passivated hardware, isolated stainless inserts, replaceable EPDM seals, and protected glass/sensor datums |
| Traceability | hardware heat/batch, seal batch, shim map, datum survey, and selected-option record |

Evidence required:

- certificate of conformity
- incoming inspection record
- panoramic option fit gauge
- glass/cowl datum transfer
- sensor datum check

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit, fixture weld, controlled cool / stress relief where WPS requires, post-weld machine where required
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, WPS/WPQR release, welder qualification, weld map and heat-input control
- Inspection methods: dimensional inspection, visual inspection, VT, MT/UT where classed, post-weld datum survey, panoramic option fit gauge, glass/cowl datum transfer, sensor datum check, water-ingress pre-test
- Tooling basis: FIX-LM3-END-FAB plus GAUGE-LM3-END-P061-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-END-P061-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-END-P061-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-END-P061-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-END-P061`<br>`DOC-LM3-EIF-SA650` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-END-FAB`<br>`GAUGE-LM3-END-P061-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-EIF-SA650`<br>`TORQUE-LM3-END-P061` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: panoramic option fit gauge | quality inspection | 0.25 | `GAUGE-LM3-END-P061` | panoramic option fit gauge | quality inspector |
| 50 | verify acceptance gate: glass/cowl datum transfer | quality inspection | 0.25 | `GAUGE-LM3-END-P061` | glass/cowl datum transfer | quality inspector |
| 60 | verify acceptance gate: sensor datum check | quality inspection | 0.25 | `GAUGE-LM3-END-P061` | sensor datum check | quality inspector |
| 70 | verify acceptance gate: water-ingress pre-test | quality inspection | 0.25 | `LEAK-TEST-LM3-END-P061` | water-ingress pre-test | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-END-P061`<br>`KIT-LM3-EIF-SA650` | item is released, tagged, and staged for parent assembly | cell lead |

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
