# Repository Scripts

This folder contains small orchestration helpers for regeneration,
documentation publishing, and repository health checks. Scripts should
stay thin: domain logic belongs in Rust crates, `design-py`, or
`mechanical-py`.

## Scripts

| Script | Purpose |
|---|---|
| [`regenerate-city.sh`](regenerate-city.sh) | Regenerate one city design from the batch catalogue |
| [`regenerate-all.sh`](regenerate-all.sh) | Regenerate the generated city catalogue |
| [`generate-design-index.py`](generate-design-index.py) | Rebuild the generated city catalogue in `designs/README.md` |
| [`generate-acceptance-evidence-report.py`](generate-acceptance-evidence-report.py) | Build the acceptance/accreditation evidence-basis report and matrix from the operations bundle |
| [`migrate-design-schema.py`](migrate-design-schema.py) | Apply mechanical TOML schema migrations to generated designs |
| [`export-light-metro-bom.py`](export-light-metro-bom.py) | Export the rolling-stock BOM CSV from the Markdown BOM source plus the generated COTS fit-out cost/source CSV |
| [`generate-qa-maintenance-data.py`](generate-qa-maintenance-data.py) | Generate operations portal assets, manufacturing schedule/materials/verification, QA register, and maintenance schedule CSV/JSON data |
| [`build-doc-book.py`](build-doc-book.py) | Build the reader-edition documentation book |
| [`generate-doc-index.py`](generate-doc-index.py) | Rebuild the central Markdown file catalogue in `docs/INDEX.md` |
| [`render-sim-screenshots.py`](render-sim-screenshots.py) | Generate README/book simulator screenshots from the current Samawah scenario |
| [`repo-health.py`](repo-health.py) | Check generated artifact drift, required files, and repository hygiene |

Typical verification:

```bash
python3 scripts/repo-health.py --quiet
```
