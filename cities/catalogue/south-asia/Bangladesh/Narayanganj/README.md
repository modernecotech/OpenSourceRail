# Narayanganj — Urban Rail Network

**Country:** BD · **Population:** 950,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Narayanganj-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.03 bn (86.6%) of external capital** and **$1.29 bn of external interest**. Capital plus saved interest totals **$2.31 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Narayanganj rail network on OpenStreetMap](narayanganj-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 28 / 3 |
| Route length | 75.3 km double track |
| Coverage / transfer reachability | 49.6% / 100% |
| Estimated station catchment | 471,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 157 × 3-car `light-metro-3car` trainsets (141 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.8 km | 11 | 63 | SE Outer ↔ NW Outer |
| line-2 | 22.7 km | 8 | 47 | NW Outer ↔ E Outer |
| line-3 | 22.8 km | 9 | 47 | S Outer ↔ NE Mid |
| **Total** | **75.3 km** | **28 unique** | **157** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 35,032 train-km/day |
| Annual traction demand | 165.7 GWh |
| Station/depot PV / storage | 13.1 MW / 53.5 MWh |
| Aggregate charging power | 14.0 MW |
| Dedicated solar plant | 93.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.8 km / 51 kWh |
| Lowest traversal charging margin | line-3: 70 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $272 M |
| Stations | $116 M |
| Depots | $8.0 M |
| Rolling stock | $141 M |
| Dedicated solar plant | $75 M |
| Residual train control | $3.8 M |
| Charging microgrids | $3.0 M |
| EPC / project services | $38 M |
| **Total city programme** | **$658 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $158 M (24.0%) |
| Domestic / local capital | $500 M (76.0%) |
| Annual public construction commitment | $55 M / yr for 7 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $1.03 bn |
| Capital + lifetime external interest saved | $2.31 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 325 assets / 1,536 tasks | [`narayanganj-operations-manifest.json`](operations/narayanganj-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`narayanganj.toml`](narayanganj.toml) | Expanded simulator scenario |
| [`narayanganj.corridor.geojson`](narayanganj.corridor.geojson) | GIS corridor and stations |
| [`narayanganj.design-quality.yaml`](narayanganj.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh narayanganj
```
