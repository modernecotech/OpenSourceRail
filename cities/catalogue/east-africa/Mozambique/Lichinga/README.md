# Lichinga — Urban Rail Network

**Country:** MZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lichinga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$240 M (88.2%) of external capital** and **$310 M of external interest**. Capital plus saved interest totals **$551 M**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lichinga rail network on OpenStreetMap](lichinga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 8 / 2 |
| Route length | 14.9 km double track |
| Coverage / transfer reachability | 80.4% / 100% |
| Estimated station catchment | 201,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 34 × 2-car `tram-2car` trainsets (30 peak revenue) |
| Peak network throughput | 19,200 passengers/hour |
| Practical service capacity | 178,560 passenger-trips/day |
| Annual paid-trip planning range | 32.6–52.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.7 km | 5 | 20 | N Outer ↔ SE Mid |
| line-2 |  6.2 km | 3 | 14 | NW Mid ↔ E Inner |
| **Total** | **14.9 km** | **8 unique** | **34** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 6,947 train-km/day |
| Annual traction demand | 21.9 GWh |
| Station/depot PV / storage | 7.1 MW / 43.5 MWh |
| Aggregate charging power | 4.0 MW |
| Dedicated solar plant | 6.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.7 km / 19 kWh |
| Lowest traversal charging margin | line-2: 31 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $53 M |
| Stations | $55 M |
| Depots | $8.0 M |
| Rolling stock | $19 M |
| Dedicated solar plant | $5.0 M |
| Residual train control | $747 k |
| Charging microgrids | $1.0 M |
| EPC / project services | $9.6 M |
| **Total city programme** | **$151 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $32 M (21.2%) |
| Domestic / local capital | $119 M (78.8%) |
| Annual public construction commitment | $17 M / yr for 10 years |
| Annual post-grace debt service | $15 M / yr |
| External capital saved vs default turnkey sensitivity | $240 M |
| Capital + lifetime external interest saved | $551 M |
| Annual OPEX | $3.5 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 84 assets / 360 tasks | [`lichinga-operations-manifest.json`](operations/lichinga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lichinga.toml`](lichinga.toml) | Expanded simulator scenario |
| [`lichinga.corridor.geojson`](lichinga.corridor.geojson) | GIS corridor and stations |
| [`lichinga.design-quality.yaml`](lichinga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lichinga
```
