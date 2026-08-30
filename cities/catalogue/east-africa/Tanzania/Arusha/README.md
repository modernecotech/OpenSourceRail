# Arusha — Urban Rail Network

**Country:** TZ · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Arusha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$794 M (86.4%) of external capital** and **$996 M of external interest**. Capital plus saved interest totals **$1.79 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Arusha rail network on OpenStreetMap](arusha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 1 |
| Route length | 63.9 km double track |
| Coverage / transfer reachability | 60.6% / 100% |
| Estimated station catchment | 424,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 153 × 3-car `light-metro-3car` trainsets (137 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.7 km | 7 | 46 | N Mid ↔ SE Mid |
| line-2 | 20.0 km | 7 | 47 | SW Mid ↔ E Outer |
| line-3 | 25.1 km | 7 | 60 | S Outer ↔ NW Outer |
| **Total** | **63.9 km** | **21 unique** | **153** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 29,706 train-km/day |
| Annual traction demand | 140.5 GWh |
| Station/depot PV / storage | 10.7 MW / 49.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 55.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 9.1 km / 76 kWh |
| Lowest traversal charging margin | line-2: 45 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $187 M |
| Stations | $98 M |
| Depots | $8.0 M |
| Rolling stock | $138 M |
| Dedicated solar plant | $45 M |
| Residual train control | $3.2 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $30 M |
| **Total city programme** | **$511 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $125 M (24.5%) |
| Domestic / local capital | $386 M (75.5%) |
| Annual public construction commitment | $46 M / yr for 7 years |
| Annual post-grace debt service | $38 M / yr |
| External capital saved vs default turnkey sensitivity | $794 M |
| Capital + lifetime external interest saved | $1.79 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 284 assets / 1,399 tasks | [`arusha-operations-manifest.json`](operations/arusha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`arusha.toml`](arusha.toml) | Expanded simulator scenario |
| [`arusha.corridor.geojson`](arusha.corridor.geojson) | GIS corridor and stations |
| [`arusha.design-quality.yaml`](arusha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh arusha
```
