# OpenSourceRail Documentation

This is the documentation front door. The repository intentionally keeps
source code, generated city designs, mechanical CAD, hardware, and
safety evidence in separate top-level areas; this page links those areas
without duplicating them.

For a single catalogue of every Markdown file in the repository, use
the generated [Markdown documentation index](INDEX.md).

## Main Reading Paths

| Reader | Start with |
|---|---|
| New reader / non-technical reviewer | [Generated one-page overview](brochures/open-source-rail-overview.html) |
| Project reviewer | [ARCHITECTURE.md](ARCHITECTURE.md), [software architecture diagrams](software-architecture-diagrams.md), then [RFCs](rfcs/) |
| New contributor | [../CONTRIBUTING.md](../CONTRIBUTING.md), [../GOVERNANCE.md](../GOVERNANCE.md), then [GLOSSARY.md](GLOSSARY.md) |
| Deployment reviewer | [Unified deployment model](deployment-model.md), [deployment roles](deployment-roles.md), then [designs/README.md](../designs/README.md) |
| First-product reviewer | [First adoptable product](first-adoptable-product.md), then [operations portal](operations-portal/README.md) |
| City/network planner | [Workbench](workbench/README.md), [City Studio](city-studio/README.md), [deployment planning reference](deployment-planning-reference.md), [cost model](cost-model.md) |
| Rolling-stock engineer | [rolling-stock/light-metro-3car/README.md](rolling-stock/light-metro-3car/README.md) |
| Mechanical/CAD reviewer | [mechanical-py/README.md](../mechanical-py/README.md) and [mechanical-py/catalog/](../mechanical-py/catalog/) |
| Hardware reviewer | [hardware/README.md](../hardware/README.md) and [hardware/rolling-stock-integration.md](../hardware/rolling-stock-integration.md) |
| Operator/maintainer / production planner | [operations/README.md](operations/README.md), [operations portal](operations-portal/README.md), [OSR Ops Core](operations-portal/ops-core.md) |
| Safety/certification reviewer | [certification/README.md](certification/README.md), [safety-case/README.md](safety-case/README.md), [formal/tla/README.md](../formal/tla/README.md) |
| v0.2 contributor | [ROADMAP.md](ROADMAP.md) |
| Engineering design/simulation contributor | [Engineering design and simulation plan](engineering-design-simulation-plan.md) |
| Embedded/software-in-loop reviewer | [Simulation software coverage](simulation-software-coverage.md), then [SBC architecture](rfcs/0005-sbc-software-architecture.md) |
| Release reviewer | [next release checklist](releases/next.md) |

## Documentation Sets

| Folder | Contents |
|---|---|
| [rfcs/](rfcs/README.md) | Design decisions and standards for architecture, rolling stock, track, stations, depots, driverless operation, hardware, energy, and safety |
| [brochures/](brochures/README.md) | Generated one-page public overview and release-PDF instructions |
| [deployment-model.md](deployment-model.md) | Unified city/deployment pipeline; Samawah is an instance, not a special fork |
| [deployment-planning-reference.md](deployment-planning-reference.md) | Canonical shared interpretation for concise generated city READMEs and national briefs |
| [deployment-roles.md](deployment-roles.md) | Owner/operator, prime integrator, assessor, insurer, EPC, workshop, finance, and regulator responsibilities |
| [first-adoptable-product.md](first-adoptable-product.md) | Ops Core + simulator + asset register + QA/maintenance/evidence portal as the first low-risk deployment wedge |
| [rolling-stock/](rolling-stock/README.md) | Light-metro trainset package: GA, body, bogie, traction, BOM, fabrication plan, drawing register, compliance |
| [civil/](civil/README.md) | Alignment, IFC4.3, IDS/BCF, Bonsai coordination, civil design and release evidence |
| [stations/](stations/README.md) | Station design material |
| [operations/](operations/) | Rulebook and operating procedures |
| [operations-portal/](operations-portal/README.md) | Browser portal for asset registers, manufacturing schedule, QA gates, maintenance schedule, Ops Core work orders, defects/NCR, audit, SQLite storage, and reconciliation |
| [workbench/](workbench/README.md) | Same-origin shell and shared context for design, simulation, OCC training and operations |
| [city-studio/](city-studio/README.md) | Git-backed city/GIS design, station intent, weekly service planning, deterministic candidates, and revision review |
| [certification/](certification/) | EN 62267 pre-submission pack: system description, hazards, safety requirements, evidence, compliance matrix |
| [safety-case/](safety-case/) | GSN safety-case source and generated views |
| [hardware/](hardware/) | Hardware bring-up docs |
| [releases/](releases/README.md) | Release packs, assets, metadata, and publication checklists |
| [screenshots/](screenshots/) | Generated UI/CAD screenshots used by READMEs |

