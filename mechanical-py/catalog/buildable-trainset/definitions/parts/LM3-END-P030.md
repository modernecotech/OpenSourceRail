# LM3-END-P030 — cowl service hatch, sensor backing bracket, washer-tube, and heater-cable clip kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 2 end kit |
| Parent assembly | `LM3-END-SA700` |
| Procurement BOM lines | `E19` |
| Maturity | `release-candidate` |

## Make / buy basis

Local brackets and service access hardware for the nose sensor and heated glass services.

## Material specification

| Field | Value |
|---|---|
| Material family | fire-retardant fiberglass composite |
| Grade / part class | E-glass FRP cast kit with bonded/moulded inserts |
| Governing standard | supplier laminate schedule plus project fire/smoke and structural coupon evidence |
| Form factor | multi-part moulded shell, bonded inserts, service hatch lands, and trim edges |
| Nominal section | laminate schedule, insert pattern, split line, and trim datum frozen by supplier drawing |
| Finish / protection | UV-stable exterior gelcoat/paint with sealed cut edges and insert corrosion isolation |
| Traceability | laminate batch, resin batch, cure record, insert pull-out record, and coupon traceability |

Evidence required:

- laminate coupon
- cure record
- insert pull-out evidence
- fire-smoke certificate

## Process specification

- Primary processes: inspect mould/trim fixture, apply release system, cut dry reinforcement or panel blank, lay up / infuse / press laminate, controlled cure, demould and post-cure where required, trim/drill to controlled datum, fit inserts/clips/gaskets, dry-fit to parent fixture
- Joining methods: potted/captive inserts, retained fasteners or clip grid, adhesive/sealant only where removal and repair rules allow
- Special process controls: released laminate schedule, resin/adhesive batch and shelf-life check, mould release record, cure temperature/time record, fire-material certificate check, edge sealing and dust-control rule, A/B-end interchange rule, glass carrier and sensor datum protection
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, hatch water test, sensor datum check, heater-cable separation, washer tube leak test, split-line gap check, water-ingress test, repair coupon demonstration
- Tooling basis: MOULD/FIX-LM3-END-P030 plus TRIM-GAUGE-LM3-END-P030
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build

## Acceptance gates

- hatch water test
- sensor datum check
- heater-cable separation
- washer tube leak test

## Source references

- `sensor_cowl.py`
- `mechanical_interfaces.py`
- `LM3-OBS-330`
