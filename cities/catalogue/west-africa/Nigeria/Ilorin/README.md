# Ilorin — Urban Rail Network

**Country:** NG · **Population:** 1,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ilorin-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$783 M (86.5%) of external capital** and **$981 M of external interest**. Capital plus saved interest totals **$1.76 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ilorin rail network on OpenStreetMap](ilorin-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 2 |
| Route length | 56.8 km double track |
| Coverage / transfer reachability | 54.9% / 67% |
| Estimated station catchment | 549,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 124 × 3-car `light-metro-3car` trainsets (111 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.9 km | 10 | 45 | SW Mid ↔ E Outer |
| line-2 | 21.7 km | 10 | 48 | W Mid ↔ NE Outer |
| line-3 | 14.2 km | 6 | 31 | NW Mid ↔ SW Outer |
| **Total** | **56.8 km** | **26 unique** | **124** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 26,416 train-km/day |
| Annual traction demand | 125.0 GWh |
| Station/depot PV / storage | 12.2 MW / 52.0 MWh |
| Aggregate charging power | 12.5 MW |
| Dedicated solar plant | 68.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.7 km / 42 kWh |
| Lowest traversal charging margin | line-3: 54 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $184 M |
| Stations | $110 M |
| Depots | $8.0 M |
| Rolling stock | $112 M |
| Dedicated solar plant | $54 M |
| Residual train control | $2.8 M |
| Charging microgrids | $2.7 M |
| EPC / project services | $29 M |
| **Total city programme** | **$503 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $122 M (24.3%) |
| Domestic / local capital | $381 M (75.7%) |
| Annual public construction commitment | $57 M / yr for 7 years |
| Annual post-grace debt service | $49 M / yr |
| External capital saved vs default turnkey sensitivity | $783 M |
| Capital + lifetime external interest saved | $1.76 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 277 assets / 1,268 tasks | [`ilorin-operations-manifest.json`](operations/ilorin-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ilorin.toml`](ilorin.toml) | Expanded simulator scenario |
| [`ilorin.corridor.geojson`](ilorin.corridor.geojson) | GIS corridor and stations |
| [`ilorin.design-quality.yaml`](ilorin.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ilorin
```
