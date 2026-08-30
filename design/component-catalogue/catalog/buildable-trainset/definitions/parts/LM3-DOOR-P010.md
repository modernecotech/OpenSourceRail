# LM3-DOOR-P010 — door four-point adjustable carrier, datum pin, dry seal, and keyed connector bracket kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 12 opening kit |
| Parent assembly | `LM3-DOOR-SA310` |
| Procurement BOM lines | `B11`, `B25` |
| Maturity | `concept` |

## Make / buy basis

The certified door remains a complete supplier cassette; four common adjustable shoes absorb body tolerance and make removal predictable.

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

## Acceptance gates

- carrier datum gauge
- interface load calculation
- seal compression record
- connector keying and cassette replacement trial

## Source references

- `small_components.py`
- `systems.py`
- `bom-skeleton.md B11/B25`
- `LM3-DOOR-200`
