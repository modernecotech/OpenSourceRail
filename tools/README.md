# Tools

| Area | Kind | Purpose |
|---|---|---|
| [`automation/`](automation/README.md) | Internal orchestration | Build, regeneration, publishing, validation and repository health |
| [`osr-aln-convert/`](osr-aln-convert/README.md) | Installable utility | OSR-ALN/LandXML conversion and validation |
| [`reference-ma/`](reference-ma/README.md) | Installable reference utility | Independent movement-authority reference model |

User workflows start with [`../osr`](../osr); domain rules stay in their owning
Rust or Python packages rather than accumulating in automation scripts.

## Shared local design workflows

`./osr design problems/run/refine/search/jobs/verify/compare/cancel/resume/export` delegates to the [shared package](../engineering/design_engine/README.md); the original Rust design compiler remains available for its legacy arguments. `./osr doctor`, `./osr capabilities`, `./osr catalogue` and `./osr check` provide preflight, the generated directory, selected-city generation and local test tiers. See [acceptance limits](../docs/design-engine/plan-status.md).
