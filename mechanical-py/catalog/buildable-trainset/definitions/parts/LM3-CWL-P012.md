# LM3-CWL-P012 — CWL-FRP-02 left cheek fiberglass cast

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 2 ea |
| Parent assembly | `LM3-CWL-SA710` |
| Procurement BOM lines | `B8` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

Locally moulded left cheek/side-return cast carrying the green livery return and split-line closure.

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
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, mould release record, insert pull-out, split-gap gauge, split-line gap check, water-ingress test, repair coupon demonstration
- Tooling basis: MOULD/FIX-LM3-CWL-P012 plus TRIM-GAUGE-LM3-CWL-P012
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build

## Acceptance gates

- mould release record
- laminate coupon
- insert pull-out
- split-gap gauge

## Source references

- `sensor_cowl.py`
- `end-cowl.md`
- `LM3-BDY-155-CWL-FRP-02`
