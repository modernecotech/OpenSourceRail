# Beni-Suef — Urban Rail Network

**Country:** EG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beni-Suef-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$503 M (86.5%) of external capital** and **$619 M of external interest**. Capital plus saved interest totals **$1.12 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Beni-Suef rail network on OpenStreetMap](beni-suef-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 40.0 km double track |
| Coverage / transfer reachability | 49.1% / 100% |
| Estimated station catchment | 171,850 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 87 × 3-car `light-metro-3car` trainsets (78 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.8 km | 7 | 36 | S Outer ↔ NE Outer |
| line-2 | 13.6 km | 6 | 30 | N Outer ↔ SW Outer |
| line-3 |  9.5 km | 4 | 21 | NW Mid ↔ E Mid |
| **Total** | **40.0 km** | **17 unique** | **87** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,577 train-km/day |
| Annual traction demand | 87.9 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 34.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.7 km / 30 kWh |
| Lowest traversal charging margin | line-3: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $110 M |
| Stations | $76 M |
| Depots | $8.0 M |
| Rolling stock | $78 M |
| Dedicated solar plant | $28 M |
| Residual train control | $2.0 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $19 M |
| **Total city programme** | **$323 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $78 M (24.2%) |
| Domestic / local capital | $245 M (75.8%) |
| Annual public construction commitment | $34 M / yr for 5 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $503 M |
| Capital + lifetime external interest saved | $1.12 bn |
| Annual OPEX | $8.8 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 189 assets / 870 tasks | [`beni-suef-operations-manifest.json`](operations/beni-suef-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beni-suef.toml`](beni-suef.toml) | Expanded simulator scenario |
| [`beni-suef.corridor.geojson`](beni-suef.corridor.geojson) | GIS corridor and stations |
| [`beni-suef.design-quality.yaml`](beni-suef.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beni-suef
```
