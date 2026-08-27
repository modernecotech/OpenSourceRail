# Jos — Urban Rail Network

**Country:** NG · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jos-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$610 M (86.9%) of external capital** and **$765 M of external interest**. Capital plus saved interest totals **$1.38 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Jos rail network on OpenStreetMap](jos-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 1 |
| Route length | 45.9 km double track |
| Coverage / transfer reachability | 42.6% / 33% |
| Estimated station catchment | 383,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 102 × 3-car `light-metro-3car` trainsets (91 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.0 km | 8 | 46 | N Outer ↔ S Outer |
| line-2 | 13.3 km | 7 | 30 | N Outer ↔ S Outer |
| line-3 | 11.6 km | 5 | 26 | NE Mid ↔ SE Mid |
| **Total** | **45.9 km** | **20 unique** | **102** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,340 train-km/day |
| Annual traction demand | 100.9 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 36.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.1 km / 26 kWh |
| Lowest traversal charging margin | line-3: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $149 M |
| Stations | $84 M |
| Depots | $8.0 M |
| Rolling stock | $92 M |
| Dedicated solar plant | $29 M |
| Residual train control | $2.3 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $24 M |
| **Total city programme** | **$390 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $92 M (23.6%) |
| Domestic / local capital | $298 M (76.4%) |
| Annual public construction commitment | $45 M / yr for 7 years |
| Annual post-grace debt service | $38 M / yr |
| External capital saved vs default turnkey sensitivity | $610 M |
| Capital + lifetime external interest saved | $1.38 bn |
| Annual OPEX | $10.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 222 assets / 1,023 tasks | [`jos-operations-manifest.json`](operations/jos-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jos.toml`](jos.toml) | Expanded simulator scenario |
| [`jos.corridor.geojson`](jos.corridor.geojson) | GIS corridor and stations |
| [`jos.design-quality.yaml`](jos.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh jos
```