## Canonical Design Artifacts

| Artifact | Location |
|---|---|
| City design catalogue and reviewed references | [designs/README.md](../designs/README.md) |
| Shared city/country planning methodology | [deployment planning reference](deployment-planning-reference.md) |
| City source list | [lib/city-batches/world-sample.toml](../lib/city-batches/world-sample.toml) |
| Mechanical FreeCAD review artifacts | [mechanical-py/catalog/](../mechanical-py/catalog/) |
| Rolling-stock BOM | [rolling-stock/light-metro-3car/bom-skeleton.md](rolling-stock/light-metro-3car/bom-skeleton.md) |
| BOM export command | `python3 scripts/export-light-metro-bom.py` (writes under `build/bom/`) |
| Generated station BOMs and travelers | [mechanical-py/catalog/buildable-stations/](../mechanical-py/catalog/buildable-stations/) |
| Hardware host-class matrix | [hardware/rolling-stock-integration.md](../hardware/rolling-stock-integration.md) |
| Deployment roles | [deployment-roles.md](deployment-roles.md) |
| First adoptable product | [first-adoptable-product.md](first-adoptable-product.md) |
| Software architecture diagrams | [software-architecture-diagrams.md](software-architecture-diagrams.md) |
| Hardware release checklist | [hardware/release-checklist.md](../hardware/release-checklist.md) |
| Rolling-stock v2 release checklist | [rolling-stock/light-metro-3car/v2-release-checklist.md](rolling-stock/light-metro-3car/v2-release-checklist.md) |
| Certification release gaps | [certification/release-gap-register.md](certification/release-gap-register.md) |
| Civil deployment release gates | [civil/deployment-release-checklist.md](civil/deployment-release-checklist.md) |
| Civil cost calibration and generated rate contract | [cost model](cost-model.md), [`civil-cost-calibration.toml`](../lib/templates/civil-cost-calibration.toml), [`civil-cost-model.toml`](../lib/templates/civil-cost-model.toml) |
| Open-source engineering toolchain and remaining execution plan | [engineering-design-simulation-plan.md](engineering-design-simulation-plan.md) |
| OpenTrack vs SUMO/native operations-simulation decision | [opentrack-evaluation.md](opentrack-evaluation.md) |
| Operations validation gates | [operations/validation-checklist.md](operations/validation-checklist.md) |
| Operations portal | [operations-portal/README.md](operations-portal/README.md) |
| City design and service-planning studio | [city-studio/README.md](city-studio/README.md) |
| Generated portfolio capital summary | [portfolio-summary.md](portfolio-summary.md) |
| Ops Core operating model | [operations-portal/ops-core.md](operations-portal/ops-core.md) |
| Acceptance/accreditation evidence status | [certification/evidence-status.md](certification/evidence-status.md) |
| Construction QA system | [rfcs/0028-construction-quality-assurance.md](rfcs/0028-construction-quality-assurance.md) |
| Maintenance schedule system | [rfcs/0029-maintenance-schedule-system.md](rfcs/0029-maintenance-schedule-system.md) |
| Manufacturing schedule system | [rfcs/0030-manufacturing-schedule-system.md](rfcs/0030-manufacturing-schedule-system.md) |
| Reader-edition PDF | `python3 scripts/build-doc-book.py` → `build/releases/` |
| Generated public overview | [brochures/open-source-rail-overview.html](brochures/open-source-rail-overview.html) |
| v0.2 roadmap | [ROADMAP.md](ROADMAP.md) |
| Next release checklist | [releases/next.md](releases/next.md) |
| GitHub metadata | [../.github/repository-metadata.yml](../.github/repository-metadata.yml) |

## Regeneration

Use the root README for the common commands. The short version:

```bash
scripts/regenerate-city.sh samawah
python3 scripts/generate-civil-cost-model.py --check
python3 scripts/generate-introduction-brochure.py --check
PYTHONPATH=mechanical-py/src python3 -m osr_mech.catalog --out mechanical-py/catalog
PYTHONPATH=mechanical-py/src mechanical-py/scripts/freecad_trainset.sh --family light-metro-3car
python3 scripts/repo-health.py --quiet
python3 scripts/generate-doc-index.py
```
