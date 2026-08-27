# Nampula — Urban Rail Network

**Country:** MZ · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nampula-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$652 M (86.0%) of external capital** and **$843 M of external interest**. Capital plus saved interest totals **$1.50 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nampula rail network on OpenStreetMap](nampula-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 51.7 km double track |
| Coverage / transfer reachability | 66.5% / 33% |
| Estimated station catchment | 532,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 122 × 3-car `light-metro-3car` trainsets (110 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.0 km | 6 | 40 | SE Mid ↔ W Outer |
| line-2 | 22.4 km | 7 | 52 | NW Outer ↔ SE Outer |
| line-3 | 12.3 km | 4 | 30 | SE Outer ↔ NE Mid |
| **Total** | **51.7 km** | **17 unique** | **122** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,031 train-km/day |
| Annual traction demand | 113.7 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 63.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.9 km / 52 kWh |
| Lowest traversal charging margin | line-3: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $148 M |
| Stations | $76 M |
| Depots | $8.0 M |
| Rolling stock | $110 M |
| Dedicated solar plant | $51 M |
| Residual train control | $2.6 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $24 M |
| **Total city programme** | **$422 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $106 M (25.2%) |
| Domestic / local capital | $315 M (74.8%) |
| Annual public construction commitment | $45 M / yr for 10 years |
| Annual post-grace debt service | $41 M / yr |
| External capital saved vs default turnkey sensitivity | $652 M |
| Capital + lifetime external interest saved | $1.50 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 230 assets / 1,121 tasks | [`nampula-operations-manifest.json`](operations/nampula-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nampula.toml`](nampula.toml) | Expanded simulator scenario |
| [`nampula.corridor.geojson`](nampula.corridor.geojson) | GIS corridor and stations |
| [`nampula.design-quality.yaml`](nampula.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh nampula
```
