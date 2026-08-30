# LM3-FIX-P030 — standard passenger-fixture saddle and equipment adapter kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-FIX-SA340` |
| Procurement BOM lines | `B14`, `B15`, `E14` |
| Maturity | `concept` |

## Make / buy basis

A small adapter family attaches seats, handrails, PIS, CCTV and cable supports to the common rail without unique body brackets.

## Material specification

| Field | Value |
|---|---|
| Material family | calculated passenger-fixture saddle and adapter family |
| Grade / part class | laser-cut/folded 304/316 or coated S355 saddles with radiused edges, anti-rotation keys, isolators and M8 captive/floating joints |
| Governing standard | fixture-specific released load calculation/drawing plus material, fastener, fire, corrosion, proof-load and passenger-safety evidence |
| Form factor | common rail-side saddle blank CNC-trimmed/drilled into seat, handrail and equipment variants without transferring primary loads through trim panels |
| Nominal section | rail engagement, edge radius, anti-rotation feature, hole/slot range and fixture keep-out fixed by the controlled adapter drawing |
| Finish / protection | passivated or coated surfaces, electrically/galvanically isolated interfaces and cleanable snag-free passenger edges |
| Traceability | material/finish batch, adapter variant, fastener lot, installed position map, torque/locking record and first-article proof test |

Evidence required:

- certificate of conformity
- incoming inspection record
- adapter gauge
- fixture load proof
- egress and snag inspection

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum, bonding/earthing hardware, segregated clipped service routing
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release, HV/LV segregation check, bend-radius check, label/revision check
- Inspection methods: dimensional inspection, visual inspection, bond continuity, insulation/isolation check where applicable, adapter gauge, fixture-specific load calculation, proof-load sample, egress and snag check
- Tooling basis: FIX-LM3-FIX-FAB plus GAUGE-LM3-FIX-P030-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- adapter gauge
- fixture-specific load calculation
- proof-load sample
- egress and snag check

## Source references

- `small_components.py`
- `bom-skeleton.md B14/B15/E14`
- `LM3-INT-230`
