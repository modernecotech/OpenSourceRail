# Mandalay — Urban Rail Network

**Country:** MM · **Population:** 1,726,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mandalay-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.05 bn (87.3%) of external capital** and **$3.94 bn of external interest**. Capital plus saved interest totals **$6.99 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mandalay rail network on OpenStreetMap](mandalay-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 75 / 14 |
| Route length | 221.9 km double track |
| Coverage / transfer reachability | 66.9% / 53% |
| Estimated station catchment | 1,154,694 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 276 × 4-car `metro-4car` trainsets (247 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 43.9 km | 15 | 70 | N Outer ↔ S Mid |
| line-2 | 32.3 km | 9 | 48 | NW Mid ↔ SE Outer |
| line-3 | 32.0 km | 10 | 49 | SW Outer ↔ NE Mid |
| line-4 | 25.8 km | 10 | 40 | W Inner ↔ NE Outer |
| line-5 | 27.3 km | 11 | 45 | E Mid ↔ SW Outer |
| line-6 | 60.7 km | 20 | 24 | NW Mid ↔ NW Mid |
| **Total** | **221.9 km** | **75 unique** | **276** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 89,070 train-km/day |
| Annual traction demand | 561.8 GWh |
| Station/depot PV / storage | 23.0 MW / 130.0 MWh |
| Aggregate charging power | 91.5 MW |
| Dedicated solar plant | 245.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 21.6 km / 241 kWh |
| Lowest traversal charging margin | line-2: 119 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $848 M |
| Stations | $434 M |
| Depots | $8.0 M |
| Rolling stock | $309 M |
| Dedicated solar plant | $197 M |
| Residual train control | $11 M |
| Charging microgrids | $21 M |
| EPC / project services | $114 M |
| **Total city programme** | **$1.94 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $444 M (22.8%) |
| Domestic / local capital | $1.50 bn (77.2%) |
| Annual public construction commitment | $206 M / yr for 10 years |
| Annual post-grace debt service | $187 M / yr |
| External capital saved vs default turnkey sensitivity | $3.05 bn |
| Capital + lifetime external interest saved | $6.99 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 692 assets / 3,050 tasks | [`mandalay-operations-manifest.json`](operations/mandalay-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mandalay.toml`](mandalay.toml) | Expanded simulator scenario |
| [`mandalay.corridor.geojson`](mandalay.corridor.geojson) | GIS corridor and stations |
| [`mandalay.design-quality.yaml`](mandalay.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh mandalay
```
