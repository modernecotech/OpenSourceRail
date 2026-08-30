# Tools

| Area | Kind | Purpose |
|---|---|---|
| [`automation/`](automation/README.md) | Internal orchestration | Build, regeneration, publishing, validation and repository health |
| [`osr-aln-convert/`](osr-aln-convert/README.md) | Installable utility | OSR-ALN/LandXML conversion and validation |
| [`reference-ma/`](reference-ma/README.md) | Installable reference utility | Independent movement-authority reference model |

User workflows start with [`../osr`](../osr); domain rules stay in their owning
Rust or Python packages rather than accumulating in automation scripts.
