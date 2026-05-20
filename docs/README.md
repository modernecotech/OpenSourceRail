# OpenSourceRail Documentation

This is the documentation front door. The repository intentionally keeps
source code, generated city designs, mechanical CAD, hardware, and
safety evidence in separate top-level areas; this page links those areas
without duplicating them.

## Main Reading Paths

| Reader | Start with |
|---|---|
| Project reviewer | [ARCHITECTURE.md](ARCHITECTURE.md), then [RFCs](rfcs/) |
| New contributor | [GLOSSARY.md](GLOSSARY.md), then [ARCHITECTURE.md](ARCHITECTURE.md) |
| City/network planner | [designs/README.md](../designs/README.md), [cost model](cost-model.md), [civil OSR-ALN format](civil/osr-aln-format.md) |
| Rolling-stock engineer | [rolling-stock/light-metro-3car/README.md](rolling-stock/light-metro-3car/README.md) |
| Mechanical/CAD reviewer | [mechanical-py/README.md](../mechanical-py/README.md) and [mechanical-py/catalog/](../mechanical-py/catalog/) |
| Hardware reviewer | [hardware/README.md](../hardware/README.md) and [hardware/rolling-stock-integration.md](../hardware/rolling-stock-integration.md) |
| Operator/maintainer | [operations/README.md](operations/README.md) |
| Safety/certification reviewer | [certification/README.md](certification/README.md), [safety-case/README.md](safety-case/README.md), [formal/tla/README.md](../formal/tla/README.md) |
| v0.2 contributor | [ROADMAP.md](ROADMAP.md) |

## Documentation Sets

| Folder | Contents |
|---|---|
| [rfcs/](rfcs/README.md) | Design decisions and standards for architecture, rolling stock, track, stations, depots, driverless operation, hardware, energy, and safety |
| [rolling-stock/](rolling-stock/README.md) | Light-metro trainset package: GA, body, bogie, traction, BOM, fabrication plan, drawing register, compliance |
| [civil/](civil/README.md) | Alignment interchange format and civil tool bridge docs |
| [stations/](stations/README.md) | Station design material |
| [operations/](operations/) | Rulebook and operating procedures |
| [certification/](certification/) | EN 62267 pre-submission pack: system description, hazards, safety requirements, evidence, compliance matrix |
| [safety-case/](safety-case/) | GSN safety-case source and generated views |
| [hardware/](hardware/) | Hardware bring-up docs |
| [screenshots/](screenshots/) | Generated UI/CAD screenshots used by READMEs |

## Canonical Design Artifacts

| Artifact | Location |
|---|---|
| Generated city catalogue | [designs/README.md](../designs/README.md) |
| City source list | [lib/city-batches/world-sample.toml](../lib/city-batches/world-sample.toml) |
| Mechanical STEP catalogue | [mechanical-py/catalog/](../mechanical-py/catalog/) |
| Rolling-stock BOM | [rolling-stock/light-metro-3car/bom-skeleton.md](rolling-stock/light-metro-3car/bom-skeleton.md) |
| Generated BOM CSV | [build/bom/rolling_stock_bom.csv](../build/bom/rolling_stock_bom.csv) |
| Hardware host-class matrix | [hardware/rolling-stock-integration.md](../hardware/rolling-stock-integration.md) |
| Hardware release checklist | [hardware/release-checklist.md](../hardware/release-checklist.md) |
| Rolling-stock v2 release checklist | [rolling-stock/light-metro-3car/v2-release-checklist.md](rolling-stock/light-metro-3car/v2-release-checklist.md) |
| Certification release gaps | [certification/release-gap-register.md](certification/release-gap-register.md) |
| Civil deployment release gates | [civil/deployment-release-checklist.md](civil/deployment-release-checklist.md) |
| Operations validation gates | [operations/validation-checklist.md](operations/validation-checklist.md) |
| Reader-edition PDF | [opensource-rail-docs-book.pdf](../opensource-rail-docs-book.pdf) |
| v0.2 roadmap | [ROADMAP.md](ROADMAP.md) |

## Regeneration

Use the root README for the common commands. The short version:

```bash
scripts/regenerate-city.sh samawah
PYTHONPATH=mechanical-py/src python3 -m osr_mech.catalog --out mechanical-py/catalog
python3 scripts/repo-health.py --quiet
```
