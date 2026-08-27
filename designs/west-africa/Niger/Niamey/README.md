# Niamey — Urban Rail Network

**Country:** NE · **Population:** 1,407,635 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Niamey-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.09 bn (87.3%) of external capital** and **$2.70 bn of external interest**. Capital plus saved interest totals **$4.79 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Niamey rail network on OpenStreetMap](niamey-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 54 / 11 |
| Route length | 157.6 km double track |
| Coverage / transfer reachability | 67.6% / 40% |
| Estimated station catchment | 951,561 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 186 × 4-car `metro-4car` trainsets (168 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.3 km | 10 | 43 | SE Outer ↔ N Mid |
| line-2 | 18.9 km | 7 | 30 | NW Mid ↔ E Mid |
| line-3 | 16.8 km | 7 | 29 | NE Mid ↔ SW Mid |
| line-4 | 21.7 km | 7 | 32 | W Mid ↔ SE Outer |
| line-5 | 19.5 km | 7 | 31 | NW Outer ↔ S Mid |
| line-6 | 53.5 km | 16 | 21 | NW Mid ↔ W Mid |
| **Total** | **157.6 km** | **54 unique** | **186** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 60,849 train-km/day |
| Annual traction demand | 383.8 GWh |
| Station/depot PV / storage | 20.9 MW / 119.5 MWh |
| Aggregate charging power | 81.0 MW |
| Dedicated solar plant | 162.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.9 km / 77 kWh |
| Lowest traversal charging margin | line-4: 127 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $554 M |
| Stations | $327 M |
| Depots | $8.0 M |
| Rolling stock | $208 M |
| Dedicated solar plant | $130 M |
| Residual train control | $7.9 M |
| Charging microgrids | $18 M |
| EPC / project services | $79 M |
| **Total city programme** | **$1.33 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $305 M (22.9%) |
| Domestic / local capital | $1.03 bn (77.1%) |
| Annual public construction commitment | $108 M / yr for 10 years |
| Annual post-grace debt service | $99 M / yr |
| External capital saved vs default turnkey sensitivity | $2.09 bn |
| Capital + lifetime external interest saved | $4.79 bn |
| Annual OPEX | $30 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 496 assets / 2,132 tasks | [`niamey-operations-manifest.json`](operations/niamey-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`niamey.toml`](niamey.toml) | Expanded simulator scenario |
| [`niamey.corridor.geojson`](niamey.corridor.geojson) | GIS corridor and stations |
| [`niamey.design-quality.yaml`](niamey.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh niamey
```
