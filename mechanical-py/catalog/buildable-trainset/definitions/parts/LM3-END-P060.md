# LM3-END-P060 — common reversible end-interface carrier ring, option bolt grid, and sealing datum kit

| Field | Value |
|---|---|
| Definition type | Product item |
| Layer | `fabricated-part` |
| Route | `MAKE` |
| Quantity per trainset | 2 end position |
| Parent assembly | `LM3-EIF-SA650` |
| Procurement BOM lines | `B2` |
| Maturity | `release-candidate` |

## Make / buy basis

Common structural and sealing datum that lets the same train end accept either the panoramic closed nose or the open mid-train connection.

## Material specification

| Field | Value |
|---|---|
| Material family | common structural end-interface steel and seal datum kit |
| Grade / part class | S355 machined carrier ring, stainless option bolt-grid inserts, drain lands, and EPDM sealing datums |
| Governing standard | released LM3-END-650 interface-control drawing plus EN 15085 weld, corrosion, and ingress evidence |
| Form factor | jig-welded/machined end carrier ring with common panoramic/open-mid bolt pattern and replaceable seal lands |
| Nominal section | one common end position envelope accepting either LM3-END-SA700 or LM3-TTART-SA850 without primary-frame rework |
| Finish / protection | blast/prime/topcoat on steel, passivated stainless inserts, sealed drain edges, and isolated mixed-metal joints |
| Traceability | steel heat, weld consumable, insert batch, machining survey, seal batch, and configuration record |

Evidence required:

- certificate of conformity
- incoming inspection record
- option bolt-grid survey
- seal datum continuity
- configuration fit gauge

## Process specification

- Primary processes: cut, form, drill/machine, de-burr, trial fit
- Joining methods: fixture tack and weld where structural, bolted/torqued installation to parent datum
- Special process controls: released drawing/revision check, material certificate check, datum gauge before parent release
- Inspection methods: dimensional inspection, visual inspection, option bolt-grid survey, seal datum continuity, A/B interchange check, end-option fit gauge
- Tooling basis: FIX-LM3-END-FAB plus GAUGE-LM3-END-P060-DATUM
- Release level: v2A drawing-controlled MAKE process; generated traveler is unsigned until build

## Acceptance gates

- option bolt-grid survey
- seal datum continuity
- A/B interchange check
- end-option fit gauge

## Source references

- `articulation.md`
- `end-cowl.md`
- `interfaces.md`
- `LM3-END-650`
