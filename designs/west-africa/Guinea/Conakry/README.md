# Conakry — Urban Rail Network

**Country:** GN · **Population:** 2,010,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Conakry-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$922 M (86.5%) of external capital** and **$1.19 bn of external interest**. Capital plus saved interest totals **$2.11 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Conakry rail network on OpenStreetMap](conakry-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 2 |
| Route length | 82.0 km double track |
| Coverage / transfer reachability | 80.6% / 67% |
| Estimated station catchment | 1,620,060 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 84 × 4-car `metro-4car` trainsets (75 peak revenue) |
| Peak network throughput | 57,600 passengers/hour |
| Practical service capacity | 446,400 passenger-trips/day |
| Annual paid-trip planning range | 81.5–130.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.9 km | 9 | 41 | NE Outer ↔ SW Mid |
| line-2 | 19.8 km | 6 | 29 | SW Inner ↔ NE Outer |
| line-3 | 35.2 km | 11 | 14 | N Inner ↔ N Inner |
| **Total** | **82.0 km** | **26 unique** | **84** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,162 one-way journeys / 29,930 train-km/day |
| Annual traction demand | 188.8 GWh |
| Station/depot PV / storage | 12.5 MW / 77.5 MWh |
| Aggregate charging power | 39.0 MW |
| Dedicated solar plant | 109.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.1 km / 61 kWh |
| Lowest traversal charging margin | line-2: 125 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $243 M |
| Stations | $114 M |
| Depots | $8.0 M |
| Rolling stock | $94 M |
| Dedicated solar plant | $88 M |
| Residual train control | $4.1 M |
| Charging microgrids | $8.6 M |
| EPC / project services | $33 M |
| **Total city programme** | **$592 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $144 M (24.3%) |
| Domestic / local capital | $448 M (75.7%) |
| Annual public construction commitment | $51 M / yr for 10 years |
| Annual post-grace debt service | $47 M / yr |
| External capital saved vs default turnkey sensitivity | $922 M |
| Capital + lifetime external interest saved | $2.11 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 230 assets / 983 tasks | [`conakry-operations-manifest.json`](operations/conakry-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`conakry.toml`](conakry.toml) | Expanded simulator scenario |
| [`conakry.corridor.geojson`](conakry.corridor.geojson) | GIS corridor and stations |
| [`conakry.design-quality.yaml`](conakry.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh conakry
```
