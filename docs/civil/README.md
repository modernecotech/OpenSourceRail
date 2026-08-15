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
| [`marketplace-cost-anchors.md`](marketplace-cost-anchors.md) | USD direct-procurement floor for at-grade track, elevated guideway, bridges, stations, depots, and charging interfaces |
| [`rapid-implementation-materials-review.md`](rapid-implementation-materials-review.md) | Internet review of rapid ballastless track, modular stations, and recycled or lower-carbon materials |
| [`slab-trackforms.md`](slab-trackforms.md) | Reference ballastless slab designs for at-grade and elevated guideway sections |
| [`viaduct-substructure-kit.md`](viaduct-substructure-kit.md) | Controlled pier/abutment EBOMs, interfaces, assembly sequences, and deployment release gates |
| [`osr-aln-format.md`](osr-aln-format.md) | OSR-ALN alignment interchange format and validation gates |
| [`Samawah/engineering/alignment/`](../../designs/west-asia/Iraq/Samawah/engineering/alignment/) | Current three-line Samawah planning OSR-ALN package, provenance, and survey replacement gates |
| [`deployment-release-checklist.md`](deployment-release-checklist.md) | Survey, geotechnical, structure, station, energy-site, and permit release gates |

## Related Tools

| Tool | Purpose |
|---|---|
| [`crates/osr-alignment`](../../crates/osr-alignment/) | Alignment geometry, quantities, exports, and stake-out data |
| [`tools/osr-aln-convert`](../../tools/osr-aln-convert/) | Companion converter for external alignment formats |
| [`mechanical-py/src/osr_mech/civil/`](../../mechanical-py/src/osr_mech/civil/) | Parametric girders, piers, abutments, slab/guideway edges, elevated platform units, and civil CAD source |
