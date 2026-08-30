# Shop traveler — LM3-WIN-P010 — replaceable window pressure frame, dry seal, drain, and captive retention kit

| Field | Value |
|---|---|
| Traveler type | `product-item` |
| Document revision | `A-DRAFT` |
| Release status | `unsigned-template` |
| Estimated labor | 4.2 h |
| Route | `MAKE` |
| Procurement BOM lines | `B10` |

## Material specification

| Field | Value |
|---|---|
| Material family | replaceable aluminium window-retention and elastomer seal kit |
| Grade / part class | 6061/6082 plate or 6063 extrusion candidate pressure frame, nonmetallic setting blocks, closed-cell/EPDM seal, aluminium drain rail, and captive stainless retainers |
| Governing standard | released LM3-WIN-210 retention calculation and drawing plus supplier glazing, aluminium, elastomer, fire, corrosion, and ingress evidence |
| Form factor | CNC-cut/extruded pressure-frame segments with keyed dry seal, protected glass-edge clearances, drain path, secondary retention, and cassette jack points |
| Nominal section | profile, corner joint, fastener pitch, setting blocks, seal compression and glass clearance fixed by the controlled window interface drawing |
| Finish / protection | anodised or coated aluminium, passivated retained hardware, isolated mixed-metal contacts, UV/ozone-resistant seal, and open inspected drains |
| Traceability | aluminium batch, seal batch/date, retained-fastener lot, cassette position map, compression record, and water/replacement test |

Evidence required:

- certificate of conformity
- incoming inspection record
- retention proof
- seal compression map
- drain test
- water-ingress and replacement trial

## Process specification

- Primary processes: receive and edge-inspect supplier cassette, machine and deburr pressure frame, gauge aperture and drains, dry-fit on protected setting blocks, install keyed seal and pressure frame, cross-pattern tighten, water and timed replacement test
- Joining methods: supplier cassette bond retained within its aluminium frame, replaceable dry elastomer compression seal, captive pressure-frame fasteners, nonmetallic setting blocks and secondary retention
- Special process controls: released retention calculation and window interface drawing, no glass-edge metal contact, seal batch and compression map, supplier surface-preparation/adhesive evidence, open drain and mixed-metal isolation checks
- Inspection methods: edge inspection, aperture/pressure-frame gauge, seal compression measurement, drain-flow test, heater/isolation test where fitted, controlled spray test, timed cassette removal/refit, pressure-frame gauge, retention calculation, seal compression record, water-ingress and replacement trial
- Tooling basis: LM3-TOOL-WINDOW-GAUGE plus LM3-TOOL-WATER-TEST
- Release level: design-reference window route; drawing, retention proof, supplier and first-article evidence required before release


## Revision approval block

| Role | Approval ID | Name | Date | Signature | Status |
|---|---|---|---|---|---|
| manufacturing engineering | `APP-LM3-WIN-P010-MFG` |  |  |  | `pending` |
| quality | `APP-LM3-WIN-P010-QA` |  |  |  | `pending` |
| design authority | `APP-LM3-WIN-P010-DA` |  |  |  | `pending` |

## Operation router

| Seq | Operation | Work center | Labor h | Tooling IDs | QA gate | Signoff role |
|---:|---|---|---:|---|---|---|
| 10 | release traveler, revision, material/certificate pack, and parent interface | production control | 0.35 | `TRV-LM3-WIN-P010`<br>`DOC-LM3-WIN-SA320` | traveler rev and parent assembly match released manifest | cell lead |
| 20 | cut, form, machine, or fabricate local hardware | fabrication cell | 1.8 | `FIX-LM3-WIN-FAB`<br>`GAUGE-LM3-WIN-P010-DATUM` | fabricated geometry matches datum/gauge requirements | operator |
| 30 | trial-fit to parent interface and record shim/adjustment pack | fit-up cell | 0.8 | `FIX-LM3-WIN-SA320`<br>`TORQUE-LM3-WIN-P010` | fit-up evidence recorded before release to assembly | operator |
| 40 | verify acceptance gate: pressure-frame gauge | quality inspection | 0.25 | `GAUGE-LM3-WIN-P010` | pressure-frame gauge | quality inspector |
| 50 | verify acceptance gate: retention calculation | quality inspection | 0.25 | `QA-LM3-WIN-P010` | retention calculation | quality inspector |
| 60 | verify acceptance gate: seal compression record | quality inspection | 0.25 | `QA-LM3-WIN-P010` | seal compression record | quality inspector |
| 70 | verify acceptance gate: water-ingress and replacement trial | quality inspection | 0.25 | `LEAK-TEST-LM3-WIN-P010` | water-ingress and replacement trial | quality inspector |
| 80 | final item release to parent assembly | production control | 0.25 | `REL-LM3-WIN-P010`<br>`KIT-LM3-WIN-SA320` | item is released, tagged, and staged for parent assembly | cell lead |

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
