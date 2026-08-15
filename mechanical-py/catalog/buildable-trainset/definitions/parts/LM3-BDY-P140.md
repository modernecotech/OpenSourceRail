# LM3-BDY-P140 — keyed clip rail, captive retainer, anti-lift, and dry-seal car kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-SHELL-A200` |
| Procurement BOM lines | `B7` |
| Maturity | `release-candidate` |

## Make / buy basis

Laser-cut/folded stainless clip hardware and replaceable EPDM seals install without a production adhesive cure cycle.

## Material specification

| Field | Value |
|---|---|
| Material family | stainless retention hardware and elastomer seal kit |
| Grade / part class | keyed hook, captive over-centre clip, independent anti-lift retainer, backing plate, and railway-grade EPDM seal |
| Governing standard | released LM3-BDY-160 joint calculation plus project corrosion, fatigue, fire, and ingress requirements |
| Form factor | laser-cut/folded clip rails, captive hardware, potted backing plates, and extruded dry seals |
| Nominal section | common 1,000 mm pitch with asymmetric key and visible closed witness mark |
| Finish / protection | passivated stainless hardware, isolated mixed-metal interfaces, UV/ozone-resistant EPDM |
| Traceability | hardware heat/batch, seal batch, proof-lot record, and car module map |

Evidence required:

- certificate of conformity
- incoming inspection record
- clip proof-load lot
- seal certificate
- water-ingress record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, clip proof load, anti-reversal gauge, retainer witness-mark check, water ingress test
- Tooling basis: FIX-LM3-BDY-FAB plus GAUGE-LM3-BDY-P140-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- clip proof load
- anti-reversal gauge
- retainer witness-mark check
- water ingress test

## Source references

- `modular_fiberglass_body.py`
- `assembly-plan.md`
- `LM3-BDY-160`
