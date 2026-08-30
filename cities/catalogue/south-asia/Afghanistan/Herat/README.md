# Herat — Urban Rail Network

**Country:** AF · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Herat-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$675 M (86.9%) of external capital** and **$872 M of external interest**. Capital plus saved interest totals **$1.55 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Herat rail network on OpenStreetMap](herat-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 3 |
| Route length | 49.5 km double track |
| Coverage / transfer reachability | 56.9% / 67% |
| Estimated station catchment | 455,199 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 108 × 3-car `light-metro-3car` trainsets (97 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.0 km | 6 | 31 | NE Mid ↔ SW Mid |
| line-2 | 14.3 km | 6 | 31 | S Mid ↔ W Mid |
| line-3 | 21.3 km | 7 | 46 | NW Outer ↔ E Outer |
| **Total** | **49.5 km** | **19 unique** | **108** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,033 train-km/day |
| Annual traction demand | 109.0 GWh |
| Station/depot PV / storage | 9.8 MW / 48.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 44.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 8.5 km / 61 kWh |
| Lowest traversal charging margin | line-2: 58 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $159 M |
| Stations | $102 M |
| Depots | $8.0 M |
| Rolling stock | $97 M |
| Dedicated solar plant | $35 M |
| Residual train control | $2.5 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $26 M |
| **Total city programme** | **$432 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $102 M (23.6%) |
| Domestic / local capital | $330 M (76.4%) |
| Annual public construction commitment | $59 M / yr for 10 years |
| Annual post-grace debt service | $54 M / yr |
| External capital saved vs default turnkey sensitivity | $675 M |
| Capital + lifetime external interest saved | $1.55 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 223 assets / 1,046 tasks | [`herat-operations-manifest.json`](operations/herat-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`herat.toml`](herat.toml) | Expanded simulator scenario |
| [`herat.corridor.geojson`](herat.corridor.geojson) | GIS corridor and stations |
| [`herat.design-quality.yaml`](herat.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh herat
```
