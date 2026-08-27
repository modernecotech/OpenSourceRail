# Damascus — Urban Rail Network

**Country:** SY · **Population:** 2,503,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damascus-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.57 bn (87.0%) of external capital** and **$3.32 bn of external interest**. Capital plus saved interest totals **$5.90 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Damascus rail network on OpenStreetMap](damascus-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 64 / 13 |
| Route length | 197.9 km double track |
| Coverage / transfer reachability | 76.7% / 87% |
| Estimated station catchment | 1,919,801 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 236 × 4-car `metro-4car` trainsets (212 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.3 km | 10 | 42 | NE Outer ↔ SW Mid |
| line-2 | 26.4 km | 9 | 40 | SE Mid ↔ W Outer |
| line-3 | 29.1 km | 11 | 46 | S Mid ↔ N Outer |
| line-4 | 24.9 km | 9 | 39 | NW Outer ↔ SE Mid |
| line-5 | 27.9 km | 8 | 43 | NE Mid ↔ SW Outer |
| line-6 | 64.3 km | 17 | 26 | W Mid ↔ W Mid |
| **Total** | **197.9 km** | **64 unique** | **236** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 77,092 train-km/day |
| Annual traction demand | 486.2 GWh |
| Station/depot PV / storage | 22.7 MW / 128.5 MWh |
| Aggregate charging power | 90.0 MW |
| Dedicated solar plant | 229.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 9.7 km / 104 kWh |
| Lowest traversal charging margin | line-4: 146 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $670 M |
| Stations | $391 M |
| Depots | $8.0 M |
| Rolling stock | $264 M |
| Dedicated solar plant | $183 M |
| Residual train control | $9.9 M |
| Charging microgrids | $20 M |
| EPC / project services | $95 M |
| **Total city programme** | **$1.64 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $383 M (23.3%) |
| Domestic / local capital | $1.26 bn (76.7%) |
| Annual public construction commitment | $244 M / yr for 10 years |
| Annual post-grace debt service | $226 M / yr |
| External capital saved vs default turnkey sensitivity | $2.57 bn |
| Capital + lifetime external interest saved | $5.90 bn |
| Annual OPEX | $36 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 601 assets / 2,629 tasks | [`damascus-operations-manifest.json`](operations/damascus-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damascus.toml`](damascus.toml) | Expanded simulator scenario |
| [`damascus.corridor.geojson`](damascus.corridor.geojson) | GIS corridor and stations |
| [`damascus.design-quality.yaml`](damascus.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh damascus
```
