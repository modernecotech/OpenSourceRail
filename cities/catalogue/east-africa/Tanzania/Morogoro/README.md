# Morogoro — Urban Rail Network

**Country:** TZ · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Morogoro-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$832 M (86.8%) of external capital** and **$1.04 bn of external interest**. Capital plus saved interest totals **$1.88 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Morogoro rail network on OpenStreetMap](morogoro-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 2 |
| Route length | 55.1 km double track |
| Coverage / transfer reachability | 61.0% / 100% |
| Estimated station catchment | 305,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 120 × 3-car `light-metro-3car` trainsets (107 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.1 km | 9 | 48 | E Outer ↔ NW Mid |
| line-2 | 16.2 km | 7 | 36 | SW Outer ↔ NE Mid |
| line-3 | 16.8 km | 8 | 36 | S Outer ↔ NW Mid |
| **Total** | **55.1 km** | **24 unique** | **120** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,600 train-km/day |
| Annual traction demand | 121.1 GWh |
| Station/depot PV / storage | 11.6 MW / 51.0 MWh |
| Aggregate charging power | 11.5 MW |
| Dedicated solar plant | 66.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 53 kWh |
| Lowest traversal charging margin | line-3: 57 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $201 M |
| Stations | $126 M |
| Depots | $8.0 M |
| Rolling stock | $108 M |
| Dedicated solar plant | $53 M |
| Residual train control | $2.8 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $31 M |
| **Total city programme** | **$533 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $126 M (23.7%) |
| Domestic / local capital | $406 M (76.3%) |
| Annual public construction commitment | $48 M / yr for 7 years |
| Annual post-grace debt service | $40 M / yr |
| External capital saved vs default turnkey sensitivity | $832 M |
| Capital + lifetime external interest saved | $1.88 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 262 assets / 1,209 tasks | [`morogoro-operations-manifest.json`](operations/morogoro-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`morogoro.toml`](morogoro.toml) | Expanded simulator scenario |
| [`morogoro.corridor.geojson`](morogoro.corridor.geojson) | GIS corridor and stations |
| [`morogoro.design-quality.yaml`](morogoro.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh morogoro
```
