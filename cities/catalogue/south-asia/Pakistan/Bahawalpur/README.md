# Bahawalpur — Urban Rail Network

**Country:** PK · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bahawalpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$630 M (86.8%) of external capital** and **$789 M of external interest**. Capital plus saved interest totals **$1.42 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bahawalpur rail network on OpenStreetMap](bahawalpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 2 |
| Route length | 44.8 km double track |
| Coverage / transfer reachability | 58.1% / 100% |
| Estimated station catchment | 522,899 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 100 × 3-car `light-metro-3car` trainsets (89 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.7 km | 7 | 37 | SW Outer ↔ NE Mid |
| line-2 | 14.9 km | 6 | 34 | NW Outer ↔ E Mid |
| line-3 | 13.3 km | 5 | 29 | E Outer ↔ W Inner |
| **Total** | **44.8 km** | **18 unique** | **100** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,853 train-km/day |
| Annual traction demand | 98.6 GWh |
| Station/depot PV / storage | 9.5 MW / 47.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 40.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-3: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $141 M |
| Stations | $103 M |
| Depots | $8.0 M |
| Rolling stock | $90 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.2 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $24 M |
| **Total city programme** | **$403 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $95 M (23.7%) |
| Domestic / local capital | $307 M (76.3%) |
| Annual public construction commitment | $54 M / yr for 7 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $630 M |
| Capital + lifetime external interest saved | $1.42 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 208 assets / 973 tasks | [`bahawalpur-operations-manifest.json`](operations/bahawalpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bahawalpur.toml`](bahawalpur.toml) | Expanded simulator scenario |
| [`bahawalpur.corridor.geojson`](bahawalpur.corridor.geojson) | GIS corridor and stations |
| [`bahawalpur.design-quality.yaml`](bahawalpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bahawalpur
```
