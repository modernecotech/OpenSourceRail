# Repository Scripts

This folder contains small orchestration helpers for regeneration,
documentation publishing, and repository health checks. Scripts should
stay thin: domain logic belongs in Rust crates, `design-py`, or
`mechanical-py`.

## Scripts

| Script | Purpose |
|---|---|
| [`regenerate-city.sh`](regenerate-city.sh) | Regenerate one city design from the batch catalogue |
| [`regenerate-all.sh`](regenerate-all.sh) | Cached design synthesis plus complete city-package refresh under `designs/`; use `--from-scratch` to force source-data rebuilding |
| [`generate-city-packages-fast.py`](generate-city-packages-fast.py) | Resynthesise designs, then refresh scenarios, maps, engineering, resilience simulation, screenshots, operations, READMEs, and completeness manifests |
| [`generate-design-index.py`](generate-design-index.py) | Rebuild the complete city catalogue index in `designs/README.md` |
| [`generate-cost-model.py`](generate-cost-model.py) | Rebuild `docs/cost-model.md` from the CAPEX template, generated civil rate contract, finance/benefit assumptions, and rolling-stock BOM |
| [`generate-civil-cost-model.py`](generate-civil-cost-model.py) | Convert canonical CAD quantities and reviewed benchmark shares into the generated civil planning-rate contract; `--check` detects drift |
| [`generate-acceptance-evidence-report.py`](generate-acceptance-evidence-report.py) | Build the acceptance/accreditation evidence-basis report and matrix from the operations bundle |
| [`export-light-metro-bom.py`](export-light-metro-bom.py) | Export the rolling-stock BOM CSV from the Markdown BOM source plus the generated COTS fit-out cost/source CSV |
| [`generate-qa-maintenance-data.py`](generate-qa-maintenance-data.py) | Generate operations portal assets, manufacturing schedule/materials/verification, QA register, maintenance CSVs, and a deterministic gzip JSON bundle with integrity manifest |
| [`build-doc-book.py`](build-doc-book.py) | Build the reader-edition documentation book |
| [`generate-doc-index.py`](generate-doc-index.py) | Rebuild the central Markdown file catalogue in `docs/INDEX.md` |
| [`render-sim-screenshots.py`](render-sim-screenshots.py) | Generate city-local simulator screenshots from any scenario |
| [`render-city-engineering.py`](render-city-engineering.py) | Render hash-linked QGIS engineering-layer and SUMO validation visuals for city READMEs |
| [`validate-ring-interchanges.py`](validate-ring-interchanges.py) | Fail close ring/radial approaches without a shared transfer, flag radial corridors that double back on themselves, and report genuinely disconnected route layouts |
| [`validate-station-clusters.py`](validate-station-clusters.py) | Fail same-line spacing below 1.2 km, unmerged cross-line stops within the 600 m station-complex envelope, and missing explicit interchange-complex records |
| [`design-iterate.sh`](design-iterate.sh) | Iterate the rolling-stock design hierarchy across external components, fabricated parts, subassemblies, and final assemblies |
| [`buildable-trainset.sh`](buildable-trainset.sh) | Generate the buildable rolling-stock product tree and current-design buildability review |
| [`freecad-generate.sh`](freecad-generate.sh) | Repository-level FreeCAD/Blender generator for mechanical review models, assemblies, FEM screens, screenshots, and animated digital twins |
| [`bonsai-civil.sh`](bonsai-civil.sh) | Generate deterministic IFC4.3 civil federations with IDS audits and BCF 3.0 release issues, import through Bonsai, and render the linked 4D construction review scene |
| [`engineering-toolchain.sh`](engineering-toolchain.sh) | Install/check the engineering environment; run smoke tests, JuPedSim/SUMO benchmarks, analysis-register validation, and station IFC interchange checks |
| [`generate-city-engineering.py`](generate-city-engineering.py) | Generate city-local QGIS packages, geometry-shaped SUMO runs, pandapower/pvlib energy screens and station-to-product mappings |
| [`generate-city-finance.py`](generate-city-finance.py) | Reconcile CAPEX; split localization-first external/local capital; compare variable foreign-turnkey cases; emit OPEX, revenue, NPV/IRR/DSCR, renewal, and risk screens |
| [`generate-national-briefs.py`](generate-national-briefs.py) | Generate concise country-specific city/factory/capital aggregates linked to the common deployment planning reference |
| [`generate-portfolio-summary.py`](generate-portfolio-summary.py) | Aggregate the current city and national-factory models into `docs/portfolio-summary.md` |
| [`recalculate-city-capex.py`](recalculate-city-capex.py) | Recalculate generated city CAPEX after removing duplicated city-level trainset factories |
| [`validate-city-simulation.py`](validate-city-simulation.py) | Run nominal and mandatory degraded-energy OSR simulations on distinct physical cores, using compact result traces, and write reproducible battery, charging, and depot validation evidence |
| [`generate-city-package-manifest.py`](generate-city-package-manifest.py) | Fail closed unless a full city package contains passing design, engineering, simulation, resilience, operations, and hash-linked acceptance artifacts |
| [`repo-health.py`](repo-health.py) | Check generated artifact drift, required files, and repository hygiene |
| [`check-markdown-links.py`](check-markdown-links.py) | Check that local links in tracked Markdown resolve inside the repository |
| [`check-readmes.py`](check-readmes.py) | Enforce titles, whitespace, provenance, common-method links and concise size limits across tracked READMEs and national briefs |
| [`validate-host-manifests.py`](validate-host-manifests.py) | Validate all five host compositions and the complete Cargo component inventory |
| [`validate-city-projects.py`](validate-city-projects.py) | Compile and validate every Git-backed OSR City Studio project, including source locks and weekly service plans |
| [`test-city-studio-gui.mjs`](test-city-studio-gui.mjs) | Drive the real City Studio GUI in headless Chrome, run every adapter, restart the server, and verify project/job persistence in an isolated disposable project |

For a single city, nominal runs and resilience cases are assigned to distinct
physical cores. The default all-city run resynthesises `design.toml` using
current raster/corridor caches where available, then regenerates every
remaining artifact required by the Samawah package manifest. It also fails if
the compact engineering or operations review package for any generated city is
excluded by Git ignore rules. Missing source caches are created automatically;
`--from-scratch` forces them to be rebuilt.
Compact
simulator output retains acceptance counters while
omitting the detailed event trace; validation's explicit `--ma-check-every 0`
uses the same movement-authority gates with bounded derived state instead of
retaining three full Raft histories. `regenerate-all.sh --jobs N`
automatically limits each city to one simulator when `N > 1`, leaving CPU
scheduling to the operating system and preventing nested parallelism.

Typical verification:

```bash
python3 scripts/repo-health.py --quiet
python3 scripts/generate-civil-cost-model.py --check
python3 scripts/validate-host-manifests.py
scripts/design-iterate.sh
scripts/buildable-trainset.sh
scripts/freecad-generate.sh --check
scripts/bonsai-civil.sh --check
```

The Samawah worked example is regenerated separately because it consumes the
city-local alignment, station, energy, simulation, and fleet package:

```bash
scripts/freecad-generate.sh --samawah-line-twin
scripts/freecad-generate.sh --fabrication-twin
scripts/bonsai-civil.sh --render
```
