# LM3-WIN-P010 — replaceable window pressure frame, dry seal, drain, and captive retention kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 18 opening kit |
| Parent assembly | `LM3-WIN-SA320` |
| Procurement BOM lines | `B10` |
| Maturity | `concept` |

## Make / buy basis

Supplier bonds glass within its aluminium cassette; the OSR pressure frame and dry seal allow routine removal without cutting adhesive at the carbody.

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

## Acceptance gates

- pressure-frame gauge
- retention calculation
- seal compression record
- water-ingress and replacement trial

## Source references

- `small_components.py`
- `cots_equipment.py`
- `bom-skeleton.md B10`
- `LM3-WIN-210`
