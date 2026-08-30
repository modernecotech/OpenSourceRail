# LM3-FIX-P010 — OSR-RAIL-42 common ceiling, waist, and seat-zone service rail kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 3 car kit |
| Parent assembly | `LM3-FIX-SA340` |
| Procurement BOM lines | `B2`, `B15`, `B21` |
| Maturity | `release-candidate` |

## Make / buy basis

One cut/drill gauge produces all common extruded aluminium equipment rails; local adapters, not rail variants, accommodate equipment.

## Material specification

| Field | Value |
|---|---|
| Material family | common extruded aluminium passenger/service datum rail |
| Grade / part class | 6063-T6 or equivalent 42 x 18 mm extrusion candidate with 50 mm datum pitch, isolated body feet and floating-nut capture |
| Governing standard | released LM3-INT-230 rail/attachment calculation plus aluminium, fire, corrosion, shock/vibration and galvanic-isolation evidence |
| Form factor | locally cut, drilled and deburred OSR-RAIL-42 lengths with end stops, isolating feet, datum marks and captive floating-nut channels |
| Nominal section | 42 x 18 mm reference section; wall, foot, pitch and nut channel remain controlled drawing dimensions |
| Finish / protection | anodised/coated cleanable finish with isolated steel fasteners, sealed cut ends and no passenger-facing sharp edges |
| Traceability | extrusion batch, finish batch, cut list, drill-gauge record, foot/fastener lot and installed rail survey |

Evidence required:

- certificate of conformity
- incoming inspection record
- rail pull-out/slip proof
- datum survey
- galvanic-isolation check

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, rail datum survey, end-deburr check, isolation/finish inspection, representative pull/slip test
- Tooling basis: FIX-LM3-FIX-FAB plus GAUGE-LM3-FIX-P010-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- rail datum survey
- end-deburr check
- isolation/finish inspection
- representative pull/slip test

## Source references

- `small_components.py`
- `bom-skeleton.md B2/B15/B21`
- `LM3-INT-230`
