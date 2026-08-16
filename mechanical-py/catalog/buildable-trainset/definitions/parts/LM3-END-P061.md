# LM3-END-P061 — panoramic-end option shim, cowl/glass carrier, and sensor datum closeout kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 2 option kit |
| Parent assembly | `LM3-EIF-SA650` |
| Procurement BOM lines | `B2` |
| Maturity | `release-candidate` |

## Make / buy basis

Default end-option kit that closes the common interface with the panoramic glass cowl, T-OBS sensor datum, coupler access, and weather seals.

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

## Acceptance gates

- panoramic option fit gauge
- glass/cowl datum transfer
- sensor datum check
- water-ingress pre-test

## Source references

- `sensor_cowl.py`
- `end-cowl.md`
- `LM3-END-650`
