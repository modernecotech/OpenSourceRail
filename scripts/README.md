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
| [`migrate-design-schema.py`](migrate-design-schema.py) | Apply mechanical TOML schema migrations to generated designs |
| [`export-light-metro-bom.py`](export-light-metro-bom.py) | Export the rolling-stock BOM CSV from the Markdown BOM source plus the generated COTS fit-out cost/source CSV |
| [`build-doc-book.py`](build-doc-book.py) | Build the reader-edition documentation book |
| [`generate-doc-index.py`](generate-doc-index.py) | Rebuild the central Markdown file catalogue in `docs/INDEX.md` |
| [`repo-health.py`](repo-health.py) | Check generated artifact drift, required files, and repository hygiene |

Typical verification:

```bash
python3 scripts/repo-health.py --quiet
```
