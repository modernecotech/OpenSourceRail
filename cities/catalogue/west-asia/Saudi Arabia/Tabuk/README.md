# Tabuk — Urban Rail Network

**Country:** SA · **Population:** 650,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tabuk-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$825 M (86.8%) of external capital** and **$1.01 bn of external interest**. Capital plus saved interest totals **$1.84 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tabuk rail network on OpenStreetMap](tabuk-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 1 |
| Route length | 63.0 km double track |
| Coverage / transfer reachability | 46.5% / 100% |
| Estimated station catchment | 302,250 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 134 × 3-car `light-metro-3car` trainsets (120 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.0 km | 9 | 40 | NE Mid ↔ W Outer |
| line-2 | 21.3 km | 8 | 46 | NW Outer ↔ S Mid |
| line-3 | 22.8 km | 9 | 48 | E Outer ↔ SW Mid |
| **Total** | **63.0 km** | **26 unique** | **134** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 29,312 train-km/day |
| Annual traction demand | 138.7 GWh |
| Station/depot PV / storage | 12.2 MW / 52.0 MWh |
| Aggregate charging power | 12.5 MW |
| Dedicated solar plant | 58.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-1: 52 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $209 M |
| Stations | $106 M |
| Depots | $8.0 M |
| Rolling stock | $121 M |
| Dedicated solar plant | $47 M |
| Residual train control | $3.2 M |
| Charging microgrids | $2.7 M |
| EPC / project services | $31 M |
| **Total city programme** | **$528 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $125 M (23.7%) |
| Domestic / local capital | $402 M (76.3%) |
| Annual public construction commitment | $36 M / yr for 5 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $825 M |
| Capital + lifetime external interest saved | $1.84 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 288 assets / 1,339 tasks | [`tabuk-operations-manifest.json`](operations/tabuk-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tabuk.toml`](tabuk.toml) | Expanded simulator scenario |
| [`tabuk.corridor.geojson`](tabuk.corridor.geojson) | GIS corridor and stations |
| [`tabuk.design-quality.yaml`](tabuk.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tabuk
```
