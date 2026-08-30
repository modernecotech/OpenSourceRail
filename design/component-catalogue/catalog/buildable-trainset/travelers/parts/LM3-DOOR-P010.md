# Shop traveler — LM3-DOOR-P010 — door four-point adjustable carrier, datum pin, dry seal, and keyed connector bracket kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B11`, `B25` |

## Material specification

| Field | Value |
|---|---|
| Material family | adjustable steel/stainless door-carrier and replaceable seal kit |
| Grade / part class | calculated S355/304 carrier shoes, hardened datum pins, sealed floating nutplates, galvanic isolators, EPDM perimeter seal, and keyed connector bracket |
| Governing standard | released LM3-DOOR-200 interface calculation/drawing plus supplier door, fastener, elastomer, corrosion, fire and EN 14752/national evidence as applicable |
| Form factor | four separately adjustable carrier shoes on two repeatable datum pins with mechanical locking, dry seal, recorded shim/adjuster map, and body-side keyed connector support |
| Nominal section | adjustment range, carrier section, fastener grip, pin fit, seal compression and supplier cassette load envelope fixed by the controlled interface drawing |
| Finish / protection | painted/passivated hardware, isolated mixed-metal interfaces, sealed wet-zone nutplates and UV/ozone-resistant replaceable elastomer |
| Traceability | hardware heat/batch, pin and fastener lot, seal batch/date, cassette serial, adjuster map, torque record, and replacement test |

Evidence required:

- certificate of conformity
- incoming inspection record
- carrier load proof
- datum gauge
- seal map
- door safety and replacement tests

## Process specification

- Primary processes: fabricate and gauge four carrier shoes, accept supplier cassette, gauge body portal, lift, pin and adjust cassette, close sealed joints and keyed services, static safety tests, water and timed replacement test
- Joining methods: four adjustable calculated carrier shoes, two repeatable datum pins, sealed high-integrity fasteners, replaceable perimeter seal, keyed body-side connector bracket
- Special process controls: released carrier calculation and interface drawing, supplier lift/installation procedure, adjustment-range and shim map, joint/locking schedule, seal compression map, door safety-test script
- Inspection methods: carrier gauge and proof, leaf/aperture survey, closed-and-locked loop, obstacle and traction-interlock test, emergency/manual release, water test, timed cassette removal/refit, carrier datum gauge, interface load calculation, seal compression record, connector keying and cassette replacement trial
- Tooling basis: LM3-TOOL-DOOR-GAUGE plus LM3-TOOL-SEAL-GAUGE
- Release level: design-reference door interface; supplier freeze, structural proof and applicable door-system acceptance remain mandatory


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-DOOR-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-DOOR-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-DOOR-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-DOOR-P010`<br>`DOC-LM3-DOOR-SA310` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-DOOR-FAB`<br>`GAUGE-LM3-DOOR-P010-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-DOOR-SA310`<br>`TORQUE-LM3-DOOR-P010` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: carrier datum gauge | quality inspection | 0.25 | `GAUGE-LM3-DOOR-P010` | carrier datum gauge | quality inspector |
| 50 | verify acceptance gate: interface load calculation | quality inspection | 0.25 | `QA-LM3-DOOR-P010` | interface load calculation | quality inspector |
| 60 | verify acceptance gate: seal compression record | quality inspection | 0.25 | `QA-LM3-DOOR-P010` | seal compression record | quality inspector |
| 70 | verify acceptance gate: connector keying and cassette replacement trial | quality inspection | 0.25 | `QA-LM3-DOOR-P010` | connector keying and cassette replacement trial | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-DOOR-P010`<br>`KIT-LM3-DOOR-SA310` | item is released, tagged, and staged for parent assembly | cell lead |

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
