# Nyala — Urban Rail Network

**Country:** SD · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nyala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$671 M (87.3%) of external capital** and **$866 M of external interest**. Capital plus saved interest totals **$1.54 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nyala rail network on OpenStreetMap](nyala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 20 / 1 |
| Route length | 46.7 km double track |
| Coverage / transfer reachability | 61.4% / 100% |
| Estimated station catchment | 368,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 99 × 3-car `light-metro-3car` trainsets (89 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.4 km | 8 | 41 | SW Outer ↔ E Outer |
| line-2 | 15.3 km | 7 | 32 | N Outer ↔ S Outer |
| line-3 | 11.9 km | 5 | 26 | SE Mid ↔ NW Outer |
| **Total** | **46.7 km** | **20 unique** | **99** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,707 train-km/day |
| Annual traction demand | 102.7 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 41.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.6 km / 29 kWh |
| Lowest traversal charging margin | line-2: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $187 M |
| Stations | $79 M |
| Depots | $8.0 M |
| Rolling stock | $89 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.3 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $26 M |
| **Total city programme** | **$427 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $98 M (22.9%) |
| Domestic / local capital | $329 M (77.1%) |
| Annual public construction commitment | $50 M / yr for 10 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $671 M |
| Capital + lifetime external interest saved | $1.54 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 217 assets / 1,000 tasks | [`nyala-operations-manifest.json`](operations/nyala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nyala.toml`](nyala.toml) | Expanded simulator scenario |
| [`nyala.corridor.geojson`](nyala.corridor.geojson) | GIS corridor and stations |
| [`nyala.design-quality.yaml`](nyala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh nyala
```
