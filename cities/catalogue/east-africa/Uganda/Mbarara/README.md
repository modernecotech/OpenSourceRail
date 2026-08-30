# Mbarara — Urban Rail Network

**Country:** UG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbarara-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$707 M (86.4%) of external capital** and **$887 M of external interest**. Capital plus saved interest totals **$1.59 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mbarara rail network on OpenStreetMap](mbarara-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 1 |
| Route length | 53.0 km double track |
| Coverage / transfer reachability | 78.4% / 100% |
| Estimated station catchment | 392,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 113 × 3-car `light-metro-3car` trainsets (102 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.2 km | 6 | 28 | E Mid ↔ SW Mid |
| line-2 | 15.1 km | 7 | 32 | NW Outer ↔ SE Mid |
| line-3 | 24.7 km | 9 | 53 | SW Outer ↔ NE Outer |
| **Total** | **53.0 km** | **22 unique** | **113** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,623 train-km/day |
| Annual traction demand | 116.5 GWh |
| Station/depot PV / storage | 10.4 MW / 49.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 64.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 8.5 km / 64 kWh |
| Lowest traversal charging margin | line-1: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $160 M |
| Stations | $102 M |
| Depots | $8.0 M |
| Rolling stock | $102 M |
| Dedicated solar plant | $52 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $26 M |
| **Total city programme** | **$455 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $111 M (24.5%) |
| Domestic / local capital | $343 M (75.5%) |
| Annual public construction commitment | $53 M / yr for 7 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $707 M |
| Capital + lifetime external interest saved | $1.59 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 241 assets / 1,122 tasks | [`mbarara-operations-manifest.json`](operations/mbarara-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbarara.toml`](mbarara.toml) | Expanded simulator scenario |
| [`mbarara.corridor.geojson`](mbarara.corridor.geojson) | GIS corridor and stations |
| [`mbarara.design-quality.yaml`](mbarara.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mbarara
```
