# Civil And Alignment

This folder holds civil-engineering interfaces and planning-grade
alignment material. It is the bridge between generated city designs,
survey/CAD tools, and the mechanical civil catalogue.

## Key Files

| File | Scope |
|---|---|
| [`osr-aln-format.md`](osr-aln-format.md) | OSR-ALN alignment interchange format and validation gates |
| [`west-asia/Iraq/Samawah/`](west-asia/Iraq/Samawah/) | Worked planning-grade line segments, compliance report, and reference alignment docs |

## Related Tools

| Tool | Purpose |
|---|---|
| [`crates/osr-alignment`](../../crates/osr-alignment/) | Alignment geometry, quantities, exports, and stake-out data |
| [`tools/osr-aln-convert`](../../tools/osr-aln-convert/) | Companion converter for external alignment formats |
| [`mechanical-py/src/osr_mech/civil/`](../../mechanical-py/src/osr_mech/civil/) | Parametric U-girders, platform L-units, and civil STEP outputs |

