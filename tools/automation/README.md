# Repository Automation

This folder contains small orchestration helpers for regeneration,
documentation publishing, and repository health checks. Scripts should
stay thin: domain logic belongs in Rust crates, `design/city-generation`, or
`design/component-catalogue`.

## Commands

| Script | Purpose |
|---|---|
| [`build-all.sh`](build-all.sh) | One-command regeneration of shared product/cost/catalogue data, browser and native applications, BOM/IFC packages, the root reader PDF, and documentation checks; invoked as `./osr build` |
| [`../../osr`](../../osr) | Root user command for the Workbench, build, simulator, tests and engineering workflows |
| [`regenerate-city.sh`](regenerate-city.sh) | Regenerate one city design from the batch catalogue |
| [`regenerate-all.sh`](regenerate-all.sh) | Cached design synthesis plus complete city-package refresh under `cities/catalogue/`; use `--from-scratch` to force source-data rebuilding |
| [`generate-city-packages-fast.py`](generate-city-packages-fast.py) | Resynthesise designs, then refresh scenarios, maps, engineering, resilience simulation, screenshots, operations, READMEs, and completeness manifests |
| [`generate-design-index.py`](generate-design-index.py) | Rebuild the complete city catalogue index in `cities/catalogue/README.md` |
| [`generate-cost-model.py`](generate-cost-model.py) | Rebuild `docs/cost-model.md` from the CAPEX template, generated civil rate contract, finance/benefit assumptions, and rolling-stock BOM |
| [`generate-civil-cost-model.py`](generate-civil-cost-model.py) | Convert canonical CAD quantities and reviewed benchmark shares into the generated civil planning-rate contract; `--check` detects drift |
| [`generate-acceptance-evidence-report.py`](generate-acceptance-evidence-report.py) | Build the acceptance/accreditation evidence-basis report and matrix from the operations bundle |
| [`export-light-metro-bom.py`](export-light-metro-bom.py) | Export the rolling-stock BOM CSV from the Markdown BOM source plus the generated COTS fit-out cost/source CSV |
| [`generate-qa-maintenance-data.py`](generate-qa-maintenance-data.py) | Generate operations portal assets, manufacturing schedule/materials/verification, QA register, maintenance CSVs, and a deterministic gzip JSON bundle with integrity manifest |
| [`audit-project-twins.py`](audit-project-twins.py) | Reconcile city family scope, source hashes, finance buckets, CPM/cashflow totals and the mechanical/civil reference evidence |
| [`build-doc-book.py`](build-doc-book.py) | Build the complete reader-edition PDF from the validated source manifest and all city models |
| [`generate-doc-index.py`](generate-doc-index.py) | Rebuild the exhaustive Markdown inventory used for search and CI diagnostics; it is not a second documentation guide |
| [`render-sim-screenshots.py`](render-sim-screenshots.py) | Generate city-local simulator screenshots from any scenario |
| [`render-city-engineering.py`](render-city-engineering.py) | Render hash-linked QGIS engineering-layer and SUMO validation visuals for city READMEs |
| [`validate-ring-interchanges.py`](validate-ring-interchanges.py) | Fail close ring/radial approaches without a shared transfer, flag radial corridors that double back on themselves, and report genuinely disconnected route layouts |
| [`validate-station-clusters.py`](validate-station-clusters.py) | Fail same-line spacing below 1.2 km, unmerged cross-line stops within the 600 m station-complex envelope, and missing explicit interchange-complex records |
| [`design-iterate.sh`](design-iterate.sh) | Iterate the rolling-stock design hierarchy across external components, fabricated parts, subassemblies, and final assemblies |
| [`buildable-trainset.sh`](buildable-trainset.sh) | Generate the LM3 product tree, supplier/COTS sourcing registers, buildability review, first-article work packages and evidence status |
| [`freecad-generate.sh`](freecad-generate.sh) | Repository-level FreeCAD/Blender generator for mechanical review models, assemblies, FEM screens, screenshots, and animated digital twins |
| [`bonsai-civil.sh`](bonsai-civil.sh) | Generate deterministic IFC4.3 civil federations with IDS audits and BCF 3.0 release issues, import through Bonsai, and render the linked 4D construction review scene |
| [`engineering-toolchain.sh`](engineering-toolchain.sh) | Install/check the engineering environment; run smoke tests, JuPedSim/SUMO benchmarks, analysis-register validation, and station IFC interchange checks |
| [`generate-city-engineering.py`](generate-city-engineering.py) | Generate city-local QGIS packages, geometry-shaped SUMO runs, pandapower/pvlib energy screens and station-to-product mappings |
| [`generate-city-finance.py`](generate-city-finance.py) | Reconcile CAPEX; split localization-first external/local capital; compare variable foreign-turnkey cases; emit OPEX, revenue, NPV/IRR/DSCR, renewal, and risk screens |
| [`generate-national-briefs.py`](generate-national-briefs.py) | Generate concise country-specific city/factory/capital aggregates linked to the common deployment planning reference |
| [`generate-portfolio-summary.py`](generate-portfolio-summary.py) | Aggregate the current city and national-factory models into `docs/portfolio-summary.md` |
| [`generate-public-overview.py`](generate-public-overview.py) | Generate and drift-check the one-page public HTML overview from the design catalogue and LM3 build-cost record |
| [`recalculate-city-capex.py`](recalculate-city-capex.py) | Recalculate generated city CAPEX after removing duplicated city-level trainset factories |
| [`validate-city-simulation.py`](validate-city-simulation.py) | Run nominal and mandatory degraded-energy OSR simulations on distinct physical cores, including combined aged/hot, consecutive missed-charge and late-running charger-overlap cases, and write compact reproducible evidence |
| [`check-tracked-file-sizes.py`](check-tracked-file-sizes.py) | Keep useful GitHub artifacts in-tree while enforcing the 50 MiB per-file repository ceiling |
| [`generate-lm3-first-article-work.py`](generate-lm3-first-article-work.py) | Freeze `LM3-FA-001` and export its 81 gaps with controlled closure state and evidence routes |
| [`validate-lm3-first-article-evidence.py`](validate-lm3-first-article-evidence.py) | Reject missing, unaccountable or checksum-drifted LM3 physical/supplier evidence submissions |
| [`publish-lm3-work-packages.py`](publish-lm3-work-packages.py) | Preview or idempotently reconcile LM3 work packages with public GitHub issues |
| [`ops-user-admin.py`](ops-user-admin.py) | Create/update a private PBKDF2 Ops Core user store with city-scoped roles |
| [`ops-core-backup.py`](ops-core-backup.py) | Create and verify a consistent SQLite plus managed-evidence backup archive |
| [`validate-simulation-components.py`](validate-simulation-components.py) | Fail closed unless every deployed software component has one explicit simulation treatment and every tick-linked component remains an `osr-sim` dependency |
| [`generate-city-package-manifest.py`](generate-city-package-manifest.py) | Fail closed unless a full city package contains passing design, engineering, simulation, resilience, operations, and hash-linked acceptance artifacts |
| [`repo-health.py`](repo-health.py) | Check generated artifact drift, required files, and repository hygiene |
| [`check-markdown-links.py`](check-markdown-links.py) | Check that local links in tracked Markdown resolve inside the repository |
| [`check-readmes.py`](check-readmes.py) | Enforce titles, whitespace, provenance, concise size limits, complete Markdown indexing, and current LM3 contract counts/links across tracked READMEs and national briefs |
| [`export-gis-context.py`](export-gis-context.py) | Convert a cached city OSM snapshot into deterministic local roads, buildings, water, protected-land and existing-rail GeoJSON layers, refreshing project source locks when present |
| [`validate-host-manifests.py`](validate-host-manifests.py) | Validate all five host compositions and the complete Cargo component inventory |
| [`validate-city-projects.py`](validate-city-projects.py) | Compile and validate every Git-backed OSR City Studio project, including source locks and weekly service plans |
| [`build-web-frontends.sh`](build-web-frontends.sh) | Build City Studio and the simulator/OCC production WASM bundles with pinned Trunk 0.21.8 |
| [`workbench-server.py`](workbench-server.py) | Serve the same-origin Workbench, proxy City Studio, mount simulator/OCC WASM, and persist Ops Core records |
| [`test-city-studio-gui.mjs`](test-city-studio-gui.mjs) | Drive the real City Studio GUI with Playwright Chromium, run every adapter, restart the server, and verify project/job persistence in an isolated disposable project |

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
python3 tools/automation/repo-health.py --quiet
python3 tools/automation/generate-civil-cost-model.py --check
python3 tools/automation/validate-host-manifests.py
tools/automation/design-iterate.sh
tools/automation/buildable-trainset.sh
tools/automation/freecad-generate.sh --check
tools/automation/bonsai-civil.sh --check
```

Build the complete documentation book with one command:

```bash
./osr book
```

The book includes canonical project and technical prose, software, deployment,
control-electronics, formal-assurance, engineering and high-level manufacturing
documentation, 43 developing-country briefs, and concise briefs generated from all 266 city
models. `./osr book --list-sources` prints the exact
validated manifest. Generated search indexes, duplicate city pages, component
definitions and signable travelers remain linked repository records rather
than repeated chapters. The illustrated build fails if a referenced local image
is missing or unreadable. Chapter source bars link to GitHub and the PDF outline
provides part, chapter, region, and country navigation.

The Samawah worked example is regenerated separately because it consumes the
city-local alignment, station, energy, simulation, and fleet package:

```bash
tools/automation/freecad-generate.sh --samawah-line-twin
tools/automation/freecad-generate.sh --fabrication-twin
tools/automation/bonsai-civil.sh --render
```
