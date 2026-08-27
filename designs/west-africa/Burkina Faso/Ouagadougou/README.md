# Ouagadougou — Urban Rail Network

**Country:** BF · **Population:** 2,531,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ouagadougou-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.70 bn (86.9%) of external capital** and **$3.49 bn of external interest**. Capital plus saved interest totals **$6.19 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ouagadougou rail network on OpenStreetMap](ouagadougou-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 77 / 9 |
| Route length | 221.6 km double track |
| Coverage / transfer reachability | 60.5% / 60% |
| Estimated station catchment | 1,531,255 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 271 × 4-car `metro-4car` trainsets (243 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.4 km | 12 | 59 | SW Mid ↔ NE Outer |
| line-2 | 24.2 km | 10 | 41 | E Mid ↔ W Mid |
| line-3 | 28.5 km | 11 | 47 | S Outer ↔ NE Mid |
| line-4 | 32.7 km | 12 | 51 | NW Outer ↔ SE Mid |
| line-5 | 32.4 km | 10 | 48 | S Mid ↔ N Outer |
| line-6 | 65.4 km | 22 | 25 | W Mid ↔ W Mid |
| **Total** | **221.6 km** | **77 unique** | **271** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 87,812 train-km/day |
| Annual traction demand | 553.8 GWh |
| Station/depot PV / storage | 26.9 MW / 149.5 MWh |
| Aggregate charging power | 111.0 MW |
| Dedicated solar plant | 237.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 14.2 km / 158 kWh |
| Lowest traversal charging margin | line-5: 142 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $691 M |
| Stations | $398 M |
| Depots | $8.0 M |
| Rolling stock | $304 M |
| Dedicated solar plant | $190 M |
| Residual train control | $11 M |
| Charging microgrids | $24 M |
| EPC / project services | $100 M |
| **Total city programme** | **$1.73 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $407 M (23.6%) |
| Domestic / local capital | $1.32 bn (76.4%) |
| Annual public construction commitment | $145 M / yr for 10 years |
| Annual post-grace debt service | $132 M / yr |
| External capital saved vs default turnkey sensitivity | $2.70 bn |
| Capital + lifetime external interest saved | $6.19 bn |
| Annual OPEX | $39 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 704 assets / 3,074 tasks | [`ouagadougou-operations-manifest.json`](operations/ouagadougou-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ouagadougou.toml`](ouagadougou.toml) | Expanded simulator scenario |
| [`ouagadougou.corridor.geojson`](ouagadougou.corridor.geojson) | GIS corridor and stations |
| [`ouagadougou.design-quality.yaml`](ouagadougou.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh ouagadougou
```
