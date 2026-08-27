# Benguela — Urban Rail Network

**Country:** AO · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Benguela-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$613 M (86.6%) of external capital** and **$753 M of external interest**. Capital plus saved interest totals **$1.37 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Benguela rail network on OpenStreetMap](benguela-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 50.5 km double track |
| Coverage / transfer reachability | 68.7% / 33% |
| Estimated station catchment | 412,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 110 × 3-car `light-metro-3car` trainsets (98 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.3 km | 8 | 47 | NE Outer ↔ SW Mid |
| line-2 | 16.8 km | 6 | 36 | NE Inner ↔ W Outer |
| line-3 | 12.3 km | 4 | 27 | W Inner ↔ SE Outer |
| **Total** | **50.5 km** | **18 unique** | **110** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,460 train-km/day |
| Annual traction demand | 111.0 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 42.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 58 kWh |
| Lowest traversal charging margin | line-3: 34 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $148 M |
| Stations | $77 M |
| Depots | $8.0 M |
| Rolling stock | $99 M |
| Dedicated solar plant | $34 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $23 M |
| **Total city programme** | **$393 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $95 M (24.2%) |
| Domestic / local capital | $298 M (75.8%) |
| Annual public construction commitment | $44 M / yr for 5 years |
| Annual post-grace debt service | $33 M / yr |
| External capital saved vs default turnkey sensitivity | $613 M |
| Capital + lifetime external interest saved | $1.37 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 220 assets / 1,047 tasks | [`benguela-operations-manifest.json`](operations/benguela-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`benguela.toml`](benguela.toml) | Expanded simulator scenario |
| [`benguela.corridor.geojson`](benguela.corridor.geojson) | GIS corridor and stations |
| [`benguela.design-quality.yaml`](benguela.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh benguela
```
