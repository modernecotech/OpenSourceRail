# Gujranwala — Urban Rail Network

**Country:** PK · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gujranwala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.23 bn (86.8%) of external capital** and **$2.80 bn of external interest**. Capital plus saved interest totals **$5.03 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gujranwala rail network on OpenStreetMap](gujranwala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 55 / 8 |
| Route length | 187.2 km double track |
| Coverage / transfer reachability | 65.3% / 70% |
| Estimated station catchment | 1,501,900 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 218 × 4-car `metro-4car` trainsets (196 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.2 km | 12 | 60 | NW Mid ↔ S Outer |
| line-2 | 32.9 km | 11 | 52 | NE Outer ↔ SW Inner |
| line-3 | 20.0 km | 6 | 32 | NW Mid ↔ S Mid |
| line-4 | 32.6 km | 10 | 51 | W Mid ↔ SE Outer |
| line-5 | 62.4 km | 16 | 23 | NW Mid ↔ NW Mid |
| **Total** | **187.2 km** | **55 unique** | **218** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 72,535 train-km/day |
| Annual traction demand | 457.5 GWh |
| Station/depot PV / storage | 19.4 MW / 112.0 MWh |
| Aggregate charging power | 73.5 MW |
| Dedicated solar plant | 217.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 13.2 km / 142 kWh |
| Lowest traversal charging margin | line-3: 155 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $593 M |
| Stations | $301 M |
| Depots | $8.0 M |
| Rolling stock | $244 M |
| Dedicated solar plant | $174 M |
| Residual train control | $9.4 M |
| Charging microgrids | $16 M |
| EPC / project services | $82 M |
| **Total city programme** | **$1.43 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $338 M (23.7%) |
| Domestic / local capital | $1.09 bn (76.3%) |
| Annual public construction commitment | $190 M / yr for 7 years |
| Annual post-grace debt service | $165 M / yr |
| External capital saved vs default turnkey sensitivity | $2.23 bn |
| Capital + lifetime external interest saved | $5.03 bn |
| Annual OPEX | $33 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 529 assets / 2,358 tasks | [`gujranwala-operations-manifest.json`](operations/gujranwala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gujranwala.toml`](gujranwala.toml) | Expanded simulator scenario |
| [`gujranwala.corridor.geojson`](gujranwala.corridor.geojson) | GIS corridor and stations |
| [`gujranwala.design-quality.yaml`](gujranwala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gujranwala
```
