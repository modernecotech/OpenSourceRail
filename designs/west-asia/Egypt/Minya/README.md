# Minya — Urban Rail Network

**Country:** EG · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Minya-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$684 M (86.7%) of external capital** and **$841 M of external interest**. Capital plus saved interest totals **$1.53 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Minya rail network on OpenStreetMap](minya-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 23 / 1 |
| Route length | 53.2 km double track |
| Coverage / transfer reachability | 68.9% / 100% |
| Estimated station catchment | 413,399 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 114 × 3-car `light-metro-3car` trainsets (102 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.3 km | 9 | 40 | NW Outer ↔ SE Outer |
| line-2 | 17.7 km | 7 | 37 | W Outer ↔ NE Outer |
| line-3 | 17.2 km | 7 | 37 | SW Mid ↔ E Outer |
| **Total** | **53.2 km** | **23 unique** | **114** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,736 train-km/day |
| Annual traction demand | 117.0 GWh |
| Station/depot PV / storage | 11.0 MW / 50.0 MWh |
| Aggregate charging power | 10.5 MW |
| Dedicated solar plant | 48.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.7 km / 70 kWh |
| Lowest traversal charging margin | line-2: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $169 M |
| Stations | $89 M |
| Depots | $8.0 M |
| Rolling stock | $103 M |
| Dedicated solar plant | $39 M |
| Residual train control | $2.7 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $26 M |
| **Total city programme** | **$438 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $105 M (23.9%) |
| Domestic / local capital | $334 M (76.1%) |
| Annual public construction commitment | $46 M / yr for 5 years |
| Annual post-grace debt service | $35 M / yr |
| External capital saved vs default turnkey sensitivity | $684 M |
| Capital + lifetime external interest saved | $1.53 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 248 assets / 1,147 tasks | [`minya-operations-manifest.json`](operations/minya-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`minya.toml`](minya.toml) | Expanded simulator scenario |
| [`minya.corridor.geojson`](minya.corridor.geojson) | GIS corridor and stations |
| [`minya.design-quality.yaml`](minya.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
scripts/regenerate-city.sh minya
```
