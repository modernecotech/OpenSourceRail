# Rajkot — Urban Rail Network

**Country:** IN · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rajkot-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.80 bn (87.2%) of external capital** and **$2.21 bn of external interest**. Capital plus saved interest totals **$4.00 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Rajkot rail network on OpenStreetMap](rajkot-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 47 / 6 |
| Route length | 133.9 km double track |
| Coverage / transfer reachability | 81.7% / 100% |
| Estimated station catchment | 1,470,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 162 × 4-car `metro-4car` trainsets (145 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.4 km | 10 | 43 | NE Outer ↔ S Mid |
| line-2 | 14.5 km | 7 | 28 | E Mid ↔ SW Mid |
| line-3 | 14.8 km | 6 | 27 | SE Mid ↔ NW Inner |
| line-4 | 23.7 km | 8 | 40 | W Mid ↔ SE Outer |
| line-5 | 55.4 km | 16 | 24 | NW Outer ↔ NW Outer |
| **Total** | **133.9 km** | **47 unique** | **162** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 49,364 train-km/day |
| Annual traction demand | 311.3 GWh |
| Station/depot PV / storage | 15.8 MW / 94.0 MWh |
| Aggregate charging power | 55.5 MW |
| Dedicated solar plant | 145.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 35.9 km / 386 kWh |
| Lowest traversal charging margin | line-3: 168 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $483 M |
| Stations | $268 M |
| Depots | $8.0 M |
| Rolling stock | $181 M |
| Dedicated solar plant | $116 M |
| Residual train control | $6.7 M |
| Charging microgrids | $13 M |
| EPC / project services | $67 M |
| **Total city programme** | **$1.14 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $262 M (23.0%) |
| Domestic / local capital | $881 M (77.0%) |
| Annual public construction commitment | $98 M / yr for 5 years |
| Annual post-grace debt service | $71 M / yr |
| External capital saved vs default turnkey sensitivity | $1.80 bn |
| Capital + lifetime external interest saved | $4.00 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 418 assets / 1,823 tasks | [`rajkot-operations-manifest.json`](operations/rajkot-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rajkot.toml`](rajkot.toml) | Expanded simulator scenario |
| [`rajkot.corridor.geojson`](rajkot.corridor.geojson) | GIS corridor and stations |
| [`rajkot.design-quality.yaml`](rajkot.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh rajkot
```
