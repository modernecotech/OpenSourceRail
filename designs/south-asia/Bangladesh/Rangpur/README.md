# Rangpur — Urban Rail Network

**Country:** BD · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rangpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$604 M (86.3%) of external capital** and **$757 M of external interest**. Capital plus saved interest totals **$1.36 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Rangpur rail network on OpenStreetMap](rangpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 46.0 km double track |
| Coverage / transfer reachability | 49.3% / 100% |
| Estimated station catchment | 394,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 99 × 3-car `light-metro-3car` trainsets (89 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.4 km | 6 | 30 | E Mid ↔ W Mid |
| line-2 | 17.7 km | 7 | 37 | NE Outer ↔ S Mid |
| line-3 | 14.9 km | 5 | 32 | SW Mid ↔ NW Outer |
| **Total** | **46.0 km** | **18 unique** | **99** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,374 train-km/day |
| Annual traction demand | 101.1 GWh |
| Station/depot PV / storage | 10.1 MW / 48.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 54.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.9 km / 44 kWh |
| Lowest traversal charging margin | line-2: 58 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $133 M |
| Stations | $88 M |
| Depots | $8.0 M |
| Rolling stock | $89 M |
| Dedicated solar plant | $44 M |
| Residual train control | $2.3 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $23 M |
| **Total city programme** | **$389 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $96 M (24.6%) |
| Domestic / local capital | $293 M (75.4%) |
| Annual public construction commitment | $33 M / yr for 7 years |
| Annual post-grace debt service | $27 M / yr |
| External capital saved vs default turnkey sensitivity | $604 M |
| Capital + lifetime external interest saved | $1.36 bn |
| Annual OPEX | $9.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 208 assets / 971 tasks | [`rangpur-operations-manifest.json`](operations/rangpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rangpur.toml`](rangpur.toml) | Expanded simulator scenario |
| [`rangpur.corridor.geojson`](rangpur.corridor.geojson) | GIS corridor and stations |
| [`rangpur.design-quality.yaml`](rangpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh rangpur
```
