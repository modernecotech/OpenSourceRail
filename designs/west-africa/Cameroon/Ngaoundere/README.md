# Ngaoundere — Urban Rail Network

**Country:** CM · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ngaoundere-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$443 M (87.3%) of external capital** and **$556 M of external interest**. Capital plus saved interest totals **$999 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ngaoundere rail network on OpenStreetMap](ngaoundere-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 29.4 km double track |
| Coverage / transfer reachability | 84.8% / 100% |
| Estimated station catchment | 296,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 64 × 3-car `light-metro-3car` trainsets (57 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.9 km | 7 | 27 | N Outer ↔ S Outer |
| line-2 |  8.6 km | 4 | 19 | NW Outer ↔ SE Outer |
| line-3 |  7.8 km | 4 | 18 | W Outer ↔ NE Mid |
| **Total** | **29.4 km** | **15 unique** | **64** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,661 train-km/day |
| Annual traction demand | 64.6 GWh |
| Station/depot PV / storage | 9.2 MW / 47.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 20.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.3 km / 28 kWh |
| Lowest traversal charging margin | line-2: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $99 M |
| Stations | $80 M |
| Depots | $8.0 M |
| Rolling stock | $58 M |
| Dedicated solar plant | $17 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.7 M |
| EPC / project services | $17 M |
| **Total city programme** | **$282 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $65 M (22.9%) |
| Domestic / local capital | $218 M (77.1%) |
| Annual public construction commitment | $24 M / yr for 7 years |
| Annual post-grace debt service | $20 M / yr |
| External capital saved vs default turnkey sensitivity | $443 M |
| Capital + lifetime external interest saved | $999 M |
| Annual OPEX | $7.1 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 153 assets / 676 tasks | [`ngaoundere-operations-manifest.json`](operations/ngaoundere-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ngaoundere.toml`](ngaoundere.toml) | Expanded simulator scenario |
| [`ngaoundere.corridor.geojson`](ngaoundere.corridor.geojson) | GIS corridor and stations |
| [`ngaoundere.design-quality.yaml`](ngaoundere.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh ngaoundere
```
