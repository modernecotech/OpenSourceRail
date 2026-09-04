# LM3-FAS-P020 — reversible front-lamp cassette tray, aiming adjusters, and retained service bracket

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 2 end set |
| Parent assembly | `LM3-CWL-SA710` |
| Procurement BOM lines | `B8`, `B17` |
| Maturity | `buildable-after-supplier-freeze` |

## Make / buy basis

One symmetrical removable bracket accepts the selected head/tail/marker lamp modules at either leading end and preserves aim after hatch removal.

## Material specification

| Field | Value |
|---|---|
| Material family | formed sheet metal / stainless local hardware |
| Grade / part class | S355 or 304/316 stainless local bracket/tray candidate, selected by exposure zone |
| Governing standard | EN 10025 / EN 10088 certificate as applicable plus project bonding/corrosion evidence |
| Form factor | laser-cut, folded, drilled sheet/plate with inserts, studs, clips, and labels |
| Nominal section | thickness, stainless grade, and galvanic isolation frozen by v2A controlled drawing |
| Finish / protection | zinc/paint/stainless passivation, orange HV marking, edge protection, and sealing as applicable |
| Traceability | heat number, coating batch, bonding test, and installation batch traceability |

Evidence required:

- mill certificate
- coating/passivation record
- bonding continuity record

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, lamp datum gauge, aiming range/retention test, harness clearance, cassette removal trial
- Tooling basis: FIX-LM3-FAS-FAB plus GAUGE-LM3-FAS-P020-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- lamp datum gauge
- aiming range/retention test
- harness clearance
- cassette removal trial

## Source references

- `end-cowl.md`
- `systems.py`
- `LM3-SYS-160`
