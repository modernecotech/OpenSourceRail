# Thika — Urban Rail Network

**Country:** KE · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Thika-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$962 M (86.3%) of external capital** and **$1.21 bn of external interest**. Capital plus saved interest totals **$2.17 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Thika rail network on OpenStreetMap](thika-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 28 / 1 |
| Route length | 75.5 km double track |
| Coverage / transfer reachability | 62.5% / 100% |
| Estimated station catchment | 218,750 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 161 × 3-car `light-metro-3car` trainsets (145 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.0 km | 11 | 62 | SW Outer ↔ NE Outer |
| line-2 | 21.3 km | 8 | 46 | E Mid ↔ W Mid |
| line-3 | 25.2 km | 9 | 53 | SW Outer ↔ NE Outer |
| **Total** | **75.5 km** | **28 unique** | **161** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 35,094 train-km/day |
| Annual traction demand | 166.0 GWh |
| Station/depot PV / storage | 11.9 MW / 51.5 MWh |
| Aggregate charging power | 12.0 MW |
| Dedicated solar plant | 95.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.9 km / 74 kWh |
| Lowest traversal charging margin | line-2: 86 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $243 M |
| Stations | $105 M |
| Depots | $8.0 M |
| Rolling stock | $145 M |
| Dedicated solar plant | $76 M |
| Residual train control | $3.8 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $36 M |
| **Total city programme** | **$619 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $153 M (24.7%) |
| Domestic / local capital | $467 M (75.3%) |
| Annual public construction commitment | $63 M / yr for 7 years |
| Annual post-grace debt service | $53 M / yr |
| External capital saved vs default turnkey sensitivity | $962 M |
| Capital + lifetime external interest saved | $2.17 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 326 assets / 1,553 tasks | [`thika-operations-manifest.json`](operations/thika-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`thika.toml`](thika.toml) | Expanded simulator scenario |
| [`thika.corridor.geojson`](thika.corridor.geojson) | GIS corridor and stations |
| [`thika.design-quality.yaml`](thika.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh thika
```
