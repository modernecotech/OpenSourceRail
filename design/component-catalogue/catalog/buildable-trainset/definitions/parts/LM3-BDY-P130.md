# LM3-BDY-P130 — one-metre clip-on solid-side fiberglass body module

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 48 module |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B6` |
| Maturity | `release-candidate` |

## Make / buy basis

Solid side-bay panels use the common 1,000 mm mould pitch and released clip grid; the final quantity is frozen by the door/window bay map.

## Material specification

| Field | Value |
|---|---|
| Material family | fire-retardant exterior fiberglass sandwich |
| Grade / part class | UV-stable E-glass/vinyl-ester 1,000 mm body module with local core and potted inserts |
| Governing standard | project exterior laminate schedule plus EN 45545 fire/smoke, insert, vibration, and aerodynamic evidence |
| Form factor | 994 mm finished side/window/door/roof variants CNC-trimmed from a common 1,000 mm mould pitch |
| Nominal section | 28 mm nominal sandwich with solid clip lands, sealed edges, and replaceable 6 mm EPDM joints |
| Finish / protection | UV-stable exterior gelcoat/paint, sealed cut edges, drained joints, and mixed-metal isolation |
| Traceability | laminate/resin/cure batch, module serial, trim record, insert batch, and fire certificate |

Evidence required:

- certificate of conformity
- incoming inspection record
- laminate coupon
- insert/clip proof
- master-frame fit
- water/vibration evidence

## Process specification

- Primary processes: inspect mould/trim fixture, apply release system, cut dry reinforcement or panel blank, lay up / infuse / press laminate, controlled cure, demould and post-cure where required, trim/drill to controlled datum, fit inserts/clips/gaskets, dry-fit to parent fixture
- Joining methods: potted/captive inserts, retained fasteners or clip grid, adhesive/sealant only where removal and repair rules allow
- Special process controls: released laminate schedule, resin/adhesive batch and shelf-life check, mould release record, cure temperature/time record, fire-material certificate check, edge sealing and dust-control rule, A/B-end interchange rule, glass carrier and sensor datum protection
- Inspection methods: laminate coupon, void/delamination visual tap check, trim-line gauge, insert pull-out where classed, fit-up survey, material/fire certificate, trim gauge, insert pull-out, master-frame dry fit, split-line gap check, water-ingress test, repair coupon demonstration
- Tooling basis: MOULD/FIX-LM3-BDY-P130 plus TRIM-GAUGE-LM3-BDY-P130
- Release level: v2A composite-process controlled MAKE item; generated traveler is unsigned until build

## Acceptance gates

- material/fire certificate
- trim gauge
- insert pull-out
- master-frame dry fit

## Source references

- `modular_fiberglass_body.py`
- `body.md`
- `LM3-BDY-160`
