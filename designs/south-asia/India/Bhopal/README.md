# Bhopal — Urban Rail Network

**Country:** IN · **Population:** 2,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bhopal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.80 bn (87.2%) of external capital** and **$3.45 bn of external interest**. Capital plus saved interest totals **$6.25 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bhopal rail network on OpenStreetMap](bhopal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 72 / 14 |
| Route length | 194.6 km double track |
| Coverage / transfer reachability | 59.3% / 60% |
| Estimated station catchment | 1,423,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 245 × 4-car `metro-4car` trainsets (219 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.9 km | 13 | 49 | E Mid ↔ W Mid |
| line-2 | 25.3 km | 11 | 45 | S Mid ↔ N Mid |
| line-3 | 22.0 km | 8 | 35 | SE Mid ↔ N Mid |
| line-4 | 35.8 km | 13 | 54 | SW Mid ↔ NE Outer |
| line-5 | 26.1 km | 7 | 39 | NW Mid ↔ SE Outer |
| line-6 | 59.4 km | 20 | 23 | NW Mid ↔ W Mid |
| **Total** | **194.6 km** | **72 unique** | **245** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 76,703 train-km/day |
| Annual traction demand | 483.8 GWh |
| Station/depot PV / storage | 25.4 MW / 142.0 MWh |
| Aggregate charging power | 103.5 MW |
| Dedicated solar plant | 224.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 14.5 km / 155 kWh |
| Lowest traversal charging margin | line-5: 144 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $697 M |
| Stations | $488 M |
| Depots | $8.0 M |
| Rolling stock | $274 M |
| Dedicated solar plant | $180 M |
| Residual train control | $9.7 M |
| Charging microgrids | $23 M |
| EPC / project services | $105 M |
| **Total city programme** | **$1.79 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $411 M (23.0%) |
| Domestic / local capital | $1.37 bn (77.0%) |
| Annual public construction commitment | $153 M / yr for 5 years |
| Annual post-grace debt service | $110 M / yr |
| External capital saved vs default turnkey sensitivity | $2.80 bn |
| Capital + lifetime external interest saved | $6.25 bn |
| Annual OPEX | $42 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 654 assets / 2,818 tasks | [`bhopal-operations-manifest.json`](operations/bhopal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bhopal.toml`](bhopal.toml) | Expanded simulator scenario |
| [`bhopal.corridor.geojson`](bhopal.corridor.geojson) | GIS corridor and stations |
| [`bhopal.design-quality.yaml`](bhopal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh bhopal
```
