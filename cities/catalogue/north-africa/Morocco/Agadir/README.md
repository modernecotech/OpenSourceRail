# Agadir — Urban Rail Network

**Country:** MA · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Agadir-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.02 bn (86.6%) of external capital** and **$1.26 bn of external interest**. Capital plus saved interest totals **$2.28 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Agadir rail network on OpenStreetMap](agadir-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 30 / 3 |
| Route length | 81.5 km double track |
| Coverage / transfer reachability | 60.6% / 100% |
| Estimated station catchment | 545,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 172 × 3-car `light-metro-3car` trainsets (155 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.6 km | 12 | 61 | SE Outer ↔ NW Mid |
| line-2 | 25.9 km | 9 | 53 | NW Outer ↔ SE Mid |
| line-3 | 27.0 km | 9 | 58 | SE Outer ↔ N Outer |
| **Total** | **81.5 km** | **30 unique** | **172** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 37,893 train-km/day |
| Annual traction demand | 179.2 GWh |
| Station/depot PV / storage | 13.7 MW / 54.5 MWh |
| Aggregate charging power | 15.0 MW |
| Dedicated solar plant | 78.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.2 km / 50 kWh |
| Lowest traversal charging margin | line-2: 65 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $238 M |
| Stations | $146 M |
| Depots | $8.0 M |
| Rolling stock | $155 M |
| Dedicated solar plant | $63 M |
| Residual train control | $4.1 M |
| Charging microgrids | $3.2 M |
| EPC / project services | $39 M |
| **Total city programme** | **$656 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $159 M (24.2%) |
| Domestic / local capital | $497 M (75.8%) |
| Annual public construction commitment | $45 M / yr for 5 years |
| Annual post-grace debt service | $32 M / yr |
| External capital saved vs default turnkey sensitivity | $1.02 bn |
| Capital + lifetime external interest saved | $2.28 bn |
| Annual OPEX | $18 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 353 assets / 1,674 tasks | [`agadir-operations-manifest.json`](operations/agadir-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`agadir.toml`](agadir.toml) | Expanded simulator scenario |
| [`agadir.corridor.geojson`](agadir.corridor.geojson) | GIS corridor and stations |
| [`agadir.design-quality.yaml`](agadir.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh agadir
```
