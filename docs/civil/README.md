# Civil And Alignment

This folder holds civil-engineering interfaces and planning-grade
alignment material. It is the bridge between generated city designs,
survey/CAD tools, and the mechanical civil catalogue.

Civil design artifacts remain planning-grade until local survey,
geotechnical, utility, permit, and structural checks are complete. The
release gates are tracked in
[`deployment-release-checklist.md`](deployment-release-checklist.md).

## Key Files

| File | Scope |
|---|---|
| [`marketplace-cost-anchors.md`](marketplace-cost-anchors.md) | Marketplace audit trail and retained benchmarks for at-grade track, elevated guideway, bridges, stations, depots, and charging interfaces |
| [`civil-cost-calibration.toml`](../../lib/templates/civil-cost-calibration.toml) | Reviewed benchmark quantities and cost shares; the human-edited input to design-derived civil rates |
| [`civil-cost-model.toml`](../../lib/templates/civil-cost-model.toml) | Generated rate contract consumed by city synthesis, finance reports, IFC metadata, and city READMEs |
| [`rapid-implementation-materials-review.md`](rapid-implementation-materials-review.md) | Internet review of rapid ballastless track, modular stations, and recycled or lower-carbon materials |
| [`slab-trackforms.md`](slab-trackforms.md) | Reference ballastless slab designs for at-grade and elevated guideway sections |
| [`depot-bogie-change-interface.md`](depot-bogie-change-interface.md) | Shared LM3 jack-point datum, synchronized depot lift, pit, and bogie-extraction assembly contract |
| [`wayside-rerailing-access-interface.md`](wayside-rerailing-access-interface.md) | Optional selected-node hardstanding, offload, bridge-bearing, handling-route, and exclusion-zone contract for portable LM3 rerailing |
| [`../../design/component-catalogue/catalog/buildable-civil/`](../../design/component-catalogue/catalog/buildable-civil/) | Generated accountability for all 19 reusable IFC types, six civil release packages, nine drawing-definition briefs, and the empty project release record |
| [`viaduct-substructure-kit.md`](viaduct-substructure-kit.md) | Controlled pier/abutment EBOMs, interfaces, assembly sequences, and deployment release gates |
| [`viaduct-design-basis.md`](viaduct-design-basis.md) | Rapid Viaduct Kit catalogue boundary, structural actions, geometry rules, and release evidence |
| [`viaduct-load-model.toml`](viaduct-load-model.toml) | Machine-readable 12-axle load/action seed |
| [`viaduct-kinematic-egress-envelope.md`](viaduct-kinematic-egress-envelope.md) | Train, walkway, parapet, and straight-span curve compatibility gates |
| [`viaduct-bearing-and-movement-schedule.md`](viaduct-bearing-and-movement-schedule.md) | Interior/end bearing counts and project movement-schedule requirements |
| [`viaduct-transport-and-erection-envelope.md`](viaduct-transport-and-erection-envelope.md) | Permit-load transport, lifting, launcher, and temporary-stage release gates |
| [`viaduct-first-article-test-plan.md`](viaduct-first-article-test-plan.md) | First mould, girder, cap, lift, erected bay, and track/egress hold points |
| [`viaduct-quantity-cost-model.toml`](viaduct-quantity-cost-model.toml) | Per-kilometre quantity seed and cost-estimate classification |
| [`osr-aln-format.md`](osr-aln-format.md) | OSR-ALN alignment interchange format and validation gates |
| [`bonsai-ifc-workflow.md`](bonsai-ifc-workflow.md) | IFC4.3/Bonsai civil federation, IDS delivery audit, BCF coordination, quantities, 4D sequencing, and engineering-authority boundary |
| [`Samawah/engineering/alignment/`](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/alignment/) | Current three-line Samawah planning OSR-ALN package, provenance, and survey replacement gates |
| [`deployment-release-checklist.md`](deployment-release-checklist.md) | Survey, geotechnical, structure, station, energy-site, and permit release gates |

## Related Tools

| Tool | Purpose |
|---|---|
| [`crates/osr-alignment`](../../crates/osr-alignment/) | Alignment geometry, quantities, exports, and stake-out data |
| [`tools/osr-aln-convert`](../../tools/osr-aln-convert/) | Companion converter for external alignment formats |
| [`design/component-catalogue/src/osr_mech/civil/`](../../design/component-catalogue/src/osr_mech/civil/) | Parametric girders, piers, abutments, slab/guideway edges, elevated platform units, and civil CAD source |
| [`tools/automation/bonsai-civil.sh`](../../tools/automation/bonsai-civil.sh) | Deterministic IFC/IDS/BCF generation, Bonsai import, saved review scene, 48-second MP4/GIF, and milestone screenshots |
| [`tools/automation/buildable-civil.sh`](../../tools/automation/buildable-civil.sh) | Reconcile the reusable IFC type set with civil-owned and interdisciplinary release packages; fail on unclassified geometry changes |
| [`tools/automation/generate-civil-cost-model.py`](../../tools/automation/generate-civil-cost-model.py) | Recalculate planning rates from current CAD quantities and reject stale output with `--check` |
| [`tools/automation/audit-project-twins.py`](../../tools/automation/audit-project-twins.py) | Reconcile every city civil/finance bucket, CPM and cashflow source hash with the validated reference IFC and mechanical package |

The IFC is a generated coordination output, not a competing geometry source.
Change the parametric CAD/BIM source or reviewed calibration, then regenerate:

```text
CAD geometry → per-route-km quantity model → civil cost contract
             ↘ IFC4.3 quantities/provenance   ↘ city CAPEX and READMEs
```

Project-specific Bonsai detail edits that are intended to become authoritative
must first be reviewed and promoted into the parametric source; otherwise the
next deterministic regeneration intentionally replaces them.

The city delivery twin schedules civil work by actual line length, civil class,
predecessors and finite crews. Its `civil` budget comes from the same generated
rate contract as city CAPEX; charging work is assigned to energy assets, not an
overhead placeholder. Survey, geotechnical, utilities, local temporary works,
permits and engineer release remain recorded gates rather than invented data.
