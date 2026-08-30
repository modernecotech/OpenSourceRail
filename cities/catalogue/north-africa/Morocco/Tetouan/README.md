# Tetouan — Urban Rail Network

**Country:** MA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tetouan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$761 M (87.0%) of external capital** and **$936 M of external interest**. Capital plus saved interest totals **$1.70 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tetouan rail network on OpenStreetMap](tetouan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 1 |
| Route length | 54.1 km double track |
| Coverage / transfer reachability | 69.3% / 100% |
| Estimated station catchment | 346,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 115 × 3-car `light-metro-3car` trainsets (103 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.6 km | 7 | 40 | W Mid ↔ NE Outer |
| line-2 | 23.2 km | 8 | 48 | NE Outer ↔ SW Outer |
| line-3 | 12.3 km | 4 | 27 | W Outer ↔ SE Inner |
| **Total** | **54.1 km** | **19 unique** | **115** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,135 train-km/day |
| Annual traction demand | 118.9 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 56.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.4 km / 46 kWh |
| Lowest traversal charging margin | line-3: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $202 M |
| Stations | $94 M |
| Depots | $8.0 M |
| Rolling stock | $104 M |
| Dedicated solar plant | $45 M |
| Residual train control | $2.7 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $29 M |
| **Total city programme** | **$486 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $114 M (23.5%) |
| Domestic / local capital | $372 M (76.5%) |
| Annual public construction commitment | $33 M / yr for 5 years |
| Annual post-grace debt service | $24 M / yr |
| External capital saved vs default turnkey sensitivity | $761 M |
| Capital + lifetime external interest saved | $1.70 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 232 assets / 1,101 tasks | [`tetouan-operations-manifest.json`](operations/tetouan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tetouan.toml`](tetouan.toml) | Expanded simulator scenario |
| [`tetouan.corridor.geojson`](tetouan.corridor.geojson) | GIS corridor and stations |
| [`tetouan.design-quality.yaml`](tetouan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tetouan
```
